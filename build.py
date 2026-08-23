#!/usr/bin/env python3
"""Build the self-contained course browser from courses.json."""
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.environ.get("COURSES", os.path.join(HERE, "courses.json"))))

BULLET = re.compile(r'^\s*([-•*·–]|\d+[.)]|[a-z][.)]\s)')


CONT_END = re.compile(r'(,|;|\b(and|or|of|the|a|an|to|in|for|with|on|by|as|that|which|is|are)\s*)$', re.I)
NEXT_ITEM = re.compile(r'^[A-Z0-9(•\-–•]')


def reflow(t):
    """PDF line wraps are layout artifacts, not paragraph breaks — rejoin them.

    The hard part is telling a wrapped prose line from a genuine one-line list
    item, since the catalogue prints unbulleted lists (topic lists, syllabi).
    Wrapped prose fills the column by construction, so only a paragraph's LAST
    line is materially short. A short line mid-block, followed by something that
    starts like a new item and not reading as a continuation, is a real break."""
    if not t:
        return []
    paras = []
    for block in re.split(r'\n\s*\n', t.strip()):
        lines = [l.rstrip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        width = max(len(l) for l in lines)
        # The value column is ~110 chars wide, so wrapped prose always produces
        # at least one long line. A multi-line block where nothing is long is a
        # list printed without bullets — keep every line as its own item.
        if width < 62 and len(lines) > 1:
            paras.append("\n".join(l.strip() for l in lines))
            continue
        out, cur = [], ""
        for n, line in enumerate(lines):
            s = line.strip()
            starts_item = bool(BULLET.match(line))
            nxt = lines[n + 1].strip() if n + 1 < len(lines) else ""
            short_break = (
                width >= 60 and len(line) < 0.72 * width and nxt
                and NEXT_ITEM.match(nxt) and not CONT_END.search(s)
                and not BULLET.match(nxt)
            )
            if starts_item and cur:
                out.append(cur); cur = s
            else:
                cur = (cur + " " + s).strip()
            if short_break or (cur and cur.endswith(":")):
                out.append(cur); cur = ""
        if cur:
            out.append(cur)
        paras.append("\n".join(x for x in out if x))
    return [p for p in paras if p]


def comp(t):
    groups, cur = [], None
    for line in (t or "").split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            cur = {"group": parts[0], "items": []}
            groups.append(cur)
            cur["items"].append([parts[1], parts[2]])
        elif len(parts) == 2 and cur:
            cur["items"].append([parts[0], parts[1]])
    return groups


# ---------------------------------------------------------------------------
# Excerpts from the MSc Statistics Student FAQ (student representatives,
# last updated 17.03.2026). Informal, explicitly NOT official ETH information.
# Grade averages are unofficial figures compiled from ETH grade statistics.
# ---------------------------------------------------------------------------
FAQ = {
    "401-3621-00L": {
        "avg": "~4.6 – 4.8", "pass": "~76 – 89%", "area": "Mathematical Statistics",
        "note": ["This is the theoretically heaviest core area. Fundamentals of Mathematical "
                 "Statistics is proof-based and requires real mathematical maturity. The 9 ECTS "
                 "reflects the workload.",
                 "Mathematical Statistics is named among the courses that are heavily proof-based "
                 "and theoretical, as opposed to the implementation-oriented courses (often in R "
                 "or Python)."]},
    "401-8623-00L": {
        "avg": "~5.0", "pass": "~92%", "area": "Mathematical Statistics",
        "note": ["Likelihood and Regression I is offered at UZH and requires separate enrolment "
                 "(see the UZH mobility section), it is a more applied less theory-heavy pick.",
                 "You can take exams at UZH for your free electives, but some specific exams are "
                 "recognised in the core areas (for example, Likelihood and Regression). You will "
                 "have to apply for a \"mobility program\" — but be quick: the deadline is the "
                 "Friday before the beginning of the lecture period.",
                 "For Autumn 2026 that lands on or around Friday 11 September 2026 — the UZH "
                 "lecture period runs 14 September to 19 December 2026. Confirm the exact date "
                 "with UZH before relying on it."]},
    "401-3622-00L": {
        "avg": "~5.4 – 5.5", "pass": "~100%", "area": "Statistical Modelling",
        "note": ["Statistical Modelling is widely considered one of the most manageable core "
                 "courses relative to its ECTS weight."]},
    "401-4623-00L": {
        "avg": "~5.6", "pass": "~100%", "area": "Statistical Modelling",
        "note": ["Time Series Analysis runs every two years.",
                 "Listed in the FAQ as \"Autumn (biennial)\" — it is running in Autumn 2026, so "
                 "the next offering after this one is expected in Autumn 2028."]},
    "401-0625-01L": {
        "avg": "~5.2 – 5.6", "pass": "~97 – 100%", "area": "Applied Statistics",
        "note": ["Course preferences depend strongly on your background and long-term goals.",
                 "Only two courses exist in the Applied Statistics core area — this one and "
                 "Computational Statistics. Since ETH allows two attempts per course, failing "
                 "this one twice would make passing Computational Statistics compulsory."]},
    "401-3632-00L": {
        "avg": "~4.9 – 5.2", "pass": "~84 – 96%", "area": "Applied Statistics",
        "note": ["Named in the FAQ among the courses that emphasise implementation and practical "
                 "tools (often in R or Python), as opposed to the heavily proof-based ones.",
                 "Only two courses exist in the Applied Statistics core area — this one and "
                 "Applied Analysis of Variance. Since ETH allows two attempts per course, failing "
                 "ANOVA twice would make passing this course compulsory."]},
    "401-4620-00L": {
        "note": ["One common option for the seminar requirement is StatsLab (a project offered in "
                 "Spring), where students work on a real consulting case for an external partner. "
                 "Alternatively, more theoretical seminars are offered each semester, and in some "
                 "cases a semester research project can fulfil this requirement.",
                 "This component is meant to develop exposure to real or research-based problems."]},
    "401-3630-04L": {"note": ["A semester research project can fulfil the seminar requirement "
                              "(minimum 4 ECTS) in place of a seminar."]},
    "401-3630-06L": {"note": ["A semester research project can fulfil the seminar requirement "
                              "(minimum 4 ECTS) in place of a seminar."]},
    "401-3630-16L": {"note": ["A semester research project can fulfil the seminar requirement "
                              "(minimum 4 ECTS) in place of a seminar."]},
    "401-3904-22L": {
        "note": ["Named in the FAQ, alongside Mathematical Statistics, as an example of a course "
                 "that is heavily proof-based and theoretical."]},
    "401-4990-02L": {
        "note": ["The Master Thesis is worth 30 ECTS and represents a substantial independent "
                 "research project. It can be theoretical or applied and is typically written in "
                 "the final stage of the program."]},
}

DEPT = {"401": "Maths", "447": "Applied Stats", "252": "CS", "227": "IT & EE",
        "263": "CS", "261": "CS", "636": "Biosystems"}

SEC_ORDER = ["Core Courses", "Subject Specific Electives",
             "Seminar or Semester Paper", "Master's Thesis"]
SUB_ORDER = ["Statistical Modelling", "Applied Statistics", "Mathematical Statistics"]

data = []
for i, x in enumerate(C):
    d = {
        "i": i,
        "sem": "A" if x["semester"].startswith("Autumn") else "S",
        "sec": x["section"],
        "sub": x["subsection"] or "",
        "code": x["code"],
        "title": x["title"],
        "type": x["type"],
        "ects": x["ects"],
        "hours": x["hours"],
        "lect": x["lecturers"],
        "flags": x["flags"],
        "url": x["url"],
        "notes": reflow(x.get("notes_text", "")),
        "abs": reflow(x.get("abstract", "")),
        "lo": reflow(x.get("learning_objective", "")),
        "cont": reflow(x.get("content", "")),
        "pre": reflow(x.get("prerequisites_notice", "")),
        "lit": reflow(x.get("literature", "")),
        "ln": reflow(x.get("lecture_notes", "")),
        "comp": comp(x.get("competencies", "")),
        "both": x["both_semesters"],
        "faq": FAQ.get(x["code"]),
        "dept": DEPT.get(x["code"][:3], ""),
    }
    # "Does not take place this semester" is a Spring 2026 fact. These courses
    # would be taken in Spring 2027, where availability is not yet published,
    # so the flag is dropped for Spring rather than asserted as still true.
    if d["sem"] == "S":
        d["flags"] = [f for f in d["flags"] if "Not taking place" not in f]
    d["secOrder"] = SEC_ORDER.index(x["section"]) if x["section"] in SEC_ORDER else 9
    d["subOrder"] = SUB_ORDER.index(x["subsection"]) if x["subsection"] in SUB_ORDER else 9
    hay = " ".join(filter(None, [
        x["code"], x["title"], x["lecturers"], x.get("abstract", ""),
        x.get("learning_objective", ""), x.get("content", ""),
        x.get("prerequisites_notice", ""), x.get("literature", ""), x.get("notes_text", "")]))
    d["hay"] = re.sub(r'\s+', ' ', hay).lower()
    data.append(d)

PAYLOAD = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

TPL = r"""<title>Statistics MSc Course Planner</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=JetBrains+Mono:wght@400;500;600&display=swap">
<style>
/* Palette derived from anthropic.com's published design tokens: canvas #FAF9F5,
   section fill #F0EEE6, ink #141413, accent #C6613F / #D97757, hairline #E6DFD8.
   Deliberately single-theme (light), so every colour is painted explicitly and
   the page holds whichever ground the viewer's host paints behind it. */
:root{
  --bg:#FAF9F5; --surface:#FFFFFF; --surface-2:#F5F2EA; --fill:#F0EEE6;
  --ink:#141413; --ink-2:#3D3D3A; --muted:#6C6A64; --faint:#8E8B82;
  --line:#E6DFD8; --line-2:#EFEAE2;
  --accent:#C6613F; --accent-2:#D97757; --accent-soft:#F7EAE3; --on-accent:#FFFFFF;
  --warn:#8A6410; --warn-soft:#FBF3DE;
  --info:#2F7A6B; --info-soft:#E4F1EE;
  --bar:#E0D3C4;
  --shadow:0 1px 2px rgba(20,20,19,.05),0 10px 28px -14px rgba(20,20,19,.22);
  --r:8px;
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:0 20px calc(var(--bar-h,92px) + 32px)}

/* ---------- masthead ---------- */
header.mast{padding:44px 0 26px; border-bottom:1px solid var(--line)}
.eyebrow{
  font-family:"JetBrains Mono",ui-monospace,monospace; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin:0 0 10px;
}
h1{
  font-family:"Source Serif 4",Georgia,serif; font-weight:400;
  font-size:clamp(32px,4.4vw,46px); letter-spacing:-.025em;
  margin:0 0 12px; text-wrap:balance; line-height:1.08;
}
.sub{color:var(--ink-2); max-width:64ch; margin:0; font-size:15px}
.sub b{font-weight:600; color:var(--ink)}

/* ---------- controls ---------- */
.controls{padding:14px 0 12px; border-bottom:1px solid var(--line); margin-bottom:2px}
.row{display:flex; flex-wrap:wrap; gap:10px; align-items:center}
.row + .row{margin-top:10px}
.search{flex:1 1 280px; position:relative; display:flex; align-items:center}
.search input{
  width:100%; padding:9px 34px 9px 12px; font:inherit; font-size:14px;
  background:var(--surface); color:var(--ink);
  border:1px solid var(--line); border-radius:var(--r); outline:none;
}
.search input:focus{border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft)}
.search kbd{position:absolute; right:9px; font-family:"JetBrains Mono",monospace; font-size:10px;
  color:var(--muted); border:1px solid var(--line); border-radius:3px; padding:1px 4px; pointer-events:none}
.seg{display:inline-flex; border:1px solid var(--line); border-radius:var(--r); overflow:hidden; background:var(--surface)}
.seg button{
  font:inherit; font-size:13px; padding:8px 13px; border:0; background:transparent;
  color:var(--ink-2); cursor:pointer; border-right:1px solid var(--line-2);
}
.seg button:last-child{border-right:0}
.seg button[aria-pressed="true"]{background:var(--accent); color:var(--on-accent); font-weight:600}
.seg button:focus-visible{outline:2px solid var(--accent); outline-offset:-2px}
.chip{
  font:inherit; font-size:12.5px; padding:6px 11px; cursor:pointer;
  background:var(--surface); color:var(--ink-2);
  border:1px solid var(--line); border-radius:99px;
}
.chip[aria-pressed="true"]{background:var(--accent-soft); border-color:var(--accent); color:var(--accent); font-weight:600}
.chip:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.chip .n{font-family:"JetBrains Mono",monospace; font-size:11px; opacity:.65; margin-left:5px}
select{font:inherit; font-size:13px; padding:8px 10px; border:1px solid var(--line);
  border-radius:var(--r); background:var(--surface); color:var(--ink)}
.toggle{display:inline-flex; align-items:center; gap:7px; font-size:13px; color:var(--ink-2); cursor:pointer}
.toggle input{accent-color:var(--accent); width:15px; height:15px}
.spacer{flex:1 1 auto}
.linkbtn{font:inherit; font-size:13px; background:none; border:0; color:var(--accent);
  cursor:pointer; padding:6px 2px; text-decoration:underline; text-underline-offset:3px}

/* ---------- table ---------- */
.sec{margin-top:34px}
.sechead{position:sticky; top:0; z-index:12; background:var(--bg);
  padding:10px 0 0; border-bottom:1.5px solid var(--ink)}
.sechead h2{font-family:"Source Serif 4",Georgia,serif; font-size:19px; font-weight:600;
  letter-spacing:-.012em; margin:0 0 7px}
.cols{display:grid; grid-template-columns:26px 106px 1fr 52px 94px 142px 20px; gap:12px;
  padding:0 8px 7px 4px; align-items:baseline}
.colh{font-family:"JetBrains Mono",monospace; font-size:9.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--muted); white-space:nowrap}
.colh.r{text-align:right}
.hourshelp{position:relative; cursor:help; display:inline-block;
  text-decoration:underline dotted var(--muted); text-decoration-thickness:1px;
  text-underline-offset:3px}
.hourshelp:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.legend{position:absolute; right:-8px; top:calc(100% + 8px); z-index:60; width:min(310px,78vw);
  white-space:normal;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r);
  box-shadow:var(--shadow); padding:12px 14px; display:none; text-align:left;
  font-family:"Inter",sans-serif; letter-spacing:0; text-transform:none; cursor:default}
.hourshelp:hover .legend,.hourshelp:focus .legend,.hourshelp:focus-within .legend{display:block}
.legend .lt{font-size:11px; color:var(--muted); margin:0 0 8px; line-height:1.45}
.legend dl{margin:0; display:grid; grid-template-columns:22px 1fr; gap:5px 10px; align-items:baseline}
.legend dt{font-family:"JetBrains Mono",monospace; font-size:12px; font-weight:600; color:var(--accent)}
.legend dd{margin:0; font-size:12px; color:var(--ink-2); line-height:1.35}
.legend .lf{font-size:10.5px; color:var(--faint); margin:9px 0 0; padding-top:8px;
  border-top:1px solid var(--line-2); line-height:1.45}
.subhead{position:sticky; top:var(--sec-h,62px); z-index:11;
  background:var(--bg); font-family:"JetBrains Mono",monospace; font-size:10.5px;
  letter-spacing:.13em; text-transform:uppercase; color:var(--muted); padding:13px 0 7px;
  box-shadow:0 1px 0 var(--line-2)}

.list{display:flex; flex-direction:column}
.course{border-bottom:1px solid var(--line-2)}
.hdr{
  display:grid; grid-template-columns:26px 106px 1fr 52px 94px 142px 20px;
  gap:12px; align-items:baseline; width:100%; text-align:left;
  padding:9px 8px 9px 4px; background:none; border:0; font:inherit; color:inherit; cursor:pointer;
}
.hdr:hover{background:var(--surface-2)}
.hdr:focus-visible{outline:2px solid var(--accent); outline-offset:-2px}
.course.open .hdr{background:var(--surface)}
.pick{display:flex; align-items:center; justify-content:center; padding-top:2px}
.pick input{accent-color:var(--accent); width:15px; height:15px; cursor:pointer}
.code{font-family:"JetBrains Mono",monospace; font-size:12px; color:var(--muted);
  white-space:nowrap; line-height:1.15}
.code .dep{display:block}
.ttl{font-weight:500; letter-spacing:-.005em; line-height:1.35}
.semtag{
  font-family:"JetBrains Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.06em;
  border:1px solid var(--line); border-radius:3px; padding:1px 4px;
  color:var(--muted); vertical-align:1.5px;
}
.ttl .semtag{margin-right:7px}
.semtag.A{border-color:var(--warn); color:var(--warn); background:var(--warn-soft)}
.semtag.S{border-color:var(--info); color:var(--info); background:var(--info-soft)}
.revlink{font-size:12px; font-weight:400; color:var(--accent); text-decoration:none;
  white-space:nowrap; margin-left:7px; border-bottom:1px solid transparent}
.revlink:hover{border-bottom-color:var(--accent)}
.revlink:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.ects{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; font-size:13px;
  font-weight:500; text-align:right; position:relative}
.hrs{font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--muted); white-space:nowrap}
.who{font-size:12.5px; color:var(--ink-2); line-height:1.35}
.caret{color:var(--muted); font-size:11px; text-align:right; transition:transform .15s}
.course.open .caret{transform:rotate(90deg)}
.flags{grid-column:3 / -1; display:flex; flex-wrap:wrap; align-items:center; gap:5px 9px; margin-top:4px}
.flag{font-family:"JetBrains Mono",monospace; font-size:10px; letter-spacing:.05em;
  padding:2px 6px; border-radius:3px; text-transform:uppercase; white-space:nowrap}
.flag.stop{background:var(--fill); color:var(--faint); text-decoration:line-through;
  text-decoration-thickness:1px}
.flag.warn{background:var(--warn-soft); color:var(--warn)}
.flag.info{background:var(--info-soft); color:var(--info)}
.flag.mute{background:var(--line-2); color:var(--muted)}
.course.dim .ttl,.course.dim .code,.course.dim .who{opacity:.5}

/* ---------- detail ---------- */
.detail{display:none; padding:4px 8px 26px 42px; background:var(--surface); border-top:1px solid var(--line-2)}
.course.open .detail{display:block}
.field{display:grid; grid-template-columns:150px 1fr; gap:18px; padding:12px 0; border-top:1px solid var(--line-2)}
.field:first-child{border-top:0}
.field > dt{font-family:"JetBrains Mono",monospace; font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); padding-top:3px}
.field > dd{margin:0; font-family:"Source Serif 4",Georgia,serif; font-size:15.5px; line-height:1.6;
  color:var(--ink-2); max-width:68ch}
.field > dd p{margin:0 0 .7em; white-space:pre-line}
.field > dd p:last-child{margin-bottom:0}
.field.note > dd{font-family:"Inter",sans-serif; font-size:13.5px; color:var(--ink-2)}
.comp{display:flex; flex-direction:column; gap:9px; font-family:"Inter",sans-serif; font-size:13px}
.compgrp > .gn{font-weight:600; font-size:12px; margin-bottom:3px}
.compgrp ul{margin:0; padding:0; list-style:none; display:flex; flex-wrap:wrap; gap:4px 6px}
.compgrp li{font-size:12px; color:var(--ink-2); border:1px solid var(--line);
  border-radius:99px; padding:1px 8px}
.compgrp li.na{opacity:.55}
.dl{display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; margin-top:16px}
.dl a{font-size:12.5px; color:var(--accent); text-decoration:none; border-bottom:1px solid var(--accent-soft)}
.dl a:hover{border-bottom-color:var(--accent)}
mark{background:var(--accent-soft); color:inherit; border-radius:2px; padding:0 1px}

/* ---------- FAQ excerpt block ---------- */
.faq{margin:18px 0 4px; border:1px solid var(--accent); border-left-width:3px;
  border-radius:var(--r); background:var(--accent-soft); padding:13px 16px 15px}
.faq h4{font-family:"JetBrains Mono",monospace; font-size:10.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--accent); margin:0 0 9px; font-weight:600}
.faq .metrics{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px}
.metric{background:var(--surface); border:1px solid var(--line); border-radius:var(--r);
  padding:5px 10px; display:flex; gap:8px; align-items:baseline}
.metric .mk{font-family:"JetBrains Mono",monospace; font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--muted)}
.metric .mv{font-family:"JetBrains Mono",monospace; font-size:14px; font-weight:600;
  font-variant-numeric:tabular-nums}
.faq p{margin:0 0 .6em; font-size:13.5px; line-height:1.55; color:var(--ink-2); max-width:70ch}
.faq p:last-of-type{margin-bottom:0}
.faq .src{font-size:11px; color:var(--muted); margin-top:10px; padding-top:9px;
  border-top:1px solid var(--line); line-height:1.45}
.gradechip{background:var(--fill); color:var(--ink-2); box-shadow:inset 0 0 0 1px var(--line)}

/* ---------- programme structure panel ---------- */
.struct{margin:26px 0 0; border:1px solid var(--line); border-radius:var(--r);
  background:var(--surface); overflow:hidden; box-shadow:var(--shadow)}
.struct > summary{
  list-style:none; cursor:pointer; padding:22px 24px 20px; display:block;
}
.struct > summary::-webkit-details-marker{display:none}
.struct > summary:hover{background:var(--surface-2)}
.struct > summary:focus-visible{outline:2px solid var(--accent); outline-offset:-3px}
.sh{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap}
.sh h2{font-family:"Source Serif 4",Georgia,serif; font-size:25px; font-weight:600;
  letter-spacing:-.02em; margin:0; line-height:1.15}
.sh .open-cue{margin-left:auto; font-size:13px; font-weight:500; color:var(--accent);
  display:inline-flex; align-items:center; gap:6px; white-space:nowrap}
.sh .open-cue::after{content:"▾"; font-size:10px; transition:transform .15s}
.struct[open] .sh .open-cue::after{transform:rotate(180deg)}
.struct[open] .sh .open-cue .lbl-shut{display:none}
.struct:not([open]) .sh .open-cue .lbl-open{display:none}
.struct-lede{margin:9px 0 0; font-size:14.5px; color:var(--ink-2); max-width:76ch; line-height:1.55}
.struct-lede b{color:var(--ink); font-weight:600}

/* the preview IS the requirement ladder — visible without expanding */
.prev{display:flex; flex-wrap:wrap; align-items:stretch; gap:6px; margin-top:16px}
.pv{display:flex; flex-direction:column; gap:1px; padding:8px 12px 8px 11px;
  background:var(--fill); border-radius:6px; border-left:2px solid var(--line)}
.pv .pn{font-family:"JetBrains Mono",monospace; font-size:16px; font-weight:600;
  font-variant-numeric:tabular-nums; letter-spacing:-.02em; line-height:1.1}
.pv .pl{font-size:11px; color:var(--muted); letter-spacing:.01em; white-space:nowrap}
.pv.key{background:var(--accent-soft); border-left-color:var(--accent)}
.pv.key .pn,.pv.key .pl{color:var(--accent)}
.pv.sum{background:var(--ink); border-left-color:var(--ink)}
.pv.sum .pn{color:var(--bg)} .pv.sum .pl{color:var(--faint)}
.pv .op{align-self:center; color:var(--faint); font-size:13px}
.prev .op{display:flex; align-items:center; color:var(--faint); font-size:14px; padding:0 1px}

.structbody{padding:6px 24px 26px; border-top:1px solid var(--line-2)}
.ladder{width:100%; border-collapse:collapse; margin:16px 0 4px; font-size:13.5px}
.ladder th{font-family:"JetBrains Mono",monospace; font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); text-align:left; font-weight:400;
  padding:0 10px 7px 0; border-bottom:1px solid var(--line)}
.ladder td{padding:10px 10px 10px 0; border-bottom:1px solid var(--line-2); vertical-align:top}
.ladder td.n{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums;
  font-weight:600; white-space:nowrap; text-align:right; padding-right:18px}
.ladder tr.rule td{background:var(--accent-soft)}
.ladder tr.rule td.n{color:var(--accent)}
.ladder tr.tot td{border-bottom:0; font-weight:600; border-top:1.5px solid var(--ink)}
.ladder td small{display:block; color:var(--muted); font-size:12px; margin-top:3px; line-height:1.45}
.structbody h3{font-family:"Source Serif 4",Georgia,serif; font-size:17px; font-weight:600;
  letter-spacing:-.01em; margin:26px 0 9px}
.structbody ul{margin:0; padding-left:18px; display:flex; flex-direction:column; gap:7px}
.structbody li{font-size:13.5px; color:var(--ink-2); line-height:1.55; max-width:76ch}
.structbody li b{color:var(--ink); font-weight:600}
.note-box{margin-top:18px; padding:12px 16px; border-left:2px solid var(--warn);
  background:var(--warn-soft); font-size:13px; color:var(--ink-2); line-height:1.6;
  border-radius:0 var(--r) var(--r) 0; max-width:88ch}
.note-box b{color:var(--ink)}
.note-box.urgent{border-left-color:var(--accent); background:var(--accent-soft)}
.disc{margin-top:20px; font-size:11.5px; color:var(--faint); line-height:1.55; max-width:80ch}

/* ---------- requirement tracker ---------- */
.reqs{display:flex; flex-wrap:wrap; gap:6px; width:100%}
.req{display:flex; align-items:baseline; gap:7px; padding:4px 9px; border-radius:var(--r);
  border:1px solid var(--line); background:var(--surface-2); font-size:12px; white-space:nowrap}
.req .rl{color:var(--muted)}
.req .rv{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; font-weight:600}
.req.done{border-color:var(--info); background:var(--info-soft); color:var(--info)}
.req.done .rl{color:var(--info)}
.req.warn{border-color:var(--warn); background:var(--warn-soft); color:var(--warn)}
.req.warn .rl{color:var(--warn)}

/* ---------- basket ---------- */
.basket{position:fixed; left:0; right:0; bottom:0; z-index:30; background:var(--surface);
  border-top:1px solid var(--line); box-shadow:var(--shadow)}
.basket{max-height:86vh; display:flex; flex-direction:column}
.basket .inner{max-width:1180px; width:100%; margin:0 auto; padding:0 20px 11px;
  display:flex; flex-direction:column; gap:10px; min-height:0}
.brow{display:flex; flex-wrap:wrap; gap:8px 16px; align-items:baseline; padding-top:11px}
.bhint{font-size:13px; color:var(--muted)}
.basket.nopicks #bcount,.basket.nopicks #bsplit,.basket.nopicks #bclear{display:none}
.basket:not(.nopicks) .bhint{display:none}
.basket .tot{font-family:"JetBrains Mono",monospace; font-size:13px; font-variant-numeric:tabular-nums}
.basket .tot b{font-size:16px; font-weight:600}
.showsel{font-family:"Source Serif 4",Georgia,serif; font-size:19px; font-weight:600;
  letter-spacing:-.012em; background:none; border:0; padding:0; margin:0; cursor:pointer;
  color:var(--ink); display:inline-flex; align-items:baseline; gap:8px}
.showsel::after{content:"▾"; font-family:"Inter",sans-serif; font-size:11px; color:var(--accent)}
.showsel[aria-expanded="true"]::after{content:"▴"}
.showsel:hover{color:var(--accent)}
.showsel:focus-visible{outline:2px solid var(--accent); outline-offset:3px; border-radius:3px}

/* ---------- expanded selection ---------- */
.selpanel{overflow-y:auto; min-height:0; max-height:min(52vh,460px);
  border-bottom:1px solid var(--line); margin:0 -20px; padding:0 20px 10px}
.selpanel[hidden]{display:none}
.selgroup{display:block}
.selsec{position:sticky; top:0; z-index:3; height:34px; display:flex; align-items:center;
  gap:12px; background:var(--surface); border-bottom:1.5px solid var(--ink); margin-top:14px}
.selsec .ss-name{font-family:"Source Serif 4",Georgia,serif; font-size:15px; font-weight:600;
  letter-spacing:-.01em}
.selsec .ss-min{font-family:"JetBrains Mono",monospace; font-size:10.5px; letter-spacing:.05em;
  text-transform:uppercase; color:var(--muted)}
.selsec .ss-got{margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:12.5px;
  font-variant-numeric:tabular-nums; font-weight:600; color:var(--warn)}
.selsec.ok .ss-got{color:var(--info)}
.selsec.ok .ss-got::after{content:" ✓"}
.selsub{position:sticky; top:34px; z-index:2; background:var(--surface);
  font-family:"JetBrains Mono",monospace; font-size:10px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); padding:9px 0 4px}
.selsub.none{color:var(--faint)}
.selrow{display:grid; grid-template-columns:106px 26px 1fr 46px 22px; gap:12px;
  align-items:baseline; padding:5px 0; border-bottom:1px solid var(--line-2)}
.selrow .code{line-height:1.15}
.selrow .st{font-size:13.5px; line-height:1.35}
.selrow .se{font-family:"JetBrains Mono",monospace; font-size:12.5px; font-weight:500;
  font-variant-numeric:tabular-nums; text-align:right}
.unpick{background:none; border:0; cursor:pointer; color:var(--faint); font-size:15px;
  line-height:1; padding:0; text-align:right}
.unpick:hover{color:var(--accent)}
.unpick:focus-visible{outline:2px solid var(--accent); outline-offset:2px; border-radius:3px}
.selnone{font-size:12.5px; color:var(--faint); padding:8px 0 9px}
.seltail{display:flex; flex-wrap:wrap; gap:6px 18px; align-items:baseline; margin-top:16px;
  padding-top:11px; border-top:1.5px solid var(--ink); font-family:"JetBrains Mono",monospace;
  font-size:12.5px; font-variant-numeric:tabular-nums}
.seltail .tl{font-family:"Inter",sans-serif; font-size:12.5px; color:var(--muted)}
.noresults{padding:44px 4px; color:var(--muted); font-size:14px}

@media (max-width:820px){
  .hdr{grid-template-columns:24px 1fr 60px 22px; row-gap:3px}
  .hdr .code{grid-column:2}
  .hdr .ttl{grid-column:2}
  .hdr .ects{grid-row:1; grid-column:3}
  .hdr .hrs,.hdr .who{grid-column:2; font-size:12px}
  .hdr .caret{grid-row:1; grid-column:4}
  .flags{grid-column:2 / -1}
  .detail{padding-left:8px}
  /* Column labels describe a grid the mobile layout doesn't use — keep only
     the Hours key, which is the one label carrying information of its own. */
  .reqs{flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none; padding-bottom:2px}
  .reqs::-webkit-scrollbar{display:none}
  .req{flex:0 0 auto}
  .cols{display:flex; gap:16px; padding:0 4px 6px}
  .cols .colh:not(:nth-last-child(3)){display:none}
  .cols .colh:nth-last-child(3){display:block}
  .legend{right:auto; left:0}
  .field{grid-template-columns:1fr; gap:5px}
}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
</style>

<div class="wrap">
<header class="mast">
  <p class="eyebrow">ETH Zürich · D-MATH · MSc Statistics</p>
  <h1>Statistics MSc Course Planner</h1>
  <p class="sub">Every course unit listed in the autumn and spring catalogues for the Master's Programme in Statistics — <b>90 course units</b> parsed verbatim from the official course catalogue, merged into one searchable table, with structure rules and course commentary from the MSc Statistics Student FAQ. Tick courses to build a semester and the credit total is checked against the graduation requirements live.</p>
  <details class="struct">
    <summary>
      <div class="sh">
        <h2>Programme structure &amp; credit rules</h2>
        <span class="open-cue"><span class="lbl-shut">Read the full rules</span><span class="lbl-open">Collapse</span></span>
      </div>
      <p class="struct-lede">Ninety credits, seven buckets, and one condition that quietly governs the rest — <b>core, electives and seminar must total 52 ECTS between them</b>, which is 21 more than their individual minimums require.</p>
      <div class="prev">
        <span class="pv"><span class="pn">12</span><span class="pl">Core · 1 per area</span></span>
        <span class="op">+</span>
        <span class="pv"><span class="pn">15</span><span class="pl">Electives</span></span>
        <span class="op">+</span>
        <span class="pv"><span class="pn">4</span><span class="pl">Seminar</span></span>
        <span class="op">→</span>
        <span class="pv key"><span class="pn">52</span><span class="pl">combined — the binding rule</span></span>
        <span class="op">+</span>
        <span class="pv"><span class="pn">2</span><span class="pl">GESS</span></span>
        <span class="op">+</span>
        <span class="pv"><span class="pn">30</span><span class="pl">Thesis</span></span>
        <span class="op">+</span>
        <span class="pv"><span class="pn">6</span><span class="pl">Free electives</span></span>
        <span class="op">=</span>
        <span class="pv sum"><span class="pn">90</span><span class="pl">to graduate</span></span>
      </div>
    </summary>
    <div class="structbody">
      <table class="ladder">
        <thead><tr><th style="text-align:right; padding-right:16px">Minimum</th><th>Component</th></tr></thead>
        <tbody>
          <tr><td class="n">12 ECTS</td><td><b>Core courses</b> — and at least one course in <b>each</b> of the three core areas: Mathematical Statistics, Statistical Modelling, Applied Statistics.
            <small>Six core courses exist in total, all in this table. Five run in Autumn; only Computational Statistics runs in Spring.</small></td></tr>
          <tr><td class="n">15 ECTS</td><td><b>Subject-specific electives</b> — deepen expertise within statistics or closely related quantitative fields.
            <small>Machine learning, high-dimensional statistics, risk management, optimization, advanced probability.</small></td></tr>
          <tr><td class="n">4 ECTS</td><td><b>Seminar or semester project</b> — read papers and present, or work an applied/theoretical project.
            <small>StatsLab (Spring) places you on a real consulting case for an external partner; a semester paper can also satisfy this.</small></td></tr>
          <tr class="rule"><td class="n">52 ECTS</td><td><b>The 52 rule</b> — core + subject-specific electives + seminar must sum to at least 52 ECTS combined.
            <small>This is the binding constraint. The three individual minimums only add to 31, so roughly 21 further ECTS must come from these three buckets.</small></td></tr>
          <tr><td class="n">2 ECTS</td><td><b>GESS — Science in Perspective</b> — ethics, philosophy of science, law, history, political and social sciences.
            <small>Not listed in these two catalogues; the section links out to the separate GESS catalogue.</small></td></tr>
          <tr><td class="n">30 ECTS</td><td><b>Master's thesis</b> — substantial independent research project, theoretical or applied, normally in the final stage.</td></tr>
          <tr><td class="n">6 ECTS</td><td><b>Free electives</b> — the remainder, from almost any department.
            <small>Also not enumerated in these catalogues. The structured requirements above reach 84 ECTS.</small></td></tr>
          <tr class="tot"><td class="n">90 ECTS</td><td>Total required to graduate</td></tr>
        </tbody>
      </table>

      <div class="note-box"><b>The one-per-area rule binds harder than the 12 ECTS.</b> The cheapest legal core combination is Time Series Analysis (4) + Applied Analysis of Variance (5) + Likelihood and Regression I (7) = 16 ECTS, which already clears 12. So treat the core requirement as "one from each area", not as a credit target — and note that Time Series Analysis is biennial and Likelihood and Regression I is hosted at UZH.</div>

      <div class="note-box urgent"><b>Time-critical for Autumn 2026.</b> Likelihood and Regression I is one of only two courses in the Mathematical Statistics core area, and it is hosted at UZH — taking it requires a mobility application whose deadline is the Friday before the lecture period begins. The UZH lecture period runs 14 September – 19 December 2026, putting that deadline on or around <b>Friday 11 September 2026</b>. If that passes, the only remaining Mathematical Statistics option is Fundamentals of Mathematical Statistics (9 ECTS, proof-based, the lowest average and pass rate of the six core courses). Verify the exact date with UZH.</div>

      <h3>Registration, withdrawal and exam rules</h3>
      <ul>
        <li>You may register for up to <b>12 exams per semester</b>, normally in the first weeks of the semester.</li>
        <li>You can <b>withdraw from an exam up to roughly 10 days before</b> the exam date, and a timely withdrawal leaves no trace on your transcript. Registering broadly and cutting later is standard practice.</li>
        <li>ETH typically offers <b>one exam session per course per year</b>. A failure counts as one attempt; you may retake once. <b>After two failed attempts the course cannot be taken again.</b></li>
        <li><b>Exam dates are announced late</b> — usually around four weeks before the end of the semester, and not all courses sit in a stable slot year to year.</li>
        <li>Grades run <b>1 to 6 in 0.25 increments</b>; 4.0 passes. Passing is generally not the hard part — scoring high is.</li>
        <li><b>Cherry-picking is permitted.</b> Once the ECTS requirements are met you may keep taking exams in the same areas and select the best results for the diploma transcript. Every attempt, passed or failed, still appears on the full academic record.</li>
        <li><b>UZH exams</b> count for free electives, and a few are recognised in the core areas — Likelihood and Regression I among them. This requires a mobility application, and the deadline is the <b>Friday before the lecture period begins</b>.</li>
        <li>There is <b>no overall exam limit and no 90-credit ceiling</b>. You may stay up to three years; around two years with an integrated internship is typical, and 1.5 years is possible but background-dependent.</li>
      </ul>

      <h3>Choosing courses</h3>
      <ul>
        <li>Pick one course per core area early, add one or two electives according to workload tolerance, then adjust within the first weeks.</li>
        <li><b>Do not overload the first semester</b> — particularly coming from an economics, engineering or other applied background, where proof-based courses are the steeper climb. Starting conservatively and scaling up beats overcommitting.</li>
        <li>Preparation reading suggested by the student reps: Schaum's Outline of Advanced Calculus (3rd ed.); Schaum's Outline of Linear Algebra (6th ed.); Blitzstein &amp; Hwang, <i>Introduction to Probability</i> (2nd ed.); Tao, <i>An Introduction to Measure Theory</i> — measure-theoretic vocabulary appears in several courses even where deep mastery is not required.</li>
      </ul>

      <p class="disc">Structure, rules and course commentary above are excerpted from the <b>ETH MSc Statistics Student FAQ</b> compiled by the MSc Statistics student representatives, last updated 17.03.2026. That document states explicitly that it is informal guidance and does <b>not</b> represent official information or positions of ETH Zürich. Grade averages and pass rates are unofficial figures compiled from ETH grade statistics and may vary year to year. For authoritative rules see the study regulations (Art. 30) and the official programme FAQ.</p>
    </div>
  </details>
</header>

<div class="controls">
  <div class="row">
    <label class="search">
      <input id="q" type="search" placeholder="Search titles, lecturers, abstracts, prerequisites…" aria-label="Search courses">
      <kbd>/</kbd>
    </label>
    <div class="seg" role="group" aria-label="Semester">
      <button data-sem="all" aria-pressed="true">Both</button>
      <button data-sem="A" aria-pressed="false">Autumn</button>
      <button data-sem="S" aria-pressed="false">Spring</button>
    </div>
    <select id="sort" aria-label="Sort order">
      <option value="cat">Catalogue order</option>
      <option value="title">Title A–Z</option>
      <option value="ects-d">Credits, high → low</option>
      <option value="ects-a">Credits, low → high</option>
      <option value="lect">Lecturer A–Z</option>
      <option value="code">Course number</option>
    </select>
  </div>
  <div class="row" id="secchips"></div>
  <div class="row">
    <label class="toggle"><input type="checkbox" id="avail"> Only courses actually running</label>
    <label class="toggle"><input type="checkbox" id="ethonly"> Exclude UZH-hosted</label>
    <label class="toggle"><input type="checkbox" id="minects"> 4+ credits only</label>
    <span class="spacer"></span>
    <button class="linkbtn" id="expandall">Expand all</button>
    <button class="linkbtn" id="reset">Reset filters</button>
  </div>
</div>

<main id="out"></main>
</div>

<div class="basket" id="basket" aria-live="polite">
  <div class="inner">
    <div class="selpanel" id="selpanel" hidden></div>
    <div class="brow">
      <button class="showsel" id="showsel" aria-expanded="false" aria-controls="selpanel">Show selection</button>
      <div class="tot" id="bcount">Selected <b id="bn">0</b> courses · <b id="be">0</b> credits</div>
      <div class="tot" id="bsplit"></div>
      <div class="bhint" id="bhint">Tick a course to start building a semester.</div>
      <span class="spacer"></span>
      <button class="linkbtn" id="bclear">Clear</button>
    </div>
    <div class="reqs" id="reqs"></div>
  </div>
</div>

<script>
const DATA = __PAYLOAD__;
const SECS = ["Core Courses","Subject Specific Electives","Seminar or Semester Paper","Master's Thesis"];
const SUBS = ["Statistical Modelling","Applied Statistics","Mathematical Statistics"];
const SEC_MIN = {"Core Courses":12,"Subject Specific Electives":15,"Seminar or Semester Paper":4,"Master's Thesis":30};
const SEMNAME = {A:"Autumn", S:"Spring"};
const st = {q:"", sem:"all", secs:new Set(), sort:"cat", avail:false, eth:false, min:false};
const open = new Set();
let picked = new Set();
try{ const s = localStorage.getItem("eth-stat-picked"); if(s) picked = new Set(JSON.parse(s)); }catch(e){}
const save = () => { try{ localStorage.setItem("eth-stat-picked", JSON.stringify([...picked])); }catch(e){} };

const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const flagClass = f => /Not taking place/.test(f) ? "stop"
  : /Fully booked|Waitlist/.test(f) ? "warn"
  : /UZH/.test(f) ? "info" : "mute";

function hi(text){
  const t = esc(text);
  if(!st.q) return t;
  const terms = st.q.split(/\s+/).filter(w => w.length > 2)
    .map(w => w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"));
  if(!terms.length) return t;
  return t.replace(new RegExp("("+terms.join("|")+")","gi"), "<mark>$1</mark>");
}
function field(label, arr, extra){
  if(!arr || !arr.length) return "";
  return `<div class="field ${extra||""}"><dt>${label}</dt><dd>${
    arr.map(p => `<p>${hi(p)}</p>`).join("")}</dd></div>`;
}

function match(c){
  if(st.sem !== "all" && c.sem !== st.sem) return false;
  if(st.secs.size && !st.secs.has(c.sec)) return false;
  if(st.avail && c.flags.some(f => /Not taking place/.test(f))) return false;
  if(st.eth && c.flags.some(f => /UZH/.test(f))) return false;
  if(st.min && c.ects < 4) return false;
  if(st.q){
    for(const w of st.q.toLowerCase().split(/\s+/).filter(Boolean))
      if(!c.hay.includes(w)) return false;
  }
  return true;
}

function sortRows(rows){
  const by = {
    cat: (a,b) => a.secOrder-b.secOrder || a.subOrder-b.subOrder || a.i-b.i,
    title: (a,b) => a.title.localeCompare(b.title),
    "ects-d": (a,b) => b.ects-a.ects || a.title.localeCompare(b.title),
    "ects-a": (a,b) => a.ects-b.ects || a.title.localeCompare(b.title),
    lect: (a,b) => (a.lect||"~").localeCompare(b.lect||"~"),
    code: (a,b) => a.code.localeCompare(b.code),
  }[st.sort];
  return rows.slice().sort(by);
}

function rowHTML(c){
  const flags = c.flags.map(f => `<span class="flag ${flagClass(f)}">${esc(f)}</span>`).join("")
    + (c.faq && c.faq.avg ? `<span class="flag gradechip">Avg grade ${esc(c.faq.avg)} · pass ${esc(c.faq.pass)}</span>` : "")
    + (c.faq && !c.faq.avg ? `<span class="flag gradechip">Student FAQ note</span>` : "");
  const dim = c.flags.some(f => /Not taking place/.test(f)) ? " dim" : "";
  const isOpen = open.has(c.i) ? " open" : "";
  return `<div class="course${dim}${isOpen}" data-i="${c.i}">
  <div class="hdr" role="button" tabindex="0" aria-expanded="${open.has(c.i)}">
    <span class="pick"><input type="checkbox" ${picked.has(c.i)?"checked":""} aria-label="Select ${esc(c.title)}"></span>
    <span class="code">${hi(c.code)}${c.dept ? `<span class="dep">${esc(c.dept)}</span>` : ""}</span>
    <span class="ttl"><span class="semtag ${c.sem}">${c.sem}</span>${hi(c.title)}<a class="revlink" href="https://coursereview.ch/course/${c.code}" target="_blank" rel="noopener">Reviews</a></span>
    <span class="ects">${c.ects % 1 ? c.ects.toFixed(1) : c.ects}</span>
    <span class="hrs">${esc(c.hours || "—")}</span>
    <span class="who">${hi(c.lect || "—")}</span>
    <span class="caret">▶</span>
    ${flags ? `<span class="flags">${flags}</span>` : ""}
  </div>
  <div class="detail">
    <dl style="margin:0">
    ${field("Abstract", c.abs)}
    ${field("Learning objective", c.lo)}
    ${field("Content", c.cont)}
    ${field("Prerequisites / Notice", c.pre)}
    ${field("Literature", c.lit)}
    ${field("Lecture notes", c.ln)}
    ${field("Enrolment notes", c.notes, "note")}
    ${c.comp.length ? `<div class="field"><dt>Competencies</dt><dd><div class="comp">${
      c.comp.map(g => `<div class="compgrp"><div class="gn">${esc(g.group)}</div><ul>${
        g.items.map(it => `<li class="${/assessed/i.test(it[1]) && !/not/i.test(it[1]) ? "" : "na"}">${esc(it[0])}</li>`).join("")
      }</ul></div>`).join("")}</div></dd></div>` : ""}
    </dl>
    ${c.faq ? `<div class="faq">
      <h4>Excerpt from MSc Notion page</h4>
      ${c.faq.avg ? `<div class="metrics">
        <div class="metric"><span class="mk">Core area</span><span class="mv" style="font-size:12px">${esc(c.faq.area)}</span></div>
        <div class="metric"><span class="mk">Avg grade</span><span class="mv">${esc(c.faq.avg)}</span></div>
        <div class="metric"><span class="mk">Pass rate</span><span class="mv">${esc(c.faq.pass)}</span></div>
      </div>` : ""}
      ${c.faq.note.map(p => `<p>${hi(p)}</p>`).join("")}
      <p class="src">MSc Statistics Student FAQ, compiled by the student representatives, last updated 17.03.2026. Informal guidance — not official ETH information. Grade averages are unofficial figures from ETH grade statistics and vary year to year.</p>
    </div>` : ""}
    <div class="dl">
      <a href="${c.url}" target="_blank" rel="noopener">ETH course catalogue ↗</a>
      <a href="https://coursereview.ch/course/${c.code}" target="_blank" rel="noopener">Student reviews &amp; ratings on coursereview.ch ↗</a>
      <span class="hrs">${SEMNAME[c.sem]} · Type ${esc(c.type)} · ${esc(c.hours || "no contact hours")}</span>
    </div>
  </div>
</div>`;
}

function render(){
  const rows = DATA.filter(match);
  const out = document.getElementById("out");
  if(!rows.length){
    out.innerHTML = `<p class="noresults">No course matches those filters. Try clearing the search, or <button class="linkbtn" onclick="document.getElementById('reset').click()">reset the filters</button>.</p>`;
  } else if(st.sort === "cat"){
    let h = "";
    for(const sec of SECS){
      const inSec = rows.filter(r => r.sec === sec);
      if(!inSec.length) continue;
      h += `<section class="sec"><div class="sechead"><h2>${esc(sec)}</h2>
        <div class="cols">
        <span></span>
        <span class="colh">Code</span>
        <span class="colh">Title</span>
        <span class="colh r">ECTS</span>
        <span class="colh"><span class="hourshelp" tabindex="0">Hours<span class="legend" role="tooltip">
          <p class="lt">Weekly contact hours per teaching format, e.g. <b>3V + 2U</b> is three hours of lecture plus two of exercises.</p>
          <dl>
            <dt>V</dt><dd>Lecture</dd>
            <dt>U</dt><dd>Exercise class</dd>
            <dt>G</dt><dd>Lecture with integrated exercises</dd>
            <dt>S</dt><dd>Seminar</dd>
            <dt>A</dt><dd>Independent project work</dd>
            <dt>D</dt><dd>Thesis</dd>
          </dl>
          <p class="lf">Hours marked A are self-directed rather than timetabled, so an 8-credit course listed 3V + 2U + 2A occupies five hours a week in the room.</p>
        </span></span></span>
        <span class="colh">Lecturers</span>
        <span></span>
      </div></div>`;
      const subs = [...new Set(inSec.map(r => r.sub))];
      for(const sub of subs){
        const g = sortRows(inSec.filter(r => r.sub === sub));
        if(sub) h += `<div class="subhead">${esc(sub)}</div>`;
        h += `<div class="list">${g.map(rowHTML).join("")}</div>`;
      }
      h += `</section>`;
    }
    out.innerHTML = h;
  } else {
    out.innerHTML = `<section class="sec"><div class="sechead"><h2>All matching course units</h2>
      <div class="cols">
        <span></span>
        <span class="colh">Code</span>
        <span class="colh">Title</span>
        <span class="colh r">ECTS</span>
        <span class="colh"><span class="hourshelp" tabindex="0">Hours<span class="legend" role="tooltip">
          <p class="lt">Weekly contact hours per teaching format, e.g. <b>3V + 2U</b> is three hours of lecture plus two of exercises.</p>
          <dl>
            <dt>V</dt><dd>Lecture</dd>
            <dt>U</dt><dd>Exercise class</dd>
            <dt>G</dt><dd>Lecture with integrated exercises</dd>
            <dt>S</dt><dd>Seminar</dd>
            <dt>A</dt><dd>Independent project work</dd>
            <dt>D</dt><dd>Thesis</dd>
          </dl>
          <p class="lf">Hours marked A are self-directed rather than timetabled, so an 8-credit course listed 3V + 2U + 2A occupies five hours a week in the room.</p>
        </span></span></span>
        <span class="colh">Lecturers</span>
        <span></span>
      </div></div>
      <div class="list">${sortRows(rows).map(rowHTML).join("")}</div></section>`;
  }
  chips();
  basket();
}

function chips(){
  const el = document.getElementById("secchips");
  if(el.dataset.built) {
    [...el.children].forEach(b => b.setAttribute("aria-pressed", st.secs.has(b.dataset.sec)));
    return;
  }
  el.innerHTML = SECS.map(s => {
    const n = DATA.filter(d => d.sec === s).length;
    return `<button class="chip" data-sec="${esc(s)}" aria-pressed="false">${esc(s)}<span class="n">${n}</span></button>`;
  }).join("");
  el.dataset.built = "1";
  el.addEventListener("click", e => {
    const b = e.target.closest("button[data-sec]"); if(!b) return;
    const s = b.dataset.sec;
    st.secs.has(s) ? st.secs.delete(s) : st.secs.add(s);
    render();
  });
}

function basket(){
  // Deduped by code, so the bar, the requirement chips and the expanded panel
  // all report the same totals. A course ticked in both semesters counts once,
  // under the earlier semester, and shows both tags in the panel.
  const sel = pickedCourses();
  // The bar is always on screen: with nothing selected it still shows the
  // requirement targets, which is the part worth seeing before you start.
  document.getElementById("basket").classList.toggle("nopicks", sel.length === 0);
  const tot = sel.reduce((a,b) => a+b.ects, 0);
  const a = sel.filter(x => x.sems.slice().sort()[0] === "A").reduce((x,y) => x+y.ects, 0);
  const s2 = sel.filter(x => x.sems.slice().sort()[0] === "S").reduce((x,y) => x+y.ects, 0);
  document.getElementById("bn").textContent = sel.length;
  document.getElementById("be").textContent = tot % 1 ? tot.toFixed(1) : tot;
  document.getElementById("bsplit").textContent = `Autumn ${a % 1 ? a.toFixed(1) : a} · Spring ${s2 % 1 ? s2.toFixed(1) : s2}`;
  requirements(sel);
  selectionPanel();
}

const num = v => v % 1 ? v.toFixed(1) : v;

/* One entry per course code. Six codes are listed in both catalogues, so a
   thesis ticked in each semester is one course carrying two semester tags,
   not two courses worth 60 ECTS. */
function pickedCourses(){
  const by = new Map();
  for(const c of DATA){
    if(!picked.has(c.i)) continue;
    const e = by.get(c.code);
    if(e) e.sems.push(c.sem); else by.set(c.code, {...c, sems:[c.sem]});
  }
  return [...by.values()];
}

function selectionPanel(){
  const el = document.getElementById("selpanel");
  if(el.hidden) return;
  const list = pickedCourses();
  const row = c => `<div class="selrow">
      <span class="code">${esc(c.code)}${c.dept ? `<span class="dep">${esc(c.dept)}</span>` : ""}</span>
      <span>${c.sems.sort().map(s => `<span class="semtag ${s}">${s}</span>`).join("")}</span>
      <span class="st">${esc(c.title)}</span>
      <span class="se">${num(c.ects)}</span>
      <button class="unpick" data-code="${esc(c.code)}" aria-label="Remove ${esc(c.title)}">×</button>
    </div>`;

  let h = "";
  for(const sec of SECS){
    const inSec = list.filter(c => c.sec === sec);
    const got = inSec.reduce((a,b) => a+b.ects, 0);
    const min = SEC_MIN[sec];
    const areas = new Set(inSec.map(c => c.sub).filter(Boolean)).size;
    const ok = got >= min && (sec !== "Core Courses" || areas === 3);
    const short = min - got;
    h += `<section class="selgroup"><div class="selsec ${ok ? "ok" : ""}">
        <span class="ss-name">${esc(sec)}</span>
        <span class="ss-min">min ${min} ECTS${sec === "Core Courses" ? " · one per area" : ""}</span>
        <span class="ss-got">${num(got)}${!ok && short > 0 ? ` · ${num(short)} to go` : ""}${
          !ok && short <= 0 && sec === "Core Courses" ? ` · ${3-areas} area${3-areas>1?"s":""} to go` : ""}</span>
      </div>`;
    if(sec === "Core Courses"){
      for(const sub of SUBS){
        const g = inSec.filter(c => c.sub === sub);
        h += `<div class="selsub ${g.length ? "" : "none"}">${esc(sub)}${g.length ? "" : " — none selected"}</div>`;
        h += g.map(row).join("");
      }
    } else {
      h += inSec.length ? inSec.map(row).join("") : `<div class="selnone">Nothing selected yet.</div>`;
    }
    h += `</section>`;
  }
  const tot = list.reduce((a,b) => a+b.ects, 0);
  const fifty = list.filter(c => c.sec !== "Master's Thesis").reduce((a,b) => a+b.ects, 0);
  h += `<div class="seltail">
      <span class="tl">The 52 rule</span><span>${num(fifty)} / 52</span>
      <span class="tl">Selected</span><span>${num(tot)} / 90</span>
      <span class="tl">GESS + free electives — not listed in these catalogues</span><span>8</span>
    </div>`;
  el.innerHTML = h;
}

/* Checks a selection against the MSc Statistics credit rules. GESS (2 ECTS)
   and free electives are not enumerated in these two catalogues, so they are
   shown as untracked rather than silently assumed satisfied. */
function requirements(all){
  // Six codes (semester papers, thesis, the two 0-credit admin units) are listed
  // in both catalogues. Count each code once, or picking a thesis in each
  // semester would read as 60 ECTS.
  const seen = new Set();
  const sel = all.filter(c => seen.has(c.code) ? false : (seen.add(c.code), true));
  const sum = f => sel.filter(f).reduce((a,b) => a+b.ects, 0);
  const core = sum(c => c.sec === "Core Courses");
  const elec = sum(c => c.sec === "Subject Specific Electives");
  const sem  = sum(c => c.sec === "Seminar or Semester Paper");
  const thes = sum(c => c.sec === "Master's Thesis");
  const areas = new Set(sel.filter(c => c.sec === "Core Courses" && c.sub).map(c => c.sub));
  const fiftytwo = core + elec + sem;
  const total = fiftytwo + thes;
  const n = v => v % 1 ? v.toFixed(1) : v;
  const rows = [
    ["Core", `${n(core)}/12`, core >= 12],
    ["Core areas", `${areas.size}/3`, areas.size >= 3],
    ["Electives", `${n(elec)}/15`, elec >= 15],
    ["Seminar", `${n(sem)}/4`, sem >= 4],
    ["52 rule", `${n(fiftytwo)}/52`, fiftytwo >= 52],
    ["Thesis", `${n(thes)}/30`, thes >= 30],
    ["Total", `${n(total)}/90`, total >= 90],
  ];
  document.getElementById("reqs").innerHTML =
    rows.map(([l,v,ok]) => `<span class="req ${ok ? "done" : (sel.length ? "warn" : "")}">
      <span class="rl">${l}</span><span class="rv">${v}</span></span>`).join("")
    + `<span class="req"><span class="rl">GESS + free electives</span><span class="rv">8</span>
       <span class="rl">not in these catalogues</span></span>`;
}

/* ---------- events ---------- */
document.getElementById("out").addEventListener("click", e => {
  const cb = e.target.closest('input[type="checkbox"]');
  const card = e.target.closest(".course");
  if(!card) return;
  const i = +card.dataset.i;
  if(cb){
    cb.checked ? picked.add(i) : picked.delete(i);
    save(); basket();
    e.stopPropagation();
    return;
  }
  if(e.target.closest("a")) { e.stopPropagation(); return; }
  if(e.target.closest(".detail")) return;
  if(e.target.closest(".hdr")){
    open.has(i) ? open.delete(i) : open.add(i);
    card.classList.toggle("open");
    card.querySelector(".hdr").setAttribute("aria-expanded", open.has(i));
  }
});
document.getElementById("out").addEventListener("keydown", e => {
  if((e.key === "Enter" || e.key === " ") && e.target.classList.contains("hdr")){
    e.preventDefault(); e.target.click();
  }
});
const qEl = document.getElementById("q");
let t; qEl.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { st.q = qEl.value.trim(); render(); }, 130); });
document.addEventListener("keydown", e => {
  if(e.key === "/" && document.activeElement !== qEl){ e.preventDefault(); qEl.focus(); }
  if(e.key === "Escape" && document.activeElement === qEl){ qEl.value = ""; st.q = ""; render(); }
});
document.querySelectorAll("[data-sem]").forEach(b => b.addEventListener("click", () => {
  st.sem = b.dataset.sem;
  document.querySelectorAll("[data-sem]").forEach(x => x.setAttribute("aria-pressed", x === b));
  render();
}));
document.getElementById("sort").addEventListener("change", e => { st.sort = e.target.value; render(); });
["avail","ethonly","minects"].forEach((id, n) => document.getElementById(id).addEventListener("change", e => {
  st[["avail","eth","min"][n]] = e.target.checked; render();
}));
document.getElementById("expandall").addEventListener("click", e => {
  const rows = DATA.filter(match);
  const allOpen = rows.every(r => open.has(r.i));
  rows.forEach(r => allOpen ? open.delete(r.i) : open.add(r.i));
  e.target.textContent = allOpen ? "Expand all" : "Collapse all";
  render();
});
document.getElementById("reset").addEventListener("click", () => {
  st.q = ""; st.sem = "all"; st.secs.clear(); st.sort = "cat";
  st.avail = st.eth = st.min = false;
  qEl.value = "";
  document.getElementById("sort").value = "cat";
  ["avail","ethonly","minects"].forEach(id => document.getElementById(id).checked = false);
  document.querySelectorAll("[data-sem]").forEach(x => x.setAttribute("aria-pressed", x.dataset.sem === "all"));
  render();
});
document.getElementById("bclear").addEventListener("click", () => {
  picked.clear(); save();
  const p = document.getElementById("selpanel"), t = document.getElementById("showsel");
  p.hidden = true; t.setAttribute("aria-expanded", "false"); t.textContent = "Show selection";
  render();
});
document.getElementById("showsel").addEventListener("click", e => {
  const p = document.getElementById("selpanel");
  p.hidden = !p.hidden;
  e.target.setAttribute("aria-expanded", String(!p.hidden));
  e.target.textContent = p.hidden ? "Show selection" : "Hide selection";
  selectionPanel();
  stickyOffsets();
});
document.getElementById("selpanel").addEventListener("click", e => {
  const b = e.target.closest(".unpick"); if(!b) return;
  DATA.filter(d => d.code === b.dataset.code).forEach(d => picked.delete(d.i));
  save(); render();
});

/* The subsection header pins directly beneath the section header, so its
   offset has to track the section header's real height — which changes when
   the column labels wrap at narrow widths. */
function stickyOffsets(){
  const sec = document.querySelector(".sechead");
  if(sec) document.documentElement.style.setProperty(
    "--sec-h", Math.round(sec.getBoundingClientRect().height) + "px");
  const bar = document.querySelector(".basket");
  const panel = document.getElementById("selpanel");
  // Measure the collapsed bar: an expanded panel scrolls internally and must
  // not push the page's bottom padding to half the viewport.
  if(bar) document.documentElement.style.setProperty("--bar-h",
    Math.round(bar.getBoundingClientRect().height
      - (panel && !panel.hidden ? panel.getBoundingClientRect().height : 0)) + "px");
}
if(window.ResizeObserver) new ResizeObserver(stickyOffsets).observe(document.body);
window.addEventListener("resize", stickyOffsets);

render();
stickyOffsets();
</script>
"""

open(os.environ.get("OUT", os.path.join(HERE, "index.html")), "w").write(TPL.replace("__PAYLOAD__", PAYLOAD))
print("written", len(TPL) + len(PAYLOAD), "bytes")
