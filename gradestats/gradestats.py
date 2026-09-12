#!/usr/bin/env python3
"""Per-course exam record keyed to catalogue codes, latest sitting first."""
import json

D = json.load(open("/home/claude/eth_grade_stats_master.json"))
S = D["sessions"]                      # chronological
SEM = D["semester_of"]
COHORT = json.load(open("/home/claude/stats_cohort.json"))

# statistics-cohort averages transcribed from the scanned reports
COHORT_MANUAL = {
    "W24": {"263-5210-00S": (5.04, 100.0), "401-0625-01S": (5.57, 100.0),
            "401-0627-00S": (5.80, 100.0), "401-3621-00S": (5.16, 89.7),
            "401-3622-00S": (5.51, 100.0), "401-3627-00S": (5.36, 100.0),
            "401-3628-14S": (5.37, 89.5), "401-4632-15S": (5.38, 100.0),
            "401-4633-00S": (5.48, 100.0), "401-8623-00S": (4.53, 87.5)},
    "S24": {"252-0220-00S": (5.23, 100.0), "261-5120-00S": (5.68, 100.0),
            "401-3632-00S": (4.92, 93.3), "851-0557-00S": (5.97, 100.0)},
    "W26": {"263-5210-00S": (5.09, 100.0), "401-0625-01S": (5.24, 97.4),
            "401-3621-00S": (4.79, 89.3), "401-3622-00S": (5.48, 100.0),
            "401-3628-14S": (5.36, 100.0), "401-4632-15S": (4.81, 95.8),
            "401-8623-00S": (5.04, 91.7)},
}


def f(x):
    return None if x in (None, "") else float(x)


out = {}
for r in D["rows"]:
    hist = []
    for s in S:
        n_all, avg, pas = r.get(f"{s}_n_all"), r.get(f"{s}_avg"), r.get(f"{s}_pass")
        if n_all is None and avg is None and pas is None:
            continue
        cm = COHORT_MANUAL.get(s, {}).get(r["code"])
        cp = COHORT.get(s, {}).get(r["code"], {})
        hist.append({
            "session": s, "sem": SEM[s],
            "n_stats": r.get(f"{s}_n_stats"), "n_all": n_all,
            "avg": avg, "pass": pas,
            "avg_stats": cm[0] if cm else f(cp.get("avg_stats")),
            "pass_stats": cm[1] if cm else f(cp.get("pct_stats")),
        })
    if not hist:
        continue
    # "latest" = last chronological sitting that carries any figure
    latest = hist[-1]
    peak = max((h["n_all"] or 0) for h in hist)
    rec = {
        "title": r["title"],
        "latest": latest,
        "history": hist,
        # a sitting far smaller than the course's usual cohort is a retake round
        "retake": bool(peak and latest["n_all"] and latest["n_all"] < 0.4 * peak),
    }
    out[r["code"][:-1] + "L"] = rec          # 401-3622-00S -> 401-3622-00L

json.dump(out, open("/home/claude/gradestats.json", "w"), indent=1, ensure_ascii=False)

cat = {c["code"] for c in json.load(open("/home/claude/courses.json"))}
hit = sorted(set(out) & cat)
print(f"{len(out)} courses with an exam record; {len(hit)} of them are in the MSc catalogue "
      f"(of {len(cat)} catalogue codes)")
withavg = [c for c in hit if out[c]['latest']['avg'] is not None]
print(f"  {len(withavg)} have an average in their latest sitting")
print(f"  retake-sitting flags: {[c for c in hit if out[c]['retake']]}")
