#!/usr/bin/env python3
"""Parse ETH Zurich Statistics MSc course catalogue PDFs into structured JSON."""
import re, json, subprocess, sys, os

# Point PDF_DIR at a folder holding the two catalogue prints. Filenames are
# matched on "Autumn"/"Spring" so the ETH export names work unchanged.
PDF_DIR = os.environ.get("PDF_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf"))
OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json"))


def find(term):
    hits = sorted(f for f in os.listdir(PDF_DIR)
                  if f.lower().endswith(".pdf") and term.lower() in f.lower())
    if not hits:
        sys.exit(f"No {term} catalogue PDF found in {PDF_DIR}. "
                 f"Set PDF_DIR, or see README for how to produce the prints.")
    return os.path.join(PDF_DIR, hits[0])


FILES = [("Autumn 2026", find("Autumn")), ("Spring 2026", find("Spring"))]

CODE_RE = re.compile(r'^(\s*)(\d{3}-\d{4}-\d{2}[A-Z])(\s+)(.*)$')
# type | credits | optional hours | lecturers
HEAD_RE = re.compile(
    r'^(?P<title>.*?)\s{2,}(?P<type>[WOEZGD])\s+'
    r'(?P<ects>\d+(?:\.\d+)?)\s+credits?\s*'
    r'(?P<hours>(?:\d+(?:\.\d+)?\s*[A-Z](?:\s*\+\s*\d+(?:\.\d+)?\s*[A-Z])*)?)\s*'
    r'(?P<lect>.*)$'
)
# same, but tolerates a single space before the type column (long titles that
# collide with the Type column, e.g. "... and Anytime- W  4 credits 2S")
HEAD_RE_LOOSE = re.compile(
    r'^(?P<title>.*?)\s+(?P<type>[WOEZGD])\s+'
    r'(?P<ects>\d+(?:\.\d+)?)\s+credits?\s*'
    r'(?P<hours>(?:\d+(?:\.\d+)?\s*[A-Z](?:\s*\+\s*\d+(?:\.\d+)?\s*[A-Z])*)?)\s*'
    r'(?P<lect>.*)$'
)
JUNK = re.compile(
    r'^\s*(\d{1,2}/\d{1,2}/\d{2},|Course Catalogue - ETH Zurich\s*$|https://vvz\.ethz\.ch|'
    r'Course Catalogue\s*$|Search result:|Course units\s+Catalogue data|\d+/\d+\s*$)'
)
# continuation fragments of a wrapped field label
LABEL_CONT = {"objective", "Notice", "notes", "of instruction", "/ Notice", "assessment"}
CANON = {
    "Abstract": "abstract",
    "Learning objective": "learning_objective",
    "Objective": "learning_objective",
    "Content": "content",
    "Lecture notes": "lecture_notes",
    "Literature": "literature",
    "Prerequisites / Notice": "prerequisites_notice",
    "Competencies": "competencies",
    "Fee": "fee",
}


def clean(path):
    txt = subprocess.run(["pdftotext", "-layout", path, "-"],
                         capture_output=True, text=True, check=True).stdout
    out = []
    for l in txt.split("\n"):
        if JUNK.match(l) or l.strip() == "\x0c":
            continue
        out.append(l.replace("\x0c", ""))
    return out


def parse_head(rest, code):
    m = HEAD_RE.match(rest) or HEAD_RE_LOOSE.match(rest)
    if not m:
        return None
    d = m.groupdict()
    return {
        "code": code,
        "title": d["title"].strip(),
        "type": d["type"],
        "ects": float(d["ects"]),
        "hours": re.sub(r'\s+', ' ', d["hours"]).strip(),
        "lecturers": d["lect"].strip(),
    }


def flush_field(course, label, buf):
    if not label:
        return
    key = CANON.get(label.strip(), re.sub(r'[^a-z0-9]+', '_', label.strip().lower()).strip('_'))
    val = "\n".join(buf).strip()
    val = re.sub(r'\n{3,}', '\n\n', val)
    if val:
        course.setdefault(key, "")
        course[key] = (course[key] + "\n" + val).strip() if course[key] else val


def parse(semester, path):
    lines = clean(path)
    courses, sec, sub = [], None, None
    cur = None            # current course dict
    valcol = None         # column where field values start
    titlecol = lectcol = None
    label, buf = None, []
    unparsed = []

    def close():
        nonlocal cur, label, buf
        if cur:
            flush_field(cur, label, buf)
            courses.append(cur)
        cur, label, buf = None, None, []

    i = 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        ind = len(l) - len(l.lstrip())
        if not s:
            if cur and label:
                buf.append("")
            i += 1
            continue

        # --- structural headers -------------------------------------------
        if ind in (5, 7, 11) and len(s) < 70 and not s.startswith("Number"):
            if ind == 7:
                close(); sec, sub = s, None
            elif ind == 11:
                close(); sub = s
            i += 1
            continue
        if s.startswith("Number") and "Title" in s:
            close(); i += 1; continue

        # --- course header row --------------------------------------------
        m = CODE_RE.match(l)
        if m and len(m.group(1)) <= 8:
            close()
            titlecol = len(m.group(1)) + len(m.group(2)) + len(m.group(3))
            head = parse_head(m.group(4), m.group(2))
            if not head:
                unparsed.append(l); i += 1; continue
            lectcol = l.rfind(head["lecturers"]) if head["lecturers"] else 10 ** 6
            cur = {"semester": semester, "section": sec, "subsection": sub,
                   "notes": [], **head}
            valcol = None
            label, buf = None, []
            i += 1
            continue

        if cur is None:
            i += 1
            continue

        # --- field label / value line -------------------------------------
        # Labels always sit in the left gutter (indent <= 8); values and their
        # continuations sit in the right column. Computing this per line rather
        # than once per course is essential: the value column drifts between
        # pages, so a fixed offset corrupts any course spanning a page break.
        if ind > 8:
            if label is None:
                # Continuation of the header row. A single line can carry BOTH a
                # wrapped title and a wrapped lecturer list, in their own columns
                # ("Applications" ... "C. Lorentzen-Geiser"), so split at the
                # lecturer column rather than treating the line as one value.
                split = (lectcol if lectcol < 10 ** 6 and len(l) > lectcol
                         and not l[max(0, lectcol - 3):lectcol].strip() else None)
                left = (l[:split] if split else l).strip()
                right = l[split:].strip() if split else ""
                if left:
                    if ind == titlecol:
                        # a word hyphenated across the line break rejoins closed
                        cur["title"] += ("" if cur["title"].endswith("-") else " ") + left
                    else:
                        cur["notes"].append(left)
                if right:
                    cur["lecturers"] += " " + right
            else:
                buf.append(re.sub(r'\s{2,}', ' | ', s) if label.strip() == "Competencies" else s)
            i += 1
            continue

        fm = re.match(r'^\s*(?P<lab>\S.*?)(?:\s{2,}(?P<val>\S.*?))?\s*$', l)
        prefix, value = fm.group("lab"), fm.group("val") or ""
        if prefix:
            if prefix in LABEL_CONT or prefix[0].islower():
                label = (label or "") + " " + prefix
            else:
                flush_field(cur, label, buf)
                label, buf = prefix, []
        if value:
            buf.append(re.sub(r'\s{2,}', ' | ', value) if (label or "").strip() == "Competencies" else value)
        i += 1

    close()
    for c in courses:
        c["lecturers"] = re.sub(r'\s+', ' ', c["lecturers"]).strip()
        c["title"] = re.sub(r'\s+', ' ', c["title"]).strip()
    return courses, unparsed


all_courses, all_unparsed = [], []
for sem, path in FILES:
    cs, up = parse(sem, path)
    print(f"{sem}: {len(cs)} courses, {len(up)} unparsed header rows")
    all_courses += cs
    all_unparsed += up

for u in all_unparsed:
    print("UNPARSED:", u[:160])

# --- derived fields ---------------------------------------------------------
import collections
SEMKEZ = {"Autumn 2026": "2026W", "Spring 2026": "2026S"}
codes = collections.Counter(x["code"] for x in all_courses)
for x in all_courses:
    n = " ".join(x["notes"])
    f = []
    if re.search(r'[Dd]oes not take place', n):
        f.append("Not taking place")
    if re.search(r'No enrolment to this course at ETH', n):
        f.append("UZH — book at UZH")
    if re.search(r'[Ff]ully booked|overbooked', n):
        f.append("Fully booked")
    m = re.search(r'[Nn]umber of participants limited to (\d+)|'
                  r'[Mm]aximal number of participants:?\s*(?:ca\.\s*)?(\d+)', n)
    if m:
        f.append(f"Limited to {m.group(1) or m.group(2)}")
    if re.search(r'not intended for', n):
        f.append("Not for CS/DS MSc")
    if re.search(r'waitlist|waiting list', n, re.I):
        f.append("Waitlist")
    x["flags"] = f
    x["both_semesters"] = codes[x["code"]] > 1
    x["notes_text"] = "\n".join(x["notes"])
    x["url"] = ("https://www.vorlesungen.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view"
                f"?lerneinheitscode={x['code']}&semkez={SEMKEZ[x['semester']]}&lang=en")

json.dump(all_courses, open(OUT, "w"), indent=1, ensure_ascii=False)
print("total:", len(all_courses))
