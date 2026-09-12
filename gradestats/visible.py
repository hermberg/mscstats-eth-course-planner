#!/usr/bin/env python3
"""Extract the grade tables using only text a human can actually SEE.

Redaction in these files is applied three different ways — vector rectangles,
raster overlays, and (in the scans) burnt into the page image. Rather than
special-case each, render the page and measure the mean luminance beneath every
word's bounding box: text under an opaque black overlay is discarded.
"""
import sys, collections, re
import pymupdf

DPI = 150
COLS = ["n_stats", "avg_stats", "sd_stats", "unterbr", "best", "nbest", "pct_stats",
        "repet", "r_unterbr", "r_best", "r_nbest", "r_pct",
        "n_all", "avg_all", "sd_all", "pct_all"]
CODE = re.compile(r'^\d{3}-\d{4}-\d{2}[A-Z]{1,3}$')
NUM = re.compile(r'^\d+(?:\.\d+)?$')


def visible_words(page, cutoff=90):
    """Words the reader can see, with coordinates in DISPLAY space.

    Some of these files store landscape pages as rotated portrait, and word
    coordinates then arrive in unrotated space while the render is rotated —
    so every word box is mapped through the page's rotation matrix first."""
    zoom = DPI / 72.0
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csGRAY)
    buf, W, H = pix.samples, pix.width, pix.height
    rot = page.rotation_matrix
    out = []
    for w in page.get_text("words"):
        r = pymupdf.Rect(w[:4]) * rot
        w = (r.x0, r.y0, r.x1, r.y1) + tuple(w[4:])
        x0, y0, x1, y1 = [v * zoom for v in w[:4]]
        xa, xb = max(0, int(x0)), min(W, int(x1) + 1)
        ya, yb = max(0, int(y0)), min(H, int(y1) + 1)
        if xb <= xa or yb <= ya:
            continue
        tot = n = 0
        for yy in range(ya, yb):
            row = buf[yy * W + xa: yy * W + xb]
            tot += sum(row); n += len(row)
        if n and tot / n >= cutoff:          # not sitting on a black field
            out.append(w)
    return out


def rows_from(page):
    words = visible_words(page)
    lines = collections.defaultdict(list)
    for w in words:
        lines[round((w[1] + w[3]) / 2 / 3.0)].append(w)
    # column anchors from this page's own header
    hdr = None
    for _k, ws in sorted(lines.items()):
        ws = sorted(ws, key=lambda w: w[0])
        txt = [w[4] for w in ws]
        if txt.count("Anzahl") >= 6 and "Durch-" in txt:
            hdr = ws
            break
    if not hdr:
        return []
    anchors = [(w[0] + w[2]) / 2 for w in hdr]
    if len(anchors) != 16:
        return []
    out = []
    for _k, ws in sorted(lines.items()):
        ws = sorted(ws, key=lambda w: w[0])
        if not ws or not CODE.match(ws[0][4]):
            continue
        code = ws[0][4]
        nums = [w for w in ws[1:] if NUM.match(w[4])]
        # numeric block starts right of the title column
        nums = [w for w in nums if w[0] > anchors[0] - 40]
        title = " ".join(w[4] for w in ws[1:] if w[2] <= anchors[0] - 40)
        rec = {"code": code, "title": title}
        for w in nums:
            c = (w[0] + w[2]) / 2
            j = min(range(16), key=lambda k: abs(anchors[k] - c))
            rec.setdefault(COLS[j], w[4])
        out.append(rec)
    return out


def parse(path):
    doc = pymupdf.open(path)
    sess = None
    m = re.search(r'Berücksichtigte Noten:\s*([A-Z]\d{2})', doc[0].get_text())
    if m:
        sess = m.group(1)
    recs = []
    for page in doc:
        recs += rows_from(page)
    return sess, recs


if __name__ == "__main__":
    for p in sys.argv[1:]:
        s, recs = parse(p)
        print(f"\n=== {p.split('/')[-1][:44]} session={s} rows={len(recs)}")
        for r in recs:
            print("   ", r["code"],
                  "n_stats=", r.get("n_stats", "·"),
                  "| n_all=", r.get("n_all", "·"),
                  "avg_all=", r.get("avg_all", "·"),
                  "pct_all=", r.get("pct_all", "·"))
