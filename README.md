# MSc Statistics @ ETH — Course Planner

A single-page course browser and credit planner for the ETH Zürich MSc in Statistics,
built from the official course catalogue.

**Live:** <https://hermberg.github.io/mscstats-eth-course-planner/>

Or open `index.html` from a checkout — the page is fully self-contained, so it needs no
server and no build step.

![Autumn and spring catalogues merged into one searchable table](docs/screenshot.png)

## What it does

- **All 90 course units** from the autumn and spring catalogues in one table, parsed
  verbatim — abstract, learning objective, content, prerequisites, literature, lecture
  notes and the competency matrix for each.
- **Full-text search** across abstracts and prerequisites, not just titles, so "causal",
  "R", or "high-dimensional" surfaces courses whose titles never say so.
- **Live requirement checking.** Tick courses and the bar checks the selection against
  the degree regulations: 12 ECTS core with one course per area, 15 electives, 4 seminar,
  the 52 rule, 30 thesis, 90 total.
- **Programme rules** — the credit ladder, registration and exam rules, and course-level
  commentary from the MSc Statistics Student FAQ, including grade averages and pass rates
  for the six core courses.
- Deep links per course to the ETH catalogue entry and to coursereview.ch.

## Repository layout

| File | Role |
|---|---|
| `parse.py` | PDF → `courses.json`. The whole extraction pipeline. |
| `build.py` | `courses.json` → `index.html`. Page template, styles and FAQ layer. |
| `courses.json` | The parsed catalogue, 90 records. The useful artifact if you only want data. |
| `index.html` | Generated page. Committed so GitHub Pages can serve it directly. |
| `pdf/` | The two catalogue prints the parse reads. |
| `robots.txt` | Keeps the published page out of search indexes. See NOTICE.md. |

## Rebuilding

```bash
python3 parse.py     # pdf/*.pdf  -> courses.json   (needs pdftotext, from poppler-utils)
python3 build.py     # courses.json -> index.html   (no dependencies)
```

Both honour environment overrides: `PDF_DIR`, `COURSES`, `OUT`.

To refresh for a new semester, print the catalogue pages from
`vvz.ethz.ch` (Statistics Master curriculum, "Catalogue data" view, print to PDF) into
`pdf/`, then re-run both scripts. Filenames only need to contain "Autumn" or "Spring".

## Notes on the parser

The catalogue is a fixed-width layout, not a table, which makes three things non-obvious:

1. **The value column drifts between pages.** Computing the label/value split once per
   course corrupts any course spanning a page break, so the split is derived per line
   from the left gutter.
2. **One line can carry two columns.** A wrapped title and a wrapped lecturer list share
   a line, so continuation lines are split at the lecturer column rather than taken whole.
   Without this, `Responsible Machine Learning with Insurance Applications` absorbs
   `C. Lorentzen-Geiser`.
3. **Lists are printed without bullets.** Wrapped prose always produces at least one
   long line, so a multi-line block where nothing is long is a list, not a paragraph.

### Verification

The parse is checked by a bidirectional word-level diff against the source text, per
course: **0 content words missing, 0 added**. Because that check compares whole records,
it cannot catch a word moving *between* fields within one course — a second check exists
for that (no title may end in initial-plus-surname; no lecturer field may contain prose
words), and that is how bug 2 above was found.

### Known source quirks

These are in the catalogue itself, not parse errors:

- `447-6237-00L` and `401-3620-24L` have genuinely empty Abstract fields.
- Four autumn courses have no lecturer listed; all are either not running or UZH-hosted.
- `401-3602-00L` lists its lecturer literally as "not available".
- Six codes appear in both catalogues — all administrative (semester papers, thesis,
  Scientific Works, Lunch Sessions). They are counted once by the planner.
- Free Electives, Science in Perspective and Additional Admission Requirements carry no
  course rows in these PDFs; those sections link out to other catalogue pages.
- The spring catalogue's "does not take place this semester" flags describe that specific
  spring and are not shown, since availability in a later spring is not yet published.

## Sources and status

See [NOTICE.md](NOTICE.md). Short version: the course data is ETH Zürich's, the
commentary and grade figures come from a student-run FAQ and are unofficial, and nothing
here is an authoritative statement of the study regulations.

## Licence

The code (`parse.py`, `build.py`, the page template) is MIT. The catalogue content and
FAQ excerpts it processes are not the author's to license — see NOTICE.md.
