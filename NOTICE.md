# Sources, provenance and status

This repository is a personal study-planning tool. It is **not** an official ETH Zürich
resource and carries no authority over any of the material it presents.

## Course catalogue data

`courses.json`, `pdf/` and the course content rendered in `index.html` are taken from
the **ETH Zürich course catalogue** (`vvz.ethz.ch`) for the Master's Programme in
Statistics, autumn and spring semesters. Copyright in that material belongs to ETH
Zürich. It is reproduced here unmodified, for personal academic planning, with each
course linking back to its catalogue entry.

The catalogue is **published openly by ETH** — no login, paywall or enrolment is required
to read any of it, and the PDFs here are ordinary prints of pages anyone can visit. So
nothing in this repository was private before it was published here. That speaks to
*exposure*, not to *copyright*: material being freely readable at its source is not the
same as being freely redistributable, which is why this repository reproduces it
unmodified, attributes it, links every course back to its catalogue entry, and licenses
only the code.

The catalogue changes continuously — courses are withdrawn, credits and lecturers change,
biennial courses skip years. **Treat anything here as a snapshot and verify against the
live catalogue before acting on it.**

## Programme structure, rules and course commentary

The credit ladder, registration and exam rules, and the per-course commentary marked
"Excerpt from MSc Notion page" are excerpted from the **ETH MSc Statistics Student FAQ**,
compiled by the MSc Statistics student representatives (last updated 17 March 2026).

That document states explicitly that it is informal guidance and does **not** represent
official information or positions of ETH Zürich.

**Grade averages and pass rates are unofficial figures** compiled from ETH grade
statistics by the student representatives. They vary year to year and should not be read
as predictions.

For authoritative rules, see the study regulations (Art. 30) and the official programme
FAQ at `math.ethz.ch/sfs/education/msc-in-statistics`.

## Grade statistics

`gradestats/` is derived from five ETH reports, *Notendurchschnitte pro Fach und Stufe für
Master-Studiengang Statistik, Regl. 15.10.2019*, for exam sessions W24, S24, W25, S25 and
W26. These are internal ETH statistics that circulate among students; they are not
published by ETH.

**The source PDFs are deliberately not committed here.** They carry more than the derived
figures — per-cohort detail, repeat-attempt breakdowns — and in one of them the redaction
is cosmetic, so distributing the file would distribute the hidden values along with it.
Only the visible, derived numbers are in this repository.

**Nothing redacted was used.** Each page was rendered and the brightness measured beneath
every word before any figure was read, so values hidden behind a black box were discarded
rather than recovered. Cells that are redacted appear as "–".

These figures describe past sittings under past examiners. They are descriptive, not
predictive, and small cohorts make single sessions noisy.

## No hosted site

GitHub Pages is switched off for this repository, on purpose. The page is meant to be
cloned and opened locally, not browsed as a website.

Note what that does and does not achieve: it removes the served site, the crawlable
`github.io` domain, and the appearance of a publication. It does **not** make the data
private — this repository is public, so `index.html` and `gradestats/` remain readable and
downloadable on github.com. Anyone who wants the numbers private should either remove
`gradestats/` from the repository or make the repository private.

`robots.txt` is left in place from the period when the page was served. It is inert now.

## Dates

Any specific dates in the interface — notably the UZH mobility application deadline —
were derived from published semester dates at the time of writing and should be confirmed
with the relevant registrar before being relied on.

## coursereview.ch

Each course links out to `coursereview.ch`. **No review content is stored in this
repository and none was scraped.** That site's `robots.txt` disallows automated agents and
carries an express reservation of rights under Article 4 of EU Directive 2019/790; the
links are ordinary references, which is what its content signal (`use=reference`) permits.
Reviews there are written by individual students and remain their authors' work.

## If you are one of the sources

If you are an ETH staff member, or one of the student representatives who wrote the FAQ,
and you would rather this material were not published here, open an issue and it will be
removed. That applies equally to the grade statistics in `gradestats/`.

## Code

The parser, the build script and the page template are MIT-licensed. That licence covers
the code only, not the catalogue content or the FAQ excerpts it processes.
