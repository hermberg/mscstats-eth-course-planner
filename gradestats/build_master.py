#!/usr/bin/env python3
"""Merge all five grade-statistics reports into one master table."""
import sys, json, csv, re
sys.path.insert(0, '/tmp/claude-0/-home-claude/a01507f1-07d5-51fe-a474-e2e846f9c3de/scratchpad')
from manual import W24, S24, W26, TITLES
from visible import parse

SRC = "/root/.claude/uploads/a01507f1-07d5-51fe-a474-e2e846f9c3de"
SESSIONS = ["W24", "S24", "W25", "S25", "W26"]
SEM_OF = {"W24": "HS 2023", "S24": "FS 2024", "W25": "HS 2024",
          "S25": "FS 2025", "W26": "HS 2025"}

def num(v):
    if v in (None, "", "·"):
        return None
    try:
        f = float(v)
        return int(f) if f == int(f) and "." not in str(v) else f
    except ValueError:
        return None

# ---- the two text-layer files, read redaction-aware -------------------------
prog = {}
titles = dict(TITLES)
for fn, tag in [("8c91f792-W25_Notenstatistik_MSc_Statistikmerged_2.pdf", "W25"),
                ("1b8806d4-S25_Statistik_MSc_Notenstatistik.pdf", "S25")]:
    sess, recs = parse(f"{SRC}/{fn}")
    assert sess == tag, (sess, tag)
    prog[tag] = {}
    for r in recs:
        if r.get("title"):
            titles.setdefault(r["code"], r["title"])
        prog[tag][r["code"]] = (num(r.get("n_stats")), num(r.get("n_all")),
                                num(r.get("avg_all")), num(r.get("pct_all")))

data = {"W24": W24, "S24": S24, "W25": prog["W25"], "S25": prog["S25"], "W26": W26}

# ---- titles: pull from the catalogue parse we already have ------------------
try:
    cat = json.load(open("/home/claude/courses.json"))
    for c in cat:
        base = c["code"][:-1]           # 401-3622-00L -> 401-3622-00
        titles.setdefault(base + "S", c["title"])
except Exception as e:
    print("note: catalogue titles unavailable:", e, file=sys.stderr)

codes = sorted({c for d in data.values() for c in d})
rows = []
for code in codes:
    row = {"code": code, "title": titles.get(code, "")}
    seen_any = False
    for s in SESSIONS:
        v = data[s].get(code)
        if v is None:
            row[f"{s}_share"] = row[f"{s}_avg"] = row[f"{s}_pass"] = None
            continue
        n_st, n_all, avg, pct = v
        # distinguish "listed but redacted" (–) from "not listed at all" (blank)
        row[f"{s}_share"] = (f"{n_st}/{n_all}" if n_st is not None and n_all is not None
                             else (f"–/{n_all}" if n_all is not None else "–/–"))
        row[f"{s}_n_stats"] = n_st
        row[f"{s}_n_all"] = n_all
        row[f"{s}_avg"] = avg
        row[f"{s}_pass"] = pct
        seen_any = True
    if seen_any or any(data[s].get(code) for s in SESSIONS):
        rows.append(row)

hdr = ["code", "title"]
for s in SESSIONS:
    hdr += [f"{s}_share", f"{s}_avg", f"{s}_pass"]

out = "/home/claude/eth_grade_stats_master.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=hdr, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)

json.dump({"sessions": SESSIONS, "semester_of": SEM_OF, "rows": rows},
          open("/home/claude/eth_grade_stats_master.json", "w"), indent=1, ensure_ascii=False)

print(f"{len(rows)} course codes across {len(SESSIONS)} sessions -> {out}")
for s in SESSIONS:
    d = data[s]
    with_share = sum(1 for v in d.values() if v[0] is not None and v[1] is not None)
    with_avg = sum(1 for v in d.values() if v[2] is not None)
    print(f"  {s} ({SEM_OF[s]}): {len(d)} rows listed, "
          f"{with_share} with stats-cohort count visible, {with_avg} with overall average")
