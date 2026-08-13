# GCSE Maths Worksheet Generator

A local web app that generates UK GCSE maths practice worksheets as PDFs with worked
solutions, searchable/browsable across 6 curriculum sections.

- **Backend**: `backend/` — Python 3.12, FastAPI, sympy (symbolic math), ReportLab (PDF + diagrams)
- **Frontend**: `frontend/` — React + Vite + TypeScript
- **Repo**: https://github.com/jamescostello1998-commits/gcse-maths-worksheet-generator (`master` is up to date — every session's work has been committed and pushed before ending)

`first-pr-practice/` in this same folder is an **unrelated** git-practice repo (its own
`.git`) — ignored via the root `.gitignore`. Don't touch it when working on this app.

## Where to pick up next

**⚠️ Read this first — topic ids changed in step 44.** Every topic id now ends in
**`_F` (Foundation) or `_H` (Higher)**, e.g. `bearings_cosine_rule_H`, `linear_two_step_F`,
`area_circle_F`. There are no bare/`_foundation`/`_higher` ids left. If you're following
an old note that names an id without the suffix, add `_F`/`_H` (the base is otherwise
unchanged; the old `_foundation`/`_higher` word was stripped, so e.g. old
`bearings_foundation` is now `bearings_F`, old `angles_triangle_higher` is now
`angles_triangle_H`). **Generator/modelled-example function names and `dedup_key`
prefixes were deliberately NOT renamed** — only `id=`/`topic_id=` strings carry the
scheme. The full chronology below still uses the *old* ids in its historical entries
(steps 1-43) — that's deliberate (they were correct at the time); mentally append the
tier suffix if you go looking for one. See step 44 for the exact rename rule and how the
migration was done safely.

**CURRENT STATE:** **320 topics**, backend suite **1004/1004**, frontend **65/65**, all 60
Practice Test papers exactly 100 marks. Steps 54-59 are all committed & pushed (steps 54-56 in `c6cce8f`, step 57 in `9ba81d8`, step 58 in `dbda953`, step 59 in the latest commit).
Practice Tests were deliberately NOT rebuilt in any of these steps (no existing diagram param
SCHEMA changed - only optional new params, label positions, and prompt text, all backward-
compatible). No known bugs.

**⚠️ One deliberately-deferred follow-up from step 59 (graph review):** the STATISTICS charts
that have a numeric-numeric axis pair (cumulative frequency, scatter, time series) still use
their reading grid with RECTANGULAR cells - only the coordinate/plotting graphs were made
square-celled (that's where the user's "never rectangles" instruction was aimed; the stats
scope they agreed was labels + finer CF/box grids, which is done). If the user asks for the
stats graphs to be square too, that's a `_draw_stats_axes` rework (compute a square-celled
centred plot area + matching `to_px`, like `_draw_scaled_axes` now does) applied to
cumulative_frequency/scatter/time_series only - bar/box have a categorical axis so square cells
don't apply there.

**What the recent sessions did — an ongoing aesthetic-review process (steps 34-59).** The user
works through the two `all_topics_review_*.pdf` documents and sends feedback, mostly as per-topic
items (occasionally by page range). Steps 34-53 are in the chronology; the most recent batches:
- **Step 54** — a coverage-gap audit against maths4everyone.com, then built the 5 genuine gaps it
  found: `collect_like_terms_F`; `midpoint_of_segment_F` + `distance_between_points_H` (new
  `coordinate_geometry.py`); `surds_add_subtract_H`; `circle_parts_F` (+ new `circle_part`
  diagram); `set_listing_F`. **314 → 320 topics.**
- **Step 55** — 5 diagram/wording fixes: semicircle-compound prompts trimmed (F uses the dp/sf
  rounding engine); subtract-compound hole labels moved into the shaded frame; sector radius label
  moved outside the wedge; `angles_straight_line_H` width-aware label placement;
  `angles_triangle_H`/`angles_exterior_H` algebraic labels moved closer to their angle.
- **Step 56** — 4 fixes on the 3D + triangle-rule diagrams: `pythagoras_3d_H` length label off the
  depth edge + prompt "Find ag"; `trig_3d_H` prompt "Find the angle gac" + base diagonal drawn;
  `sine_rule_H`/`cosine_rule_H` context removed (vertices A/B/C lettered on the diagram, unknown
  angle drawn as a bare arc via `angle_X_label=""`); `triangle_area_sine_rule_H` legible-shape
  fallback for very acute angles (`_triangle_min_angle` < 28° → plausible scalene).
- **Step 57** — 3 fixes: bigger plans/elevations blank grids (10×10 squares, real squared-paper
  size); the cube diagram foreshortened (`is_cube` cabinet projection) so it reads as a cube;
  **every volume/surface-area prompt standardised** to "Here is a {shape}. Find its
  {volume|surface area}[, correct to … | in terms of π]." with dimensions read off the diagram
  (cuboid/cube/prism/cylinder F+H/cone/sphere/pyramid/frustum; `compound_3d_*` left as-is — no
  single shape name).
- **Step 58** — histograms fixed so a student never estimates frequency density off the graph
  (`histogram_plot_H`/`histogram_interpret_H`): frequencies now built as `k × (width÷5)` so every
  density is an exact multiple of **0.2** (whole-number frequencies kept), and `draw_histogram`
  rebuilt as genuine fine squared paper (small squares worth 0.2 density × 2.5 x, visually square,
  y numbered every 1.0, x every 10) so every bar top lands on a gridline — density read by counting
  squares. Also fixed the old clipped axis labels. +1 regression test (density ≡ 0.2 multiple).
  Suite 1000 → 1001. No practice-test rebuild (no frozen paper uses a histogram topic; param
  schema unchanged).
- **Step 59** — a whole-app **graph review** (all coordinate/plotting graphs + stats charts). The
  algebra graph engine (`_draw_scaled_axes`) was reworked so every grid cell is a **true square**
  (never a rectangle — user's emphatic instruction): nice major step per axis + one shared
  pixel-per-square + a shared minor subdivision, so a lopsided range (steep line, cubic, 0-360 trig)
  is absorbed by a bigger major step instead of stretching cells, and a fine minor grid means every
  plotted/read value lands on a line. The **flat-cap clamp bug** was fixed (curves now clipped
  cleanly at the window via `_clip_curve_segments`, not drawn flat). **Axis titles** no longer clip:
  long y-titles rotate vertically up the axis (`_vertical_label`), x-titles centre below - applied
  to both `_draw_scaled_axes` and `_draw_stats_axes`. Stats: **cumulative-frequency & box-plot grids
  made finer** (`_grid_minor_step` divisor). User chose **compact** size (square cells, current
  footprint) and **different units per axis OK** (square pixels, e.g. trig 10°×0.2). +3 regression
  tests. Suite 1001 → 1004. No practice-test rebuild (rendering-only, no schema change - verified a
  frozen paper with function_graph+piecewise still renders). See the deferred stats-square note above.

See chronology steps 54-59 for the full technical detail on each.

**Next natural step (if the user returns to the review):** the next chunk of review feedback (the
review is NOT confirmed finished — steps 49-57 were per-topic items the user sent directly rather
than page ranges, so expect either those or another page range; they may equally have a new
one-off feature in mind, as steps 45-46 were). The review workflow each batch: read the named
items → fix them (render REAL PDFs to verify diagram/overlap
fixes; don't trust unit tests for visual issues) → if a topic count changed, bump the four
`== N` assertions (`test_routes.py` ×2, `test_modelled_example_renderer.py`,
`test_worksheet_builder.py`) and the per-section table below → if any diagram param SCHEMA
changed, rebuild the 60 Practice Test papers (`python -m app.practice_tests.build`, from
`backend/`) and confirm all 100 marks → full `pytest` → regenerate + send both
`all_topics_review_*.pdf` (`python -m scripts.generate_review_pdfs`) → commit+push. If there's
ever a gap with no pending review feedback, see "Ideas for a future session" (bottom of file).

*(Historical note: chronology steps 34-46 were merged to `master` long ago — the old PR #3 /
`aqa-spec-gap-topics` branch is deleted, and the diagram-scale-overhaul (step 47) is also
merged. Ignore any "not merged"/branch/`HEAD` wording in the chronology below; it was correct
at the time. `master` is the working branch and is fully up to date.)*

Once the user's next chunk of feedback (or confirmation the review is fully done)
arrives, check "Ideas for a future session" (bottom of this file) for candidate
follow-ups (the remaining medium-confidence OCR-spec gaps from step 32's audit, the
remaining medium/low-confidence AQA-spec gaps from step 31's audit, stem-and-leaf
diagrams, standard deviation, a handful of lower-confidence curriculum-audit candidates,
saved worksheet history, deployment, a KS3 Bell Tasks tier, the full language-variety
rollout beyond the 4 files step 35 piloted it on, etc.) if there's ever a gap with no
pending review feedback.

## Current state

*(For a session-by-session history of how it got here, see the Chronology section below.)*

**320 topics across 6 sections**, all procedurally generated with independent
correctness verification (never trust the generator's own arithmetic — always
cross-check via a second method: sympy substitution/solve, coordinate geometry,
stdlib `statistics`/`Decimal`, brute-force sample-space enumeration, etc.),
**except the 3 Constructions topics** (`construction_angle_bisector`,
`construction_perpendicular_bisector`, `construction_triangle`), which are
"describe the method" text questions with no way to numerically check a
described construction — author-review only, no `verify()` at all (see
chronology step 27).
Full backend and frontend suites passing (see "Where to pick up next" above for the
current counts — this line is deliberately not a hardcoded snapshot, since it drifted
out of date for many sessions in a row before being replaced with this pointer).

**Practice Tests (fixed/static content, not procedural — the one deliberate exception
to the paragraph above)**: a 7th homepage section, `backend/app/practice_tests/`,
holds 60 committed papers (`data/*.json`) — **10 sittings per tier, each a real
OCR-shaped sitting of 3 separate 100-mark, 1h30m papers** (`foundation-01-paper1`
.. `foundation-10-paper3`, `higher-01-paper1` .. `higher-10-paper3`), matching how a
real OCR GCSE Maths series is actually structured (J560/01-03 Foundation, J560/04-06
Higher). This structure, the mark-scheme conventions, and the Formulae
Sheet (all below) were calibrated in chronology step 30 by directly reading real OCR
papers and mark schemes spanning June 2017 to June 2024 (via revisionmaths.com's past-
papers page) — **never by copying their actual question or mark-scheme text**, only
their structure, marking conventions, and generic mathematical facts (formulae are not
copyrightable expression). **Paper 2 (Foundation) and Paper 5 (Higher) — the middle
paper of every 3-paper sitting — are non-calculator**, matching the real OCR J560
specification read directly in chronology step 32 (this had been built wrong in step
30 — assumed calculator-allowed throughout — until the actual spec PDF was read and
said otherwise). `PracticeTestPaper.calculator_allowed` drives this: `build.py`
computes a second, calculator-filtered topic pool per tier
(`topic_selection.eligible_topics_by_section(tier, calculator_allowed=False)`, which
excludes every topic in the curated `CALCULATOR_ONLY_TOPIC_IDS` frozenset — messy-
decimal trigonometry, calculator-π area/volume topics, `standard_form_calculator`,
`iteration`, etc., err-toward-inclusion since this only affects 1 of every 3 papers)
and uses it whenever `paper_number == 2`; the cover page's instructions box and meta
line both reflect this (`"You must NOT use a calculator for this paper"` /
`"Non-calculator"`), and the frontend shows a "Non-calculator" badge on the affected
paper card. Each paper is still assembled by *freezing* real output
from the existing 296 generators rather than writing new exam-style content by hand —
that identity is unchanged from when this feature was first built (step 22). Built via
a one-time script (`build.py`, run manually — `python -m app.practice_tests.build` —
not at request time): `topic_selection.py` picks a spread of topics per paper
(a curated per-section mark-share target approximating real GCSE weighting, plus a
`core`/`common`/`niche` per-topic priority tag so frequently-examined skills recur
across several papers while advanced ones appear less often — see its module
docstring for the exact numbers), then each chosen topic's `generate_xxx(fixed_tier,
random.Random(seed))` is called **directly** (bypassing `build_worksheet`) with a seed
derived deterministically from `(paper_id, topic_id)` via SHA-256 (never Python's
built-in `hash()`, which is randomised per-process for strings) — confirmed via a
full-codebase grep that no generator anywhere touches the bare `random` module outside
its passed-in `rng`, so this is fully reproducible: re-running `build.py` produces
byte-identical JSON every time, verified by a test. `select_paper_topics` is called
independently (fresh seed) once per paper — it only dedupes topics *within* one paper,
so the same topic can legitimately recur across a sitting's 3 papers, matching how
real OCR papers work (a skill can appear on more than one paper in a series). Every
paper's marks sum to **exactly 100**, enforced by `topic_selection.select_paper_topics`'s
fill-then-close algorithm (self-restarts with a perturbed seed if it paints itself into
a corner) plus a `build.py`-level repair pass (`_repair_to_target`) for the handful of
topics whose `solution_steps` length varies by branch, occasionally drifting the real
total from the "typical" total the selection was planned against — and a whole-paper
retry (`MAX_PAPER_RETRIES`) as the final safety net.

The OCR-style mark scheme (`app/practice_tests/mark_scheme.py`) is a **systematic
approximation calibrated against real OCR mark schemes** (spanning June 2017 to June
2024, both tiers) rather than hand-authored per-question mark allocations: a
question's own `solution_steps` become M1 method marks (1 per step, capped at 4, with
any overflow folded into the last one) followed by one A1 accuracy mark quoting the
question's own `final_answer` with `oe` appended (e.g. `"30 oe"`); a multiple-choice-
style `final_answer` (matches `^[A-D]\)`, e.g. `"B) 3/4"`, this app's convention for
"identify the correct one" questions) gets a single independent B1 instead, since
there's no method to mark. `oe`/`isw`/`nfww`/`rot`/`soi`/`dep` were all confirmed
current and stable 2017→2024 by reading the real "Subject-Specific Marking
Instructions" pages directly; **`cao` ("correct answer only") was explicitly defined
in the 2017/2019 schemes but is dropped from the 2022/2024 ones in favour of plain
accepted-answer wording** — this module deliberately follows the current convention,
not the retired one (the original build, before real papers were available to check
against, used `"{answer} oe (cao)"`). The rendered mark-scheme PDF now also opens with
a short, own-words summary of M/A/B marking convention and the abbreviation key (in
`practice_test_renderer.py`'s `_marking_instructions_box`) — paraphrased from what was
read, not copied. **`PracticeQuestion`/`PracticeTestPaper`
(`practice_tests/models.py`) are deliberately separate from `core/models.py`'s
`Question`/`TopicDefinition`** — none of the 296 existing generators or their tests
were touched to build this feature. `PracticeTestPaper` carries `sitting_id`/
`paper_number` alongside the original `id`/`name`/`tier`/`questions`, so the API/
frontend can group a sitting's 3 papers together without any route-shape changes —
`paper_id` (e.g. `foundation-03-paper2`) is still the one unique identifier for
`GET /api/practice-tests/{paper_id}/paper` and `.../mark-scheme`. Two PDF renderers
(`app/pdf/practice_test_renderer.py`) follow the existing `SimpleDocTemplate` +
flowable-list idiom: `render_practice_test_paper` (an original-wording — not copied
from any real OCR paper — cover page with candidate-detail boxes and an instructions
box, now followed by a tier-specific **Formulae Sheet page** — `_formulae_sheet_elements`
— before Q1, reusing the existing `right_triangle`/`general_triangle` diagram kinds for
its reference figures; then numbered questions with marks shown as `[n]` in a
right-aligned column, followed by real exam-style working space — `_working_lines`
draws a number of ruled lines scaled to the question's own mark value
(`_lines_for_marks`, roughly 2 lines per mark) — and a distinct boxed `_answer_line`
below it, added in chronology step 32 per direct user request to make the paper look
more like a real OCR script) and `render_mark_scheme` (the marking-instructions box described
above, then a `Question | Answer | Marks | Guidance` table, one row per question, each
M1/A1/B1 point stacked in the Guidance cell). Three GET routes (`GET /api/practice-tests`,
`.../{id}/paper`, `.../{id}/mark-scheme`) since content is fully static per id — no
request body needed, unlike the POST-based worksheet/modelled-example endpoints.
Frontend: `PracticeTestsView` groups the flat paper list by `sittingId` client-side
(mirroring how `SectionView` already groups client-side by tier) before rendering one
`PracticeTestCard` per sitting; each card shows all 3 papers with their own independent
Test Paper/Mark Scheme download buttons (`PracticeTestCard`'s `papers` prop is now an
array, one `useDownloadTestPaper`/`useDownloadMarkScheme` hook pair per paper), rendered
as a distinct block **underneath** `HomeScreen` in `App.tsx` (not folded into the
6-section grid, since a static paper list is structurally different from the
procedural topic tree).

**A real, pre-existing diagram bug was found and fixed while building the Formulae
Sheet** (via rendering the actual PDF and looking closely, not a unit test — same
story as most gotchas in this file): `draw_general_triangle` (`app/pdf/diagrams.py`,
shared by the existing sine-rule/cosine-rule/triangle-area topics) placed its
`side_c_label` only 6 units above the "Diagram NOT accurately drawn" caption, which
visibly overlapped once a caller labelled all three sides *and* used the default
not-to-scale caption at the same time — several existing cosine-rule topics already
do exactly this (label `side_a`/`side_b`/`side_c` together), so this was a latent bug
in already-shipped output, only now surfaced because the Formulae Sheet's reference
triangle is the single densest use of this diagram kind (all three sides and all
three angles labelled at once). Fixed by moving the label closer to the base
(offset `-8` instead of `-12`), giving real clearance from the caption.

**Real bug found and fixed while building this** (via this feature's first end-to-end
visual check, not the existing unit tests — same story as most gotchas in this file):
`estimation.py`'s `_round_to_1sf` used `Decimal.quantize(Decimal(1).scaleb(exp), ...)`
to round to 1 significant figure — correct in *value* (which is why the existing
independent-verification check never caught it), but when the rounded value lands on
a positive power of ten (e.g. 27.3 → 30), `Decimal.quantize` keeps that exponent
internally, so plain `str()`/f-string interpolation prints `"3E+1"` instead of `"30"`.
This had been silently shipping in `estimation_rounding`'s prompt/steps text (and its
modelled-example twin) since chronology step 5 — never caught because no prior content
type rendered that generator's raw `solution_steps` text somewhere a human would
actually read closely enough to notice, until the practice-tests mark scheme did.
Fixed by reformatting through fixed-point notation (`Decimal(format(quantized, "f"))`)
inside `_round_to_1sf` itself, so every caller (both the normal generator and the
modelled example) is fixed by the one change.

**Bell Tasks (chronology step 33)**: a third homepage feature, `backend/app/bell_tasks/`,
sitting alongside the 6-section grid and Practice Tests exactly like Practice Tests sits
alongside the grid (its own sibling `<section>` in `App.tsx`, not folded into either). A
teacher picks a KS3/KS4 sub-menu (KS3 is a disabled dead link, "for later", per direct
request — only KS4 is built) then, for KS4, exactly 6 topics from the full flattened list
of all 296 existing topics (no curation - every topic is eligible, including diagram-heavy
ones) via 6 searchable topic pickers (`BellTasksView.tsx`, one per box — a plain `<select>`
was tried first but a 296-option native dropdown is unusable, so each box is a
`SearchableTopicSelect.tsx` combobox instead: a text input that shows the full topic list
on focus and filters it live by substring as the teacher types, reusing `TopicSearch.tsx`'s
established filter-as-you-type convention rather than inventing a new one), each excluding
topics already chosen in another box so the 6 stay distinct without a separate validation
error state. `POST /api/bell-tasks` (`GenerateBellTasksRequest.topic_ids`, a Pydantic
`field_validator` enforcing exactly 6 distinct ids) returns a **fresh, freshly-random
`.pptx` every single call** — no persistence anywhere, matching the plain Worksheet
Generator's behaviour, not Practice Tests' frozen/static one. `generate_bell_tasks_pptx`
(`app/bell_tasks/generator.py`) calls `build_worksheet(topic_id, topic.fixed_tier, count=5,
rng=shared_rng)` once per chosen topic (one shared `random.Random()` across all 6, same
precedent as `create_modelled_example`'s multi-call sharing) — **100% reuse of the existing
verified generator pipeline**, no new question-generation logic anywhere in this feature.

The output deck's exact visual style (a purple `#531D60` theme, two real logo images -
Sparx and "Need to Know Book & Planners" - a page-number box, a live date field, and a
3×2 grid of 6 numbered boxes per slide) was **not rebuilt from scratch** — the user
supplied a real reference PowerPoint and explicitly chose "keep everything exactly as-is",
so the reference file itself (already containing exactly 5 correctly-styled blank
slides, one per weekday) was copied in verbatim as
`app/bell_tasks/assets/bell_task_template.pptx` and is opened fresh per request via
`python-pptx` (`Presentation(template_path)`) — never mutated on disk, only in memory,
then saved to a `BytesIO` and returned as bytes. **Box numbering is column-major**,
matching the template's own existing "1./3./5." (row 0) / "2./4./6." (row 1) cell
content — confirmed by reading the real XML, not assumed — so box *N* is a fixed topic
for the whole week: box *N*'s cell on weekday-slide *K* holds that topic's *K*th (of 5)
generated question (`app/bell_tasks/layout.py`'s `BOX_TO_ROW_COL`). No answer key is
generated at all (a deliberate, explicit user choice, unlike every other feature in this
app) - purely question-only output, matching the reference file's own blank template.

Three new supporting pieces, all built and verified in isolation before any pptx-specific
code was written (this project's own established "verify the riskiest piece first"
diagram-engine precedent): (1) `app/bell_tasks/diagram_raster.py` rasterizes a topic's
existing ReportLab `Drawing` (from `render_diagram`, completely unchanged) to PNG bytes for
embedding as a picture shape — via `reportlab.graphics.renderPDF` (pure vector-to-PDF, no
Cairo/`renderPM` needed) to a small in-memory one-page PDF, then `fitz` (already pinned)
rasterizes page 0 - reusing this project's own established PDF-to-PNG pattern (see
"Verifying new topics visually" below) but applied to a single standalone `Drawing` instead
of a whole rendered page; (2) `app/bell_tasks/math_tokenizer.py`'s `tokenize()` adapts
`mathtext.py`'s existing fraction/exponent/variable/vector regexes, but instead of building
ReportLab markup, splits a prompt into an ordered list of typed tokens - plain `TextSpan`s
(rendered as a normal `python-pptx` run, `"Calibri"` for words or `"Cambria Math"` for
bare digits/operators/`x`/`n`, a literal per-token **font** switch per the user's original
instruction) plus three *structural* token types - `FractionSpan`, `ExponentSpan`,
`FractionalExponentSpan` - promoted to real, native PowerPoint equation objects instead (see
(3) below); (3) `app/bell_tasks/omml.py` builds those equation objects as raw OOXML (Office
Math Markup Language) inserted directly into a paragraph's XML via `lxml`, since
`python-pptx` has **no built-in support for equations at all**. A spike (build a minimal
equation fragment, save, open in real PowerPoint via COM automation, look at the result)
found the mechanism a slide actually needs: a bare `<m:oMath>` as a direct child of `<a:p>`
is silently dropped - unlike a Word document, a PowerPoint slide's DrawingML text needs the
Office-2010 math extension wrapper, `<mc:AlternateContent><mc:Choice Requires="a14"><a14:m>
<m:oMathPara><m:oMath>...</m:oMath></m:oMathPara></a14:m></mc:Choice><mc:Fallback>` (plain-
text run for older PowerPoint) `</mc:Fallback></mc:AlternateContent>`, coexisting inline
with ordinary `<a:r>` runs before/after it on the same line - confirmed working for both a
real stacked fraction (`<m:f>`) and a real superscript (`<m:sSup>`, including a fraction
nested inside one for a fractional exponent), each sized/coloured correctly via an `<a:rPr>`
nested inside each math run's own `<m:rPr>`. Given this real complexity, exponents are only
promoted to a true native superscript when the base is unambiguous - a bare digit run or a
single letter not itself preceded by another letter (`x^2`, `n^2`, `f^-1`, `10^-3`) - real
generator output also has exponents on a whole bracketed expression (`(x - 3)^2`), a multi-
letter identifier (`cos^-1`), or a run-together coefficient+variable (`at^2`, meaning
`a * t^2`, not `(at)^2`); correctly identifying the true base in those cases would need
balanced-parenthesis scanning or word-level disambiguation, judged a materially bigger
undertaking than asked for, so they deliberately keep the pre-existing plain "^n" inline-
text rendering instead of risking a wrongly-scoped superscript.

**Diagram sizing was reworked after a user report that embedded diagrams looked squeezed**:
the original `layout.diagram_rect` computed a (width, height) box from the cell alone and
handed both dimensions straight to `add_picture`, which does not preserve an image's own
aspect ratio when both dimensions are given explicitly - it stretches to fill whatever box
it's told, regardless of the diagram's real proportions, and different diagram kinds have
genuinely different native `Drawing` sizes (not always the same `DIAGRAM_WIDTH`/
`DIAGRAM_HEIGHT` defaults). Fixed by threading the diagram's own native width/height (in
points, straight from the rendered `Drawing`) through to `diagram_rect`, which now treats
the cell-derived box as a maximum bounding area only and scales the native size down (never
up, capped at 1.0×) to the largest size that fits inside it without distortion, centred
horizontally within the reserved zone - the diagram may end up noticeably smaller than the
old behaviour's box, but is never stretched, and stays crisp even at the smaller size since
rasterization DPI is unchanged.

**Several real bugs were found and fixed via this session's own end-to-end visual
verification, not by any unit test written in advance** - the same story as most gotchas in
this file: (1) the tokenizer's first version classified *any* bare `-` character as a
math/minus-sign token, including the hyphen inside compound words like "right-angled" or
"square-based" (real generator output), rendering half a word in Cambria Math - fixed with
a lookahead (`-(?![A-Za-z])`) so a hyphen immediately followed by a letter is left as plain
prose, while a genuine minus sign (followed by a digit or space) still counts as math; (2) a
long, data-listing prompt (e.g. `bar_chart_construct`, which spells out several
category:value pairs in the question text itself) wrapped to 4 lines and ran straight
into a diagram placed at a fixed height fraction with no regard for how much text sat
above it, visibly overlapping in a real rendered slide - fixed by estimating the prompt's
own wrapped-line count from its character length and the cell's width first
(`layout.estimate_text_line_count`), then shrinking the diagram's reserved height to
whatever's genuinely left (`layout.diagram_rect`, returns `None` - skip the diagram
entirely - when even a legible minimum wouldn't fit), plus a full extra line of headroom
since a rough width-based estimate can legitimately run a touch long; (3) some topic
*names* already end with their own tier disambiguator by this app's own naming convention
(e.g. `"Dividing Fractions (Foundation)"`, for a Foundation/Higher sibling pair) - the
frontend's dropdown label helper originally appended `"(Foundation)"`/`"(Higher)"`
unconditionally, doubling up to `"... (Foundation) (Foundation)"` for those specific
topics; fixed by checking whether the name already ends with that exact suffix first;
(4) the single most subtle bug this feature produced: every native equation object
(fraction or exponent) rendered as **completely blank** the first time real generator
content was checked in PowerPoint, even though the inserted XML was well-formed and had
already been proven correct in an isolated spike. Root cause - a real table cell, once
`TextFrame.clear()`'d (exactly what `_set_cell_content` does before rebuilding it), leaves
a trailing `<a:endParaRPr>` element behind, which the DrawingML schema requires to always
be the **last** child of a paragraph; the isolated OMML spike used a brand-new textbox with
no such element, so it never exposed the bug. `omml.py`'s equation-building code used a
plain `etree.SubElement(paragraph_xml, ...)` append, which has no schema awareness and
lands *after* `endParaRPr` - PowerPoint silently drops anything positioned there rather than
erroring, which is also why this had nothing to do with the XML's own validity and nothing
a schema-only check would have caught. Fixed with `_insert_before_end_para_rpr`, which finds
any trailing `endParaRPr` and inserts before it instead of blindly appending - `python-pptx`'s
own `add_run()` already gets this right internally, which is exactly why every plain-text
run continued to work throughout and only the hand-built equation XML was affected.

Verified end-to-end: full backend+frontend suites; a real generated `.pptx` opened via
`python-pptx` read-back (structural assertions - correct slide/cell/box↔topic mapping,
correct `font.name`/`font.size` per run, real `<m:f>`/`<m:sSup>` equation elements present
and correctly positioned relative to `endParaRPr`, every added picture's bounding box
contained within its own cell and its aspect ratio preserved) *and*, since this Windows
machine has no LibreOffice installed (the project's pptx-authoring skill's usual visual-QA
path doesn't work here - confirmed, its `soffice.py` wrapper throws on `socket.AF_UNIX`), a
genuine visual check via COM-automating the real Microsoft PowerPoint already installed on
this machine (`pywin32`, installed ad hoc for this one-off QA step only - deliberately
**not** added to `requirements.txt`, since it's a local verification tool, not something
the app itself depends on) to export real rendered slide images and look closely at them,
exactly like this project's established "render and look closely" discipline, just via a
different renderer than usual; plus a full live browser click-through (KS3 disabled, KS4
topic-picker with live search-as-you-type and cross-box exclusion confirmed directly via
the running app, Generate, a real `.pptx` downloaded with a 200 OK and no console errors).

Backend suite grew from 756 to 828 tests (across 5 files mirroring the `practice_tests/`
subpackage-test precedent - `test_diagram_raster.py`, `test_math_tokenizer.py`,
`test_layout.py`, `test_omml.py` (new), `test_generator.py` - plus 4 new route tests);
frontend grew from 46 to 61 (`BellTasksView.test.tsx` plus a new
`SearchableTopicSelect.test.tsx`).

**Modelled Example feature (on every topic, including new ones)**: a second button, "Generate
Modelled Example," sits next to "Generate Worksheet" on every topic card
(`TopicDefinition.generate_modelled_example` is set on every topic — the field
still exists as an `Optional` opt-in mechanically, but nothing is opted out).
Clicking it downloads a separate 2-page PDF via `POST /api/modelled-examples`:
page 1 is a single, richly-narrated worked example (`ModelledExample` in
`core/models.py`) — `worked_calculation` is a terse, boxed, numbers-only
calculation shown right under the prompt (so the student sees the numeric answer
path first), and `teaching_steps` is the prose underneath, meant to read like a
teacher talking through the *why* (not just the terse calculation-only
`Question.solution_steps` used everywhere else, and not just a relabelling of
it); page 2 is 5 practice questions generated the normal way (via
`build_worksheet(..., count=5)`, so they get the topic's real generator and
dedup logic) but rendered with **backward fading**
(`app/pdf/modelled_example_renderer.py`'s `_steps_shown_count`) — Q1 shows nearly
the whole worked solution with just the answer blanked, each later question shows
progressively less, and Q5 is fully independent (and deliberately does *not* show
a blank line per hidden step, so the blank-line count doesn't leak how many steps
the real solution has — see the `shown == 0` branch in `_practice_block`). No
answers are ever revealed on the practice page. Every topic has its own
`generate_modelled_example_xxx(tier, rng) -> ModelledExample` function living
alongside its normal `generate_xxx`, with genuinely new, more verbose explanatory
text — verified the same way as every other generator (independent second
computation path). Piloted first on 6 topics (one per section —
`fractions_add_subtract`, `linear_two_step`, `percentage_of_amount`,
`angles_triangle`, `probability_single_event`, `stats_mean_and_range`) to check
the format/pedagogy before committing to writing this content for all 129 topics
that existed at the time, then rolled out to the remaining 123 in one session
(see Chronology step 11) once that pilot was approved. Writing a
`generate_modelled_example_xxx` alongside the normal generator is now standard
practice for any new topic — the 13 topics added in the second curriculum audit
(step 13) all got one from the start, no separate "rollout" needed.

| Section | Groups | Topics |
|---|---|---|
| Number | Fractions, Decimals, Order of Operations (BIDMAS), Standard Form, Estimation & Bounds, Negative Numbers, Multiplying & Dividing by Powers of 10, Factors/Multiples & Primes, Powers/Roots & Indices | 57 |
| Algebra | Expressions/Formulae/Equations/Identities (incl. Collecting Like Terms), Solving Linear Equations, Forming and Solving Equations, Changing the Subject of a Formula, Substitution into Formulae, Expanding Brackets, Factorising, Algebraic Indices, Completing the Square, Turning Point of a Graph, Solving Quadratic Equations, Equation of a Circle, Functions, Algebraic Fractions, Simultaneous Equations, Inequalities, Algebraic Proof, Sequences, Iteration, Kinematics (SUVAT), Plotting Graphs, Equation of a Line, Real-Life Graphs, Transformations of Graphs, Coordinate Geometry | 84 |
| Ratio & Proportion | Percentages, Best Buys, Ratio, Proportion, Compound Measures | 37 |
| Geometry | Area & Perimeter, Parts of a Circle, Angles, Pythagoras' Theorem, Trigonometry, Sine Rule, Cosine Rule, Area of a Triangle, Vectors, Geometric Vectors, Circle Theorems, 3D Shapes, Congruence Proof, Symmetry, Transformations, Bearings, Map Scales and Scale Drawings, Constructions, Loci | 90 |
| Probability | Probability, Tree Diagrams, Sets and Counting, Tables and Diagrams, Venn Diagrams | 23 |
| Statistics | Averages from a List, Frequency Tables, Working Backwards, Charts and Graphs, Cumulative Frequency & Box Plots, Histograms, Sampling and Populations | 29 |

**First curriculum-audit dual-tier siblings**: Foundation-difficulty siblings for three
previously-Higher-only topics, flagged by an earlier audit and deliberately deferred
at the time, were later completed — `reverse_percentage_foundation` (friendlier
numbers), `angles_parallel_lines_foundation`/`angles_exterior_foundation` (pure-numeric,
no algebraic solve, unlike their Higher counterparts which embed a linear equation), and
`angles_polygon_interior_foundation` (numeric only; also covers exterior-angle and
interior-angle-sum sub-questions, needed for dedup-key variety since "regular polygon
with n sides" alone only has ~19 valid n — see `_REGULAR_POLYGON_SIDES`, divisors of
360). Also added `area_circle_foundation`, a Foundation sibling of `area_circle` that
gives a decimal (calculator-π) answer instead of exact form in terms of π.

**Second curriculum audit (13 new/retiered topics, 129→142)**: a from-scratch pass
over every topic against real AQA/Edexcel spec content (not just previously-flagged
candidates), evidence-checked by reading each generator's actual code before
building anything. High-confidence fixes: `area_subtract_compound_foundation` (new
— identical technique to the already-Foundation `area_composite_rectangles`);
`area_semicircle_compound` retiered Higher→Foundation (it already used
calculator/decimal π, the Foundation style) with a new `area_semicircle_compound_higher`
requiring exact π form; `pythagoras_ladder_context` was silently 50/50
triple-or-surd under one Higher-only label — split into
`pythagoras_ladder_context_foundation` (triple only) and tightened the Higher
version to always require a surd; `ratio_share_three_part_foundation` (new —
identical technique to `ratio_share_two_part`); `angles_straight_line_higher`/
`angles_around_point_higher`/`angles_triangle_higher` (new — the missing Higher
algebraic siblings that every *other* angle-fact topic already had). Medium-high
fixes (new Foundation siblings with friendlier numbers, same pattern as the first
audit): `compound_percentage_foundation`, `stats_reverse_mean_foundation`,
`stats_mean_grouped_frequency_table_foundation`, `set_notation_foundation` (same
Venn-diagram skill, phrased in plain English instead of formal ∪/∩/' notation —
the notation itself is the genuinely Higher-only part), `fractions_divide_foundation`,
`standard_form_multiply_divide_foundation`. This exposed two label-overlap
diagram bugs (see the two bullets below) and one grammar bug in generated teaching
text, all fixed. A handful of lower-confidence candidates were flagged but
*not* built — see "Ideas" below.

**Algebraic expressions and units on diagrams, not just bare `x`/numbers**:
`angles_parallel_lines` (Higher) had hardcoded its diagram's unknown-angle label to
literal `"x"` even when the real unknown was an algebraic expression like
`(3x + 50)°` — fixed to show the actual expression, matching how
`angles_exterior`/`angles_polygon_interior` already did this correctly. Separately,
`area_composite_rectangles`/`area_subtract_compound`'s L-shape diagram showed its
inner cut-out dimensions as bare numbers with a literal `x` for multiply (which
`mathtext.py` then italicised as if it were the algebra variable) while the outer
rectangle correctly showed units — now both show `"6 cm × 5 cm"` consistently.
`area_semicircle_compound` showed completely unlabelled bare numbers — now labelled
with units like every other area diagram. **When adding a diagram, always pass
pre-formatted label strings with units from the generator (matching the prompt's
units) — never bare numbers or bare unknowns — and check the draw function doesn't
silently drop them.**

**Label-anchor-direction diagram bugs (found via the fix above)**: giving
`angles_parallel_lines` a real algebraic label (much wider than `"x"`) exposed a
latent overlap bug in `draw_parallel_lines`: the "alternate" angle-pair layout
anchored the unknown label so long text grew back across the transversal line.
Fixed by choosing the label's text anchor (`"start"`/`"end"`) based on which side
of the vertex its offset sits, so text always grows away from the vertex. The same
fix pattern was needed again in `draw_triangle_angles` once `angles_triangle_higher`
gave it a wide label for the first time — there, centered-anchor labels at the two
bottom vertices collided with each other when both were wide, so instead the label's
*inset toward the centroid* (not its anchor) scales with `stringWidth` — wider
labels sit further from the vertex, giving more clearance from both sloped edges.
**When a diagram kind's labels have only ever been short (`"31°"`, `"x"`), adding a
wider one (algebraic expressions, longer units) can expose an untested overlap —
render and visually check, don't just trust the unit tests.**

**Frontend topic-card decluttering**: `TopicCard` takes a `showTierBadge` prop
(default `true`); `SectionView` passes `false` since its topic lists are already
tier-filtered (the Foundation/Higher pill was repeating the same word on every
card there) — `TopicSearch` still shows it, since its results span both tiers.
Action button labels shortened ("Generate Worksheet"/"Generate Modelled Example" →
"Worksheet"/"Modelled Example") and made `flex: 1` so they sit on one row instead
of stacking — every card grew a second button once the Modelled Example rollout
finished, and stacked full-width buttons made every card taller and near-identical.

**Per-topic question count**: `TopicDefinition.question_count` (default `None` = 20,
via `worksheet.builder.DEFAULT_COUNT`) lets a topic override the usual 20-question
worksheet — used by the 5 "Plotting Graphs" topics and `tree_diagram_drawing` (all
`question_count=5`, since a worksheet of 20 near-identical "plot this graph"/"draw
this tree" questions isn't useful). `routes.py`'s `create_worksheet` reads
`topic.question_count or DEFAULT_COUNT` when calling `build_worksheet`. This is
exposed to the user via each `TopicCard`'s collapsed-by-default "Options" panel (see
below) as the pre-filled default of a `count` override.

**User-facing worksheet options (question count + answers-only)**: every `TopicCard`
has an "Options ▾" toggle (collapsed by default, to keep the common one-click path
uncluttered — `TopicCard.test.tsx` covers it) that reveals a question-count number
input (bounded `worksheet.builder.MIN_COUNT`–`MAX_COUNT` = 5–40, pre-filled from the
topic's `default_question_count`, a new field on `TopicSummary`/`Topic` computed as
`t.question_count or DEFAULT_COUNT`) and an "Answers only" checkbox. Both are wired
through `GenerateWorksheetRequest.count` (`Optional[int]`, pydantic `ge=MIN_COUNT,
le=MAX_COUNT` — out-of-range returns 422) and `.answers_only` (`bool`) on
`POST /api/worksheets`; `count` is only sent when changed from the topic default,
so the common case's request body is unchanged from before. `render_worksheet` grew
an `answers_only: bool = False` param — when true it renders a compact "Answers"
page (`Q{n}. {final_answer}`, one line each) instead of the full "Worked Solutions"
page with steps/diagrams. The count `<input>` deliberately does **not** clamp on
every keystroke (an early version did, and it mangled typing a two-digit number —
e.g. typing "10" got clamped to "5" after the first digit, then the second digit
appended to *that* instead of continuing "10"); it now stores the raw typed string
and only clamps on blur and on Generate.

**Two-diagram questions**: `Question.solution_diagram` (alongside the original
`Question.diagram`) lets a question show a *different* diagram on the worked-solution
page than on the question page — `renderer.py`'s `_solution_block` renders it if
present. Used by every "plot this graph" topic (blank gridded axes on the question,
the same axes with the curve/line plotted on the solution) and `tree_diagram_drawing`
(no diagram at all on the question — the student draws it — full tree on the
solution).

**To-scale gridded graphs vs schematic diagrams**: `diagrams.py` now has two families.
The original family (`draw_parabola`, `draw_linear_graph_pair`, `draw_general_triangle`,
etc.) is deliberately schematic/"not to scale", for questions where the numbers are
given in the text. The new `_draw_scaled_axes` helper (used by `draw_function_graph`
and `draw_piecewise_graph`) draws real gridded, numbered axes and returns an
`(x, y) -> pixel` transform, for questions where the student must *read exact values
off the graph* (e.g. `line_equation_from_graph`) or *plot exact points onto it* (the
Plotting Graphs group) — get the scale wrong here and the maths becomes unreadable,
so these are never "not to scale". `draw_function_graph` takes `kind` ∈
`linear`/`quadratic`/`cubic`/`reciprocal` plus a `blank: bool` flag (blank axes only,
vs. axes + curve) so one renderer covers both the question and solution diagram of
every plotting topic. `draw_piecewise_graph` is the same idea for distance-time/
velocity-time graphs (a straight-line-segment polyline through explicit `points`,
axis-labelled e.g. "Time (minutes)"/"Distance (km)"). `GRAPH_WIDTH`/`GRAPH_HEIGHT` are
both 210 (square, not the old 230×175 rectangle) — user-reported visual feedback.

**Angle-label spacing**: after adding arcs (above), a follow-up user report found labels
overlapping rays/arcs, worst for algebraic labels like `(3x + 12)°` (wide text, centered
anchor pulls half the string back toward the vertex) and for narrow angles (a small
wedge has little lateral room even far from the vertex). Fixed per-diagram by pushing
label radius/inset further from the vertex than the arc radius (with headroom for the
widest realistic label string — check via `stringWidth` if adding a new one), and for
`draw_angle_line` specifically, placing labels for angles under 20° just beyond the ray
tips entirely rather than cramming them into the narrow wedge.

**Gridded graph axes always cross at the true origin**: `_draw_scaled_axes` clamps
its incoming `x_min`/`x_max`/`y_min`/`y_max` to always include 0 before computing
anything, so the axis lines are never drawn at a data-range edge instead of at (0, 0)
— this was a real bug (found via user report) affecting `plot_straight_line`,
`plot_quadratic`, and `line_equation_from_graph` whenever their y-range happened to
be entirely positive or entirely negative (e.g. y = x² + 4 over x = -3..3 never
touches y = 0).

**Angle arcs**: every diagram kind that labels an angle now draws a small arc between
the two rays forming it (standard exam-diagram convention), via `_angle_arc`/
`_vertex_angle_arc`/`_sector_arc_for_label` helpers (ReportLab `ArcPath`) in
`diagrams.py`. Side-length-only diagrams (`right_triangle`, `vector_triangle`) are
unaffected — right angles keep their square marker instead. New diagram kinds that
label an angle should add an arc too.

**Venn diagrams** (`draw_venn_diagram`, kind `"venn_diagram"`): a fixed two-circle
layout (`_VENN_CX_A`/`_VENN_CX_B`/`_VENN_CY`/`_VENN_R`) inside a bounding "universal
set" rectangle. The four atomic regions (`"a_only"`, `"b_only"`, `"both"`,
`"neither"`) are each their own closed, independently-fillable shape — `"a_only"`/
`"b_only"`/`"both"` (the lens) are built from actual circle-circle intersection
geometry via `ArcPath.addArc` (two arcs meeting at the two intersection points,
computed analytically since both circles share one radius — see `_venn_lens_path`/
`_venn_a_only_path`/`_venn_b_only_path`), while `"neither"` uses a simpler
fill-then-erase trick (fill the rectangle, then paint both circles over it in the
page background colour). Any named region from the real specs (A, B, A∩B, A∪B, "A
only", A′, (A∪B)′, etc.) is just the right combination of 1–4 of these atomic
regions shaded together with the same colour — see the mapping table in
`venn_diagrams.py`'s topics for exactly which combination each named region needs.
`params["region_text"]` independently supports showing a count/element-list/
algebraic-expression string in any region (used by the notation/probability/algebra
Venn topics), orthogonal to `params["shade"]` (used by the shading topic) — a
diagram can use either, both, or neither. Getting the lens-shape arc geometry right
on the very first real render (all four atomic regions plus several combinations)
was the highest-risk part of this diagram kind; see the chronology for how it was
verified.

**⚠️ Gotcha (found and fixed via this diagram kind, see chronology)**: `diagrams.py`'s
old `_text_runs`/`_math_runs` italicised **any** occurrence of the characters `x`/`n`
in a diagram label, with no word-boundary check at all (unlike `mathtext.py`'s
prose-text handling, which always had one) — so a label reading "Green" rendered as
"Gree" plus a stray italic "n". This had been silently shipping since diagram labels
were originally assumed to always be short numeric/algebraic strings, never English
words — an assumption the tree-diagram topics (branch labels like "Red"/"Green"/
"Yellow") had already quietly broken. Fixed by giving `diagrams.py` the same
word-boundary regex `(?<![A-Za-z])[xn](?![A-Za-z])` that `mathtext.py` already used.
If you ever add a diagram label containing a real word with an `x` or `n` in it,
this is already handled — no special-casing needed.

**Statistics chart diagrams** (`draw_bar_chart`, `draw_pie_chart`, `draw_box_plot`,
`draw_histogram`, `draw_cumulative_frequency`, `draw_time_series`): six new diagram
kinds built for the Statistics Phase 2 session, all sharing a single new
`_draw_stats_axes` helper — deliberately a *separate* function from the existing
`_draw_scaled_axes` (used only by algebra function/piecewise graphs), because
`_draw_scaled_axes` draws a fine gridline at every integer unit regardless of range,
which is fine for small algebra ranges (-10 to 10) but would draw hundreds of
gridlines (or hang) for a statistics chart with a y-axis running into the tens or
hundreds. `_draw_stats_axes` spaces gridlines/ticks via `_nice_tick_step` instead
(same helper the algebra axes use for *numbered* ticks, just not for gridline
density), and supports `x_ticks`/`y_ticks` as explicit position lists (`[]` to
suppress an axis's ticks entirely, `None` for computed "nice" spacing) plus
`show_y_axis=False` to omit the y-axis altogether for a chart with no meaningful
y-scale (`draw_box_plot`, which is 1D). `draw_bar_chart` takes either a flat
`series` (plain bars) or `list[list[number]]` (a stacked "composite" bar chart, with
`series_labels` for the legend) — one function serves both, controlled by params,
not two separate diagram kinds. `draw_pie_chart` uses `Wedge` (imported since the
original diagram set but never actually used for a filled pie slice until now) with
cumulative start/end angles computed from each category's proportion of the total.
`draw_time_series`/`draw_cumulative_frequency` both plot a `points` list via
`PolyLine` — deliberately two thin separate functions rather than one shared one,
since they differ in defaults (axis labels, whether x-ticks are auto-spaced vs. at
exact class boundaries) even though the underlying mechanism is nearly identical.
**Gotcha found and fixed while building these**: the first `draw_box_plot`
implementation put row labels (`"Class A"`/`"Class B"`, for the two-box-plot
comparison view) too close to the axis start, so a long label overlapped the
leftmost whisker — fixed by reserving a dedicated label-column width on the left
(shifting the whole plot area right) whenever any box has a `"label"`, rather than
just nudging the label's x-position, which would only have worked for short labels.

**Number line diagrams** (`draw_number_line`, kind `"number_line"`): a ticked
horizontal axis (reusing the existing `_draw_stats_axes` helper with `x_ticks`
covering every integer in `params["range"]` and `show_y_axis=False`) plus an open
(`PAPER`-filled) or closed (`ACCENT`-filled) circle at each of 1–2 boundary values,
and a thick coloured line marking the solution region — a ray with an arrowhead for
a single-boundary inequality (`params["shade"] = "left"/"right"`), or for two
boundaries either the segment between them (`"between"`) or two outward rays
(`"outside"`, for an "either/or" compound inequality). `params["blank"]` draws the
bare ticked line only (boundaries omitted), for the question-page half of a
"draw it yourself" question — the same `diagram`/`solution_diagram` split used by
the Plotting Graphs topics. Used by `inequalities_number_line_foundation`/`_higher`.
**Gotcha found and fixed while building this**: the very first version of the
Higher (compound) generator displayed the lower bound's symbol un-flipped — e.g.
"Draw the solution set of 3 > x < 6" instead of "3 < x < 6" — because the internal
`lo_op` variable (meaning "x >= lo_val") was reused directly as the displayed
symbol between `lo_val` and `x` instead of being flipped first; caught by rendering
an actual worksheet PDF and reading the prompts, not by the unit tests (which only
checked the underlying region logic, not the displayed string) — fixed, and a new
`_check_between_display` independent check was added specifically to verify the
*displayed* string's meaning against the region, not just the region logic itself.

**Fractional exponents in `mathtext.py`** (e.g. `x^(1/4)`, written by
`algebraic_indices.py`'s Higher topic): typeset as a single flat raised
`<super>(1/4)</super>` rather than a nested raised-numerator/lowered-denominator
fraction inside a superscript — nesting `<super>` inside `<super>` was tried first
and rendered with the numerator and denominator overlapping each other (verified by
rendering both side by side in an isolated script before picking one). All three
numeric patterns `mathtext.py` recognises (fractional exponent, plain integer
exponent, standalone fraction) are now matched by *one* combined regex in a single
pass rather than three sequential passes — a fractional exponent's raised "(1/4)"
is otherwise a bare digit-slash-digit substring indistinguishable from a standalone
fraction, and a later, separate fraction-matching pass would re-match and mangle it
into a broken doubly-nested result. **Gotcha found while fixing this**: the unicode
division slash U+2215 ("∕") was tried as a way to dodge that re-matching risk and
turned out to have no Helvetica glyph either (same class of issue as the `⁻¹`
gotcha below) — stick to a plain ASCII "/" for any future math-text character, and
verify any new non-ASCII character actually renders (not just that it's "a valid
unicode math symbol") before relying on it.

**Fraction-shape and dice/spinner/bag diagrams** (`draw_fraction_shapes`, kind
`"fraction_shapes"`; `draw_dice`, kind `"dice"`; `draw_spinner`, kind `"spinner"`;
`draw_bag`, kind `"bag_of_counters"`): built in chronology step 21.
`draw_fraction_shapes` takes `params["shapes"]`, a list of 1–4
`{"kind": "bar"|"circle", "parts", "shaded", "label"}` dicts laid out left to right —
a bar is a `Rect` split into `parts` equal vertical segments (leftmost `shaded`
filled), a circle is `parts` equal `Wedge`s (same cumulative-angle construction as
`draw_pie_chart`), and each shape's `label` goes through the existing `_label()`
helper so a bare `"n/d"` string automatically gets the vinculum treatment built (but
previously unused by any real topic) in step 16. Used by
`fractions_equivalent_diagram`. `draw_dice` takes `params["values"]` (1–2 die faces,
standard pip layout) and optional `params["highlight"]` (indices getting an
`ACCENT`-coloured border). `draw_spinner` takes `params["sectors"]` (equal wedge
labels) and optional `params["highlight"]` (sector indices filled `HIGHLIGHT`, the
rest left neutral `PAPER` — deliberately not a full rainbow palette, matching this
app's existing "shade only the interesting bit" convention) plus a small centre
pointer. `draw_bag` takes `params["counts"]` (colour name → count) and draws a
rounded-rect body with a tied neck, small counters packed in rows grouped by colour,
using a direct colour-name-to-hex map (`_COUNTER_COLOURS`) rather than the abstract
`CHART_COLORS` palette, since the prompt text names the literal colour. These three
are retrofitted onto 9 existing Probability topics (see chronology step 21 for the
exact list and which branches were deliberately left text-only rather than inventing
unstated values) — illustrative only, never determine the answer, so no new
verification logic was needed anywhere they were added.

Every Geometry topic and a handful of Algebra topics (parabola for turning point,
line-pair for simultaneous-graphically) render an actual ReportLab-drawn figure
matching that question's real generated values — see `backend/app/pdf/diagrams.py`.

Nothing is a stub/placeholder — every topic has real generation logic, a real
independent verification check, and a real test file with ~200–400-trial seeded runs.

**Frontend**: each section has a Foundation/Higher tier-picker sub-menu before showing
its topic groups — see `SectionView.tsx`. Topics with `fixed_tier=None` (currently
unused) would show under both.

**Typesetting**: `backend/app/pdf/mathtext.py` centrally converts plain-ASCII math in
generator output (`x`, `n`, `x^2`, `10^-3`, `3/4`) into real PDF typesetting — the
variables `x` and `n` are italicised, `^n` becomes a real superscript, and a standalone
fraction is rendered as a **true stacked vinculum** (numerator over a horizontal rule
over denominator, e.g. `3/4` → a small inline image, matching the diagram-label
treatment below) — applied once at render time in `renderer.py`,
`modelled_example_renderer.py`, and `practice_test_renderer.py` (all three share the
same `to_markup`), so any topic that follows the ASCII convention gets this for free.
Only `x`/`n` are italicised, not `a`/`b` or other letters — see the "Italicising more
variables" bullet below for why a blanket rule can't safely cover every single letter
(e.g. `a` collides constantly with the English indefinite article).

**A true vinculum in prose text (chronology step 28)** — originally deferred (step 16)
as "too fragile for the payoff" because ReportLab's inline `<img>` tag needs a real
image *file*, and ReportLab's own vector-to-image rasteriser (`renderPM`) isn't
installed here (needs Cairo bindings) — was revisited and built once the user asked
again, using the workaround already scoped out at the time: `app/pdf/fraction_images.py`
draws the numerator/rule/denominator directly with **PIL** (already an installed
dependency of reportlab/pymupdf, now pinned explicitly in `requirements.txt`) onto a
transparent-background PNG, using the same Windows TrueType fonts
(`C:\Windows\Fonts\arial.ttf`/`arialbd.ttf`) ReportLab itself would fall back to, at
4x supersampling for crisp print quality. Results are cached in memory (keyed by
every visual parameter: numerator, denominator, font size, bold, colour) and written
once per unique fraction to a per-process temp directory (cleaned up via `atexit`),
since the same fraction (e.g. `1/2`) recurs constantly across a 20-question worksheet.
`to_markup` therefore needs the caller's font size/colour/bold-ness to size and colour
the image correctly — its signature grew `font_size`/`color`/`bold` keyword params,
and every `_fmt(text)` call site across the 3 renderer files became `_fmt(text, style)`,
deriving those three from the actual `ParagraphStyle` being used (so a fraction in a
bold green answer line renders bold and green, not always plain black). The `<img>`
tag's `valign="bottom"` attribute was confirmed — by rendering real text at several
valign values side by side and comparing pixel-for-pixel — to align the fraction's own
visual baseline (the bottom of the denominator digits) with the surrounding text's
baseline with no extra offset maths needed. A negative fraction's sign (`-3/4`) stays
a plain baseline character in front of the image — only the num/den/rule are drawn as
one unit. The old `<sub>`+comma ReportLab spacing quirk (documented below) no longer
applies to fractions at all now that they're images, so its workaround code was
removed as dead.

**Real bug found and fixed while building this** (via an actual end-to-end worksheet
render, not a unit test — same story as most gotchas in this file): the very first
version ran the `x`/`n`-italicising regex pass *after* the fraction-substitution pass.
Since a fraction is now replaced with an `<img src="{temp file path}">` tag, and
`tempfile.mkdtemp`'s random suffix can itself contain a bare "x" or "n" flanked by
non-letters (e.g. `...gcse_fractions_k_x7ili6\frac_0.png`), the later italics pass
re-scanned and corrupted part of the just-inserted file path, breaking image loading
entirely for any worksheet unlucky enough to hit a matching random suffix — synthetic
spike text never happened to trigger it, only a real render across many questions did.
Fixed by reordering `to_markup` to italicise first, then substitute fractions/exponents
last, so the inserted markup (including file paths) is never re-scanned by anything
else — with a deterministic regression test (monkeypatching the image path to force
the exact scenario) added alongside the probabilistic real-world discovery.

Diagram labels keep their own, separate true-vinculum implementation
(`diagrams.py`'s `_label()`/`_math_runs()`/`_draw_fraction()`) rather than sharing
`fraction_images.py` — diagrams are already drawn as vector shapes (`String`/`Line`
in a `Group`) inside a `Drawing`, not Paragraph markup, so they never had the
inline-image constraint prose text does, and don't need PNGs at all.

**Bearings, Constructions, and Loci** (Geometry Phase 4b, chronology step 27
— the final piece of the large user-supplied Geometry expansion): three new
groups. `draw_bearings` (kind `"bearings"`) is a schematic (not-to-scale)
diagram for `bearings_cosine_rule` — two legs of a journey with a north
arrow + full clockwise-from-north `_bearing_arc` at *both* turn points (not
just the start), built on a new `_north_arrow` helper. `draw_loci_construction`
(kind `"loci_construction"`) and `draw_loci_region` (kind `"loci_region"`)
share the existing `_draw_scaled_axes` grid engine and a new `_scaled_circle`
helper — a circle of true radius r on that grid always uses `Ellipse` with
separately-computed x/y pixel radii, never plain `Circle`, since the grid's
pixel scaling is never exactly uniform even on a square data window (verified
directly: a circle on a deliberately wide non-square window still rendered
as a true circle, not an ellipse). `draw_loci_region`'s shaded region is a
rasterized dot mesh (sample a fine grid, evaluate every constraint at each
point, paint a small translucent `fillOpacity` dot wherever all hold) rather
than hand-built boolean region geometry (the `draw_venn_diagram` technique) —
confirmed fast enough (hundreds of dots, milliseconds) and legible at normal
diagram size. Both loci diagram kinds follow the established blank-question/
completed-solution `diagram`/`solution_diagram` split (`draw_loci_construction`'s
`circle`/`segment` params and `draw_loci_region`'s `shade_constraints` param
are the "answer", omitted on the question page; `draw_loci_construction`'s
`given_lines` and `draw_loci_region`'s `boundaries` are given information, so
they're drawn on *both* pages, matching how `draw_grid_transformation` always
shows its mirror line/centre/vector regardless of whether the image is
present). The 3 Constructions topics (`construction_angle_bisector`/
`construction_perpendicular_bisector`/`construction_triangle`) have no
diagram at all and, uniquely in this codebase, **no `verify()`** — they are
"describe the method" text questions with randomised numbers/labels in fixed
per-scenario method text, author-review only (there is no way to numerically
check a described construction).

**Compound-3D surface area, spinner diagrams, and bold vector labels**
(chronology step 29 — three "Ideas" items the user picked directly).
`compound_3d_surface_area` (Higher, `solids_curved_compound.py`) is the
surface-area sibling of `compound_3d_volume`, reusing the exact same 3
variants/param ranges and the exact same `draw_compound_3d` diagram
unchanged, but excluding each shape-pair's internal shared/join face from
the formula — the exact problem the volume topic's own original design
deliberately avoided. Unlike the volume topic (where the cuboid_pyramid
variant is exact, no π/no irrationality), this topic's cuboid_pyramid slant
height is routinely irrational, so **all three variants** give a rounded
3-s.f. decimal answer here (matching the sibling standalone pyramid topic's
own surface-area branch, which accepts the same trade-off for the same
reason) — a genuine, deliberate asymmetry from its volume sibling, not an
oversight.

`draw_spinner` was refactored to extract its wedge/label/pointer body into a
shared `_draw_spinner_at` helper (pure extraction, output unchanged), enabling
a new `draw_spinner_pair` (kind `"spinner_pair"`, two independent spinners
side by side on one wider canvas, no highlight support since two-spinner
scenarios never mark a target outcome) — this fixes the last diagram gap
flagged in step 21: `probability_listing_outcomes`'s `two_spinner3`/
`spinner3_spinner4` scenarios. Separately, `probability_expectation`'s
`"spinner"` context (previously text-only — no side-count to draw from) now
reuses its already-generated `numerator`/`denominator` directly as the
spinner's own sector count/highlight, so the diagram is *exactly* consistent
with the stated probability, capped at `denominator <= 12` (the two larger
denominators in `_EXPECTATION_DENOMINATORS`, 20 and 25, stay text-only to
avoid a visually degenerate wafer-thin-wedge spinner — verified at the n=12
boundary case specifically). `relative_frequency`'s `"spinner"` item gets a
simple fixed illustrative spinner (matching how its existing "biased dice"
diagram is *also* purely illustrative, always showing face 6 regardless of
the real frequency numbers — diagrams here never determine the answer).

Vector labels `a`/`b` are now **bold**, not unstyled, matching real exam
convention (deferred since chronology step 16 pending exactly this design).
Rather than a blanket regex (impossible here — bare "a" collides constantly
with the English indefinite article, e.g. "OAB **is a** triangle with OA =
**a**"), generators mark each genuine vector mention explicitly at the
source with a new ASCII sentinel, `\vec{a}`/`\vec{b}` (module constants
`_VEC_A`/`_VEC_B` in `vectors.py`) — a plain-text convention in the same
spirit as this app's existing `^n`/`num/den`, not hand-written PDF markup
(no topic in this codebase does that). `mathtext.py` gained `_VECTOR_RE`,
substituted in the same early pass as the x/n italics regex (before
fraction/exponent substitution, for the same file-path-corruption-avoidance
reason already documented there); `diagrams.py` gained a parallel
`_LABEL_FONT_BOLD` and folded the vector pattern into one combined
`_TEXT_RUN_RE` alongside its own x/n regex, so `vector_triangle` diagram
labels (`draw_vector_triangle`'s `a_label`/`b_label`) get the same bold
treatment via its separate, non-mathtext styling pipeline. Every genuine
`a`/`b` occurrence across both `vectors.py` functions (arithmetic and
geometric, including their modelled-example twins) was individually audited
against "genuine vector vs. English article" — confirmed via full end-to-end
PDF rendering that "is a triangle" stays plain while every genuine mention,
including ones sitting in the very same sentence, renders bold, and that
bold vectors compose correctly alongside fraction-vinculum images (e.g.
"Answer: -(1/5)**a** + (1/5)**b**") with no interference between the two
systems.

Backend suite grew from 668 to 682 tests (274→275 topics — only
`compound_3d_surface_area` is a new topic; the other two pieces changed
existing topics/shared rendering code). Frontend unaffected (45/45).

**⚠️ Gotchas (bit us, see below)**:
- Never use the literal Unicode superscript-minus character `⁻` (e.g. in `f⁻¹`,
  `cos⁻¹`) — Helvetica has no glyph for it in ReportLab and it renders as a
  missing-glyph box. Always write `f^-1(x)`, `cos^-1(...)` etc. and let `mathtext.py`
  superscript it properly. (`²`, `√`, `π`, `≤`, `°`, `×`, `÷`, `£` are all fine as
  literal Unicode — only `⁻` specifically is the problem.)
- The Unicode Latin-subscript-letter block (`ₙ` U+2099, `ₓ` U+2093, subscript
  digits/`+`/`-`) is NOT a usable shortcut for hand-rolled subscripts either —
  Arial has no glyphs for most of them either (confirmed via a `font.getmask` spike:
  they fall back to the exact same `.notdef` bbox as a deliberately-invalid
  codepoint). Use a real `<sub>` tag (see mathtext.py's `_SUBSCRIPT_RE`, chronology
  step 37) or manual multi-run drawing (see `fraction_images.py`'s `_draw_run`, for
  content that must be drawn as raw PIL text instead of Paragraph markup) — never a
  Unicode subscript character.
- ReportLab renders a comma **glued and raised** to the preceding digit when it
  immediately follows a closing `</sub>` with no space in between (verified in
  isolation with a throwaway script — periods, colons, semicolons, question marks and
  closing parens in the same position are all fine, and so is a comma after
  `</super>`; only sub+comma with zero gap breaks). This first surfaced in chronology
  step 16 (the old `<super>`/`<sub>` fraction approximation) and was worked around
  with a non-breaking space; once fractions became `<img>` tags instead (step 28),
  `<sub>` was removed from the codebase entirely and the workaround became dead code.
  Step 37 reintroduced `<sub>` for real (`x_n`/`x_(n+1)` subscript notation, see
  mathtext.py's `_SUBSCRIPT_RE`) and hit this again — confirmed still present via a
  real rendered-PDF spike. **Fixed with a thin space (U+2009), not a non-breaking
  space or zero-width space** — a zero-width space was tried first and rejected
  (Helvetica has no glyph for it, same class of issue as the `⁻¹` gotcha below,
  confirmed via a `font.getmask` spike showing it falls back to the exact same
  `.notdef` bbox as a deliberately-invalid codepoint); a non-breaking space fixes the
  glue but leaves a visibly larger gap than real typesetting would use. `mathtext.py`'s
  `_SUB_COMMA_RE` inserts the thin space wherever `</sub>` is immediately followed by
  a comma — if you ever hand-write more `<sub>...</sub>` markup directly elsewhere,
  watch for this again.

## How this was built (chronology, for context)

1. Initial build: FastAPI backend + React frontend, 8 flat topics, PDF renderer, full test suite.
2. Restructured into the current 6-section/group/topic hierarchy (each old topic's
   internal random "shape" promoted to its own standalone, tier-exclusive subtopic).
   Added a new frontend nav: `HomeScreen` → `SectionView` → `TopicCard`, plus global search.
3. Added 13 new Number topics (Fractions/Decimals/Standard Form) and the Geometry
   diagram-rendering engine. (56 topics)
4. Added a Foundation/Higher tier-picker sub-menu inside each section (frontend only).
   Investigated a "Geometry diagrams don't render" report — turned out to already be
   working correctly end-to-end; no fix needed.
5. Added Number's Estimation & Bounds group (3 topics) and built `mathtext.py` to
   centrally italicise `x` and superscript `^n` everywhere (worksheet text + diagram
   labels), replacing ad hoc per-generator text. (59 topics)
6. Added 7 new Geometry groups — Trigonometry, Sine Rule, Cosine Rule, Area of a
   Triangle, Vectors, Geometric Vectors, Circle Theorems (12 topics) — plus 6 new
   diagram kinds. Did a curriculum audit of Foundation/Higher tier placement across
   *all* existing topics: retagged `pythagoras_shorter_leg` to Foundation (it only
   ever produced clean triples, so Higher was wrong), and added Foundation-difficulty
   siblings for `linear_both_sides`, `linear_brackets`, `expand_double_brackets`, and
   `factorise_quadratics` (positive-coefficient-only versions), since those are
   genuine Foundation+Higher overlap content on the real specs. (75 topics)
7. Added 14 new Algebra topics — Functions, Completing the Square, Turning Point of a
   Graph, Expanding Triple Brackets, Simultaneous Equations (5 sub-topics), Sequences
   (4 sub-topics) — plus 2 new diagram kinds (parabola, line pair). Found and fixed the
   `⁻` glyph bug (see Gotcha above) during visual verification; it also affected two
   topics from step 6 (cosine rule, trig missing angle). (89 topics)
8. Added an Algebra "Graphs" cluster (11 topics: 5 plotting topics — straight line,
   quadratic, cubic, reciprocal, distance-time, each fixed at 5 questions per
   worksheet with blank gridded axes always provided on the question page — plus
   equation-of-a-line-from-a-graph, parallel lines, perpendicular lines, interpreting
   distance-time graphs, interpreting velocity-time graphs, and transformations of
   graphs) and a Probability cluster (8 topics: tree diagrams — independent,
   dependent, and a 5-question "drawing" variant — plus set notation, product rule
   for counting, relative frequency, two-way tables, and sample space diagrams).
   Introduced `TopicDefinition.question_count` (per-topic worksheet-size override,
   for the 5-question topics) and `Question.solution_diagram` (a second diagram
   shown only on the worked-solution page, for "plot the graph"/"draw the tree"
   questions where the question page must show blank axes / no diagram and the
   *solution* shows the completed figure). Built a new to-scale gridded-axes
   diagram engine (`_draw_scaled_axes`, `draw_function_graph`, `draw_piecewise_graph`)
   alongside the existing schematic one, plus `draw_graph_transformation`,
   `draw_tree_diagram`, `draw_two_way_table`, and `draw_sample_space_diagram`.
   (108 topics)
9. Added 16 new Number topics — dividing decimals, multiplying/dividing by powers of
   10, negative number arithmetic, prime numbers, multiples, factors, prime factor
   decomposition (Foundation product form + Higher index form), LCM/HCF by listing,
   HCF & LCM via prime factorisation, fractions of an amount, powers & laws of
   indices (Foundation positive-integer + Higher negative/zero/fractional), and
   square/cube roots plus simplifying surds — across 4 new Number groups. Also
   completed the 3 previously-flagged-but-deferred curriculum-audit dual-tier
   siblings from step 6 (see "Ideas" below, now resolved):
   `reverse_percentage_foundation`, three Foundation `angles.py` siblings
   (`parallel_lines`/`exterior`/`polygon_interior`, pure-numeric, no algebraic
   solve), and `area_circle_foundation` (decimal/calculator-π answer). (129 topics)
10. Visual-feedback fixes from user testing, plus a new "Modelled Example" pilot
    feature (topic count unchanged at 129 — no new practice topics this step).
    Added angle arcs (`_angle_arc`/`_vertex_angle_arc`/`_sector_arc_for_label`
    in `diagrams.py`) to every angle-labelling diagram kind, then a follow-up
    fix once arcs revealed label/line overlap (worst for wide algebraic labels
    like `(3x + 12)°` and for narrow angles) by pushing label radius/inset
    further from the vertex than the arc, with an extra rule in
    `draw_angle_line` to place labels for angles under 20° just beyond the ray
    tips. Made `GRAPH_WIDTH`/`GRAPH_HEIGHT` square (210×210, was 230×175).
    Fixed a real bug where `_draw_scaled_axes` could draw the x/y axis at a
    data-range edge instead of at the true origin whenever a curve's values
    sat entirely on one side of an axis (now clamps the visible range to
    always include 0). Then built the Modelled Example pilot described above
    in "Current state" — new `ModelledExample` model,
    `TopicDefinition.generate_modelled_example` opt-in field,
    `app/pdf/modelled_example_renderer.py`, `POST /api/modelled-examples`,
    and a second frontend button — piloted on 6 topics, one per section.
11. Two follow-up requests on the Modelled Example pilot, in the same session.
    First, a layout fix: added `ModelledExample.worked_calculation` (terse
    numeric-only lines) and reordered the page so the boxed calculation now sits
    directly under the prompt, with the prose `teaching_steps` ("How it works")
    following underneath — previously the prose came first with no separate
    numeric summary. Retrofitted `worked_calculation` onto all 6 pilot topics'
    existing `generate_modelled_example_xxx` functions. Second, per the user's
    go-ahead, rolled the feature out to the other 123 topics: every topic across
    all 6 sections now has a `generate_modelled_example_xxx` function (verified
    independently, same conventions as every other generator) wired onto its
    `TopicDefinition`, done section-by-section (mostly via parallel subagents,
    one per topic-module cluster) with a full-suite check and a commit+push after
    each section. Finished by replacing the old "pilot scope" gate tests
    (`test_modelled_example_renderer.py`'s `PILOT_TOPIC_IDS`-based tests,
    `test_routes.py`'s 404-for-topic-without-one test) with full-coverage
    equivalents — the 404 branch is still tested, now via a monkeypatched
    stand-in topic rather than a real topic lacking a modelled example, since
    none do anymore. Backend suite grew from 177 to 244 tests, all passing;
    frontend unaffected (its "Generate Modelled Example" button was already
    driven by a per-topic API flag, so no frontend changes were needed).
12. New session, three user-reported/requested fixes. First, `angles_parallel_lines`
    (Higher) was showing its diagram's unknown angle as bare `"x"` instead of the
    real algebraic expression from the question — fixed, which exposed a label-
    overlap bug in `draw_parallel_lines` (fixed via anchor-direction-by-offset-sign).
    Second, units weren't reaching some diagrams even though the prompt had them
    (L-shape inner cut-out dimensions, semicircle-compound width/height) — fixed by
    always passing pre-formatted unit strings from the generator. Third, a frontend
    declutter pass: removed the redundant tier badge from tier-filtered topic lists
    (`TopicCard`'s new `showTierBadge` prop) and put the two action buttons on one
    row with shorter labels, since every card had grown a second button since the
    Modelled Example rollout and looked increasingly stacked/repetitive.
13. Same session, a second curriculum audit (the first, from step 6/9, was
    explicitly narrow — only the already-flagged candidates). This one started
    from scratch: read every topic's actual generator code and checked it against
    real AQA/Edexcel spec content, rather than assuming the existing Foundation/
    Higher split was already correct. Found 11 genuine gaps (listed in "Current
    state" above), resolved as 13 new topic definitions plus a retier and a
    tightening of two existing ones (129→142 total). Building `angles_triangle_higher`
    exposed a second label-overlap bug, this time in `draw_triangle_angles` (fixed
    via width-scaled centroid inset rather than anchor direction, since two wide
    bottom-vertex labels growing away from their vertices collided with each other
    in the middle). Backend suite grew from 244 to 253 tests; frontend unaffected
    except +1 test from step 12's `showTierBadge` prop (now 26/26).
14. New session, a user-requested expansion of Ratio & Proportion (not a curriculum
    audit — the user supplied the topic list directly, with clarifying questions
    asked up front on grouping/scope). Split the section's content into two new
    groups alongside the existing Percentages/Ratio — **Proportion**
    (`app/topics/proportion.py`, new file) and **Compound Measures**
    (`app/topics/compound_measures.py`, new file) — since direct/inverse proportion
    and speed/density/pressure don't fit under "Ratio" on the real specs; groups
    need no registration beyond the string set on `TopicDefinition.group`, so this
    was a clean addition. Three already-requested items turned out to already exist
    (sharing a ratio, ratio given one amount, combining ratios) and were skipped.
    Built via 3 parallel subagents, one per cluster, each required to independently
    verify every generator, write its own test file, and self-check dedup-key
    space — then registry wiring, the full-suite run, and visual PDF/browser
    verification was done centrally afterward to avoid merge conflicts across the
    agents. Added 18 new topics (129→142 was step 13; this step is 142→160):
    `ratio_1_to_n`, `ratio_difference`(`_higher`), `ratio_to_equation`,
    `ratio_shape_similar_foundation`/`_higher` (Ratio); `direct_proportion`,
    `inverse_proportion`, `algebraic_direct_proportion`,
    `algebraic_inverse_proportion` (Proportion); `sdt_mixed`,
    `speed_with_conversions`, `unit_conversions`(`_higher`), `density`(`_higher`),
    `pressure`(`_higher`) (Compound Measures). No new diagram kinds — kept
    deliberately text-only to control scope for a batch this size. Backend suite
    grew from 253 to 282 tests (the 4 hardcoded `142`-topic-count assertions in
    `test_routes.py`/`test_modelled_example_renderer.py`/`test_worksheet_builder.py`
    were updated to `160`); frontend unaffected (26/26 — new groups render
    generically, no frontend code changes needed).
15. Same session, two of the "Ideas for a future session" items from the list below
    were promoted to real features on user request (after a clarifying question to
    confirm which two of several candidate ideas were meant): user-facing adjustable
    question count and answer-only PDF mode — see "User-facing worksheet options"
    above for the full design. `GenerateWorksheetRequest` gained `count`
    (bounds-checked, 422 on out-of-range) and `answers_only`; `render_worksheet`
    gained an `answers_only` branch; `TopicSummary`/`Topic` gained
    `default_question_count`; `TopicCard` gained a collapsed-by-default "Options"
    panel. Caught and fixed a real bug during browser verification: clamping the
    question-count input on every keystroke corrupted multi-digit typing, fixed by
    only clamping on blur/submit. Backend suite grew from 282 to 287 tests; frontend
    from 26 to 29.
16. Same session, two more "Ideas" items promoted on user request (with clarifying
    questions asked up front, since both had real design decisions hiding in them).
    First, italics beyond `x`: extended `mathtext.py`/`diagrams.py` to also italicise
    `n` (safe everywhere it actually appears — `sequences.py`'s nth-term topics,
    `angles.py`'s polygon-interior topics, `ratio_1_to_n` — verified by grepping every
    real literal-`n` occurrence in generator output, not just trusting the regex).
    Vectors' `a`/`b` were explicitly deferred to a separate future session, per the
    user's choice, since (a) real exam convention prints vectors in **bold**, not
    italic, and (b) a blanket regex can't safely italicise/bold `a`/`b` without
    editing every vector prompt string to mark genuine vector mentions apart from the
    English article "a" (e.g. "OAB is a triangle with OA = a" uses "a" both ways in
    one sentence). Second, fractions: the user asked for a true vinculum (horizontal
    bar) everywhere, removing the plain slash. Built the real thing in
    `diagrams.py` (`_draw_fraction`, vector shapes — cheap and safe, though currently
    unexercised by any real topic). For prose text, discovered mid-implementation that
    a true inline vinculum needs PNGs rendered to temp files with a hardcoded Windows
    font path (ReportLab's own rasteriser isn't installed here) — flagged this new
    finding back to the user rather than silently building it, and by their choice
    shipped the lighter `<super>`/`<sub>` approximation in `mathtext.py` instead. That
    surfaced a genuine, narrow ReportLab rendering bug (comma glued/raised immediately
    after a closing `</sub>` with zero gap, nothing else affected) caught by rendering
    an actual PDF and looking closely, not by the unit tests — isolated with a
    throwaway script, then fixed with a non-breaking-space insertion (see the Gotchas
    above). Backend suite grew from 287 to 304 tests; frontend unaffected (no
    frontend-visible change, this was all backend PDF rendering).
17. New session, Phase 1 of a large user-supplied Probability + Statistics topic
    list (explicitly split into two phases after clarifying questions, since the
    full list needed ~7 brand-new chart-drawing diagram engines and was judged too
    big for one pass — Statistics is Phase 2, not yet started). This phase covered
    all of Probability (160→169 topics): `probability_listing_outcomes`,
    `probability_and_or_rule`, `probability_expectation` (existing "Probability"
    group); `tree_diagram_algebraic`, `tree_diagram_mixed` (existing "Tree Diagrams"
    group — `_mixed` reuses the `trig_mixed` 50/50-dispatcher-over-two-existing-
    generators pattern via `dataclasses.replace`); and 4 new topics in a brand-new
    "Venn Diagrams" group (`venn_diagrams.py`, new file): `venn_diagram_shading`,
    `venn_diagram_probability`, `venn_diagram_notation`, `venn_diagram_algebra`.
    Built via 3 parallel subagents (one per cluster above) plus a new
    `draw_venn_diagram` diagram kind (see "Venn diagrams" above) built and visually
    verified directly rather than delegated, since it was the highest-risk new
    geometry this project has attempted — the circle-circle intersection arc math
    for the crescent/lens regions worked correctly on the first real render.
    Resolved several ambiguities via clarifying questions up front (recommended
    options chosen throughout): retired nothing this phase (no existing topics were
    superseded); disambiguated exactly what each of the 4 requested Venn topics
    should test before building any of them. Found and fixed a real pre-existing
    bug during the Tree Diagrams agent's visual check (flagged rather than fixed,
    since `diagrams.py` was off-limits for that agent's delegated task) — see the
    `diagrams.py` word-boundary Gotcha above. Backend suite grew from 304 to 335
    tests (335 includes the diagrams.py bug-fix test); the 4 hardcoded `160`-topic-
    count assertions were updated to `169`; frontend unaffected (29/29 — new groups
    render generically).
18. New session, Phase 2 (Statistics) of the same user-supplied list — the larger,
    more diagram-heavy half. Investigated reuse first rather than assuming 7 fully
    new diagram engines were needed: time series and cumulative frequency graphs
    turned out to be able to reuse the existing point-plotting mechanism (though
    ultimately given their own thin functions rather than literally reusing
    `draw_piecewise_graph`, once it became clear that function's underlying
    `_draw_scaled_axes` draws a fine gridline every single integer unit — fine for
    small algebra ranges, but would hang or clutter badly for a statistics chart
    with a y-axis in the tens/hundreds). Built 6 new diagram kinds (see "Statistics
    chart diagrams" above) and 21 new topics across 4 new files: `stats_mean`,
    `stats_mode`, `stats_median`, `stats_range`, `stats_averages_combined` (retiring
    the old combined `stats_mean_and_range`/`stats_median_and_mode`, confirmed with
    the user), `stats_mode_frequency_table`, `stats_median_frequency_table`,
    `stats_range_frequency_table`, `stats_interquartile_range` (all in the existing
    `statistics.py`); `bar_chart_construct`/`_interpret`, `composite_bar_chart`,
    `pie_chart_construct`/`_interpret`, `time_series_graph` (new `charts.py`, new
    "Charts and Graphs" group); `cumulative_frequency_plot`/`_interpret`,
    `box_plot_construct`/`_interpret` (new `cumulative_frequency.py`, new
    "Cumulative Frequency & Box Plots" group); `histogram_plot`/`_interpret` (new
    `histograms.py`, new "Histograms" group). 142→169 was step 17; this step is
    169→188 (169 + 21 new − 2 retired).

    Dispatched 4 parallel subagents for the 4 clusters (mirroring Phase 1's
    strategy), but all 4 hit an API session-usage limit mid-task and terminated
    early — only the statistics.py cluster had actually reached the
    write-and-test-pass stage before failing (verified independently and kept);
    the other 3 clusters had produced no file changes at all. Rather than wait
    for the limit to reset, built the remaining 3 clusters' topics directly
    (same specs originally written for the subagents), which also surfaced and
    fixed several real verification bugs a first pass of hasty "independent"
    checks had introduced — a `sorted(..., reverse=True)` tie-break mismatch
    against `.index()`'s first-occurrence convention (`bar_chart_interpret`'s
    "highest/lowest category" question), a Decimal divide-then-multiply-vs-
    multiply-then-divide rounding mismatch that should have used exact `Fraction`
    comparison instead (`pie_chart_interpret`'s percentage question), and several
    modelled examples with only a 1-line `worked_calculation` where the test
    convention across this codebase requires ≥2 (caught by running the same
    smoke-test loop the subagent prompts had specified, before writing the
    official test files). Also found and fixed a real box-plot layout bug during
    visual verification (not the same one fixed in Phase 1's Venn work): the
    two-box-plot comparison view's row labels (`"Class A"`/`"Class B"`) sat close
    enough to the axis start to overlap a long label's whisker line — fixed by
    reserving a dedicated label-column width on the left whenever any box has a
    `"label"`, shifting the whole plot area right, rather than just nudging the
    label position (see "Statistics chart diagrams" above). Backend suite grew
    from 335 to 383 tests; the 4 hardcoded `169`-topic-count assertions were
    updated to `188`; frontend unaffected (29/29 — new groups render generically).
19. New session, a large user-supplied Algebra topic list (11 items: expressions/
    formulae/equations/identities, forming and solving equations from words/angles/
    area-perimeter, solving inequalities, satisfying inequalities, solving quadratic
    inequalities, algebraic proof, the quadratic formula, algebraic fractions,
    rationalising surds, iteration, inequalities on a number line), plus two extras
    the user approved after a clarifying-questions round (changing the subject of a
    formula, algebraic indices — both genuine AQA/Edexcel gaps spotted while
    reviewing the existing Algebra section). Also asked up front, per the user's
    choice: build both directions for the number-line topic (draw *and* read),
    cover both number-property *and* identity-style proofs... resolved to
    number-property proofs only (the classic GCSE style), and give
    `forming_equations` a Foundation+Higher pair matching the existing split-topic
    convention. Added 20 new topics (188→208): `classify_expressions`;
    `forming_equations_foundation`/`_higher`; `change_subject_foundation`/`_higher`;
    `solving_inequalities_foundation`/`_higher`, `satisfying_inequalities_foundation`/
    `_higher`, `quadratic_inequalities` (new `inequalities.py`);
    `inequalities_number_line_foundation`/`_higher` (new `inequalities_number_line.py`,
    same "Inequalities" group, different file); `algebraic_proof` (24-template curated
    bank, `question_count=24` — the same "fixed pool, not 20 random draws" pattern as
    the Plotting Graphs topics' `question_count=5`, since a proof is a claim about
    *all* integers and can't be meaningfully re-randomised per question);
    `quadratic_formula`; `algebraic_fractions_add_subtract`/`_multiply_divide`;
    `rationalise_denominator` (appended to the existing `powers_roots.py`/Number
    section, alongside the pre-existing surd-simplification topic it's a natural
    sequel to); `algebraic_indices_foundation`/`_higher`; `iteration`. Built via 5
    parallel subagents (one per cluster of 2–5 related topics) plus the new
    number-line diagram kind (see "Number line diagrams" above) built and visually
    verified directly, matching the precedent set by Venn diagrams as the highest-
    risk new geometry in a batch. One subagent was launched with `isolation:
    "worktree"` by mistake (a second attempt at worktree isolation for a different
    agent then failed outright with a directory-already-exists race, so the rest of
    the batch ran directly in the main working tree instead) — its two files were
    recovered by copying them out of `.claude/worktrees/<agent-id>/` before removing
    the worktree, rather than merging a branch, since the agent hadn't committed
    anything. Two real bugs were caught only through end-to-end visual verification,
    not the unit tests (both now documented as gotchas above, and both are now
    genuinely fixed with an added regression test, not just individually patched):
    the number-line "between" compound inequality showing its lower bound the wrong
    way round (e.g. "3 > x < 6" instead of "3 < x < 6"), and `x^(1/4)`-style
    fractional exponents not being raised at all (only the inner "1/4" got the
    standalone-fraction treatment, leaving a literal "^(" ")" sitting on the
    baseline) — fixing the second one required restructuring `mathtext.py` from
    three sequential regex passes into one combined pass (see "Fractional exponents"
    above) and, along the way, surfaced that a straight rewrite of the file had
    silently normalised the module's non-breaking-space constant back to a plain
    ASCII space, un-fixing an older documented ReportLab quirk — caught by the
    existing regression test for that quirk, not missed. Central registry wiring,
    the 4 hardcoded `188`-topic-count assertions (updated to `208`), the full
    backend+frontend suite, and browser-driven end-to-end verification (worksheet
    *and* modelled-example generation through the real running app, for topics
    spanning the new diagram kind, fractional-exponent typesetting, and iteration's
    `x_(n+1)` notation) were all done centrally afterward, per the established
    parallel-subagent pattern. Backend suite grew from 383 to 455 tests; frontend
    unaffected (29/29 — new groups render generically).
20. New session, a large user-supplied Number topic list (~35 items spanning
    fractions, decimal arithmetic, recurring decimals, BIDMAS, negative-number
    arithmetic, indices, surds, standard form, and several percentage/ratio topics).
    Started with a research pass (2 Explore agents auditing every existing Number
    and Ratio & Proportion topic file) before asking anything, so the clarifying
    questions and final report could say precisely what already existed vs. what
    was genuinely new — several requested items turned out to already exist
    (dividing decimals, standard form multiply/divide without a calculator,
    large-number standard form "to", negative indices already inside the Higher
    "negative & fractional indices" topic, rationalising a conjugate surd
    denominator, applying a percentage increase/decrease) and were skipped.
    Asked 4 clarifying questions up front (all resolved to the recommended option):
    defer "equivalent fractions in diagrams" (a new diagram engine) to a future
    session and build the numerical version only now; split the existing combined
    "Negative Number Arithmetic" topic into two (add/subtract, multiply/divide)
    rather than four or zero; split "recurring decimals to fractions" into 3
    sheets by length of the recurring block (the existing Higher topic already
    covers the hardest "mixed" sheet, so only 2 new easier topics were needed);
    and confirmed "change of base indices" meant solving equations via a common
    base (e.g. 9^x = 3^5), not logarithms. Also made several lower-stakes
    judgement calls without a second question round (stated transparently in the
    session's chat rather than re-asking): retired the old combined negative-number
    topic in favour of the split pair (matching this app's established pattern
    elsewhere); interpreted "algebraic surds" as expanding brackets containing
    surds (FOIL/squared-bracket, e.g. (2+√3)(4-√3)); kept the new percentage/
    interest/best-buys topics in the existing "Ratio & Proportion" section rather
    than literally under "Number", matching where percentages already live.
    Added 25 new topics, retired 2 (net +23, 208→231): `fractions_equivalent`,
    `fractions_ordering`, `fractions_improper_mixed` (fractions.py);
    `decimals_add_subtract`, `decimals_multiply`, `recurring_decimal_single_digit`
    (Foundation), `recurring_decimal_two_digit` (Higher) (decimals.py); `bidmas`
    (new `order_of_operations.py`, new "Order of Operations (BIDMAS)" group);
    `negative_add_subtract`, `negative_multiply_divide`, `negative_ordering`
    (negative_numbers.py, replacing the retired single `negative_numbers` topic);
    `negative_indices` (Foundation — a genuine tier-accurate gap, since real
    specs put negative integer indices at Foundation and only fractional indices
    at Higher), `simplifying_indices_challenging`, `indices_common_base_equations`,
    `surds_multiply_divide`, `algebraic_surds` (powers_roots.py);
    `standard_form_to_small`, `standard_form_from_large`, `standard_form_from_small`
    (split from the retired combined `standard_form_from`), `standard_form_calculator`
    (standard_form.py); `simple_interest`, `find_percentage_change`,
    `percentage_increase_decrease_calculator`, `mixed_percentages` (percentages.py);
    `best_buys` (new `best_buys.py`, new "Best Buys" group). Built via 5 parallel
    subagents (one per cluster, each also required to update its own existing test
    file rather than replace it, since most of this batch appended to already-heavily-
    tested files), then central registry wiring, the full suite, and browser/PDF
    verification done afterward as usual.

    Three real issues were caught and fixed centrally, none of them by the parallel
    agents' own unit tests: (1) the `bidmas` topic's four question shapes picked
    their division operands independently at random, so most questions evaluated
    to an ugly improper fraction (e.g. "118/3") instead of the clean whole-number
    answer every real BIDMAS worksheet uses — fixed by picking the divisor first
    and constructing the dividend as a guaranteed multiple of it in all four shapes
    (caught only by rendering an actual worksheet and reading the answers, since
    the unit tests only checked the arithmetic was *correct*, not that it looked
    like real worksheet content). (2) One of the parallel agents (percentages/
    best-buys) incidentally discovered and flagged, but correctly left unfixed as
    out of scope, a pre-existing bug in `percentages.py`: `HIGHER_PERCENTS` includes
    decimal-string percentages like `"17.5"`, and `sp.Rational("17.5")` prints as
    the unreduced fraction `"35/2"` rather than `"17.5"` when interpolated into a
    prompt — this silently affected the already-shipped `reverse_percentage` and
    `compound_percentage` (Higher) topics (e.g. "After a 35/2% increase..."), fixed
    centrally by keeping the original decimal string alongside the `Rational`
    conversion for display purposes only, everywhere `HIGHER_PERCENTS` is used.
    (3) Confirmed the exact `≥`/`≤` symbol and grouping counts matched across
    Foundation/Higher tier pickers and section topic counts via the running app,
    not just the test suite. Backend suite grew from 455 to 487 tests; frontend
    unaffected (29/29 — new groups render generically).
21. New session, two "Ideas for a future session" items the user picked directly from
    the list (no new topic list this time): the equivalent-fractions shaded-diagram
    topic deferred in step 20, and dice/spinner/bag illustrations deferred since the
    Venn/tree/table diagram work. Entered plan mode first given the scope (two new
    diagram engines plus a topic-list retrofit); researched via 2 parallel Explore
    agents (one on `fractions.py`/`diagrams.py` conventions, one auditing every
    Probability topic for die/spinner/bag scenarios and their existing param shapes)
    before writing the plan, then confirmed two scope decisions with the user up
    front: the fractions diagram ships as a new sibling topic
    (`fractions_equivalent_diagram`, matching this app's established sibling-topic
    pattern) rather than retrofitting the existing numeric topic, and the
    illustrations retrofit all three shapes onto existing topics rather than a
    smaller pilot.

    Built 4 new diagram kinds in `diagrams.py`, all visually verified directly by
    rendering actual PDFs before trusting them (same highest-risk-first precedent as
    Venn/number-line diagrams): `draw_fraction_shapes` (1-4 bar or circle shapes,
    each divided into `parts` equal segments with `shaded` of them filled — reuses
    the existing `_label()` vinculum-fraction helper, built in step 16 but unexercised
    by any real topic until now, for the "n/d" caption under each shape);
    `draw_dice` (1-2 die faces with standard pip layouts, optional accent-highlighted
    target face); `draw_spinner` (equal wedge sectors, kept neutral/`PAPER` except a
    highlighted target sector, plus a small centre pointer — deliberately not a
    rainbow palette, matching this app's existing "shade only the interesting bit"
    convention); `draw_bag` (a rounded-rect body with a tied neck, small counters
    packed in rows grouped by colour, mapped directly from colour name to a matching
    hex rather than the abstract `CHART_COLORS` palette since the prompt text names
    the literal colour).

    Added one new topic (231→232): `fractions_equivalent_diagram` in `fractions.py`
    (Foundation, same group as its numeric sibling), with two shapes —
    `fill_missing_diagram` (Shape A given shaded, Shape B shown blank via `diagram=`
    then shaded via `solution_diagram=`, the same blank-then-revealed split the
    Plotting Graphs topics use) and `identify_equivalent_diagram` (one reference
    shape plus 3 labelled A/B/C candidates, reusing the existing numeric topic's
    verified-non-equivalent-distractor construction). Denominators are deliberately
    capped at a small "nice" set (4/6/8/9/10/12) rather than reusing the numeric
    topic's much larger range (up to ~90 in its distractor construction), since a
    diagram needs legible segment counts where the numeric topic doesn't.

    Retrofitted the dice/spinner/bag diagrams onto 9 existing Probability topics that
    already described the matching scenario in prose and had no diagram yet — no new
    topics, no topic-count change, purely additive `diagram=`/`solution_diagram=`
    wiring using values the generators already compute, so no new verification logic
    was needed (the diagrams never determine the answer). All 9 targets live in the
    same file (`probability.py`), so this was done directly in one pass rather than
    via parallel subagents, to avoid same-file edit conflicts: `probability_single_event`
    /`probability_complement`/`probability_conditional` always get a bag diagram (with
    the target colour highlighted on the first two); `probability_combined_dice`
    always gets two decorative dice (illustration only, not tied to the actual
    sum/product being asked); `probability_and_or_rule` always gets a diagram of one
    of the three kinds (bag for the OR branch's mutually-exclusive colours, with a
    third "other" bag share added when the two given probabilities don't already sum
    to 1; die or spinner for the AND branch's independent events, die taking priority
    if both a die and spinner appear since a coin can pair with at most one of them —
    required extending `_independent_event`'s return tuple with per-event diagram
    info); `probability_expectation` only gets a die diagram for its `context=="die"`
    branch (the `spinner` branch has no side-count in the generator, so drawing one
    would mean inventing a number not actually in the question — left text-only
    rather than fabricate); `probability_listing_outcomes` only gets a spinner diagram
    for its two single-spinner scenarios (`coin_spinner3`/`coin_spinner4` — the two
    two-spinner scenarios were left text-only since `draw_spinner` only draws one
    spinner and showing just one of two would misrepresent the scenario, not
    illustrate it). Also retrofitted `relative_frequency` in `data_handling.py` for
    its `"biased dice"` context specifically (a fixed pairing with the event "shows a
    six", so highlighting face 6 on a standard die is faithful, not invented) while
    leaving its `"spinner"` context text-only for the same missing-side-count reason
    as expectation's spinner branch. This partial/skip pattern was scoped up front in
    the plan, not discovered as a limitation partway through — no bugs were found
    while building it, and no diagrams needed reworking after the visual PDF checks.

    Backend suite grew from 487 to 503 tests; frontend unaffected (29/29 — no
    frontend changes were needed, new groups/topics render generically and the
    Modelled Example button was already driven by a per-topic API flag).
22. New session, a large user-requested feature with real design decisions up front:
    "practice tests" underneath the 6 topic sections — a Foundation/Higher picker,
    10 fixed (not procedural) OCR-GCSE-styled 100-mark papers per tier, each with a
    separate test-paper and mark-scheme download, the mark scheme in OCR's coded
    (M1/A1/B1) format. Asked clarifying questions up front per the user's explicit
    request, resolving: 20 papers total (10 per tier, not 10 total); content built by
    **freezing real output from the existing 232 generators** rather than hand-
    authoring new multi-part exam questions (the user's choice, given this app's
    established "always verify independently" identity doesn't extend to hand-written
    content); one 100-mark paper per test, not OCR's real 3-paper-per-sitting
    structure; full OCR marking codes, not a simplified answer-only scheme; and
    proceeding on general OCR/exam-board convention knowledge rather than real
    reference papers (none were available). Entered plan mode given the scope (the
    single largest addition this project has attempted) and researched via 3 parallel
    Explore agents (backend worksheet/PDF/models architecture, frontend homepage/
    section structure, full topic inventory + diagram availability + determinism)
    before writing the plan, then delivered via an explicit pilot-first sequencing
    matching this project's own established precedent (the Modelled Example feature
    piloted on 6 topics before the full rollout): built the whole pipeline, generated
    just 2 pilot papers (1 Foundation + 1 Higher), visually verified both PDFs end to
    end before generating the remaining 18.

    Built new `backend/app/practice_tests/` package (`models.py`, `mark_scheme.py`,
    `topic_selection.py`, `build.py`, `loader.py`, `data/*.json` — see "Current state"
    above for the full design) and `app/pdf/practice_test_renderer.py` (two new
    renderers), 3 new GET routes, and a new homepage section
    (`PracticeTestsView`/`PracticeTestCard`, mirroring `SectionView`/`TopicCard`
    exactly). Two real bugs were caught during the pilot's visual check, not by unit
    tests: (1) `estimation_rounding` silently printing `"3E+1"` instead of `"30"` in
    its prompt/solution text whenever a value rounds to a positive power of ten (see
    "Current state" above for the fix — a genuine multi-session-old bug, first
    exposed because this was the first content type to render that generator's raw
    text somewhere worth reading closely); (2) `topic_selection`'s gap-closing repair
    pass could compute a negative "marks still needed" value when a paper overshot
    100 (no topic can ever have negative marks, so those attempts silently wasted the
    whole retry budget) and used a non-randomised, easily-cycling backtrack order —
    both fixed (skip negative gaps; randomise which question gets swapped), plus a
    whole-paper retry (`MAX_PAPER_RETRIES`, regenerating with a perturbed seed) added
    as a final safety net after the fix still left one real paper (out of 20) short.
    Determinism (re-running `build.py` reproduces byte-identical JSON) and the
    exactly-100-marks constraint are both covered by dedicated tests, not just
    asserted once by hand.

    Backend suite grew from 503 to 526 tests; frontend grew from 29 to 45.
23. New session, a large ~30-item Geometry topic list from the user, split up front
    into 4 phases after checking the actual code (not memory) for repeats, per the
    user's explicit request: found 2 genuine repeats (`ratio_shape_similar_foundation`/
    `_higher` already cover "similar shapes"/"similar areas and volume", just filed
    under Ratio & Proportion not Geometry; circumference is already a random branch
    inside `area_circle`/`area_circle_foundation`) and 1 same-name-different-skill
    false positive (`graph_transformations` transforms *y = f(x)*, not a shape on a
    grid). Resolved a few scope ambiguities via clarifying questions up front:
    constructions/loci will be describe-the-method text questions (no meaningful way
    to "solve" a construction numerically); "cosine rule in bearings" is literally
    just that one combination; "mixed 2D shapes" is one new topic freely combining
    rectangle+triangle+circle-parts. Agreed the 4-phase split with the user:
    **Phase 1** (this step) — 2D area extensions; **Phase 2** — 3D shapes (properties,
    volume & surface area of cuboid/cube/triangular prism/cylinder/cone/sphere/
    pyramid/frustum, compound 3D shapes); **Phase 3** — trig/Pythagoras extensions +
    congruent proof (exact trig values, exact trig values in triangles, 3D
    Pythagoras, 3D trig, congruent triangle proof); **Phase 4** — transformations,
    bearings, constructions & loci (line/rotational symmetry, reflections/rotations/
    translations/enlargements including negative and fractional scale factors both
    completing and describing, cosine rule in bearings, the three constructions,
    loci and regions). Phases 2-4 are not started.

    **Phase 1** added 7 new topics to the existing Area & Perimeter group (39→46
    Geometry topics, 232→239 total) — 5 requested items became 7 because arc length
    and area of a sector are genuine both-tier content (Foundation calculator/decimal,
    Higher exact π-fraction form), mirroring the existing `area_circle_foundation`/
    `area_circle` split: `area_parallelogram`, `area_trapezium` (both Foundation, no
    real Higher differentiation for these two), `area_mixed_compound` (Higher — a
    rectangle with a triangular roof added and a quarter-circle cut from one bottom
    corner, genuinely mixing all three shape types unlike the existing two-shape-only
    compounds), `arc_length_foundation`/`arc_length`, `area_sector_foundation`/
    `area_sector`. New verification techniques introduced (both are now precedent for
    future geometry topics): a shoelace-formula coordinate-geometry cross-check for
    parallelogram/trapezium (shearing the top edge doesn't change the shoelace area,
    proven algebraically before coding, so it's a genuine second method); and a
    cross-formula check between arc length and sector area (`area = ½ × arc × r`,
    the inverse relation) rather than restating the same formula. Built 4 new diagram
    kinds (`draw_parallelogram`, `draw_trapezium`, `draw_sector` — shared by all 4
    arc/sector topics since the picture is identical regardless of which quantity is
    asked for, only the prompt text differs — and `draw_mixed_compound`, whose
    quarter-circle corner cut reuses `draw_venn_diagram`'s "neither"-region
    fill-then-erase trick), all visually verified before wiring into topics, matching
    this project's highest-risk-first precedent. One real bug caught and fixed via
    that visual check, not the unit tests: initially let Higher's arc/sector angle be
    any value 1-359, which produced mathematically-correct but unrealistically ugly
    exact-form fractions (e.g. `(4901/360)π`) whenever the angle didn't divide 360
    cleanly — fixed by restricting Higher's angle to multiples of 15° (23 values),
    which keeps denominators small and exam-realistic while still varying freely
    (239 distinct dedup keys per topic over 500 trials). A second, purely cosmetic
    diagram fix: the mixed-compound cut-radius label overlapped the arc when the
    radius was small — moved it outside the shape entirely rather than scaling its
    offset with the radius.

    Backend suite grew from 526 to 534 tests; frontend unaffected (45/45 — new
    topics render generically through the existing section/topic-card UI).
24. New session, Phase 2 (3D Shapes) of the same Geometry expansion, per the user's
    explicit "start phase 2" — no new clarifying-questions round was needed since the
    scope was already agreed in step 23. This phase's highest-risk work was a
    brand-new pseudo-3D diagram engine: `diagrams.py` had **no** 3D/oblique-projection
    drawing code at all before this session. Entered plan mode given the scope
    (matching this project's precedent for large features), researched via 2 parallel
    Explore agents (diagram-primitive/helper conventions in `diagrams.py`; topic/
    registry/test conventions in `area_perimeter.py`/`registry.py`) before writing the
    plan.

    Built and **visually verified centrally, before any topic code was written**
    (matching the established highest-risk-first precedent from Venn/number-line/arc-
    sector diagrams): 9 new diagram kinds in `diagrams.py` — `draw_cuboid` (also used
    for cube — same function, equal edge labels), `draw_triangular_prism`,
    `draw_cylinder`, `draw_cone` (with an optional dashed Pythagoras-helper triangle
    for the "derive the slant height" question branch), `draw_sphere` (doubles as a
    hemisphere via a `hemisphere` param), `draw_pyramid`, `draw_frustum`, `draw_net`
    (dispatches on shape to lay out cuboid/cylinder/cone/triangular-prism/pyramid nets
    — purely topological, not scaled to real dimensions, since only the layout matters
    for a "which net" question), and `draw_compound_3d` (3 variants: cylinder+
    hemisphere "capsule", cone+hemisphere "ice cream", cuboid+pyramid "silo roof" —
    reuses the standalone functions' coordinate helpers rather than duplicating
    projection math). New `Ellipse` import (not previously used in this file) for
    circular faces drawn in perspective. Convention: fixed oblique "depth" offset
    applied to front-face coordinates for straight-edged solids (cuboid/prism/
    pyramid), with dashed hidden edges at the one vertex/edge the shared-face-
    visibility analysis showed was genuinely hidden from the viewing angle; rounded
    solids (cylinder/cone/sphere/frustum) draw both ellipse boundaries fully solid
    rather than splitting hidden/visible arcs — a deliberate lower-risk simplification
    matching how most textbook diagrams actually render these. Caught and fixed
    several real label-overlap bugs via rendering actual PDFs at high DPI, not just
    trusting the first render (matching this project's established "render and look
    closely" precedent): the cone's slant/height labels initially collided when both
    were shown together (fixed by moving the slant label further down its own line);
    the pyramid's height label initially crossed the right-hand slant edge, then
    (after the first fix) was found — via a *second*, higher-DPI zoomed render — to
    instead cross the dashed back-base edge, finally fixed by placing it just above
    the diamond's back vertex where it clears both; the sphere/hemisphere/capsule
    radius labels sat too close to their equator-ellipse curves; and the standalone
    "silo" compound diagram's base label collided with the "Diagram NOT accurately
    drawn" caption because its box was drawn too low on the canvas.

    Added 12 new topics (239→251) in a new "3D Shapes" Geometry group, built via 4
    parallel subagents (one per cluster, each independently verifying its own
    generators and writing its own test file, per this project's established
    pattern), across 4 new files rather than one shared file specifically so the
    agents could run truly in parallel with zero risk of clobbering each other's
    edits (a deliberate refinement of the original plan's "one new file" wording,
    made once it was clear 4 agents would otherwise contend for the same file):
    `solids_properties.py` (`properties_3d_shapes` — faces/edges/vertices curated
    bank of 9 solids, verified against Euler's formula for the 6 true polyhedra;
    `nets_3d_shapes` — net-composition curated bank of 6 solids, using the new
    `draw_net` kind; both Foundation, `question_count=len(TEMPLATES)` per the
    `algebraic_proof.py` curated-bank precedent), `solids_prisms.py`
    (`volume_surface_area_cuboid`/`_cube`/`_triangular_prism`, all Foundation, each
    combining volume+surface-area into one topic via `rng.choice` exactly like the
    existing `area_rectangle` combines area+perimeter — the triangular prism uses
    scaled Pythagorean triples so its hypotenuse, needed for surface area, is always
    a clean integer), `solids_cylinders_cones.py`
    (`volume_surface_area_cylinder_foundation`/`_cylinder` — a Foundation-decimal/
    Higher-exact-π sibling pair mirroring `area_circle_foundation`/`area_circle`
    exactly; `volume_surface_area_cone`, Higher only, randomly either giving the
    slant height directly or requiring it be derived via Pythagoras from radius+
    height first), `solids_curved_compound.py`
    (`volume_surface_area_sphere` — sphere or hemisphere; `volume_surface_area_pyramid`
    — square-based, slant height of a triangular face via Pythagoras;
    `frustum_volume_surface_area` — the hardest topic this session, verified via two
    genuinely different volume formulas, cone-difference-via-similar-triangles vs. the
    closed-form `(1/3)πh(R²+Rr+r²)`, cross-checked with `sp.simplify`;
    `compound_3d_volume`, **volume only** — a deliberate scope cut, since correctly
    excluding a compound solid's internal shared face from a surface-area calculation
    was judged too much added risk for this first pass — all four Higher only, since
    cone/sphere/pyramid/frustum/compound-3D are genuinely Higher-only content on the
    real specs, needing no Foundation sibling). Cone/sphere/pyramid/frustum/compound
    are Higher-only by design, not an oversight — see the plan's "Scope decisions".

    Two of the four parallel agents independently found and fixed the **same** real
    bug during their own visual-PDF verification (not caught by unit tests, same
    story as most gotchas in this file): `sp.N(expr, 3)` — the display pattern
    copied from `area_perimeter.py`'s Foundation-decimal topics — silently switches
    to scientific notation (e.g. `"1.41E+4 cm³"`) once a value reaches four digits,
    which every `area_perimeter.py` topic this pattern was copied from happens to
    never hit, but cylinder/cone/sphere/frustum/compound volumes and surface areas
    comfortably do at the top of their ranges. This is the same *class* of bug as
    `estimation_rounding`'s power-of-ten formatting bug from chronology step 22 (a
    `Decimal`/`sympy` numeric-formatting edge case that's exact in value but wrong in
    display), not a repeat of the same bug — each cluster fixed it independently in
    its own file with its own `_round_to_3sf`/`_fmt_sig3` helper (Decimal-based fixed-
    point formatting) and added a dedicated regression test. During central review, a
    fifth issue was caught directly (not by an agent): `volume_surface_area_cube`'s
    dedup-key space measured at only 26 (13 side-lengths × 2 measures) against the
    default 20-question worksheet — thin enough to risk retries — widened to
    `rng.randint(2, 20)` (38 max keys) before integration. A sixth, cosmetic-only
    issue was caught during this session's own final end-to-end PDF check (not by any
    agent, and only visible at high DPI): the pyramid diagram's height label crossed
    the slant edge; see the diagram-fixes paragraph above for how it was resolved.

    Central integration (registry wiring across 4 new imports, the 4 hardcoded
    `239`-topic-count assertions updated to `251`, full suite, browser/PDF end-to-end
    verification) was done directly afterward, per the established parallel-subagent
    pattern. Backend suite grew from 534 to 592 tests (592 includes the cube dedup-
    space widening and pyramid label fix); frontend unaffected (45/45 — the new group
    renders generically through the existing section/topic-card UI, confirmed live via
    the browser preview: Geometry's Foundation/Higher split grew from 23/23 to 29/29).

25. New session, Phase 3 (trig/Pythagoras extensions + congruent proof) of the
    same Geometry expansion, per the user's explicit choice of Phase 3 over
    Phase 4 when asked (this session's plan also confirmed two design
    decisions up front: all 5 items are Higher-only except congruent triangle
    proof, which also gets a Foundation "state the criterion" sibling; and
    congruent triangle proof uses a curated template bank like
    `algebraic_proof.py`, not a procedural generator, since a proof's claim
    can't be meaningfully re-randomised). Entered plan mode given the scope,
    researched via 3 parallel Explore agents (trig/Pythagoras generator and
    verification conventions; the Phase 2 3D diagram engine's extensibility;
    the curated-bank pattern) plus a Plan agent, then verified every fact
    against the real files before finalizing the plan.

    Added 6 new topics (251→257): `exact_trig_values` (new
    `exact_trig_values.py`, Trigonometry group — a 14-entry `(ratio, angle)`
    lookup table for sin/cos/tan at 0°/30°/45°/60°/90°, verified independently
    via `sp.simplify` against sympy's own trig evaluation rather than
    re-checking the same hardcoded table); `exact_trig_values_triangles`
    (same file — reuses the existing `draw_trig_triangle` diagram unchanged,
    angle restricted to {30,45,60}, answer an exact surd/fraction verified by
    comparing the hand-derived value against a raw floating-point
    `math.sin`/`cos`/`tan` computation, a genuinely different computation
    path); `pythagoras_3d`/`trig_3d` (new `solids_3d_trig.py`, shared cuboid-
    dimension generation — a reroll-based `_cuboid_dims` helper keeps the
    space diagonal always irrational/decimal, mirroring
    `pythagoras.generate_hypotenuse_decimal`'s reroll pattern; both verified
    via the 3D coordinate distance formula / vector dot-product, a genuinely
    different route than the "apply Pythagoras/trig twice" method used for the
    displayed steps); `congruent_triangle_proof`/`_foundation` (new
    `congruent_triangle_proof.py` — an 18-entry curated bank of SSS/SAS/ASA/RHS
    scenarios, in a brand-new "Congruence Proof" Geometry group mirroring
    `algebraic_proof.py`'s dedicated-group precedent exactly; one shared
    template bank, two question shapes per the confirmed design — Higher gets
    the full written proof, Foundation just states the criterion; each
    template's `verify()` builds one concrete coordinate instance satisfying
    its stated givens, via two small reusable helpers
    (`_point_from_two_distances` for shared-side/SSS scenarios,
    `_third_vertex_asa` via the law of sines for ASA scenarios), then confirms
    all 3 corresponding side lengths match between the two triangles — the
    actual geometric consequence of any of the four criteria).

    Built and **visually verified first, before any topic code was written**
    (matching this project's established highest-risk-first precedent from
    Venn/3D-shapes/arc-sector diagrams): a new `two_triangle_congruence`
    diagram kind (`draw_two_triangle_congruence` + a new `_tick_marks` helper
    for equal-side marks, reusing the existing `_vertex_angle_arc` at two
    radii for nested equal-angle arcs) plus an additive `diagonal_label`
    extension to the existing `draw_cuboid` (a dashed space-diagonal line,
    following the exact optional-param-gated precedent already set by
    `draw_cone`'s `show_height_triangle`/`draw_pyramid`'s built-in height
    line). The spike caught a real bug immediately: the congruence diagram's
    default "Diagram NOT accurately drawn" caption overlapped the bottom-right
    vertex label — fixed by raising the triangles' vertical position within
    the canvas, giving the caption clearance. Deliberately decided *against*
    drawing an angle arc for `trig_3d`'s diagram (only the one diagonal line):
    these solids are fixed-proportion oblique sketches, and an arc between the
    *projected* 2D directions of two 3D lines would misrepresent the true 3D
    angle - the angle is described in the prompt text instead.

    One real bug was caught and fixed only by rendering an actual PDF and
    reading it closely — not by any unit test, the same story as most gotchas
    in this file: `mathtext.py`'s auto-fraction regex matched the trailing
    "2/2"/"3/2" substring inside an exact-value surd string like "√2/2"
    regardless of the preceding "√", raising/lowering just the digits and
    leaving a stray literal "√" in front (rendered as a confusing "√²/₂").
    Fixed with a `(?<!√)` negative lookbehind on the fraction alternative, so
    a fraction glued directly after "√" is left as plain text, while an
    unrelated plain rational trig value like "1/2" still gets the normal
    vinculum-style treatment. A second, pre-existing issue was fixed in
    passing: `backend/requirements.txt` was missing `pymupdf` even though this
    project's own documented "Verifying new topics visually" workflow (and
    several past chronology entries) rely on it — added as a real pinned
    dependency rather than an undocumented ad hoc install.

    Central integration (registry wiring — `solids_3d_trig` slotting into the
    existing "Pythagoras' Theorem"/"Trigonometry" groups, `congruent_triangle_
    proof` establishing the new "Congruence Proof" group — the 4 hardcoded
    `251`-topic-count assertions updated to `257`, full suite, browser/PDF
    end-to-end verification for all 6 new topics across both diagram kinds)
    was done directly, following the established parallel-subagent-session
    pattern even though this session's build was done directly rather than via
    subagents (the 3 files' interdependency — shared diagram kinds, a shared
    "which existing group" placement — made a single continuous pass simpler
    than coordinating parallel agents for a batch this size). Backend suite
    grew from 592 to 616 tests (23 new + 1 new `mathtext.py` regression test);
    frontend unaffected (45/45 — confirmed live via the browser preview:
    Geometry's Foundation/Higher split grew from 29/29 to 30/34, and the new
    "Congruence Proof" group appears correctly under Geometry).

26. New session, Geometry Phase 4a (Symmetry + Transformations) of the same
    expansion. The full original Phase 4 scope (transformations, bearings,
    constructions, loci) was judged too large for one pass, mirroring the
    precedent already set by splitting the overall Geometry expansion into
    Phases 1-4 back in step 23 — confirmed with the user up front, along with
    two other open questions from the paused prior session: construction
    topics (Phase 4b, not built this session) get no `verify()` at all
    (author-review only); and "describe the transformation" is wanted for all
    4 transform types, with enlargement getting a Foundation (positive
    integer scale factor) / Higher (negative/fractional) sibling pair for its
    "complete" style. Entered plan mode, researched via 2 parallel Explore
    agents (the `_draw_scaled_axes`/`to_px` gridded-diagram machinery and the
    blank/solution two-diagram pattern; registry conventions, existing
    Foundation/Higher split precedent, and confirmation of zero collision
    with any existing topic) plus a Plan agent, then confirmed two further
    scope decisions before writing code: centres of rotation/enlargement and
    translation vectors are always integer grid points (only the enlargement
    scale factor itself goes negative/fractional, sidestepping any risk of
    `mathtext.py`'s fraction regex firing mid-coordinate); and
    `transform_rotate_describe`/`transform_enlarge_describe` are Higher-only
    even though their "complete" siblings include a Foundation version
    (finding an unknown centre from before/after shapes is a harder,
    discriminator-level skill than reading one off).

    Added 11 new topics (257→268) in one new file, `transformations.py`,
    across two new Geometry groups: **Symmetry** (`symmetry_lines`,
    `symmetry_rotational` — an 11-entry curated bank of named shapes
    (rectangle, square, equilateral/isosceles triangle, isosceles trapezium,
    regular pentagon/hexagon, parallelogram, kite, rhombus, irregular
    pentagon) with hand-computed lines-of-symmetry/rotational-order claims,
    `question_count=len(_SYMMETRY_SHAPES)` per the `algebraic_proof.py`
    curated-bank precedent — verified independently and rigorously at
    *import time*, not just by a test: `_count_symmetries` re-derives both
    the line-count and rotational order from raw vertex coordinates alone,
    trying every geometrically possible reflection axis and rotation order
    from first principles, and raises immediately if any bank entry's claim
    doesn't match) and **Transformations** (`transform_reflect_complete`/
    `_describe`, `transform_rotate_complete`/`_describe`,
    `transform_translate_complete`/`_describe`,
    `transform_enlarge_complete_foundation`/`_complete_higher`/`_describe` —
    all procedurally generated on a fixed -8..8 grid, using a small pool of
    hand-picked *asymmetric* polygon templates (0 lines of symmetry,
    rotational order 1 — required so a "describe" question has a uniquely
    identifiable answer) with a reroll loop for parameter combinations that
    would land off-grid). Two new diagram kinds, both visually spiked and
    iterated on *before* writing topic content (this project's established
    highest-risk-first precedent): `draw_symmetry_shape` (a single named
    polygon, auto-scaled to fit the schematic box, with optional dashed
    symmetry line(s) or a rotational-order indicator on the solution page)
    and `draw_grid_transformation` (one flexible kind covering all 4
    transform types × both question styles, built on `_draw_scaled_axes` —
    draws the original shape always, the image only when given (the
    existing blank/solution split), and any combination of a dashed mirror
    line, a centre-of-rotation/enlargement dot, or a translation-vector
    arrow, independent of whether the image is shown, since those are
    *given* information the student needs, not the answer).

    Each transform type's independent verification uses a genuinely
    different method than the primitive used to build the displayed steps,
    per this project's established convention: reflection via the
    perpendicular-bisector definition (not a re-derived coordinate formula);
    rotation via complex-number multiplication (`× i`/`-1`/`-i`) instead of
    the coordinate swap/negate used for the steps; translation via an
    invariant-displacement check across every vertex; enlargement via a
    squared-distance ratio plus a collinearity check plus a dot-product sign
    check, together pinning down the transform without ever recomputing
    `q = centre + k*(p - centre)` directly. "Describe" topics reuse the same
    checks in the reverse direction.

    **Five real diagram/generator bugs were found and fixed during this
    session's own visual spike and follow-up verification passes — none by
    the unit tests, all by rendering actual output and looking closely, or
    by a programmatic scan once eyeballing individual renders stopped
    catching everything:**
    1. A long "centre of rotation"/"centre of enlargement" text label
       reliably collided with a nearby vertex's own label whenever the
       centre sat close to (or exactly on) a shape vertex — a common,
       pedagogically normal setup (e.g. "enlarge from vertex A"). Fixed by
       dropping the text label entirely (just the dot remains; the
       coordinate is stated in the prompt/solution text instead).
    2. A shrinking enlargement (scale factor 1/2) combined with a small
       shape and a centre at/near one of its own vertices produced a tiny,
       hard-to-label image. Led to widening `_SHAPE_TEMPLATES`' minimum edge
       length and, more fundamentally, discovering (2) and (5) below.
    3. `math.atan2(...) % math.pi`, used by `_count_symmetries` to dedupe
       candidate symmetry axes, hit a real floating-point wraparound: an
       angle just below zero reduces to just-under-π instead of
       just-above-zero, so a genuine axis could be double-counted as two
       distinct ones. Fixed with a `_same_axis` helper that checks both
       `abs(a-b)` and its distance from the `0`/`π` wraparound boundary —
       caught immediately at module import time (`square` computed 5 lines
       of symmetry instead of 4), not by a test.
    4. When a reflection's mirror line coincided exactly with the y-axis or
       x-axis (`x = 0`/`y = 0`), the dashed mirror line drew directly on top
       of the solid axis and the "x = 0" label collided with the axis's own
       permanent "y"/"x" name label. Fixed by excluding 0 from the mirror
       line's random-choice pool entirely, rather than special-casing the
       rendering.
    5. **The most significant finding**: a programmatic scan (extracting
       every rendered vertex label's real pixel position across hundreds of
       generated instances per topic, rather than trusting individual
       spot-checks) found that `rotate`/`translate`/`enlarge` still had a
       10-25% rate of two *unrelated* vertices' labels landing within a few
       pixels of each other — a centroid-distance "well separated" check
       had let the two shapes' bounding boxes overlap whenever either shape
       was elongated, or (for rotation/enlargement specifically) a vertex
       sat close to the transform's own centre, which by definition keeps
       its image close too. A stricter "bounding boxes must be fully
       disjoint" check was tried next but proved geometrically
       near-impossible for a plain positive-scale-factor enlargement on a
       bounded grid (analysis showed the required gap from the centre grows
       with `span / (k - 1)`, easily exceeding the grid's own size for
       `k = 2`) — so enlargement's centre is now *constructed* just outside
       the shape's own bounding box (a random cardinal direction, gap 2-4
       units) rather than chosen uniformly at random and hoped for, and
       separation itself is checked by predicting each label's actual
       landing position (replicating `diagrams.py`'s own outward-push-from-
       centroid formula in grid units) and requiring every pair to clear a
       minimum distance — directly targeting the real problem (labels
       colliding) without over-constraining shapes that merely overlap or
       cross without their labels colliding. Re-running the same
       programmatic scan afterward found zero collisions across 4500
       rendered instances (9 generators × 500 trials each). The reroll
       budget was also raised (200 → 4000 attempts) once the stricter combined
       checks made some parameter combinations - especially fractional-scale-
       factor Higher enlargement - genuinely rare rather than merely uncommon.

    A sixth, smaller issue (grammar, not a diagram bug): symmetry prompts
    read "a isosceles trapezium" for any shape name starting with a vowel
    sound — fixed with a small `_article()` helper.

    Central integration (registry wiring, the 4 hardcoded `257`-topic-count
    assertions updated to `268`), the full backend+frontend suite, and
    browser-driven end-to-end verification (worksheet *and* modelled-example
    generation through the real running app, plus a direct
    `render_worksheet`/`render_modelled_example` script per this project's
    documented "Verifying new topics visually" workflow, covering all 11 new
    topics) were all done directly in this session, built solo rather than
    via parallel subagents given the diagram-kind/verification-helper
    interdependency across all 11 topics in a single new file. Backend suite
    grew from 616 to 638 tests; frontend unaffected (45/45 — confirmed live
    via the browser preview: Geometry grew from 38 Foundation/37 Higher
    topics with new "Symmetry" and "Transformations" groups both appearing
    correctly, and both the worksheet and modelled-example endpoints
    returned 200 OK for a live topic in this group).

27. New session, Geometry Phase 4b (bearings, constructions, loci) — the
    last remaining piece of the original Phase 4 scope, resuming from a
    prior session that had paused after a full plan-mode research pass (3
    parallel Explore agents + 1 Plan agent, plus two technical claims —
    ReportLab `ArcPath`'s sweep direction and `fillOpacity` genuinely
    rendering in real PDF output — independently re-verified by direct
    experiment) with every design decision already confirmed but no plan
    file written and no code started. This session re-verified the
    codebase's state hadn't drifted (topic count, registry import block,
    and topic-list tail all matched the prior research exactly), wrote the
    final plan straight from those preserved findings, and proceeded to
    implementation without re-running the research.

    Added 6 new topics (268→274) across 3 new files: `bearings_cosine_rule`
    (Higher, new `bearings.py`, new "Bearings" group) reimplements
    `triangle_rules.py`'s SAS cosine-rule maths (not imported — matches that
    file's existing sine_rule/cosine_rule/triangle_area sibling-function
    pattern) as a two-leg bearings word problem: the included angle at the
    turn point is derived from the two given bearings (back-bearing +
    difference) before applying the cosine rule, verified in two independent
    stages (coordinate-geometry angle re-derivation via dot product, then
    the same coordinate-distance cross-check `cosine_rule` itself uses).
    `construction_angle_bisector` / `construction_perpendicular_bisector` /
    `construction_triangle` (all Foundation, new `constructions.py`, new
    "Constructions" group) are "describe the method" text questions with
    **no `verify()` at all** (author-review only, per the confirmed design —
    the sole exception to this codebase's "always verify independently"
    rule, since there is no way to numerically check a described
    construction) and no `TEMPLATES` bank — randomised numbers/labels
    embedded in fixed per-scenario method text instead, giving a state space
    in the thousands-to-millions rather than a fixed handful.
    `loci_constructions` (Foundation: locus from a point / two points / two
    lines, one of three branches per question) and `loci_regions` (Higher: a
    genuinely two-constraint shaded region — "within r cm of A AND closer to
    A than B") both live in new `loci.py`, new "Loci" group, and both use the
    same blank-question/completed-solution `diagram`/`solution_diagram`
    split as the Phase 4a grid-transformation topics.

    Three new diagram kinds were built and visually spiked first, before any
    topic code was written (this project's established highest-risk-first
    precedent): `draw_bearings` (a new `_bearing_arc` helper sweeps the
    *full* clockwise-from-north bearing via `ArcPath.addArc`, unlike
    `_angle_arc`'s shortest-arc-only behaviour — needed since a bearing arc
    is often reflex; a new `_north_arrow` helper; both drawn at *both* turn
    points, matching real exam bearings diagrams) and
    `draw_loci_construction`/`draw_loci_region` (built on the existing
    `_draw_scaled_axes` grid engine, sharing a new `_scaled_circle` helper
    that always uses `Ellipse` with separately-computed x/y radii rather
    than `Circle` — confirmed necessary by rendering a circle on a
    deliberately wide non-square grid window and seeing it stay a true
    circle, not an ellipse; `draw_loci_region`'s shading is a rasterized dot
    mesh, sampling a fine grid and painting a small translucent
    `fillOpacity` dot wherever every constraint holds, rather than
    hand-built boolean region geometry).

    The bearings diagram spike caught and fixed several real label-collision
    bugs via rendering actual PDFs across a wide sweep of bearing
    combinations (reflex, near-cardinal, both turn directions) — not by unit
    tests, the same story as most diagram gotchas in this file: vertex
    labels at the two turn points routinely collided with their own north
    arrow when pushed straight up by the usual outward-from-centroid rule
    (fixed by detecting a near-vertical outward direction at an arrow-bearing
    vertex and pushing sideways instead); leg-length/unknown-distance labels
    centre-anchored on their offset point swung back over a near-vertical
    leg and collided with that vertex's own "N" label (fixed with the same
    anchor-by-offset-sign rule already used by `draw_parallel_lines`/
    `draw_triangle_angles`, plus a wider offset distance); and a
    downward-pushed label at the bottom-most point could land on top of the
    "Diagram NOT accurately drawn" caption (fixed by asymmetric margins
    reserving headroom at both the top, for arrows, and the bottom, for
    pushed-down labels). `draw_loci_construction` also gained a
    `given_lines` param (always drawn, on both question and solution pages —
    the two rays forming an angle to bisect, or the segment between two
    points to bisect) and `draw_loci_region` gained a `boundaries` param
    (each constraint's own dashed circle/segment boundary, always drawn,
    independent of whether the shading itself is present yet) — both follow
    the same "given information is always shown" convention
    `draw_grid_transformation` established for its mirror line/centre/vector
    in Phase 4a.

    Central integration (registry wiring — 3 new imports at their
    alphabetical slots, one contiguous topic block appended after Phase 4a's
    block and before `# Probability`, matching how every previous phase's
    block was appended in one place), the 4 hardcoded `268`-topic-count
    assertions updated to `274`, the full backend+frontend suite, and
    browser-driven end-to-end verification (worksheet *and* modelled-example
    generation through the real running app for all 6 new topics, plus
    confirming the new "Bearings"/"Constructions"/"Loci" groups appear
    correctly under Geometry's Foundation/Higher tier picker — Foundation
    grew 38→42, Higher grew 37→39) were all done directly in this session.
    Backend suite grew from 638 to 658 tests; frontend unaffected (45/45 —
    new groups render generically through the existing section/topic-card
    UI).

28. New session, a direct user request to revisit standalone fractions in
    prose text (worksheet prompts/solution steps/answers): replace the
    `<super>`/`<sub>` raised-numerator/lowered-denominator approximation
    (shipped in step 16, when a true vinculum was judged "too fragile for
    the payoff") with a real stacked vinculum, matching a reference image
    the user provided. Asked two clarifying questions up front per the
    user's request: confirmed scope was prose text only (diagram labels
    already had a true vinculum) and confirmed proceeding with the
    previously-identified PIL/PNG approach rather than re-investigating
    alternatives first.

    Built `app/pdf/fraction_images.py`: PIL draws the numerator, a
    horizontal rule, and the denominator directly onto a transparent PNG
    (4x supersampled) using the same Windows TrueType font files ReportLab
    itself falls back to, cached in memory per unique (num, den, font_size,
    bold, colour) and written once per fraction to a per-process temp
    directory (`atexit`-cleaned). Added `Pillow` as an explicit pinned
    dependency in `requirements.txt` (it was already an installed transitive
    dependency of reportlab/pymupdf, but now genuinely imported directly, matching
    this project's established precedent of pinning what's actually used —
    see the `pymupdf` addition in step 25). `mathtext.py`'s standalone-
    fraction branch now emits `<img src="..." valign="bottom"/>` instead of
    `<super>/<sub>`; the leading sign of a negative fraction stays a plain
    baseline character in front of the image, not part of it. `to_markup`
    grew required `font_size`/`color` keyword params (plus optional `bold`),
    and all 15 `_fmt(text)` call sites across the 3 PDF renderers
    (`renderer.py`, `modelled_example_renderer.py`, `practice_test_renderer.py`)
    became `_fmt(text, style)`, deriving those three from the real
    `ParagraphStyle` in use so a fraction in bold green answer text renders
    bold and green, not always plain black.

    The `valign="bottom"` attribute (and the exact image height needed to
    make it work) was determined empirically, not from documentation alone:
    a spike script rendered the same fraction inline at 8 different `<img
    valign>` values side by side in a real PDF, rasterized at high DPI, and
    compared pixel-for-pixel against the surrounding text's own baseline —
    `"bottom"` (ReportLab's own default) turned out to align correctly with
    no extra offset maths needed at all, once the PNG's own bottom edge was
    drawn flush with the denominator's glyph bottom. Verified across a wide
    battery of real cases the same way: negative fractions, mixed numbers,
    a fraction immediately before a comma/period/closing-paren, bold text,
    ACCENT-coloured bold text, multi-digit numerators/denominators, and
    several fractions in one line — all correct on the first full pass.

    **Real bug found and fixed via an actual end-to-end worksheet render,
    not a unit test** (same story as most gotchas in this file — the
    synthetic spike text never happened to trigger it): the first working
    version italicised `x`/`n` *after* substituting fractions, but a
    fraction is now an `<img src="{temp path}">` tag, and
    `tempfile.mkdtemp`'s random directory-name suffix can itself contain a
    bare "x" or "n" flanked by non-letters (e.g. `..._k_x7ili6\frac_0.png`)
    - the later italics pass re-scanned and corrupted that path, breaking
    image loading entirely for any worksheet unlucky enough to hit a
    matching random suffix. Fixed by reordering `to_markup` to italicise
    first and substitute fractions/exponents last, so inserted markup
    (including file paths) is never re-scanned by anything else — with a
    new deterministic regression test (monkeypatching the fraction-image
    path to force the exact "x in the path" scenario) added alongside the
    real-world discovery, since the bug itself was probabilistic and
    wouldn't reliably reproduce in a normal test run.

    The old `<sub>`+comma ReportLab spacing quirk (documented in the
    Gotchas list above) no longer applies now that fractions are images,
    not `<sub>` tags — since nothing in this codebase emits `<sub>` at all
    any more, its non-breaking-space workaround was removed as dead code
    (the Gotchas entry itself was kept, marked historical/resolved, in case
    `<sub>` markup is ever hand-written again). `test_mathtext.py`'s
    fraction tests were rewritten from exact-string equality (no longer
    possible, since the output embeds a dynamically-generated temp path) to
    structural assertions via a regex extracting the `<img>` tag's
    attributes; a new `test_fraction_images.py` covers the PNG renderer
    directly (real file on disk, correct dimensions/colour, caching
    behaviour). Visually verified end-to-end across genuinely different
    real topics (not just the synthetic spike) — `fractions_add_subtract`,
    `fractions_simplify`, `fractions_equivalent`, `probability_single_event`
    (worksheet, worked solutions, *and* the modelled-example page, which
    exercises three more paragraph styles including the boxed bold worked-
    calculation and the bold ACCENT-coloured answer line) — plus the
    practice-test mark scheme's dense 9pt table, the smallest font size
    fractions appear at anywhere in the app. Diagram labels were untouched
    (they already had their own, separate true-vinculum implementation in
    `diagrams.py`, which doesn't share `fraction_images.py` since diagrams
    draw as vector shapes, not Paragraph markup, and never had the inline-
    image constraint prose text does). Backend suite grew from 658 to 668
    tests; frontend and Geometry Phase 4b both unaffected (this session
    touched only the shared math-typesetting layer).

29. New session, three items from the "Ideas for a future session" list that
    the user picked directly (shown the list, chose two categories: "loose
    ends from finished phases" and "diagram gaps on existing topics"), plus a
    4th candidate (`probability_combined_dice`) the user asked about that
    turned out to already exist. Given the size and number of embedded
    design decisions (a new topic, a cross-cutting typesetting refactor, a
    generator-content change plus a new diagram kind, and 5 separate
    lower-confidence curriculum-audit candidates CLAUDE.md itself flagged as
    needing a decision before building), asked scoping questions up front
    via `AskUserQuestion` before committing to anything, then entered plan
    mode given the resulting scope: 3 parallel Explore agents (one per
    remaining piece) followed by 1 Plan agent, with every finding
    independently re-verified by reading the actual current file contents
    directly (not just trusting agent reports) before finalizing the plan.

    **`probability_combined_dice` was confirmed to already exist** — a
    fully-built Higher topic (`generate_combined_dice`, three event
    branches, brute-force-verified against the 36-outcome sample space).
    This was exactly the "may overlap" candidate flagged by the original
    curriculum audit (step 13) as needing a check first; confirmed now that
    it's not overlap, it's a duplicate. Nothing built, reported back to the
    user, dropped from scope.

    Built, in this order (diagram-layer work first, per this project's own
    established precedent): (1) spinner diagram gaps — `draw_spinner`
    refactored into a shared `_draw_spinner_at` helper plus new
    `draw_spinner_pair`, wired into `probability_listing_outcomes`'s
    two-spinner scenarios, `probability_expectation`'s spinner branch (now
    reusing its own numerator/denominator as the sector count/highlight,
    capped at `denominator <= 12`), and `relative_frequency`'s spinner item
    (fixed illustrative spinner); (2) `compound_3d_surface_area` — new
    Higher topic, same 3 variants/diagram as `compound_3d_volume`, excluding
    each internal join face, verified via the same independent-float-
    recomputation pattern already proven by its sibling topics in the same
    file; (3) bold vector labels — a new `\vec{a}`/`\vec{b}` ASCII sentinel
    convention (see "Compound-3D surface area, spinner diagrams, and bold
    vector labels" above for full technical detail on all three). One open
    scope question was resolved with the user via `AskUserQuestion` before
    building: accept that `compound_3d_surface_area`'s diagram won't show
    the slant height (unlike its standalone cone/pyramid siblings), rather
    than extending `draw_compound_3d` — kept the diagram-reuse zero-risk.

    Every piece was visually verified end-to-end via real worksheet/
    modelled-example PDF renders (not just unit tests) before considering it
    done, per this project's established discipline — including the
    two-spinner diagram in a real `probability_listing_outcomes` worksheet,
    the `denominator = 12` boundary case for `probability_expectation`'s
    spinner, all 3 `compound_3d_surface_area` variants (question, solution,
    *and* modelled-example pages), and bold vectors composing correctly
    alongside fraction-vinculum images in the same line. No bugs were found
    during this session's own verification passes (unlike most prior
    sessions in this file) — the extensive up-front research and plan
    validation this time caught the design issues (the cuboid_pyramid
    rounding asymmetry, the denominator-cap threshold) before any code was
    written rather than after. Central integration (registry wiring, the 4
    hardcoded `274`-topic-count assertions updated to `275`, full
    backend+frontend suite, browser-driven end-to-end verification for all 7
    touched/new topics) was done directly. Backend suite grew from 668 to
    682 tests; frontend unaffected (45/45 — confirmed live via the browser
    preview: Geometry grew from 81 to 82 topics, "Compound 3D Shapes
    (Surface Area)" appears correctly alongside its volume sibling in the
    "3D Shapes" group).

30. New session, a user-reported gap: neither the Practice Tests papers nor
    their mark scheme actually represented a real OCR GCSE Maths exam. The
    user pointed at revisionmaths.com's OCR past-papers page as a reference
    and asked for clarifying questions before any changes. Fetched that page,
    then read (via pymupdf/`fitz`, since `WebFetch` can't parse PDF binaries)
    an actual June 2024 Foundation paper + its mark scheme, both tiers' real
    Formulae Sheets, and — after the user asked to check more than just one
    year for variety — 4 more mark schemes spanning June 2017 to June 2022
    (Foundation and Higher). This confirmed three genuine gaps: (1) real OCR
    GCSE Maths is 3 separate 100-mark, 1h30m papers per tier per sitting
    (J560/01-03 Foundation, /04-06 Higher), calculator allowed on all three
    (no non-calculator paper, unlike AQA/Edexcel) — the app built one combined
    100-mark "paper" per test id; (2) real mark-scheme conventions (M1/A1/B1/
    SC, `oe`/`isw`/`nfww`/`rot`/`soi`/`dep`) were confirmed stable 2017→2024,
    but `cao` — which the app's mark scheme hardcoded onto every accuracy
    mark — was dropped from OCR's own abbreviation list after 2019 in favour
    of plain accepted-answer wording, so the app was following a retired
    convention; (3) every real paper ships a tier-specific Formulae Sheet,
    which the app didn't render at all. Asked 4 clarifying questions up front
    via `AskUserQuestion` (paper structure, sittings-per-tier, mark-scheme
    fidelity, formulae sheet) — all resolved in favour of the full rebuild:
    3-paper sittings, 10 sittings/tier (30 papers/tier, 60 total, up from 20),
    real mark-scheme conventions, and the formulae sheet. Entered plan mode
    given the scope (touches the data model, the build script, the mark
    scheme, both PDF renderers, the API schema, and both practice-test
    frontend components) and read every relevant file directly (not via
    subagents, since the design questions were interdependent) before writing
    the plan.

    A hard boundary was set and kept throughout: content stays generated by
    this app's own 275 verified generators (frozen the same way as before) —
    the real papers were used only to calibrate *structure, mark-scheme
    conventions, and generic mathematical facts*, never to copy OCR's actual
    copyrighted question or mark-scheme text.

    `PracticeTestPaper` gained `sitting_id`/`paper_number` fields;
    `build.py` now loops 10 sittings × 3 papers per tier (`SITTINGS_PER_TIER`,
    `PAPERS_PER_SITTING`), each paper built by the same per-paper assembly
    logic as before (fill-then-close, repair, retry) just invoked 3× per
    sitting with its own seed — `topic_selection.py` itself needed no changes,
    since its existing within-paper-only dedup already allows a topic to
    recur across a sitting's 3 papers, which is exactly how real OCR papers
    behave. `mark_scheme.py`'s accuracy-mark description changed from
    `"{answer} oe (cao)"` to `"{answer} oe"`. `practice_test_renderer.py`
    gained a new Formulae Sheet page (`_formulae_sheet_elements`, inserted
    between the cover page and Q1) — trapezium area, prism volume, circle
    circumference/area, Pythagoras, sin/cos/tan for both tiers, plus the
    quadratic formula, sine rule, cosine rule, area of a triangle, and
    conditional probability for Higher only — reusing the existing
    `right_triangle`/`general_triangle` diagram kinds for its reference
    figures (no new diagram kind needed) and matching this app's existing
    ASCII math conventions exactly (grepped `pythagoras.py`/`triangle_rules.py`/
    `quadratic_equations.py` for the established phrasing — `"a² + b² = c²"`,
    `"a / sin(A) = b / sin(B) = c / sin(C)"`, `"x = (-b ± √(b^2 - 4ac)) / 2a"` —
    rather than inventing new notation). Also added a short, own-words
    marking-instructions paragraph to the mark-scheme PDF
    (`_marking_instructions_box`) summarising the M/A/B convention and
    abbreviation key. `PracticeTestSummary` (API schema) and the frontend
    `PracticeTestSummary` type both gained `sittingId`/`paperNumber`; no route
    shape changed, since `paper_id` was already the one unique identifier.
    `PracticeTestsView` now groups the flat paper list by `sittingId`
    client-side (mirroring `SectionView`'s existing client-side tier
    grouping) before rendering one `PracticeTestCard` per sitting;
    `PracticeTestCard`'s prop changed from a single `paper` to a `papers`
    array, rendering one row per paper with its own independent download
    buttons. The homepage's static "Practice Tests" teaser copy in `App.tsx`
    (hardcoded "10 Foundation and 10 Higher, 100 marks each" / "20 papers")
    was also stale and needed updating — caught only by browsing the actual
    running app during verification, not by any test, since this text isn't
    covered by any assertion.

    **One real, pre-existing diagram bug was found and fixed** via rendering
    the actual Formulae Sheet PDF and looking closely, not by a unit test —
    same story as most gotchas in this file: `draw_general_triangle`
    (`app/pdf/diagrams.py`, shared by the existing sine-rule/cosine-rule/
    triangle-area topics) positioned its `side_c_label` only 6 units above
    the "Diagram NOT accurately drawn" caption, which visibly overlapped once
    a caller labelled all three sides together — several existing cosine-rule
    topics already do exactly this, so this was latent in already-shipped
    output, only now surfaced because the Formulae Sheet's reference triangle
    is the single densest use of this diagram kind (all three sides and all
    three angles labelled at once). Fixed by tightening the label's offset
    from the base (`-12` → `-8`), confirmed clear via a second, zoomed render.
    A smaller, purely cosmetic authoring issue was also caught the same way:
    the sin(A)/cos(A)/tan(A) trio was originally written as one
    space-separated formula line, and ReportLab's Paragraph whitespace
    collapsing ran them together into an unreadable single line — split into
    3 separate lines.

    All 20 old `data/*.json` files (old `foundation-NN`/`higher-NN` id scheme)
    were deleted and `build.py` was re-run to produce all 60 new papers
    fresh — re-confirmed byte-identical/exactly-100-marks via the existing
    (now updated) determinism and mark-total tests. Backend suite grew from
    682 to 684 tests (2 new tests render a real Foundation and Higher paper +
    mark scheme via `fitz` and assert the Formulae Sheet page and the current
    mark-scheme wording are actually present, and that the retired `cao` tag
    is not — an automated stand-in for the manual visual check, since this is
    new page content that would otherwise only be caught by eye); frontend
    unaffected in count (45/45 — `PracticeTestCard.test.tsx`/
    `PracticeTestsView.test.tsx` fixtures were updated for the new grouped-
    by-sitting shape). Verified end-to-end via the running app: cover page,
    Formulae Sheet (both tiers, both reference diagrams legible with no label
    overlap), and mark-scheme wording were all screenshotted from real
    rendered PDFs; the browser preview confirmed each sitting card shows 3
    papers with 6 working download buttons, and a real paper + mark-scheme
    download was exercised through the actual UI (network requests confirmed
    200 OK for `foundation-01-paper1/paper` and `foundation-01-paper2/
    mark-scheme`).

31. New session, a user-requested audit: read all 6 AQA 8300 spec pages
    (Number, Algebra, Ratio & Proportion, Geometry & Measures, Probability,
    Statistics) and cross-referenced every one against the app's 275 existing
    topics to find genuine content gaps. Reported findings by confidence tier
    (high/medium/low, matching this project's own curriculum-audit
    convention) rather than building anything immediately, per the user's
    explicit "ask any clarifying questions" instruction. Found 7 high-
    confidence gaps: solving quadratics by factorising/completing the square
    (only the quadratic-formula method existed as an actual "solve for x"
    topic - factorise/complete-the-square topics only manipulated the
    expression), graphs of exponential/trigonometric functions, equation of a
    circle + tangent, plans and elevations of 3D solids, basic/Foundation
    bearings (only the Higher cosine-rule application existed), scatter
    graphs & correlation (previously flagged in this file's own "Ideas" list
    but never built), and sampling/populations (a genuinely new finding).
    Asked the user to prioritize; entered plan mode given the scope (research
    via 3 parallel Explore agents covering: quadratic-solving/graph-plotting/
    circle-equation code, bearings/3D-diagram code, stats-axes/no-diagram-
    topic code) and confirmed via `AskUserQuestion` to build all 3 phases
    (reuse-heavy quick wins → moderate diagram extensions → two brand-new
    diagram engines) in one session.

    **Phase 1** (reuse existing code, minimal new diagram work): solving
    quadratics by factorising (`solve_quadratic_factorising_foundation`/
    `_higher`, added to `expand_factorise.py`, reusing its existing
    `_find_factor_pair`/root-construction helpers directly) and by completing
    the square (`solve_quadratic_completing_square`, `quadratic_graphs.py`,
    constructing a guaranteed-real-root quadratic via a square-free surd
    offset, reusing `powers_roots._SQUARE_FREE_FACTORS`); `sampling_methods`
    (new "Sampling and Populations" Statistics group, `sampling.py` - a
    genuinely randomised stratified-sample calculation branch verified via
    exact integer/Fraction round-half-up cross-checks, plus a scenario-bank
    branch for bias/method-identification questions, each scenario still
    randomising its own cosmetic numbers/locations for dedup-key variety);
    `circle_equation` (new "Equation of a Circle" Algebra group,
    `circle_equation.py`, Higher only - needed **zero new diagram code**,
    since `draw_loci_construction` (built for `loci.py` in step 27) already
    accepted exactly the `circle`/`segment` param shape this needed).

    **Phase 2** (extend one existing function per item): `bearings_foundation`
    (Foundation, same "Bearings" group as the existing Higher cosine-rule
    topic) needed a genuine extension to `draw_bearings` - the existing
    function always drew a full 3-point/2-leg/2-arc diagram with no clean way
    to get a 2-point single-leg diagram through params alone (confirmed by
    checking: setting the second bearing to the back-bearing degenerates
    point C onto point A instead of omitting it), so a new
    `_draw_bearings_single_leg` branch was added, dispatched whenever
    `bearing_at_B` is omitted - back-bearing and reading-a-bearing question
    types built on top. `plot_exponential`/`trig_graph` (new topics in
    `graphs.py`'s existing "Plotting Graphs" group) needed one new `elif`
    branch each in `diagrams.py`'s `_fn_value` (trig limited to sin/cos, not
    tan, to avoid the asymptote-branch-splitting complexity `draw_function_
    graph`'s reciprocal kind already needs).

    **Phase 3** (new diagram engines, built and visually verified before any
    topic code was written, per this project's established highest-risk-
    first precedent): `draw_scatter_graph` (new diagram kind, built on the
    existing `_draw_stats_axes` engine but deliberately *not* mirroring
    `draw_time_series`/`draw_cumulative_frequency`'s connecting `PolyLine`,
    since scatter points must never be joined; added a from-scratch line-of-
    best-fit renderer, no precedent for that anywhere in this file) powers
    `scatter_graph_construct`/`_interpret` (new topics in `charts.py`'s
    sibling `scatter_graphs.py`, "Charts and Graphs" group) - data is
    generated around a known line with random noise, then the actual (noisy)
    data's Pearson correlation sign is independently recomputed and checked
    against the intended direction, rerolling if unlucky noise flipped it,
    rather than trusting the generating parameters alone. `draw_plans_and_
    elevations` (genuinely new from-scratch diagram engine - confirmed no
    existing helper produces true orthographic front/side/plan views, since
    every other 3D diagram in `diagrams.py` uses oblique projection via the
    shared `_offset()` helper) powers `plans_and_elevations` (new topic,
    "3D Shapes" group, `plans_elevations.py`) for cuboids and triangular
    prisms (reusing `solids_prisms.py`'s own validated dimension generation),
    laid out in the standard first-angle arrangement (plan below the front
    view sharing its width, side view beside the front view sharing its
    height) - the question page reuses the existing oblique `draw_cuboid`/
    `draw_triangular_prism` diagrams unchanged for the "given" solid, and the
    new engine only appears on the solution page.

    **Several real bugs were found and fixed via this session's own testing
    and visual-verification passes, not by writing code and assuming it was
    right:**
    - A latent sign-formatting bug in `quadratic_graphs.py`, present since
      the file was first written (chronology step 7): three step-text lines
      hand-reconstructed `"x^2 {sign}x + {c}"` instead of calling the
      already-correct `_fmt_quadratic` helper, so a negative constant term
      printed as `"+ -3"` instead of `"- 3"` - caught only because the new
      `solve_quadratic_completing_square` generator copied the same buggy
      pattern and a console print surfaced it; fixed at the root in all
      three pre-existing occurrences plus the new one, with a regression
      test added across every generator in the file.
    - `_draw_scaled_axes`'s tick-spacing helper (`_nice_tick_step`) had a
      flat "step 10 for any span over 50" rule that no existing caller had
      ever exceeded by much (the widest was `circle_equation`'s radius-25
      case, span ≈ 52) - `trig_graph`'s 0-360-degree domain (span 360)
      exposed it immediately: every integer from 1 to 360 was crammed into
      the tick labels as unreadable overlapping text. Fixed by extending the
      tiering (20/50/100 for larger spans) - purely additive, confirmed no
      existing diagram's span reaches the tiers that changed.
    - `trig_graph` was first built with only 2 truly distinct dedup keys
      (sin, cos) and a `question_count` override to match - but a modelled
      example always builds 5 distinct *practice* questions for its own
      topic regardless of that override (`routes.py`'s hardcoded
      `PRACTICE_QUESTION_COUNT`), so every modelled-example request failed.
      Fixed by adding genuine further variety (reflection in the x-axis,
      and a second 360-degree window) rather than papering over it, giving
      8 real combinations and letting `question_count` return to the
      sibling-topic default of 5 - caught by the full suite's existing
      "render a modelled example for every topic" test, not a bug found by
      inspection.
    - `plot_exponential`'s curve visibly flattened at its right-hand edge in
      the rendered PDF: the usual "+1 unit" x-margin the sibling plotting
      topics use pushed the curve just far enough past `y_max` to trigger
      `draw_function_graph`'s existing clamp-to-y_max behaviour, which
      flattens rather than continues the curve - fixed by dropping that one
      topic's right-hand margin only (exponential growth needs it far less
      than the mild curves the shared margin was tuned for).
    - `sampling_methods`'s stratified-sample calculation initially cross-
      checked its exact-Fraction round-half-up answer against a plain
      `round(float)` computation - passed a 300-trial smoke test, then
      failed at a wider trial count from a genuine floating-point precision
      issue exactly at .5 tie boundaries (not, as first suspected, Python's
      round-half-to-even convention). Fixed by making the independent check
      exact too (integer-arithmetic round-half-up cross-checked against
      Fraction-based round-half-up - two different code paths through
      Python's numeric stack, neither touching binary floats), then
      confirmed clean across 180,000 trials.

    Central integration (registry wiring for all 11 new topics across 8
    files, the 4 hardcoded `275`-topic-count assertions updated to `286`,
    dedicated test files written or extended for every new topic following
    this project's established `GENERATORS` list + 200-400-trial pattern -
    3 brand-new test files plus 4 existing ones extended, none of which had
    any dedicated coverage before this step's "write proper tests" pass),
    the full backend+frontend suite, and browser-driven end-to-end
    verification (worksheet *and* modelled-example generation through the
    real running app for a sample of the new topics, including a live
    search confirming both new "Solving Quadratic Equations" siblings and
    the new "Equation of a Circle" group render correctly) were all done
    directly in this session. Backend suite grew from 684 to 715 tests;
    frontend unaffected (45/45 - all new topics render generically through
    the existing section/topic-card UI, confirmed live via the browser
    preview).

32. New session, two user requests handled in sequence. First: make Practice
    Test papers look more like a real OCR script. Asked 2 clarifying
    questions up front (both resolved to the recommended option): working
    space scaled to a question's own mark value rather than a fixed amount,
    and a distinct boxed "Answer" line beneath it, matching real exam
    convention. Built `_lines_for_marks`/`_working_lines`/`_answer_line` in
    `practice_test_renderer.py` and wired them into `_question_block` -
    verified visually (papers grew from ~6-7 pages to ~18-20, as expected
    once every question gets real working room) and confirmed diagrams and
    working space don't collide.

    Second: the user linked the real OCR GCSE Mathematics specification
    (J560, ocr.org.uk) and asked to check every one of its content points
    against this app's 286 existing topics. Downloaded the PDF directly
    (`WebFetch` can't parse PDF binaries, same lesson as step 30) and read
    the entire subject-content section (pages 12-51, all 12 strands) via
    `fitz` text extraction - the extraction jumbles table-column order but
    keeps every phrase intact, workable for a content audit. Every candidate
    gap was verified against the *actual current generator code* (grep/read,
    not just inferred from the spec text) before being reported - this
    caught several false positives early (e.g. `decimals.TOPIC_ORDERING`
    already mixes fraction/decimal/percent types, so "ordering mixed
    fractions/decimals/percentages" wasn't actually a gap; `velocity_time_
    interpret` already covers area-under-graph = distance). Found 10
    genuinely missing high-confidence gaps plus 5 lower-confidence ones,
    and one structural finding unrelated to topic coverage: the real spec
    requires Paper 2 (Foundation)/Paper 5 (Higher) - the middle paper of
    every 3-paper sitting - to be non-calculator, contradicting step 30's
    build (which had concluded, from real past papers, that OCR was
    calculator-allowed throughout - true for the papers checked, but not
    the actual current spec). Asked the user via `AskUserQuestion` which
    gaps to build and whether to fix the calculator-paper mismatch too -
    both resolved to "everything, now."

    Entered plan mode given the scope (10 topics across many files plus a
    structural Practice Tests change), researched via 3 parallel Explore
    agents (practice-tests calculator-tier plumbing; graphs.py/diagrams.py
    conventions for a tan-graph extension and a new inequality-region
    diagram; transformations.py/bearings.py/changing_subject.py conventions
    for the remaining new topics) plus direct reads of `constructions.py`/
    `circle_theorems.py`/`iteration.py`, then wrote the plan.

    **Shared diagram infrastructure was built and visually verified first**
    (this project's own established precedent), directly rather than
    delegated: two new circle-theorem diagrams (`draw_circle_same_segment`,
    `draw_circle_alternate_segment`, following the existing `draw_circle_
    angle_centre`-family pattern exactly); tan(x) support for the trig-graph
    plotting engine, deliberately scoped to x-windows that stay strictly
    between two consecutive asymptotes (e.g. -80..80°) rather than general
    asymptote branch-splitting (which the existing `reciprocal` kind already
    needs and a general tan implementation would too) - just one line added
    to `_fn_value`'s trig lookup; and a new `inequality_region` diagram kind
    (`draw_inequality_region`), built on the existing `_draw_scaled_axes`
    engine plus the exact rasterized-dot-mesh shading technique `draw_loci_
    region` already proved, deliberately scoped to inequalities of the form
    `y <op> m*x + c` (never general `ax+by=c` or a vertical line) - dashed
    boundary for strict `<`/`>`, solid for `<=`/`>=`.

    The 10 gaps were then delegated to 7 parallel background subagents by
    independent file cluster (no shared files, so true parallelism): (1)
    `substitution.py` - new Foundation/Higher pair for substituting given
    values into a formula, verified via Fraction arithmetic vs. independent
    sympy `.subs()`; (2) `kinematics.py` - new Higher `kinematics_suvat`
    topic (the three SUVAT equations), deliberately scoped to avoid ever
    solving `s = ut + ½at²` for `t` (a quadratic) - only `s`/`u`/`a` are
    ever the unknown for that equation; (3) `sequences.py` + `iteration.py`
    extensions - `special_sequences_foundation`/`_higher` (triangular/
    square/cube-number sequences; Fibonacci-type and geometric progressions)
    and `trial_and_improvement` (a genuinely different skill from the
    file's existing `x_(n+1)=g(x_n)` recurrence topic - systematic decimal
    search on a cubic with a confirmed sign-change interval); (4) `circle_
    theorems.py` + `constructions.py` extensions - two new theorem shapes
    ("angles in the same segment", "alternate segment theorem") added to
    the existing `circle_theorems` topic's shape pool (4→6, no new topic
    ID) using the new diagram kinds, plus a new `construction_perpendicular_
    from_point` topic (both "from an external point" and "at a point on the
    line" scenarios), following this file's unique no-`verify()` convention;
    (5) `transformations.py` extension - `combined_transformations` (Higher),
    scoped to 4 GCSE-safe composition rules with known closed forms (two
    translations → vector sum; two reflections in parallel mirrors → a
    translation; two rotations about the same centre → angle sum; reflect
    in both axes → 180° rotation about the origin), verified by simulating
    both transforms in sequence and confirming the claimed single transform
    reproduces the identical final coordinates; (6) `map_scales.py` (new
    "Map Scales and Scale Drawings" Geometry group) + `inequalities_region.py`
    (new Higher topic using the new diagram kind, mirroring `inequalities_
    number_line.py`'s exact draw/read question-direction split) + a `graphs.py`
    extension teaching `trig_graph` a `tan` branch; (7) the Practice Tests
    non-calculator retrofit - `calculator_allowed` added to `PracticeTestPaper`,
    a curated `CALCULATOR_ONLY_TOPIC_IDS` frozenset in `topic_selection.py`
    (every messy-decimal/calculator-labelled topic - trigonometry, calculator-
    π area/volume topics, `standard_form_calculator`, `iteration`, etc., erring
    toward inclusion since it only affects 1 of every 3 papers), `build.py`
    building a second calculator-filtered topic pool and using it whenever
    `paper_number == 2`, the cover page's instructions conditional on the new
    flag, and the field threaded through the API schema and the frontend
    (`PracticeTestCard` gained a "Non-calculator" badge).

    **5 of the 7 background agents hit a hard monthly API spend limit mid-task
    and were killed** - a real external constraint, not a bug to route around.
    Rather than assume the work was lost, checked `git status` directly: every
    agent (including the 5 killed ones) had already written its actual code,
    tests, and new files to disk before dying, mid-verification at worst - the
    only casualties were a handful of `.png` scratch files never cleaned up
    and (for the transformations agent specifically) a diagram fix it had
    identified but not yet applied. Confirmed every file's completeness
    directly (tails ending in a real `TopicDefinition`, not mid-edit) before
    trusting any of it, then ran the full suite (all 756 passed immediately,
    even before central registry wiring, since each cluster's own test file
    imports its module directly).

    Central integration (registry wiring for all 10 new/extended topics -
    286→296 - the 4 hardcoded `286`-topic-count assertions updated to `296`,
    full backend+frontend suite, rebuilding all 60 Practice Test papers now
    that the calculator-tier logic and new topics were registered, confirmed
    via a direct JSON scan that every non-calculator paper is genuinely free
    of every `CALCULATOR_ONLY_TOPIC_IDS` topic) was done directly. **Three
    real bugs were found and fixed via this session's own visual-verification
    pass, not by any unit test** - the same story as most gotchas in this
    file: (1) a *pre-existing*, unrelated bug in `draw_circle_two_tangents`
    (present since long before this session) - its external point/label sat
    above the `Drawing`'s own declared canvas height, so the "117°"-style
    label silently bled upward into the question's prompt text, only now
    surfaced because verifying the two *new* theorem shapes meant rendering
    this diagram kind closely for the first time in a while - fixed by
    giving that one function a taller canvas; (2) `draw_inequality_region`
    (this session's own new code) drew each boundary line between its raw
    `x_min`/`x_max` endpoints without clipping to the visible window, so a
    steep line's off-screen endpoint sent the drawn line far outside the
    `Drawing`'s bounds, bleeding into the page title above - fixed with a
    new `_clip_line_to_window` helper that finds the line's true intersection
    with the rectangle's four edges, confirmed clean across 300 trials; (3)
    `combined_transformations` (also this session's new code) - its wider
    double-prime labels (`A''`) could land close enough to an axis to collide
    with that axis's own numbered tick labels, a class of overlap the
    existing `_clear_of_axis_name_labels` check doesn't cover (it only
    guards the two axis-*name* spots, not every tick along the line) - fixed
    with a new `_clear_of_axis_tick_labels` check added to all 4 combo
    reroll functions, confirmed zero collisions across 500 trials. Browser-
    driven end-to-end verification confirmed all 296 topics live, the
    section/group counts match exactly (Algebra 63→70, Geometry 84→87,
    others unchanged), search finds every new topic, a real worksheet
    download returns 200 OK, and the Practice Tests "Non-calculator" badge
    renders correctly on Paper 2 - which also surfaced and fixed one small
    CSS nit (the paper label wrapping mid-text once the badge took up extra
    row space; added `white-space: nowrap`).

    The 5 medium-confidence gaps this session's audit found were **not**
    built (reported, not actioned, per the user's explicit choice to build
    only the 10 high-confidence ones) - see "Ideas for a future session".
    Backend suite grew from 715 to 756 tests; frontend grew from 45 to 46.

33. New session, a large brand-new feature ("Bell Tasks") built from a real
    reference PowerPoint the user supplied for style ("Bell Task planning DO
    NOT SAVE.pptx", from their Downloads - read directly by unzipping its raw
    XML, since this project's `pptx`-authoring skill's usual `markitdown`/
    LibreOffice tooling either wasn't installed (`markitdown`) or doesn't work
    on this Windows machine (LibreOffice absent entirely; its `soffice.py`
    wrapper throws on `socket.AF_UNIX`)). Asked two rounds of clarifying
    questions up front per the user's explicit request (8 questions total,
    covering topic-pool scope, the box↔topic↔day layout mapping, whether an
    answer key was wanted, branding/logo handling, diagram handling inside a
    small box, what a mystery "10" placeholder should show, and regeneration
    behaviour) before writing anything, then entered plan mode given the
    scope (3 parallel Explore agents covering backend generation/routes
    architecture, frontend homepage/section architecture, and diagram-kind/
    pptx-tooling availability, followed by 1 Plan agent) and read every
    critical file directly before finalizing the plan.

    Built the feature described in "Bell Tasks" above in `Current state`
    (full technical detail there, not repeated here): a new
    `backend/app/bell_tasks/` package (`diagram_raster.py`, `math_tokenizer.py`,
    `layout.py`, `generator.py`, plus the reference file copied in verbatim as
    a template asset), a new `POST /api/bell-tasks` route/schema, and a new
    `BellTasksView.tsx` frontend screen wired in as a third homepage feature
    alongside the 6-section grid and Practice Tests. `python-pptx` (1.0.2) was
    added as a new pinned backend dependency - confirmed absent beforehand,
    the first time this project has needed to read/write `.pptx` rather than
    PDF output.

    The single riskiest piece - rasterizing one of this app's existing
    ReportLab `Drawing` diagrams to a PNG for embedding in a `.pptx` picture
    shape, with no prior precedent anywhere in this codebase and CLAUDE.md's
    own note that ReportLab's bitmap renderer (`renderPM`) isn't installed
    here - was spiked and validated in complete isolation first, per this
    project's own established discipline: `reportlab.graphics.renderPDF`
    (pure vector-to-PDF, needs no Cairo bindings) renders the `Drawing` to a
    small in-memory one-page PDF, then `fitz` (already pinned) rasterizes it -
    confirmed working first against synthetic shapes, then against several
    real diagram kinds (a triangle, a rectangle, a bar chart), before any
    pptx-specific code was written.

    Three real bugs were found and fixed via this session's own end-to-end
    visual verification (not by any test written in advance) - see the full
    writeup in "Bell Tasks" above: a tokenizer bug classifying compound-word
    hyphens ("right-angled") as minus-sign math tokens; a genuine text/diagram
    overlap for long, data-listing prompts once actually rendered in
    PowerPoint (fixed with a text-length-aware shrink-or-skip layout, not just
    a bigger fixed margin); and a doubled tier suffix
    ("... (Foundation) (Foundation)") for the handful of topics whose own
    display name already ends with their tier in parentheses.

    Visual QA for the generated `.pptx` couldn't use this project's usual
    LibreOffice-based render-and-look-closely workflow (not installed on this
    machine), so `pywin32` was installed ad hoc (a one-off local QA tool, not
    added to `requirements.txt`, since the app itself never depends on it) to
    COM-automate the real Microsoft PowerPoint already installed here and
    export actual rendered slide images - confirming the fixes above and
    giving genuine confidence in fonts/colours/branding/diagram placement
    that a structural-only check couldn't. Full backend+frontend suites and a
    live browser click-through (KS3 disabled, KS4 6-topic picker, Generate, a
    real 200 OK `.pptx` download with no console errors) were also run.
    Backend suite grew from 756 to 808 tests; frontend grew from 46 to 52.

    Same feature, continued in a follow-up conversation before step 33 had
    ever been committed, per 3 pieces of direct user feedback on the first
    real generated deck: diagrams looked squeezed/stretched, the 296-option
    plain `<select>` dropdowns needed search, and Cambria Math should mean
    PowerPoint's actual native equation objects, not just a font choice. See
    "Bell Tasks" in `Current state` above for the full technical detail on
    all three fixes (aspect-preserving diagram sizing; `SearchableTopicSelect.tsx`;
    real OMML equations via a new `app/bell_tasks/omml.py`) and the fourth
    real bug they surfaced (native equations silently rendering blank because
    of paragraph-child ordering relative to `endParaRPr` - the single most
    subtle gotcha this feature produced, found only by rendering real
    generator content in real PowerPoint, not by any test written in
    advance). Backend suite grew from 808 to 828 tests; frontend grew from 52
    to 61.

Everything above, including step 33 (Bell Tasks, and this follow-up round of
fixes), is committed and pushed (see `git log`).

34. New session. First, two small housekeeping requests: confirmed the two step-33
    follow-up commits were already picked up by the open PR (`gh pr view 3`) automatically
    (a PR tracks its head branch directly - `aqa-spec-gap-topics` - so nothing extra was
    needed), then updated the PR's own description to mention Bell Tasks (it previously
    only described steps 31's AQA-gap topics, the PR's original scope) and refreshed its
    test-plan counts to the current 828/61.

    Second, and the larger piece: the user is starting a broad aesthetic-review pass across
    every topic and asked for a PDF with one question from every topic, plus a separate
    answers PDF, so feedback could be given in stages. Asked 3 clarifying questions up front
    (layout - one topic per page vs continuous flow; topic labelling - full Section/Group/
    Tier breadcrumb vs bare name; answer-PDF depth - full worked solution vs answer-only),
    all resolved to the recommended option. Built `backend/scripts/generate_review_pdfs.py`
    - a one-off dev script, not part of the app itself - that reuses the real renderer's own
    block-building helpers directly (`_question_block`/`_solution_block` from
    `app/pdf/renderer.py`, `build_styles()` from `app/pdf/styles.py`) rather than
    reimplementing them, so the output is a true preview of the app's actual current
    styling. Walks `sections_tree()` in the app's own declared order, calling
    `build_worksheet(topic.id, topic.fixed_tier, count=1, rng=shared_rng)` once per topic
    (one shared, fixed-seed `random.Random(42)` across all 296 topics, so re-running the
    script after a fix reproduces the *same* questions for direct before/after comparison,
    the same "share one rng" precedent used elsewhere in this codebase) - each topic gets
    its own page headed `Section › Group › Topic Name (Tier)` plus a `Topic N of 296 • id:
    topic_id` line (the id makes it trivial to jump straight to the right generator file
    from a piece of feedback). Generated both PDFs and sent them directly to the user (not
    just written to disk) via the file-send tool. Verified before sending: page counts
    (`all_topics_review_questions.pdf` is exactly 296 pages, one per topic, confirming no
    topic was skipped or duplicated; `all_topics_review_answers.pdf` is 299 - 3 topics'
    worked solutions genuinely spill onto a second page - `trig_graph`'s table-of-values,
    `plot_distance_time`'s journey narrative, `loci_regions`'s two-constraint description -
    confirmed by reading those specific pages' text directly, not just assumed, since a
    stray page-count mismatch could just as easily have been a real bug) and spot-checked
    rendered pages at both ends and the middle of each document, including one diagram-
    bearing topic, all correct. No app code was touched this step - this was purely a new
    internal tool built from 100% existing, already-verified rendering code, so no topic
    count or test count change. The script was committed and pushed (see the intro's PR
    note above).

35. New session, a large batch of concrete review feedback on Number-section topics from
    the aesthetic-review pass (step 34's PDFs), plus several items explicitly marked
    "change throughout" - meaning fix the underlying typesetting capability once,
    centrally, rather than per-topic. Asked two clarifying questions up front via
    `AskUserQuestion` (both genuinely ambiguous, not guessable): "curved x" meant
    switching the italic font used for variables app-wide from Helvetica-Oblique
    (straight strokes, easily confused with ×) to a genuinely curved italic font; the
    recurring-decimal notation should use dot(s) over the repeating digit(s) (confirmed
    UK GCSE convention), not a bar over the block. Entered plan mode given the scope
    (research via direct file reads plus one Plan agent, since the design was already
    well understood from the codebase's own documented conventions) - the plan phased
    the work as: spike the 4 riskiest new rendering pieces first, land them as shared
    `app/pdf/mathtext.py` engine capabilities, then apply the specific Number-topic
    content fixes on top, then pilot a language-variety helper.

    **Phase 0 spikes** (all done and visually confirmed correct before any real topic
    code was touched, matching this project's "verify the riskiest piece first"
    precedent): (1) TTF font registration in ReportLab - genuinely new territory for
    this codebase (`fraction_images.py`'s existing TTF usage is PIL-only, a separate
    mechanism) - registered Times New Roman Italic/Bold Italic
    (`C:\Windows\Fonts\timesi.ttf`/`timesbi.ttf`) via `pdfmetrics.registerFont(TTFont(...))`,
    confirmed via a real rendered-PDF spike that an explicit `<font name="...">` tag
    (not `<i>`, which only resolves to the Standard-14 family's own oblique face) works
    standalone, nested inside `<super>`, in bold contexts, and at small (9pt) sizes -
    and that `String(fontName=...)` in `diagrams.py`'s vector-shape labels accepts the
    same registered name directly. (2) A full-length radical image (hook + bar spanning
    the radicand) - hand-drawn via PIL polygon/line primitives sized to the radicand's
    measured width, mirroring `fraction_images.py`'s architecture. (3) A fraction image
    (via `get_fraction_image` at a reduced size) nested inside `<super>` - confirmed it
    rises and aligns correctly even at the smallest font size fractions appear anywhere
    in the app (the practice-test mark scheme's 9pt table), reversing an earlier
    deliberate "not worth the complexity" decision documented in `mathtext.py`. (4) A
    recurring-decimal dot-mark image (single dot over a lone repeating digit; dots over
    both the first and last digit of a longer block) - rendered as one flat PIL image
    per occurrence (not composited via Paragraph markup) since placing the dot(s)
    accurately needs to measure each digit's own position.

    **Engine changes**, all landed centrally in `app/pdf/mathtext.py` (plus two new
    sibling modules, `app/pdf/radical_images.py` and `app/pdf/recurring_decimal_images.py`,
    mirroring `fraction_images.py`'s caching/tempdir architecture) - each fixes every
    topic using the same ASCII convention, not just the topic that surfaced the request:
    (a) the curved-italic-x font swap, applied identically in `diagrams.py` (which now
    imports the same registered font name directly from `mathtext.py` rather than
    maintaining its own independent constant, so prose and diagram labels can never
    drift apart); (b) `_MATH_RE` grew alternatives for a bare variable exponent (`8^x`)
    and a generic compound-parenthesised exponent (`9^(x+2)`, `5^(3x)`) - both need
    `_VARIABLE_RE` to leave an `x`/`n` immediately after `^` un-italicised (added `^` to
    its negative-lookbehind class) so `_MATH_RE`'s own alternative can claim it and
    superscript it correctly; (c) a `√(?P<radn>\d+)` alternative renders a full-length
    radical for any bare-digit radicand, with a `(?!/\d)` lookahead deliberately
    preserving the existing flat-text exact-trig-value convention (`√2/2` stays
    untouched, per the module's own documented "Surd-over-integer gotcha"); (d) the
    fractional-exponent alternative now renders a real reduced-size vinculum image
    raised in `<super>` instead of flat `<super>(1/4)</super>` text; (e) two new
    explicit ASCII sentinel markers, `\frac{NUM}{DEN}` and `\recur{PREFIX}{BLOCK}` -
    the same precedent as the existing `\vec{a}`/`\vec{b}` marker (a blanket regex can't
    safely auto-detect an unknown-value placeholder, an algebraic/surd numerator, or
    which digits are a decimal's recurring block, so the generator marks it explicitly)
    - protected from the earlier italics/vector passes via a new placeholder-extraction
    step in `to_markup` (pulls marker spans out to opaque Private Use Area characters
    before `_VARIABLE_RE`/`_VECTOR_RE` run, splices the real rendered `<img>` back in
    after `_MATH_RE`), closing off the same bug class already documented for the
    fraction-image temp-path corruption, this time for marker content instead of a
    random tempfile suffix; (f) a defensive end-anchored regex strips a trailing "."
    immediately after a decimal number (e.g. "...3.5." → "...3.5") - lives in the one
    function shared by all three PDF renderers, so it covers every topic's prompt with
    no per-topic-file changes needed at all.

    **Real bug found via this session's own visual verification, not by any unit test**
    (same story as most gotchas in this file): rendering `powers_higher`'s answer
    exposed that `"1/{base}^{exponent}"`-style text (denominator immediately followed by
    a bare `^exponent`, with nothing grouping them) had *always* rendered wrong - the
    plain-fraction regex claimed just the "1/{base}" part, leaving the exponent to
    superscript separately, reading as "(1/base)^exponent" instead of the intended
    "1/(base^exponent)". This was latent since long before this session (the old flat
    `<super>`/`<sub>` fraction markup had the exact same regex-matching behaviour), only
    now made visually obvious by the new, much more prominent vinculum image. Found and
    fixed **10 occurrences of the same pattern across `powers_roots.py`** (not just the
    one topic that surfaced it) by wrapping the denominator in parentheses,
    `"1/({base}^{exponent})"`. Also fixed, in the same file, a smaller pre-existing
    cosmetic issue surfaced by the new vinculum's higher visual prominence: the
    conjugate-rationalisation branch always showed an explicit coefficient of 1 in its
    surd term (e.g. "7 + 1√7" instead of "7 + √7"), unlike the simple-rationalisation
    branch which already special-cased this.

    **Number-topic content fixes**, all built on top of the engine changes:
    `fractions_ordering`/`decimals_ordering` reworded to "ascending order"/"descending
    order" (`decimals_ordering` gained a genuine descending variant - it was previously
    ascending-only); `fractions.py`'s `generate_multiply_fractions`/
    `generate_divide_fractions`/`generate_divide_fractions_foundation` (+ modelled
    twins) fixed via reroll-on-collision so numerator can never equal denominator (a
    disguised-integer risk, e.g. "5/5") - deliberately NOT switched to the file's other
    dependent-draw pattern, which would have also silently eliminated improper
    fractions these Foundation topics are meant to produce; an Explore-agent audit of
    every other topic file confirmed no further instances of this bug class exist
    elsewhere in the app. `number_theory.py`'s `factors` gained a new low-probability
    third branch ("How many factors does N have?", via weighted `rng.choices`, verified
    independently via the prime-factorisation divisor-count formula) plus a matching
    modelled-example path (previously unconditional, only ever demonstrating
    "list_factors" style). `fractions_equivalent` now randomly asks for either the
    missing numerator or denominator (previously always numerator) and uses the new
    `\frac{?}{d}` marker for the unknown placeholder instead of plain literal text.
    `fractions_equivalent_diagram` had its fraction-caption labels stripped from every
    diagram shape in both existing branches (the student now reads the fraction from
    the shading itself), plus a new third "diagram_only" branch with a short prompt and
    none of the "Shape A is divided into N equal parts..." explanatory prose, since the
    now-caption-free diagram communicates that visually. `rationalise_denominator`'s
    both branches (simple and conjugate) now build their answers via the `\frac{}{}`
    marker instead of raw string concatenation. All 3 recurring-decimal topics
    (`recurring_decimal_single_digit`/`_two_digit`, `decimals_recurring_to_fraction`)
    switched from parenthesised `"0.(digits)"` text to the `\recur{}{}` marker -
    surfaced a second real bug via a rendered-PDF spike (not caught by the unit tests,
    which only check the underlying regex/image logic): `valign="bottom"` (the
    fraction/radical images' own proven-correct setting) visibly sank the recurring-
    decimal image below the true text baseline, because unlike those two image kinds
    (whose ink touches both the top AND bottom of the image), this image only has
    padding ABOVE the digits (reserved for the dot mark) - `"bottom"` aligns to the
    line's descender space instead of the true baseline in that specific case. Fixed by
    using `valign="baseline"` for this one marker only, confirmed via the same
    side-by-side valign-comparison spike technique `fraction_images.py`'s own docstring
    already documents using originally.

    **Language-variety pilot**: new `app/topics/phrasing.py` (small categorised
    verb-pool helpers - `evaluate_verb`/`amount_verb`/`simplify_verb`/`convert_phrasing`,
    each a thin `rng.choice` over a pool sized to fit one sentence shape, since not
    every synonym fits every grammatical pattern) applied throughout `fractions.py`,
    `decimals.py`, and `powers_roots.py` (every hardcoded "Work out"/"Simplify"/"Find X
    of Y"/"Write X as Y" prompt in those 3 files now varies per-question). Full rollout
    across the other ~250 topics is deliberately out of scope for this session -
    flagged as a follow-up, matching this project's own pilot-then-rollout precedent
    (e.g. Modelled Examples, step 10→11).

    No topic count change (296 - this was entirely rendering/wording fixes, no new or
    retired topics). Central verification: full backend suite, the review-PDF script
    re-run to regenerate both all-topics PDFs (confirming the "change throughout" items
    landed correctly on topics never directly touched this session, e.g. a Pythagoras
    surd-hypotenuse answer and a plain linear-equations prompt both spot-checked and
    confirmed correct), and a live browser click-through (worksheet + modelled example
    downloads both 200 OK, no console errors) for `fractions_equivalent_diagram`'s new
    branch. Backend suite grew from 828 to 862 tests (new `test_radical_images.py`,
    `test_recurring_decimal_images.py`, `test_phrasing.py`, plus extended
    `test_mathtext.py`/`test_fractions.py`/`test_powers_roots.py`); frontend unaffected
    (61/61 - no frontend files were touched this session).

36. New session, a large batch of concrete Algebra-section feedback from the same
    aesthetic-review pass (step 34's PDFs), covering ~20 named items across diagrams,
    wording, and one systemic "the fraction line is a plain slash, check this
    everywhere" request. Entered plan mode given the scope; worked mostly directly
    (diagram-engine and shared-renderer changes first, per this project's own
    precedent), then dispatched parallel background agents once the remaining work
    was well-isolated per-file. One item — `iteration` ("remove the underscore and
    make it look like the picture attached") — is **still blocked**: no image
    actually reached the conversation, so it was left untouched pending the user's
    reference image next session (see "Where to pick up next").

    **Shared diagram-engine changes** (`app/pdf/diagrams.py`), all done directly and
    visually verified before any topic-level work: `_draw_scaled_axes` now prefers a
    true square unit grid (equal px-per-unit on both axes, like real squared exercise
    paper) whenever the tighter of the two per-axis scales still gives a legible
    unit-square size (>= `_MIN_SQUARE_UNIT_PX`), falling back to the old independent
    per-axis scaling only for genuinely lopsided ranges (e.g. a steep straight-line
    gradient, or `trig_graph`'s 360°-vs-±1 domain) - decided per-render from the
    actual data range, not hardcoded per topic, so e.g. `plot_straight_line` goes
    square for shallow gradients and gracefully falls back for steep ones.
    `draw_linear_graph_pair` (`simultaneous_graphically`) no longer marks the
    intersection with a dot/`"?"` label at all (the intersection point IS the
    answer the student must read off the graph) - each line's own label is now
    anchored a fixed 85%/10% fraction along its own line, with an `anchor` chosen so
    the label text always grows in the direction the line is moving away from (never
    back over the line, the other line, or either axis name label) - found via two
    real rendering iterations, not by inspection alone (a naive "extend past the
    endpoint" version collided with the axis-name label at the corner; a
    "midpoint + flat vertical offset" version had the text's trailing edge swing
    back over a descending line). `draw_function_graph` no longer draws `table_points`
    dots for `line_equation_from_graph` specifically (the two marked points on a
    "read the equation off this line" question shouldn't be pre-marked) - achieved by
    just not passing `table_points` for that one topic, not a diagram-kind change,
    since every *other* plotting topic's dots (showing the table of values the
    student computed) are correctly still shown. `draw_graph_transformation`'s
    generic `y = f(x)` curve is now a genuinely smooth 40-point sample of a real
    function (`_transform_base_fn`, `y = 0.5x^2 - 1.5` - confirmed algebraically to
    exactly reproduce the 7 originally hand-picked points) instead of a coarse
    7-point polyline. `turning_point_of_graph` no longer has a diagram at all (its
    parabola diagram was showing the vertex label as the literal answer coordinates
    anyway, so removing it was strictly simpler than fixing the leak). Two small new
    diagram kinds/params: `polygon_angles` (a `draw_triangle_angles` generalisation
    to n vertices, used for `forming_equations_higher`'s quadrilateral-angle branch)
    and `draw_l_shape`'s new optional `right_labels` param (splits the notch-adjacent
    edge into two independently labelled real segments instead of a single combined
    "(m + n) cm" label that read like unevaluated arithmetic - found and fixed via
    the same render-and-look-closely pass that built it).

    **`forming_equations_foundation`/`_higher`** (`app/topics/forming_equations.py`):
    per a scoped clarifying question, the "words" (think-of-a-number) branch stays
    text-only (nothing to draw); the angles branch (straight/point/triangle for
    Foundation, quadrilateral for Higher) now gets a real angle diagram via a new
    shared `_angle_fact_diagram` helper (`angle_line`/`triangle_angles`/
    `polygon_angles` depending on the fact), and the area/perimeter branch gets a
    `rectangle` diagram, in both cases trimming the prompt down to just state the
    total (e.g. "The perimeter of the rectangle shown is 32 cm...") since the side
    lengths are now on the diagram instead of repeated in prose. Higher's perimeter
    branch dropped the word "composite" entirely by becoming a real, correctly
    geometric L-shape (`_l_shape_perimeter_diagram`) - the bottom width is the
    algebraic `(x + k)`, and the notch height is deliberately set to exactly `m` so
    the right-hand edge is a real notch-divided segment labelled `n`/`m` rather than
    a fabricated "(m + n)" combined label. All 4 modelled-example counterparts got
    the identical treatment.

    **`kinematics_suvat`**: a new generic `TopicDefinition.preamble_lines` mechanism
    (threaded through `Worksheet.preamble_lines`, `render_worksheet`'s new
    `_preamble_box` helper, and `render_modelled_example`'s equivalent) shows all 3
    SUVAT equations in a boxed "Formulae" panel at the top of both the worksheet and
    the modelled-example PDF, before Q1 - reuses the exact same boxed styling as the
    modelled-example page's existing worked-calculation box for a consistent house
    style. This is genuinely new, reusable renderer plumbing (no prior topic had a
    fixed preamble), not a one-off special case - any future topic that wants the
    same "formulae shown once, up front" treatment just sets `preamble_lines` on its
    `TopicDefinition`.

    **Wording/behaviour tweaks** (each independently scoped, no shared mechanism):
    `substitution_foundation`/`changing_subject.py`/`classify_expressions.py` - the
    rectangle-length variable `l` (which reads as a capital `I`) is now `L`
    throughout all three files (their formulas/prompts/steps/final answers), leaving
    the unrelated slant-height `l` in the solids files untouched (genuine standard
    exam notation, not the same collision). `expand_double_brackets_foundation`/
    `expand_double_brackets` now say "Expand and simplify" (matching the sibling
    triple-bracket topic, which already did); a new `_rand_x_coeff` helper makes a
    bracket's own x-coefficient negative under 0.5% of the time instead of 50%
    (constants can still be either sign as before) for `expand_double_brackets`/
    `expand_triple_brackets`. `quadratic_inequalities`'s leading coefficient is now
    always `1` (never the "upside-down U" `-1` case). `inequalities_number_line_higher`'s
    "draw" prompt now reads "Draw the inequality/ies of ... on a number line."
    `sequences_nth_term`/`sequences_quadratic_nth_term` now put "Find an expression
    for the nth term." on its own line - via a new, generically-useful mechanism in
    `mathtext.py`: a literal `"\n"` in any generator's prompt/step text (which
    `_escape()` leaves untouched, unlike a hand-written `"<br/>"` which would get
    escaped into visible text) is converted to a real ReportLab `<br/>` at the very
    start of `to_markup`, available to any future topic that wants a forced line
    break. `special_sequences_foundation` no longer shows "(term number x)" alongside
    the ordinal ("Find the 6th term..." instead of "...(term number 6)").
    `special_sequences_higher`'s geometric branch no longer states "Each term is
    found by multiplying the previous term by a common ratio."

    **The fraction-line audit** ("id: algebraic_fractions_add_subtract - fraction
    line is a /, this must be checked on everything") turned out to be the largest
    single piece of this session. `mathtext.py`'s auto-detect regex only converts a
    standalone fraction to a real vinculum image when *both* numerator and
    denominator are bare unsigned digit sequences - anything else (an algebraic
    letter, brackets, a negative-signed denominator, a "?" placeholder, a surd
    coefficient > 1) silently renders as a flat, un-typeset slash instead, with no
    error or warning. Rather than fix just the one named topic, audited **every**
    `app/topics/*.py` file (3 parallel research-only agents, ~65 files/functions
    read, not just grepped) for genuine instances - explicitly excluding unit-rate
    "per" expressions (`km/h`, `£/kg`) and already-safe bare-digit fractions,  which
    correctly stay untouched. Found genuine instances in **12 files**: `fractions.py`,
    `powers_roots.py` (mostly `rationalise_denominator`), `algebraic_fractions.py`
    (systemic - every fraction in the file, including the final answer, was affected),
    `changing_subject.py` (systemic - every rearranged-formula answer), `substitution.py`
    (the acceleration shape), `sequences.py` (the triangular-number formula),
    `kinematics.py` (most of the algebraic SUVAT rearrangements - several with a
    denominator that can itself be negative, e.g. `(v-u)/a` when `a` is a
    deceleration, which the auto-detect regex can't handle even when both sides are
    otherwise plain digits), `quadratic_equations.py` (the surd-root final answer and
    substituted quadratic-formula steps), `functions.py` (the inverse-function
    shape), `iteration.py` (the quadratic/reciprocal formula shapes),
    `inequalities.py`/`inequalities_region.py` (a unit-fraction coefficient
    rendering as e.g. `"x/2"`), and `circle_equation.py` (gradient fractions with a
    possibly-negative denominator). Fixed via 7 parallel write-capable agents (one
    per cluster of unrelated files) plus 3 files done directly (`changing_subject.py`,
    `substitution.py`, `kinematics.py` - already mid-edit this session for the `l`→`L`
    and preamble work, so kept in-hand to avoid merge conflicts). Every fix follows
    the established `\frac{NUM}{DEN}` marker convention (already precedented by
    `\vec{a}`/`\vec{b}` and `\recur{}{}`), never touching the underlying
    verification/arithmetic - purely a display-string change.

    **Four real bugs were found and fixed via this session's own visual verification,
    not by any unit test** - the same story as most gotchas in this file:
    1. `exact_trig_values.py`'s `_fmt_exact` only special-cased a coefficient-1 surd
       over an integer (e.g. "√3/2", deliberately left flat per an existing
       documented gotcha) - a *computed* coefficient > 1 (e.g. `"5√3/2"`, reachable
       from `exact_trig_values_triangles`'s triangle-side generator, never from the
       base lookup table) fell through both the auto-detect and the flat-text
       special case untouched. Fixed with an explicit `\frac{}{}` branch for that
       specific case only, leaving the genuine coefficient-1 case exactly as before.
    2. `algebraic_indices_higher`'s multiply-fractional-exponents step built a
       compound exponent like `x^(1/2+3/2)` - individually-valid bare fractions, but
       joined by a "+" inside the same `^(...)`, which defeats `_MATH_RE`'s
       fractional-exponent alternative (it requires *exactly* `^(digits/digits)`)
       and falls through to the generic flat-raised-text compound-exponent case
       instead. Fixed by wrapping each half in its own `\frac{}{}` marker before
       joining with "+" inside the `^(...)` - confirmed via a real render that two
       correctly-scaled small vinculum fractions now sit side by side inside the
       superscript, not a flat "1/2+3/2".
    3. The single most significant finding: converting `rationalise_denominator`'s
       conjugate-branch steps to `\frac{}{}` (per the audit above) introduced a
       **new** visual bug the audit itself couldn't have caught, since it only
       exists once real PDF output is inspected - a step combining two wide,
       bracket-heavy fraction images on one line (`\frac{a}{denom} = \frac{a(conj)}
       {[(denom)(conj)]}`) rendered tall enough to visibly overlap the *previous*
       solution step's text line, because `SolutionStep`'s paragraph style
       (`leading=15, spaceAfter=2`) was tuned years earlier against simple
       plain-digit fractions (which happen to be almost exactly 15pt tall) and never
       revisited for a wide algebraic fraction (measured at 16.5pt+ for content
       involving brackets/surds). Root-caused via an isolated PIL bbox spike before
       touching any real code (confirmed `font.getbbox()` genuinely returns a taller
       box for bracket/surd-containing strings than for plain digits at the same
       font size) - a first fix attempt (make every fraction image the same height,
       based on the font's fixed ascent/descent metrics) was tried, rendered, and
       **rejected**: it fixed the wide case but made every simple fraction *taller*
       too, which broke previously-fine spacing across the whole document instead of
       just the outlier - reverted in favour of two smaller, lower-risk fixes: (a)
       splitting the one genuinely too-dense solution step into two separate steps
       in `powers_roots.py` (one fraction's image per line, not two), and (b) a
       modest `spaceAfter`/`spaceBefore` increase (2-6pt) to `SolutionStep`,
       `FinalAnswer`, `WorkedCalcLine`, and `ScaffoldGiven` in `app/pdf/styles.py` -
       general headroom for any inline fraction image slightly taller than a single
       text line, benefiting every topic that uses these styles, not just this one.
       Confirmed via a full re-render that the overlap is gone and page counts
       didn't measurably bloat.
    4. (Documented under "Compound-3D..." precedent, but worth restating here since
       it directly follows from finding #3): any *future* addition of a
       multi-fraction-per-line solution step should be rendered and visually checked
       before being considered done - the underlying image-height-vs-leading gap is
       now better cushioned, not eliminated, and a sufficiently dense line could
       still in principle re-trigger it.

    Central verification: full backend suite (862/862, unchanged count - this
    session was entirely rendering/wording/formatting fixes to existing topics, no
    new or retired topics), frontend suite (61/61, untouched - no frontend files
    changed), and the review-PDF script re-run to send a fresh comparison pair back
    to the user (296 question pages, unchanged; 302 answer pages, up from 299 -
    expected, since a few more topics' solutions now spill onto a second page as a
    direct, accepted consequence of the `SolutionStep` spacing increase in finding
    #3). The `iteration` item remains open, blocked on the user's reference image
    (see "Where to pick up next").

37. New session, resolving the single item step 36 left blocked: the user supplied the
    reference image (a "3 Minute Maths" slide showing `x_(n+1) = ∛(3 - x_n)` with a true
    subscript - no visible underscore or parentheses - for the recurrence notation). Fixed
    at the engine level in `app/pdf/mathtext.py`, not as a one-off patch to `iteration.py`'s
    strings, per this project's own "engine-level fix, not topic-local" convention: a new
    `_SUBSCRIPT_RE` matches `x_n`/`x_(n+1)`-style ASCII notation and converts it to a real
    `<sub>` tag (parentheses stripped, not shown), run BEFORE the italics pass so the bare
    letter inside is still italicised normally afterward. Confirmed via a full-codebase grep
    that no topic other than `iteration.py` ever emits this exact "x_" pattern as real
    rendered text (several dozen false-positive hits were all either Python variable names
    in source code or unrelated dict keys like `params["x_label"]`, never actual prompt/step
    string content) - so this is a zero-risk addition for every other topic.

    **Reintroducing `<sub>` revived the historical "comma glued to `</sub>`" ReportLab
    quirk** documented elsewhere in this file (previously marked resolved only in the sense
    that the codebase no longer emitted `<sub>` at all) - confirmed still present via a real
    rendered-PDF spike before shipping (iteration.py's own prompt text has exactly this
    shape: "x_1, x_2 and x_3"). A zero-width space was tried first and rejected the same way
    the `⁻¹`/`∕` gotchas were - Helvetica has no glyph for it, confirmed via a `font.getmask`
    spike showing it falls back to the exact same `.notdef` bbox as a deliberately-invalid
    codepoint. A thin space (U+2009, which Helvetica does have) fixes the glue with only a
    negligible visible gap - `_SUB_COMMA_RE` inserts it wherever `</sub>` is immediately
    followed by a comma.

    A second, narrower problem: two of the topic's three shapes (quadratic, reciprocal)
    embed a literal "x_n" *inside* a `\frac{}{}` marker's own numerator/denominator (e.g.
    quadratic's formula numerator "a - x_n^2") - this content is drawn as raw PIL text by
    `get_fraction_image` with no markup interpretation at all, so mathtext.py's new regex
    never sees it (it's already extracted into an opaque placeholder and rendered to an
    image before `_SUBSCRIPT_RE` would run). Fixed narrowly in
    `app/pdf/fraction_images.py`: a new `_XN_RE` matches ONLY the exact literal substring
    "x_n" (optionally with a trailing "^digits", so "x_n^2" composes correctly as a real
    subscript immediately followed by a real superscript, both attached to the same "x" -
    standard notation for "the square of the nth term"), and `_measure_run`/`_draw_run`
    manually walk the numerator/denominator left to right, drawing "x_n" as a real
    italic-font subscript instead of three literal characters. This is deliberately much
    narrower than a general "any `^digits` inside any fraction becomes a superscript" rule,
    which was considered and rejected - several *other* topics already use `\frac{}{}` for
    fractions containing a genuine unrelated "^" (`changing_subject.py`, `kinematics.py`,
    `quadratic_equations.py`, among the 12 files from step 36's fraction-line audit), and a
    blanket rule would have risked altering their already-correct, already-shipped
    rendering; matching only the literal "x_n" substring makes this a zero-risk addition for
    every one of those files. The subscript "n" (and the base "x") are drawn in the same
    Times Italic font `mathtext.py` uses for variables elsewhere, even though the
    surrounding fraction digits stay in plain Arial (an accepted, pre-existing simplification
    for `\frac{}{}` content generally - see mathtext.py's "Surd-over-integer gotcha" - and
    invisible at this size, since no other topic's fraction content contains a bare "x_n"
    for the font mismatch to affect).

    Separately, swapped the sqrt shape's literal word "sqrt(...)" for a real "√(...)" symbol
    in both `_formula_str` and `_subst_expr`, matching the rest of the app's convention
    (confirmed safe: since the radicand is algebraic, not bare digits, this renders as a
    plain literal "√" character per mathtext.py's already-documented behaviour for non-digit
    radicands, not a full vinculum-radical image - no new radical-engine work needed).

    All three shapes were rendered and visually inspected before considering this done (per
    this project's own "render and look closely" discipline) - including a native-resolution
    pixel check of the fraction-embedded subscript/superscript specifically, since an early
    screenshot at a small crop size made the denominator digits look mis-sized purely from
    image-scaling interpolation, not a real bug (re-confirmed correct once measured/viewed at
    native resolution). `trial_and_improvement` (this topic's sibling, which never uses "x_"
    notation) was re-rendered too, to confirm it's genuinely unaffected. Backend suite grew
    from 862 to 873 tests (6 new subscript tests in `test_mathtext.py`, 4 new `\frac{}{}`
    "x_n" tests in `test_fraction_images.py`, 1 new test in `test_iteration.py` confirming
    the sqrt-symbol swap); frontend unaffected (61/61 - this session touched only backend
    PDF rendering). No topic count change (still 296). The review PDFs were regenerated
    (still 296/302 pages, as expected with no topic count change) and sent back to the user.

38. New session, a batch of Ratio & Proportion review feedback (6 named items:
    `best_buys`, `ratio_find_missing_share`/`ratio_difference`/`ratio_difference_higher`,
    `ratio_1_to_n`, `ratio_shape_similar_foundation`/`_higher`, `direct_proportion`).
    Asked clarifying questions up front via `AskUserQuestion` on the genuinely ambiguous
    items before touching code: whether `ratio_difference`'s restyle should switch to
    giving one share's value directly (matching the user's literal example) or keep
    giving the difference with just terser wording (chosen: **keep the difference**,
    since that's what makes the topic distinct from `ratio_find_missing_share` -
    otherwise the two topics would test near-identical content); what shape/orientation
    the new similar-shapes diagram should use (chosen: **two rectangles, same
    orientation** - simplest, since a rectangle's own width/height already disambiguate
    corresponding sides without needing rotation); and whether the best_buys g→kg
    scope should extend to `direct_proportion`'s recipe template, which was found via
    the "check for the same pattern elsewhere" pass to have the exact same issue
    (chosen: **yes**, plus ml→L too, for symmetry).

    **best_buys / direct_proportion g→kg, ml→L conversion**: new
    `app/topics/units.py` (`display_qty`/`needs_larger_unit`) - a raw base-unit amount
    (grams, millilitres) displays in the larger unit (kg, litres) once it reaches 1000,
    e.g. `display_qty(1200, "g")` → `"1.2kg"`. Fixed-point formatting only
    (`format(Decimal, "f")`, never a bare `Decimal` `.normalize()`/`str()`) - confirmed
    via a real spike that the same "3E+1"-style scientific-notation bug documented for
    `estimation_rounding` (chronology step 22) reproduces here too for a qty that
    normalizes to a round number, even though no current caller's range actually reaches
    it. Wired into `best_buys.py` (pack-size mentions in the prompt/option-list/final
    answer) and `proportion.py`'s `direct_proportion` recipe template (`display_qty`
    used for prompt/final-answer "narration", while the actual division/multiplication
    steps still work in raw grams throughout) - both add an explicit
    `"1.2kg = 1200g"`-style conversion clause wherever the two forms differ, so no step
    ever jumps from a kg-displayed number straight into a gram-based division with no
    explanation. `direct_proportion`'s other three templates (shopping, map, currency)
    never reach this threshold, so are unaffected.

    **`ratio_find_missing_share`/`ratio_difference`/`ratio_difference_higher` restyled
    to a letter-equation format** (e.g. "a : b = 1 : 7. a = 10. What is the value of
    b?"), replacing the old "Two amounts are in the ratio..." prose framing. New
    `_LETTER_PAIRS`/`_LETTER_TRIPLES` pools (`ratio.py`) vary which letters are used per
    question - **deliberately excludes "x" and "n"**, the only two letters
    `mathtext.py`'s engine italicises by default, since pairing an italicised letter
    with a plain one in the same ratio (e.g. "x : y") looks like a rendering
    inconsistency even though each letter's styling is individually correct - found via
    an actual render during this session, not assumed up front. `ratio_find_missing_share`
    now always asks for the other letter's value directly (the old "or find the total"
    branch was dropped, matching the user's literal example - it had no total-asking
    variant); `ratio_difference`/`_higher` **keep** giving the difference (per the
    clarifying-question answer above) and keep their existing "or also ask for the
    total" branch, just restyled with letters (e.g. "a : b = 3 : 5. b - a = 12. Find a
    and b, and their total.") - the bigger/smaller letter in the difference clause is
    picked from the actual generated values (`bigger_letter, smaller_letter = (l1, l2)
    if a > b else (l2, l1)`), not hardcoded, so it's always stated as a true positive
    quantity.

    **`ratio_1_to_n`'s "n" is no longer italicised** - a genuine gap in `mathtext.py`'s
    "x/n are always italic" convention, since here "n" is a plain ratio-form
    placeholder ("1:n"), not an algebraic variable, and real exam convention leaves it
    upright. Rather than special-case this one topic, added a new general engine
    capability: **`\plain{X}` opts a bare letter OUT of the automatic italics** - the
    third explicit ASCII sentinel marker in `mathtext.py` (alongside `\frac{}{}`/
    `\recur{}{}`), extracted into the same placeholder mechanism *before* the italics
    pass runs, then spliced back as fully bare/literal content afterward (opting out of
    every later pass, not just italics, since there's nothing else in `ratio_1_to_n`'s
    content that would need markup applied to a bare "n" anyway). Every literal "n" in
    `ratio_1_to_n`'s prompt/steps/worked_calculation/teaching_steps was audited and
    converted to `\plain{n}` - confirmed via a real render that "n" now sits upright
    everywhere it appears, prompt through modelled example.

    **`ratio_shape_similar_foundation`/`_higher` restyled with a new diagram**, moving
    the numeric side-length data out of the prompt text (which now just states "Shape A
    and Shape B are similar. Find the length of side x." for Foundation, or "...The
    area of shape B is 360 cm². Find the area of shape A." for Higher, unchanged from
    the user's example) and into a new `two_similar_rectangles` diagram kind
    (`app/pdf/diagrams.py`) - two separate, non-overlapping rectangles ("Shape A"/
    "Shape B"), same orientation (so correspondence is just "width↔width, height↔
    height", no rotation needed), explicitly **NOT drawn to true relative scale**
    (`_not_to_scale`) since one side is often the very unknown the student must find -
    drawing it at its real proportion would let a careful ruler-measurement leak the
    answer, the same reasoning this app already applies to schematic triangles/circles
    elsewhere. All four side labels are optional (`params.get(...)`, no KeyError if
    omitted) since the Higher (area/volume) version only ever states ONE corresponding
    length pair (the area/volume itself, not a second length, is what's given/asked
    for) - Foundation passes all four (two full dimensions per shape, one of which is
    the unknown letter), Higher passes only the two width labels. New
    `_UNKNOWN_LETTERS = ["x", "y", "z"]` pool varies the Foundation topic's unknown-side
    letter per question, matching the user's "(letters can be changed)" note. **A real
    bug was found and fixed via this diagram's own first spike render**, before any
    topic code was wired up (this project's established "verify the riskiest piece
    first" precedent): the initial layout gave Shape B's height label too little
    clearance from the canvas's right edge, so a two-digit label like "45 cm" clipped
    off completely - fixed by narrowing both rectangles slightly and shifting Shape B
    left, re-confirmed clean across several longer-label test cases before wiring it
    into the real topics.

    **`direct_proportion` wording**: every one of its 4 templates (shopping, recipe,
    map, currency) now opens with "If ..." (e.g. "If 8 pencils cost £21.68, how much
    would 15 pencils cost?"), restructuring what used to be two separate sentences into
    one conditional clause. The currency template's `amount_noun` ("value in dollars")
    and its prompt's own "in dollars" mention both gained a parenthetical "($)"
    immediately after the bare word "dollars" - the one place in this file a currency
    is ever named by word without its symbol sitting right next to a figure - so every
    teaching-step sentence built from `amount_noun` picks up the clarification
    automatically, with no separate per-sentence edit needed.

    Central verification: full backend suite (873→892 tests - `test_units.py` (new),
    plus new tests in `test_ratio.py`, `test_diagrams.py`, `test_best_buys.py`,
    `test_proportion.py`, and 3 new `\plain{}` tests in `test_mathtext.py`); frontend
    unaffected (61/61 - no frontend files touched). No topic count change (still 296 -
    this was entirely rendering/wording/diagram fixes to existing topics). Every
    changed topic was rendered and visually inspected (worksheet, worked solutions, and
    modelled-example pages) before considering it done, plus a live browser
    click-through (both similar-shapes topics generated a real worksheet/modelled
    example, 200 OK, no console errors). The review PDFs were regenerated (296
    question pages, unchanged; 303 answer pages, up from 302 - expected, since the two
    similar-shapes topics' worked solutions now include a diagram) and sent back to the
    user.

39. New session, a large Geometry review-feedback batch (~35 named items across
    diagrams/wording/behaviour, plus several items explicitly marked "change
    throughout" meaning all 296 topics, not just Geometry) — by far the largest
    single batch since step 34's review process began, comparable in scope to the
    biggest past multi-session phases (steps 23-27, 31, 32, 36). Two items were
    ambiguous enough to need clarification up front (resolved via `AskUserQuestion`):
    the rounding-instruction change is a **real behavioural change** (each applicable
    question randomly picks 1 dp/2 dp/3 sig figs and the actual answer is rounded to
    that precision, not just a wording swap), and `congruent_triangle_proof_foundation`
    redesigns to a lettered multiple-choice format. Per the user's explicit choice,
    the batch was split into 6 phases (cross-cutting engine work first, then named
    topic fixes grouped by area) and planned via `EnterPlanMode`, with the full plan
    (including exact file/function/line references from research) written to
    `C:\Users\James\.claude\plans\adaptive-coalescing-gosling.md` — kept as the
    authoritative, continuously-updated tracker across sessions rather than
    duplicated in full here (see "Where to pick up next" above). **This session
    completed Phases 1-3**; Phases 4-6 are picked up in a future session.

    **Phase 1 (cross-cutting diagram/engine fixes, all in `app/pdf/diagrams.py`
    unless noted)**: larger angle-label font size app-wide; `_not_to_scale`
    neutered to a no-op so "Diagram NOT accurately drawn" no longer renders anywhere
    (kept as a real function, not deleted, for easy re-enabling); double-chevron
    arrow marks added to `draw_parallel_lines`; `_north_arrow`'s length constant
    increased (fixes both bearings topics via the one shared default);
    `draw_sector` reworked (dropped the dashed full-circle outline, enlarged the
    sector, added a real angle arc); `draw_trapezium`'s label-overlap fixed;
    `draw_cuboid` gained an `is_cube` flag (square front face, wired into
    `volume_surface_area_cube`) and a `vertex_labels` param (A-H lettering, wired
    into `pythagoras_3d`/`trig_3d`); `draw_vector_triangle` gained direction
    arrowheads; formula preamble boxes (reusing the `TopicDefinition.preamble_lines`
    mechanism from `kinematics_suvat`, step 36) added to the 6 cone/sphere/pyramid/
    frustum/compound-3D topics; "right-angled triangle" wording removed from
    `trigonometry.py`/`exact_trig_values.py` prompts where the diagram already shows
    the right-angle marker; Pythagoras topics switched to a consistent "find x"
    convention (diagram unknown label + prompt both say "x" instead of "?"/
    descriptive wording) and "legs" renamed to "sides" throughout `pythagoras.py`/
    `solids_prisms.py`/`congruent_triangle_proof.py`.

    Rendering during this phase's own checkpoint found and fixed 4 real bugs, none
    caught by unit tests: (1) `draw_sector`'s new angle arc used `_angle_arc`, which
    always takes the shortest of the two possible sweeps between two rays - wrong
    for a sector, whose own angle is routinely reflex (>180°), drawing the
    complementary arc outside the wedge instead; fixed with a direct `ArcPath.addArc`
    matching the wedge's own sweep. (2) The same rework's narrow-angle labels (<40°)
    collided with the sector's own radius label, which always anchors near the same
    "top" ray tip the bisector approaches for a narrow angle; fixed by placing a
    narrow angle's label *behind* the vertex (opposite the wedge's own opening
    direction) instead of along the bisector. (3) `draw_trig_triangle`'s angle label
    used a fixed `(dx, dy)` offset from vertex B that, for some adjacent/opposite
    ratios, landed close enough to the hypotenuse to visibly overlap it (this is the
    exact "overlap on angle size and shape" bug the user flagged for
    `trig_missing_side_foundation`, which shares this diagram kind, and it also
    fixed `sine_rule`/`cosine_rule`/`triangle_area`/`exact_trig_values_triangles`
    for free via the shared `draw_general_triangle`/`draw_trig_triangle` functions)
    - fixed with a centroid-direction push (same fix pattern already established for
    `draw_general_triangle`'s own angle labels). (4) The new cuboid diagonal label
    (`"?"`) sat at the exact midpoint of the diagonal, which - once vertex letters
    were added - put it right on top of vertex D (a hidden-vertex dashed-edge
    cluster); fixed by moving the label 60% of the way along the diagonal instead
    of 50%.

    **Phase 2 (rounding-precision randomization engine)**: confirmed via a fresh
    grep that the "always 3 significant figures" pattern was **not centralized** -
    ~50+ hand-written occurrences across 11 files, no shared helper. Built
    `app/topics/rounding.py` (a `pick_rounding(rng) -> RoundingSpec` returning one
    of "1 decimal place"/"2 decimal places"/"3 significant figures" plus a
    Decimal-based `round_fn` that avoids the scientific-notation display bug already
    documented elsewhere in this file), proved the pattern directly on
    `trigonometry.py` and `area_perimeter.py` (two different existing verification
    styles), then rolled out to the remaining 7 files via 3 parallel background
    agents (`solids_curved_compound.py` alone; `solids_cylinders_cones.py` +
    `solids_3d_trig.py`; `bearings.py` + `substitution.py` + `triangle_rules.py`),
    each given the exact proven pattern and told to decouple display rounding from
    verification (compare full-precision values via two computation paths, never an
    already-rounded one) rather than just swapping the display text. Deliberately
    left untouched: angle answers (always 1 d.p. by real exam convention, never
    swappable to significant figures), the standard-form mantissa's own "round to 3
    s.f." convention (part of standard form's own notation, not a final-answer
    instruction), and the `rounding_to_significant_figures` topic itself (teaches
    the skill, wording changes would undermine it). One agent found and flagged
    (rather than fixed, correctly out of its assigned scope) a real pre-existing
    bug: `mathtext.py`'s radical regex only matched bare-integer radicands, so an
    intermediate 4-s.f. decimal like `bearings.py`'s `ac_sq_str` (e.g. "205.1")
    rendered with only "205" under the radical bar and ".1" stranded as plain text
    right after it - fixed directly in this session by extending the regex to
    `√(?P<radn>\d+(?:\.\d+)?)`, confirmed via a real rendered PDF (`√591.1` now
    fully covered) and a new regression test.

    **Phase 3 (Area & Perimeter topics)**: stripped restated prose from every area
    topic whose diagram already carries the needed measurement(s) -
    `area_rectangle`, `area_triangle` (no redesign, per the confirmed clarifying
    answer - just render-verified for overlap), `area_composite_rectangles`,
    `area_parallelogram`, `area_trapezium`, `area_circle`/`_foundation`,
    `arc_length`/`_foundation`, `area_sector`/`_foundation` - e.g. "A rectangle has
    length X cm and width Y cm. Find its area." became "Find the area of the
    following rectangle." `area_subtract_compound`/`_foundation` redesigned: a new
    `shade_frame` mode on `draw_l_shape` (fill-then-erase, the same trick already
    used by `draw_mixed_compound`'s quarter-circle cut and `draw_venn_diagram`'s
    "neither" region) shades the remaining region, with exactly 2 real edge labels
    per shape (outer rectangle + inner hole) replacing the old 4-outer-label-plus-
    combined-caption style; prompts reworded to "Find the shaded area."
    `area_mixed_compound` fully reworked from one fixed rectangle+triangle+
    quarter-circle-cut shape into a genuine 3-piece composite: a rectangle body with
    a randomly chosen top piece (triangular roof or semicircular dome) and cut piece
    (quarter-circle corner cut or semicircular edge notch) - 4 real combinations,
    each independently verified (full-precision cross-check via a second π source,
    same discipline as every other topic in this file) and wired into the new Phase
    2 rounding engine.

    Rendering found and fixed 3 more real bugs in this phase: (1) a narrow inner
    hole (small `ih_s`) made the new shaded L-shape's 2 stacked inner labels cross
    the hole's own top/bottom edges - fixed with an adaptive layout (side-by-side
    instead of stacked, smaller font, when the hole is too short to stack). (2) The
    plain `draw_circle`'s radius label sat directly on the radius line itself (a
    pre-existing bug, only now consequential since the label is often the *only*
    place the radius appears once the prose was stripped) - fixed with more vertical
    clearance. (3) The new `draw_mixed_compound`'s own labels needed two rounds of
    fixing: the triangular-roof label used a fixed offset that crossed the sloped
    roof edge for a shallow/wide roof (fixed with a proper outward-perpendicular-
    from-the-edge offset, the same technique already used for `draw_trig_triangle`'s
    hypotenuse label this session), and the semicircular-dome label's fixed offset
    crossed the dome's own arc for a large-radius dome even after an initial "move
    it lower" attempt didn't fully solve it - the robust fix was moving the label
    entirely outside the dome, into the always-clear canvas margin above the apex,
    rather than trying to find a horizontal offset that works for every dome size.
    Also fixed, matching the exact overlap the user originally flagged for
    `area_triangle`: `draw_triangle_area`'s height label used a fixed offset from
    the dashed height line that crossed the triangle's own sloped right edge for a
    narrow/tall triangle (computed algebraically that for a sufficiently narrow
    triangle there is *no* position along that edge with enough horizontal
    clearance) - fixed by moving the label entirely outside the triangle, to the
    right of its widest point, matching the same "guaranteed clear space" principle
    used for the dome fix.

    This phase's changes also surfaced two real regressions, both found and fixed
    via the full test suite rather than visual inspection: `bell_tasks`' own
    "5 distinct questions across the week" test assumed prompt text alone proves two
    questions differ, which broke once `area_rectangle`'s prompt stopped repeating
    its numbers (two different rectangles can now share the identical prompt text,
    distinguished only by their diagram) - fixed by teaching the test to also
    compare each box's embedded diagram image bytes (matched to its box via
    position, since `diagram_rect` always places a box's picture within that box's
    own cell bounds), not just text - a fix that will keep working as more topics
    get the same prose-stripping treatment in future phases. Separately,
    `area_mixed_compound`'s diagram param shape change (`top_kind`/`cut_kind` now
    required, where the old shape had neither) made the frozen Practice Test JSON's
    saved diagrams for that topic unrenderable - fixed by regenerating all 60 papers
    via `python -m app.practice_tests.build` (confirmed still exactly 100 marks each
    afterward).

    **Phase 4 (Angles, Pythagoras, Trigonometry)**: re-reading the plan file's Phase 4
    section (continued in a later session) confirmed 6 of its 7 items were already
    completed as a side effect of Phase 1's own diagram-engine work (the "find x"
    Pythagoras convention, legs→sides rename, cuboid vertex letters, trig-triangle
    label fix, right-angled-triangle wording removal — all done in the same pass as
    the shared engine changes, since the files were already open). Only
    `angles_polygon_interior_foundation` (`app/topics/angles.py`) was genuine unstarted
    work: its `interior_sum` branch (asking for the *whole shape's* angle total) now
    has no diagram at all - a marked angle adds nothing to a question about the sum -
    while its `interior_angle` and `exterior_angle` branches keep a diagram, per the
    original feedback's "sum vs one interior angle" distinction. Implementing this
    surfaced a real pre-existing bug, not caught until this item was actually built:
    `draw_polygon` (`app/pdf/diagrams.py`) always marked an *interior* angle with "?"
    regardless of which angle the question asked about, so the `exterior_angle`
    branch's diagram was silently showing the wrong angle - fixed with a new
    `"mode": "exterior"` option that extends one polygon side past its vertex and arcs
    the angle between that extension and the next side, mirroring
    `draw_exterior_triangle`'s existing extend-a-side technique exactly. Both the
    generator and its modelled-example twin were updated together;
    `test_angles.py`'s two "every generator/modelled-example attaches a diagram" tests
    were adjusted to allow `None` for this one topic's `interior_sum` branch, plus a
    new dedicated test confirms all 3 measure branches get the exactly-right diagram
    treatment across 200 trials. Rendered and visually confirmed both fixes (the
    exterior-angle wedge is correctly marked outside the extended side; the sum
    question has no diagram at all).

    Central verification after each phase: full backend suite grew from 892 to 913
    across the 4 phases (Phase 1 added no new tests - pure diagram/wording work, no
    new tests needed beyond updating a couple of existing assertions in
    `test_pythagoras.py`; Phase 2 added the new `test_rounding.py` plus a
    rounding-variety test per touched file; Phase 3 added mixed-compound variety/
    combination coverage; Phase 4 added 1 new test in `test_angles.py`), frontend
    unaffected throughout (61/61 - no frontend files touched this session). No topic
    count change (296, unchanged - this batch is entirely rendering/wording/diagram/
    verification-precision fixes to existing topics). Every changed topic was
    rendered and visually inspected before considering its phase done, and the
    review PDFs (`generate_review_pdfs.py`) were regenerated and sent back to the
    user after each phase, not just at the end.

    **Phase 5 (Vectors, Congruence, Circle Theorems, Nets, Plans & Elevations,
    Cube)**, continued in a later session: re-reading the plan file's Phase 5
    section confirmed items 3 (`geometric_vectors` arrowheads) and 8
    (`volume_surface_area_cube`'s `is_cube` flag) were already done in Phase 1 -
    the remaining 6 items were built this session.

    `vectors_arithmetic_foundation`/`_higher`'s `_fmt_vector` rendered a plain
    `(x, y)` coordinate pair - real GCSE convention is a column vector, two
    stacked numbers inside a single tall bracket. Built new
    `app/pdf/vector_images.py` (mirrors `fraction_images.py`'s PIL/cache/tempdir
    architecture exactly) and a new `\colvec{TOP}{BOTTOM}` mathtext marker.
    The brackets themselves are real `"("`/`")"` glyphs from the same TrueType
    font, scaled to a point size whose own ink height spans the two stacked
    rows - not hand-drawn curves, since a font glyph already has the right
    shape at any size. **A real design problem was caught via a rendered-PDF
    spike before wiring this in anywhere** (this project's own "verify the
    riskiest piece first" precedent): a first version drew the two rows at
    full text size, making the whole image roughly 2 line-heights tall, which
    visibly collided with the line below wherever it appeared inline (the
    same class of issue as step 36's wide-fraction-image overlap finding) -
    fixed by shrinking the rows (mirroring fraction images' own digit-shrink
    precedent) so the total height stays close enough to one line's normal
    leading that no paragraph-style spacing changes were needed anywhere it's
    used. Separately, `vectors_arithmetic_higher`'s expression builder could
    print a literal double sign, `"2a - -4b"`, whenever the second scalar was
    itself negative - fixed with a new `_join_vector_terms` helper that
    parenthesises it (`"2a - (-4b)"`), matching the plan's exact scope (only
    when `op == "-"` and the second scalar is negative; the `op == "+"` case,
    e.g. `"3a + -2b"`, was deliberately left as-is).

    `circle_theorems`'s prompt-trimming item turned out narrower than
    originally scoped once the actual diagrams were checked: none of the 6
    shape kinds (`draw_circle_angle_centre`, `_semicircle`, `_cyclic_quad`,
    `_two_tangents`, `_same_segment`, `_alternate_segment`) label any point at
    all - only angle *values* are drawn - so almost every "A, B, C are points
    on a circle where..." sentence is the *only* place a point's identity is
    established, not redundant restating of something the diagram already
    shows. Trimmed only the two clauses that genuinely were pure restating:
    `_cyclic_quadrilateral`'s "(all four vertices lie on a circle)"
    parenthetical (the diagram already visibly shows exactly that), and
    `_alternate_segment`'s "...the tangent to the circle at P **is shown**"
    (a clear diagram-narrating tell, tightened to "with a tangent at P").

    `congruent_triangle_proof_foundation` redesigned to a shuffled lettered
    multiple-choice prompt (`A) SSS  B) SAS  C) ASA  D) RHS`, order randomised
    per question via a new `_shuffled_mc_options` helper reused by both the
    generator and its modelled example), `final_answer` now e.g. `"C) ASA"` -
    matching the practice-test mark scheme's existing `^[A-D]\)` convention
    for a multiple-choice-style answer (a single independent B1 mark there,
    should this topic ever be frozen into a paper).

    `nets_3d_shapes`'s diagram no longer appears on the question page - all 3
    prompt variants (`describe`/`what 2D shapes`/`how many X`) ask the student
    to reason from the solid's name alone, per the user's literal instruction -
    moved from `diagram` to `solution_diagram` so the net is still revealed as
    the answer, matching this app's established blank-question/completed-
    solution split. The modelled-example twin is unaffected (`ModelledExample`
    has only one `diagram` field, and its page always shows the full solved
    answer regardless).

    `plans_and_elevations`: dimensions capped at 8 via a new, topic-local
    `_PLANS_TRIANGLE_TRIPLES`/`_plans_triangular_prism_dims` - deliberately
    NOT touching `solids_prisms.py`'s shared `_triangular_prism_values`, which
    legitimately goes larger for its own volume/surface-area topic and must
    stay untouched. The question page previously showed only the oblique 3D
    sketch, with the actual plans/elevations appearing solely on the solution
    page; added a blank squared grid for the student to sketch into, via two
    new diagram pieces - `draw_plans_and_elevations_blank` (3 empty ruled
    boxes, fixed equal size regardless of the real solid's proportions, so the
    blank grid itself never leaks shape/proportion information) and
    `draw_plans_and_elevations_question` (stacks the existing oblique solid
    sketch above the blank grid into one composed Drawing, since a `Question`
    only carries a single question-page diagram slot) - registered as a new
    `"plans_and_elevations_question"` diagram kind used only for this topic's
    question-page `diagram`; the solution page's existing `"plans_and_
    elevations"` kind is unchanged. The composition technique itself (nesting
    one already-built `Drawing` inside another via a translated child, `outer.
    add(inner); inner.transform = (1, 0, 0, 1, dx, dy)`) was spiked and
    confirmed working in total isolation before being relied on anywhere -
    ReportLab's `Drawing` is itself a `Group` subclass, so this "just works"
    with no special-casing needed, a genuinely new technique for this
    codebase (no prior diagram had needed to embed one whole existing Drawing
    inside another).

    **A real, pre-existing bug was found and fixed via this session's own
    visual verification, not by any unit test** - the same story as most
    gotchas in this file: `draw_plans_and_elevations`'s "Front elevation"/
    "Side elevation" captions are centred over their own box, but a small
    solid shrinks both boxes (and the gap between them) while the caption
    text itself stays a fixed width - for a small enough solid the two
    captions ran together with zero gap at all ("Front elevationSide
    elevation"), only actually noticed once a modelled-example page (which
    renders this diagram smaller than the worksheet solution page does) was
    rendered and read closely. This was latent since the diagram kind was
    first built (step 31) - unrelated to this session's own 8-cap change,
    which if anything made solids on average *larger* relative to the
    diagram's fixed target cell size, not smaller. Fixed by measuring the two
    captions' own text width (`stringWidth`) and widening the gap between the
    front/side boxes whenever they would otherwise overlap - confirmed via a
    zoomed rendered-PDF comparison before/after, plus a new direct regression
    test in `test_diagrams.py` that reads the actual `String` elements'
    positions out of the rendered `Drawing` and asserts the two captions'
    real pixel extents don't overlap (not just a proxy check).

    Backend suite grew from 913 to 930 tests (new `test_vector_images.py`,
    plus extensions to `test_mathtext.py`, `test_vectors.py`,
    `test_congruent_triangle_proof.py`, `test_solids_properties.py`,
    `test_plans_elevations.py`, `test_diagrams.py`); frontend unaffected
    (61/61 - no frontend files touched this session). No topic count change
    (still 296 - this phase, like the others in this batch, is entirely
    rendering/wording/diagram/behaviour fixes to existing topics). Every
    changed topic was rendered and visually inspected before considering its
    item done, and the review PDFs were regenerated (296 question pages,
    unchanged; 303 answer pages, unchanged from step 38) and sent back to the
    user at the end of the phase.

    **Phase 6 (Transformations & Bearings)** - the final phase of this whole
    batch, continued in a later session: item 4 (`bearings_foundation`'s
    longer north arrow) was already done in Phase 1; the remaining 3 items
    were built this session.

    `transform_reflect_complete`/`_describe` (both Foundation-only) had their
    mirror-line pool reweighted: vertical/horizontal (the easiest reflections)
    dominate, `"y = x"` is occasional, and `"y = -x"` (genuinely the hardest -
    neither coordinate keeps its sign) is excluded entirely at Foundation, via
    a new per-tier `_MIRROR_KIND_WEIGHTS` dict threaded through
    `_random_mirror_line`/`_random_reflect_instance`. **Threading `tier`
    through surfaced a real, genuinely pre-existing bug, found via property-
    based sampling (not visual inspection this time) rather than trusting the
    reweighting alone**: every one of the 4 shared `_SHAPE_TEMPLATES` spans
    7-9 units in the y - x direction, which made a `"y = x"` reflection
    geometrically impossible to ever satisfy within the grid's own +/-7 fit
    range, no matter how the shape was positioned or how the mirror line's
    offset was chosen - confirmed via direct simulation (0 successes in
    200,000 attempts) that this was already true in the code exactly as it
    stood before this session, not something the reweighting introduced (only
    `"y = -x"` had ever actually been reachable, since those templates happen
    to be far more compact in the y + x direction). Fixed with a new small
    compact triangle template (`_COMPACT_REFLECT_TEMPLATE`, `((0,0),(3,0),
    (0,2))`), deliberately used ONLY by a new `_random_reflect_shape` (kept
    separate from the shared `_random_shape` used by rotate/translate/
    enlarge, so those three topics are completely unaffected) - confirmed via
    the same direct-simulation approach that `"y = x"` now succeeds at a
    realistic rate (~1.6% of draws) comfortably within the existing
    4000-attempt reroll budget, then confirmed again via a real rendered PDF.

    `transform_translate_complete`'s diagram no longer draws a direction arrow
    for the translation vector (dropped `translation_vector`/`vector_label`
    from both the question and solution `DiagramSpec` params) - the vector is
    still stated in the prompt/solution text exactly as before, just not
    visualised with an arrow. `transform_translate_describe` was reworded to
    refer to generic "shape A"/"shape B" rather than per-vertex `ABC`/`A'B'C'`
    names, with both diagrams now passed an all-empty label list per vertex -
    confirmed (rather than assumed) that `draw_grid_transformation`'s existing
    "empty label = no text drawn, dot only" behaviour renders correctly with
    zero `diagrams.py` changes needed, exactly as a prior session's research
    had anticipated.

    Central verification: full backend suite grew from 930 to 935 tests (new
    tests in `test_transformations.py` covering the tier-weighted mirror pool,
    the compact-triangle fix, and the no-arrow/no-label diagram changes);
    frontend unaffected (61/61). No topic count change (still 296). Every
    changed topic was rendered and visually inspected, and the review PDFs
    were regenerated (296 question pages, unchanged; 304 answer pages, up by
    one from step 38's 303) and sent back to the user.

    **This closed out the entire 6-phase Geometry review-feedback batch** -
    every phase in the plan file is now done, committed, and pushed.

40. New session, two more review-feedback batches - Probability and Statistics -
    completing the full first-pass review cycle across all 6 curriculum sections
    (Number: step 35; Algebra: steps 36-37; Ratio & Proportion: step 38; Geometry:
    step 39; Probability + Statistics: this step). Both batches were scoped via
    `AskUserQuestion` clarifying rounds up front (matching this project's established
    pattern), then implemented directly session-long rather than via parallel
    subagents, given how much of both batches was genuinely cross-cutting diagram-
    engine work touching many topic files at once.

    **Probability batch** (~10 named items): `draw_bag` reworked from a rounded
    "pouch" shape to a plain rectangle, with counters interleaved round-robin across
    colours (not grouped into blocks) and auto-sized/gridded to fill the available
    space regardless of count - and the old "Target colour: X" caption text removed
    entirely (used by `probability_single_event`/`_complement`/`_and_or_rule`'s OR
    branch). `probability_combined_dice` dropped its unrelated decorative dice
    diagram. `probability_conditional` swapped its bag diagram for a tree diagram -
    blank (branch structure and labels only) on the question page, fully solved on
    the solution page - reusing a genuinely overhauled `draw_tree_diagram`: much
    larger and better-spaced (the old version's branch/probability labels collided
    as soon as a tree had more than a couple of branches, the concrete complaint
    that started this item), with new optional column headers and a blank-
    probability placeholder (a short underscore instead of a fraction) for exactly
    this "student fills it in" case. Two new diagram kinds, `draw_coin` (a circle
    split H/T, matching how `draw_spinner` already shows every sector at once
    rather than one outcome) and `draw_event_pair` (composes two single-object
    diagrams side by side via the same nested-translated-Drawing technique
    `draw_plans_and_elevations_question` established) - wired into
    `probability_listing_outcomes`'s two previously-undiagrammed scenarios (coin+
    die, two coins) and into `probability_and_or_rule`'s AND branch, which
    previously only ever illustrated ONE of its two events (a `kind_a=="die" or
    kind_b=="die": ... elif ... else: diagram=None` priority chain - the `else`
    branch turned out to be dead code, since the two events can never both be
    "coin" given how `_independent_event`'s `exclude_kind` works, but the AND
    branch still only ever showed one object, never both) - now every
    `and_or_rule` question shows both events. `draw_venn_diagram`'s A/B set-name
    labels moved from inside the circles to just above them, still inside the
    bounding rectangle. `set_notation`/`_foundation` gained a genuinely new
    fillable Venn diagram (blank on the question page, all four regions filled
    with their real elements on the solution page) - previously these two topics
    had no diagram at all, unlike their `venn_diagrams.py` siblings. `two_way_
    tables` now leaves its missing cells genuinely blank (not "?") and always has
    exactly 2 of them (solved via whichever margin - row or column total - has
    only one unknown in it, always resolvable for any 2 cells chosen from a 2x2
    grid), with the prompt trimmed to "Find the missing values." `sample_space_
    diagrams`' question-page grid is now blank except the given axis numbers,
    with a genuinely new `solution_diagram` showing the completed, highlighted
    grid - fixing a real pre-existing bug (found by an Explore agent's research
    pass, not assumed) where the full answer was shown on the question page with
    no solution diagram at all.

    **Statistics batch** (~15 named items) - the larger of the two, requiring
    several genuinely new shared `_draw_stats_axes` capabilities used across five
    diagram kinds at once. A new `_cross_marker` helper (two crossing `Line`s)
    replaces every filled-dot plotted-point marker app-wide - not just
    Statistics's `draw_scatter_graph`/`draw_cumulative_frequency`/
    `draw_time_series`, but also the Algebra Plotting-Graphs group's `draw_
    function_graph`'s `table_points` and `draw_piecewise_graph` (confirmed via a
    full-file grep this was every genuine plotted-data-point `Circle(` call in
    `diagrams.py`, as opposed to a geometry vertex/centre dot or a decorative one,
    which were all left alone). A new `_draw_square_grid`/`_grid_minor_step`
    capability in `_draw_stats_axes` (`square_grid=True`) draws a light squared-
    paper background whose square size is derived from each axis's own "nice"
    tick step (e.g. a step of 10 gives squares worth 5, not an arbitrary always-1
    unit) - applied to `draw_bar_chart`, `draw_box_plot` (which needed its dummy
    `plot_h=1` replaced with the real canvas height first, since its y-axis
    carries no numeric meaning and the grid needs a real pixel span to fill),
    `draw_histogram`, `draw_cumulative_frequency`, and `draw_scatter_graph`.
    `draw_cumulative_frequency`'s curve is now a real smooth curve
    (`_smooth_curve`, a Catmull-Rom spline sampled densely into one dense
    `PolyLine`, each segment's x/y clamped between its own two endpoints so it
    never overshoots past a neighbouring point) instead of straight `PolyLine`
    segments - already started at (0,0), confirmed unchanged. `draw_bar_chart`'s
    gap math was fixed so the axis-to-first-bar gap equals the inter-bar gap
    (previously exactly half, since the gap used to be split evenly either side
    of a centred bar) - the gap now sits consistently before every bar instead.
    `draw_pie_chart` dropped its per-slice `CHART_COLORS` fill and legend
    entirely; every wedge is now unfilled and labelled with its own category name
    and angle out of 360 directly on (or, for a narrow slice, just outside) the
    wedge - mirroring `draw_spinner`'s existing narrow-sector label handling.
    `draw_histogram`/`draw_cumulative_frequency` switched their x-axis from ticks
    fixed to the class boundaries to the normal computed "nice" spacing, so a
    histogram's bar placement isn't given away by the tick marks (cumulative
    frequency deliberately kept boundary-aligned ticks, since its points
    genuinely sit at those boundaries and reading them off the axis is part of
    the point).

    Topic-level: `stats_mean/_mode/_median/_range_frequency_table` and the
    grouped-mean sibling pair all gained a real value/frequency (or class/
    frequency) table - reusing `draw_two_way_table` directly rather than any new
    table-drawing code, since a plain row-per-value table with one data column
    already fits that function's existing row-label/col-label/cells contract -
    with prompts trimmed to "Find the mean/mode/median/range number of X."
    (previously long prose listings). `stats_reverse_mean`/`_foundation` now
    spell out the stated count in words ("The mean of four numbers is...") via a
    new shared `num_word()` helper in `number_format.py` (moved there from a
    first draft in `statistics.py` once `box_plot_construct` turned out to need
    the exact same "Here are {n} {context}" pattern) - deliberately NOT applied
    to numbers appearing only in solution-step prose (a natural-language aside,
    not the question text itself), matching the audit's actual scope.
    `pie_chart_construct` gained a new `pie_chart_with_table` composed diagram
    kind (Category/Frequency/Angle table, blank Angle column on the question page
    via a plain `two_way_table`, stacked above the completed pie chart on the
    solution page via the same nested-Drawing composition technique used
    elsewhere this session) - the prompt no longer restates the survey counts in
    prose either. `scatter_graph_construct` gained a two-row x/y data table (row
    labels the axis names, columns numbered 1..9) replacing its own prose pair
    listing. `scatter_graph_interpret`'s `read_value` question no longer shows
    the line of best fit already drawn - the student draws it themselves (blank
    scatter diagram on the question page, the line only appearing on the
    solution page) - `correlation_type` questions were unaffected (never needed a
    line at all). `cumulative_frequency_plot` gained a new `cumulative_frequency_
    question` composed diagram kind (class/frequency table stacked above the
    blank squared axes) for its question page. `box_plot_construct` dropped the
    "the five number summary (min, Q1, median, Q3, max)" phrase from its prompt
    (which was essentially handing over the method) in favour of "Draw a box plot
    for this data," and `draw_box_plot` gained a `blank` param so the question
    page can show the squared axis with no box drawn yet, matching every other
    "construct" topic's blank/solved split. `histogram_plot` gained a
    `histogram_question` composed diagram kind (class/frequency table above blank
    regular-axis squared paper). `histogram_interpret`'s highest-frequency
    question dropped its "(not frequency density)" parenthetical hint from the
    prompt.

    **One real, pre-existing bug was found and fixed via this session's own
    visual verification, not by any unit test** - the same story as most gotchas
    in this file: `draw_two_way_table`'s row-label column used a fixed 66-unit
    width regardless of the actual label text, which visibly overflowed through
    the header/first-cell border for any label longer than a couple of words
    (first surfaced by `scatter_graph_construct`'s new "Weekly sales (£1000s)"
    row label) - fixed by sizing the header column to the longest row label's
    real measured width (via `stringWidth`), with the old 66 kept only as a floor
    for short labels.

    Central verification: full backend suite grew from 935 to 936 tests (one new
    test for `probability_conditional`'s blank/solved tree split; the Statistics
    batch's changes were covered by updating existing tests' assertions to match
    the new diagram shapes, not by adding new test functions); frontend
    unaffected throughout (61/61 - no frontend files were touched in either
    batch). No topic count change (still 296 - both batches were entirely
    rendering/wording/diagram/behaviour fixes to existing topics). Every changed
    topic in both batches was rendered and visually inspected before being
    considered done, and the review PDFs were regenerated and sent back to the
    user after each batch (296 question pages throughout; answer pages went
    304 → 305 after the Probability batch, then 305 → 307 after the Statistics
    batch, both expected from the taller composed table+diagram pages). Both
    batches were committed and pushed separately (two commits on
    `aqa-spec-gap-topics`).

    **This completes the first full review-feedback pass across all 6
    sections** - Number (step 35), Algebra (steps 36-37), Ratio & Proportion
    (step 38), Geometry (step 39), and now Probability + Statistics (this step).
    See "Where to pick up next" above for what a future session should do with
    that milestone.

41. New session, a large review-feedback batch (~24 named items) covering the
    first 100 pages of the `all_topics_review_*.pdf` documents - explicitly a
    **paginated continuation** of the same review process (steps 34-40), not a
    second full pass. Items spanned Number/Algebra topics plus several
    "fix the underlying capability, not just this one topic" requests. Two
    background research passes (Explore agents) plus direct file reads
    established exact current behaviour before committing to fixes; two design
    decisions were confirmed via `AskUserQuestion` (a new "rearranging by
    factorising" topic is Higher-only in the existing "Changing the Subject of
    a Formula" group; a new substitution variant is "rearrange for a different
    subject, then substitute" rather than "substitute knowns, solve for the
    missing one"). Phased via `EnterPlanMode` into 6 phases, worked through
    directly (no parallel subagents this time, given how much of the batch was
    genuinely cross-cutting engine work touching the same shared files).

    **Phase 0 (engine spike, `app/pdf/fraction_images.py`)**: extended the
    `\frac{}{}` marker's raw-PIL-text rendering (previously only special-cased
    `iteration.py`'s literal "x_n") with three new token kinds, needed for a
    genuine fractional-exponent superscript and a real radical bar to work
    *inside* a fraction for the first time. **This went through three
    genuinely wrong designs, each only caught by rendering real output, not
    assumed correct from the code**: (1) a first attempt captured "base^exp"
    as one token with the base limited to a single character - silently left
    a multi-character base like "10^2" or a parenthesised base like "(-2)^2"
    unsuperscripted, found via `substitution_rearrange_higher`'s own solution
    steps; (2) simplifying to match mathtext.py's own "just match the bare
    ^exp suffix, leave the base as ordinary preceding text" approach fixed
    that, but exposed that a bare "x"/"n" preceding an exponent then needed
    its own separate italicisation token (mathtext.py's `_VARIABLE_RE`
    equivalent), since the base is no longer captured/re-drawn as a unit; (3)
    the new radical token's hook+bar geometry, mirrored from
    `radical_images.py`'s proportions, collapsed to an illegible sliver at the
    smaller size a fraction's own digits render at - fixed with a dedicated,
    less-shrunk `_RAD_DIGIT_SCALE` font plus absolute pixel floors on the
    hook's tick/diag/stroke dimensions; then a **second**, more fundamental
    radical bug surfaced after that fix (the hook's own vertical span formula
    was missing a `pad_top + rad_h` term present in `radical_images.py`'s
    original geometry, collapsing the hook to a tiny fraction of the digit's
    real height) - found by rendering side-by-side against the already-correct
    standalone `radical_images.py` output and noticing the quality gap, not by
    assuming the mirrored formula was transcribed correctly. All three token
    kinds (plus the pre-existing "x_n" case) now share one combined, priority-
    ordered `_TOKEN_RE`. 8 new tests in `test_fraction_images.py`.

    **Phase 1 (Number wording, `fractions.py`/`decimals.py`/
    `order_of_operations.py`/`negative_numbers.py`)**: `fractions_simplify`
    dropped "the fraction"; `fractions_equivalent`'s prompt always says "the
    missing number" instead of naming numerator/denominator;
    `fractions_equivalent_diagram`'s `fill_missing_diagram` branch lost its
    leftover "Shape A is divided into..." context sentence, now identical to
    `diagram_only`'s already-short prompt (the two branches were collapsed
    into one, since they'd become behaviourally identical apart from a no-
    longer-existing wording difference); `decimals_ordering` gained a random-
    window constraint capping the four values' spread at 0.2; the three
    recurring-decimal-to-fraction topics gained a 50/50 "Write X as a
    fraction..." / "Show that X can be written as {answer}..." phrasing split
    (new shared `_recurring_fraction_prompt` helper); `bidmas` dropped "Use
    the correct order of operations"; `negative_ordering` switched from
    "smallest to largest"/"largest to smallest" to the same "ascending"/
    "descending" convention `decimals_ordering`/`fractions_ordering` already
    use for their prompts (kept the more descriptive phrasing in the solution
    steps).

    **Phase 2 (`powers_roots.py`/`algebraic_indices.py`)**: `powers_higher`,
    `simplifying_indices_challenging`, and `algebraic_indices_higher` were all
    reweighted (via `rng.choices` instead of a flat `rng.choice`) toward their
    fractional-exponent branch(es), since a genuine fractional power is each
    topic's own distinguishing content and a flat split under-represented it -
    verified concretely by re-running the fixed-seed-42 review script and
    confirming each topic's single sampled question now shows a real "^(n/d)"
    vinculum. `surds_multiply_divide`/`roots_higher`'s coefficient+radical
    rendering ("a√b") was confirmed already correct via the top-level
    mathtext.py regex (no code change needed there).
    `rationalise_denominator`'s radical-inside-a-fraction rendering is fixed
    by Phase 0's engine work alone.

    **Phase 3 (5 new Algebra topics)**: `change_subject_factorise_higher`
    (`changing_subject.py`, new topic, Higher-only) - `{letter}x + {q}x = {r}`
    with `letter` drawn from a pool deliberately excluding "x"/"n" (pairing an
    italicised and a plain letter in one equation would look like a rendering
    inconsistency, same reasoning as `ratio.py`'s `_LETTER_PAIRS`), verified
    via `sp.solve` with the letter left as a free symbol.
    `substitution_rearrange_foundation`/`_higher` (`substitution.py`, 2 new
    topics) - reuse the exact same formula shapes as `substitution_
    foundation`/`_higher` (kinematics/perimeter/area/triangle-area;
    speed-squared/kinetic-energy/acceleration) but ask the student to
    rearrange for a *different* letter first, then substitute - each verified
    both via `sp.solve` (symbolic rearrangement) and by substituting the
    derived value back into the *original* equation. `expand_double_brackets_
    no_coefficient_foundation` (`expand_factorise.py`, new topic) - the
    existing `expand_double_brackets_foundation`'s own docstring comment
    claimed "(x+p)(x+q), no coefficient" but its actual code drew x-
    coefficients up to 4 (a stale comment, not a bug - left unchanged as a
    genuine "harder Foundation" variant) - this new sibling genuinely pins
    both coefficients to 1. `functions_inverse_evaluate` (`functions.py`, new
    topic, Higher) - evaluates f^-1 at a numeric input, distinct from the
    existing `functions_composite_inverse`'s symbolic-only f^-1(x)
    derivation, reusing its `_fmt_inverse` display helper. All 5 wired into
    `registry.py`; the 4 hardcoded `296`-topic-count assertions updated to
    `301`. New/extended test files for all 5 (`test_changing_subject.py`,
    `test_substitution.py` gained a parallel `REARRANGE_GENERATORS` list
    rather than folding into the existing one, since the existing generic
    test hardcodes each generator's expected topic_id;
    `test_expand_factorise.py`, `test_functions.py`).

    **Phase 4 (`algebraic_fractions.py`)**: `_fmt_binom`'s `(x + a)`/`(x - a)`
    parens are redundant whenever the result is the *entire* content of a
    `\frac{}{}` marker by itself (the vinculum bar already visually groups
    it) - added a new bare `_fmt_binom_bare` used only at those specific call
    sites (both topics' prompt fractions, and the correspondingly bare
    denominators in a few solution-step lines), while every *juxtaposed*
    usage (two factors multiplied together as one denominator/numerator, a
    coefficient times a bracket) correctly keeps `_fmt_binom`'s parens, since
    removing those would genuinely change the expression's meaning.
    `algebraic_fractions_multiply_divide`'s `"(x^2 - d)"` also lost its own
    redundant self-wrap; its "powers showing as x^2 not properly
    superscripted" complaint is fixed by Phase 0's engine work directly. 2 new
    regression tests confirming no lone-fraction content contains a bracket.

    **Phase 5 (3 diagram fixes)**: `draw_number_line`'s boundary circle/
    shaded-segment/arrow now draw on a `mark_y` line offset above the ticked
    axis, rather than directly on top of it. `draw_linear_graph_pair`
    (`simultaneous_equations.py`'s `simultaneous_graphically`) was rebuilt
    from a schematic "not to scale" pair of lines into a genuine gridded plot
    on `_draw_scaled_axes` (which already prefers a true square unit grid),
    reusing the generator's own real `m1/c1/m2/c2`/`sol_x/sol_y` values
    (newly threaded through `DiagramSpec.params`) - this diagram's label
    placement took **four** iterations of its own, each only disproven by a
    real render: anchoring at a line's own endpoint and growing inward was
    safe against that line but not the *other* one (which sits close
    alongside for much of the window when the two slopes are similar, e.g.
    3 vs 4); a single-point pixel offset away from the other line ignored that
    a wide text label spans a real horizontal pixel range, and on a square
    grid a slope of 3-4 is visually very steep (pixel-slope ≈ data-slope), so
    the other line can sweep vertically across the *entire* label width even
    when clear at the label's centre point; clearing only the other line's
    span across that width still let the label collide with its *own* line,
    for the identical reason applied to the wrong line; the final version
    computes both lines' y-range across the label's actual `stringWidth`-
    measured footprint and places the label entirely outside the combined
    zone, plus a small additional nudge keeping the label's x away from the
    y-axis (where its own tick-number labels live). A background research
    agent (`aa97049009e939784` internally, not user-facing) independently
    confirmed and precisely diagnosed the other two named diagram bugs by
    executing the real drawing code across hundreds of seeds and measuring
    `stringWidth`-based bounding boxes directly, rather than guessing:
    `draw_rectangle`'s `height_label` had zero `stringWidth` awareness at all
    (fixed-pixel offset) and overflowed the canvas by ~2.5pt whenever a wide
    rectangle (width scale-bound) paired with a two-digit height value -
    fixed with a `stringWidth`-based clamp, mirroring `draw_sector`'s existing
    pattern; `draw_angle_line`'s narrow-wedge (<20°) label, used only by
    `forming_equations_foundation`'s `around_point` angle branch, had no
    canvas clamp at all and could land ~20pt past the top edge when a narrow
    wedge oriented near-vertically - fixed with the same `max(10, min(...))`/
    `max(8, min(...))` clamp `draw_sector` already uses. 2 new regression
    tests. Regenerating `simultaneous_graphically`'s diagram param shape
    required rebuilding all 60 Practice Test papers (`python -m
    app.practice_tests.build`) - the exact same "frozen JSON goes stale when
    a diagram param shape changes" gotcha already documented for
    `area_mixed_compound` in step 39, confirmed still exactly 100 marks per
    paper afterward.

    Central verification: full backend suite grew from 936 to 957 tests;
    frontend unaffected (61/61 - no frontend files touched this batch). Topic
    count grew from 296 to 301 (the only topic-count change across the whole
    steps-34-41 review-feedback arc so far - every other review batch was
    pure rendering/wording/diagram fixes). The review PDFs were regenerated
    (301 question pages, up from 296; 312 answer pages, up from 307) and sent
    back to the user. **Not yet committed/pushed as of the end of this
    session** - unlike most prior steps in this chronology, which explicitly
    note committing before ending.

42. New session, a review-feedback batch covering pages 101-200 of the
    `all_topics_review_*.pdf` documents (~20 named items) - another
    paginated continuation of the same review process (steps 34-41), this
    time spanning Algebra (kinematics, graph plotting), Ratio & Proportion,
    and a large chunk of Geometry (area, angles, Pythagoras, trig). Researched via 3
    parallel Explore agents plus direct code reads, downloaded and visually
    inspected the Corbett Maths "Area of Compound Shapes" PDF the user
    linked (used only to calibrate shape variety/structure, never to copy
    its content), and rendered the two "no diagram!!!!" Pythagoras topics
    directly before proposing a fix (confirmed a diagram genuinely was
    already present and correctly drawn - the real answer, confirmed via
    `AskUserQuestion`, was "remove it anyway", not "fix it"). 4 scope
    questions were confirmed via `AskUserQuestion` before planning (recorded
    in the plan file, `sparkling-swinging-lovelace.md`): `area_composite_
    rectangles` reworked in place with several shape branches rather than
    new topics; `best_buys`/`direct_proportion`/`inverse_proportion` keep
    their existing content and get new `_noncalculator` siblings rather than
    being rewritten; the ladder diagrams are removed outright; and the
    squared-paper grid fix goes into the shared `_draw_scaled_axes` helper
    so every caller benefits, not just the 7 named topics. Worked directly
    through 6 phases (no parallel subagents this session, given how much of
    the batch was genuinely cross-cutting engine work touching the same
    shared files), verifying every change with real renders before moving on
    - per this project's own "render and look closely" discipline, several
    of this session's fixes only existed because a first attempt was
    rendered and found wanting, not because the second attempt was
    guessed correctly up front.

    **Phase 0 (shared engine work)**: `_draw_scaled_axes` (`diagrams.py`)
    reworked from "one shared px-per-RAW-UNIT scale, falling back to
    independent rectangular scaling for lopsided ranges" to "independent
    'nice' step per axis, one shared pixel-size-per-square" - real squared
    exercise-book paper convention (a square can represent a different
    number of units on each axis, e.g. 50° by 0.2, while still rendering as
    a visual square) - fixing what turned out to be the ACTUAL root cause of
    "very messy" graphs: the old fine-gridline loop used a hardcoded 1-raw-
    unit step regardless of which branch fired, so even the "rectangular
    fallback" for a wide-domain topic like `trig_graph` (360° span) or
    `plot_cubic` (54-unit y-span) crammed hundreds of 1-unit gridlines into
    ~170px, rendering as a dense grey smear - confirmed by rendering the
    actual pre-fix output before assuming the fix was needed at all. Fixes
    `trig_graph`, `plot_cubic`, `plot_reciprocal`, `plot_distance_time`,
    `distance_time_interpret`, `velocity_time_interpret`, and (per the
    confirmed "fix everywhere" scope) every other `_draw_scaled_axes` caller
    - `draw_grid_transformation`, `draw_loci_construction`,
    `draw_loci_region`, `circle_equation`, `draw_inequality_region` - all
    re-rendered and confirmed unaffected/improved, not just the 7 named
    topics. Also added `_swept_angle_arc` (mirroring `draw_sector`'s own
    established direct-`ArcPath.addArc` technique) for `draw_angle_line`'s
    "around a point" missing angle, which is routinely reflex - `_angle_arc`
    always takes the non-reflex sweep between two ray directions, so it was
    silently drawing the small complementary wedge on the wrong side instead
    of the real (often reflex) missing angle, fixing `angles_around_point`/
    `_higher`'s "still no arc on the missing angle" complaint.

    **Phase 1**: `kinematics_suvat`'s SUVAT preamble box already rendered
    correctly on both pages (no fix needed there) - only the "Find the X"
    phrasing in the 3 shared helper functions needed the SUVAT letter
    appended in brackets (e.g. "Find its final velocity (v)."), fixing both
    the practice and modelled-example pages at once since both call the same
    3 functions.

    **Phase 2**: fixed `algebraic_inverse_proportion`'s unconditional
    `f"x^{n}"` (printed the literal "x^1" when the exponent happened to be
    1) via a new `_pow_expr` helper. Added 3 new topics -
    `best_buys_noncalculator`, `direct_proportion_noncalculator`,
    `inverse_proportion_noncalculator` (296→301 was step 41; this session is
    301→304) - each using deliberately clean, mental-math-friendly numbers
    (quantities always a multiple of 100 for best buys so the division is
    always exact; small numbers related by a clean multiple/factor for the
    two proportion topics) rather than just being "not guaranteed to need a
    calculator" like their existing siblings. The 3 existing topics were
    added to `CALCULATOR_ONLY_TOPIC_IDS` so a non-calculator Practice Test
    paper now picks the new friendly siblings instead.

    **Phase 3**: `ratio_difference`/`_higher` gained line breaks (a literal
    `"\n"`, already converted to a real `<br/>` by `mathtext.py`) after the
    initial ratio statement and before "Find". `draw_two_similar_rectangles`
    reworked so the shape with the numerically larger given width is drawn
    visibly larger and positioned first/left (parsing the leading number out
    of the label strings, which are always real given numbers here, never
    the unknown itself) - a real bug was caught and fixed in the first
    version, which had the size ternary tied to the wrong variable (`a_bigger`
    controlled which shape got large vs small instead of which POSITION
    (left/right) got large vs small, so the numerically bigger shape was
    rendering smaller) - caught by rendering, not by re-reading the code.

    **Phase 4**: `area_triangle`/`area_parallelogram` height labels now sit
    inside the shape when there's genuinely room (measured via `stringWidth`,
    falling back to outside only when a narrow/tall triangle doesn't have
    space) - the parallelogram fix in particular found the OTHER side of the
    dashed height line has far more room by construction (0.85×base vs
    0.15×base), a purely structural fix needing no dynamic measurement.
    `area_composite_rectangles` (`area_perimeter.py`) reworked from one fixed
    corner-notch L-shape into 4 branches - the existing L (now also a mirrored
    second orientation via a new `corner` param on `draw_l_shape`), a new
    T-shape (`draw_t_shape`, a genuinely new diagram kind - a horizontal bar
    over a narrower stem, verified via a real bounding-box-minus-two-notches
    independent decomposition), and a "given the total area, find x" reverse
    branch (verified via `sp.solve`) that reuses the existing L-shape diagram
    with zero new diagram code, just different label content. `area_subtract_
    compound`/`_foundation` gained a genuine minimum-hole-size safety net in
    `draw_l_shape`: `stringWidth`-measured stacked/side-by-side layout
    checks, falling back to a single combined caption below the hole (in the
    always-spacious shaded frame) when a hole is too small for either -
    replacing a cramped "5 cm2 cm" collision found by rendering a small-hole
    case directly (also tightened the generators' own minimum inner
    dimension from 2 to 3 to reduce how often the fallback is even needed).
    `draw_sector`'s radius label moved from near the arc's own endpoint to
    the midpoint of the fixed top ray, verified correct across narrow/right-
    angle/reflex sector angles.

    **Phase 5**: `angles_triangle_higher`'s shared `draw_triangle_angles`
    radius bumped 45→52 (a general "make angle diagrams bigger where there's
    room" pass, applied opportunistically per the user's standing
    instruction rather than as an isolated fix). `draw_parallel_lines`/
    `draw_exterior_triangle` reworked so the drawn geometry roughly visually
    matches the real angle value passed in (a genuine numeric `known_value`/
    `interior1_value` now reaches the diagram, not just pre-formatted label
    strings) - bucketed into 3 pre-verified-safe slopes/apex positions rather
    than a continuous function, since the existing label-offset tuning was
    calibrated against one moderate shape and an untested extreme risked a
    new overlap; confirmed via a 3×3 grid render (3 angle buckets × 3
    relation types) that a ~90° angle now genuinely looks like a right angle
    for every relation type, directly fixing the user's own named example.
    `draw_exterior_triangle`'s own rework surfaced a real, independently
    confirmed overlap: the wide `interior2_label` (e.g. "(2x+4)°") crossed
    its own vertex's angle arc - two fix attempts (scaling the existing
    centroid-inset distance; switching to `anchor="start"`) were tried and
    rendered before the real fix (a much more aggressive `stringWidth`-based
    inset factor, keeping the default centred anchor) actually cleared it,
    confirmed across all 3 angle buckets × 2 shape variants.

    **Phase 6**: removed the diagram entirely from `pythagoras_ladder_context`/
    `_foundation` (both the practice and modelled-example generators, both
    tiers) per the user's explicit confirmation - text-only now. While in
    the file, fixed a real, unrelated pre-existing bug noticed in passing:
    the Foundation generator's `k=1..3` multiplier on the shared
    `PRIMITIVE_TRIPLES` pool could produce a ladder over 180m (confirmed via
    a direct render showing "122 m"/"183 m") - capped to 125m (the largest
    cap that still keeps at least 20 distinct (triple, k) combinations
    available, needed for this topic's own default 20-question worksheet - a
    first, stricter cap of 80m only left 18 combinations and was caught by
    the full suite's own dedup-variety test, not assumed sufficient).
    Fixed the review script's doubled tier suffix ("Ladder Context
    (Foundation) (Foundation)", for any topic whose display name already
    ends with its own tier in parentheses) - a second bug noticed in passing
    while verifying the ladder topics' actual review-PDF pages. Fixed a real
    `draw_cuboid` bug affecting `pythagoras_3d`/`trig_3d`: vertex D (the one
    hidden back-bottom-left vertex) projects visually INSIDE the front
    face's own silhouette in oblique projection, unlike every other vertex -
    pushing it outward from the overall centroid by the same small fixed
    distance used for every other vertex left it overlapping the dashed
    lines converging there; a first fix (push straight down below the front
    face) collided with the width label instead ("D14 cm" running together),
    confirmed only by rendering; the working fix pushes D further down,
    clearing both. Added genuine shape variety to `draw_trig_triangle`/
    `draw_general_triangle` (both previously 100% fixed vertex coordinates
    every single render) via a new `_shape_variant` helper - a small index
    derived deterministically from each diagram's own label content (an
    explicit char-code sum, NOT Python's built-in `hash()`, which is
    randomised per-process for strings, per this file's own documented
    gotcha) - bucketed into 3 pre-verified-safe vertex layouts per diagram
    kind, confirmed via a 6-image grid render that all 3 genuinely look
    different and that the existing centroid-inset label-clearance logic
    still works at the new range of shapes. That same verification render
    caught a real, independently confirmed bug: `draw_trig_triangle`'s angle
    label used a fixed 0.4 centroid-inset factor (unlike its sibling
    `draw_general_triangle`, which already had `stringWidth`-based scaling)
    - fine for short labels, but a wide algebraic one like "(2x+15)°"
    visibly crossed the hypotenuse on the wider/flatter of the 3 new
    variants; fixed by applying the same `stringWidth`-based scaling
    `draw_general_triangle` already used, confirmed clean across all 3
    variants afterward.

    Central verification: full backend suite grew from 957 to 958 tests (one
    new test confirming the two ladder topics have no diagram); frontend
    unaffected (61/61 - no frontend files touched this session). Topic count
    grew from 301 to 304 (the 3 new non-calculator siblings). All 60 Practice
    Test papers rebuilt (`area_composite_rectangles`' diagram param shape
    changed - the same "frozen JSON goes stale" gotcha already documented
    for `area_mixed_compound`/`simultaneous_graphically` in steps 39/41),
    confirmed still exactly 100 marks per paper afterward. The review PDFs
    were regenerated (304 question pages, up from 301; 315 answer pages, up
    from 312) and sent back to the user. Committed and pushed - see `git
    log` for the exact commit.

43. New session, a review-feedback batch covering pages 201-250 of the
    `all_topics_review_*.pdf` documents (~14 named items, mostly Geometry) -
    another paginated continuation of the same review process (steps 34-42).
    Clarifying questions were asked up front only where genuinely ambiguous;
    most items were direct fixes. A task list tracked the 14 items. Every
    diagram fix was verified by rendering real PDFs (a reusable
    `scratchpad/rdiag.py` harness renders any diagram kind or a topic's
    worksheet to PNG), not by trusting unit tests - the standing discipline
    for visual issues. Highlights:
    - **pythagoras_3d/trig_3d** (`draw_cuboid`): vertices relabelled `a`-`h`
      lowercase; the one hidden vertex (`d`) now sits beside its own vertex
      with a short leader line instead of floating at the bottom; a new
      `show_diagonal` param draws the dashed space diagonal with NO
      `?`/`theta` label (the dash indicates it).
    - **All trig triangles (the flagged priority)**: `draw_trig_triangle`,
      `draw_general_triangle` and `draw_right_triangle` were rewritten around
      new shared helpers - `_TRIG_TRIANGLE_VARIANTS`/`_GENERAL_TRIANGLE_VARIANTS`
      (6 genuinely different orientations/sizes each, incl. mirrored and
      apex-down), `_place_side_label` (outward-normal generic side placement),
      `_place_angle_label` (an ANALYTIC clearance formula - distance along the
      bisector derived from the label's own footprint and the half-angle - so
      the angle value never overlaps the two sides, fixing the recurring
      complaint), and `_right_angle_marker` (orientation-independent). Side and
      angle labels now share one size (`_TRIANGLE_LABEL_SIZE = 9.5`).
    - **circle_theorems**: diagram label fonts bumped to 10; every prompt
      trimmed to "Find the size of angle x." (the diagram already shows the
      values) so the student must choose the theorem.
    - **congruent_triangle_proof_foundation** REDESIGNED (the user was
      frustrated it hadn't been done): now two triangles with real NUMERIC
      measurements (`_foundation_congruence` picks SSS/SAS/ASA/RHS and labels
      the matching sides/angles), prompt "Shown below are two congruent
      triangles. Give a reason why they are congruent." + shuffled MC. Needed
      `draw_two_triangle_congruence` extended with numeric side/angle-label +
      right-angle-marker support (the Higher topic keeps its tick/arc marks).
      Now procedural (dropped `question_count=len(TEMPLATES)`).
    - **cylinder/cone/frustum/compound-3D diagrams**: measurement overlaps
      fixed and dashed radius lines added where missing (frustum gained a
      dashed axis + two radius dashes; both compound round variants gained a
      dashed radius). Cylinder prompt trimmed to "Find the {measure} of the
      cylinder, correct to ...".
    - **pyramid**: the derived (usually-irrational) decimal slant label was
      removed from the diagram - only the integer base/height show now.
    - **vectors_arithmetic_higher**: `_join_vector_terms` now parenthesises a
      negative second term for BOTH ops, so `4a + -3b` reads `4a + (-3b)`.
    - **transformations**: "Draw and label the image A'B'C'" removed from all
      four "complete" prompts; all four "describe" topics reworded to
      "...maps shape A onto shape B" with whole-shape A/B labels (new
      `original_shape_label`/`image_shape_label` params on
      `draw_grid_transformation`, drawn at the centroid) and NO per-vertex
      labels. (The reflect mirror-line weighting and the translate no-arrow
      were already done in step 39.)
    - **bearings**: `_north_arrow` default length 20→30 (all bearings).
    - **properties_3d_shapes** split into a no-diagram version (name-only
      recall) plus a NEW `properties_3d_shapes_diagram` sibling (shows the
      solid) - 304→305 topics, the only count change this step.
    - **The review script** (`scripts/generate_review_pdfs.py`) now renders
      each topic's `preamble_lines` formula box, since the cone/sphere/frustum/
      pyramid formula boxes already existed in the app (step 39) but were
      invisible in the review PDF, making the user think formulas weren't
      given (they were).
    Backend suite grew 958→959; frontend unaffected (61/61). Practice Tests
    were NOT rebuilt - all the diagram changes kept backward-compatible param
    branches, so the frozen papers still render fine (verified via the suite).
    Committed as `42ffe3d`; a follow-up `3ca66af` fixed the topic-count
    numbers in CLAUDE.md (304→305, and reconciled a pre-existing drift in the
    per-section table's Ratio & Proportion count 34→37).

44. Same session, a large mechanical refactor the user requested "before the
    [next] feedback": **streamline every topic id to a `name_F`/`name_H`
    convention.** Confirmed 3 decisions up front via `AskUserQuestion`: (a)
    strip any existing `_foundation`/`_higher` word and append `_F`/`_H` by
    tier (so `bearings_foundation`→`bearings_F`, `angles_triangle_higher`→
    `angles_triangle_H`, `linear_two_step`→`linear_two_step_F`,
    `bearings_cosine_rule`→`bearings_cosine_rule_H`); (b) migrate the 60
    frozen Practice Test papers IN PLACE (rewrite only their `topic_id`
    fields, keeping content byte-identical) rather than rebuild (rebuilding
    would change every paper, since each paper's seed is derived from
    `(paper_id, topic_id)` via SHA-256); (c) rename IDs ONLY - not the
    generator/modelled-example function names, not `dedup_key` prefixes.
    Machine-generated the old→new map from the registry first and confirmed
    no collisions and no tier-word mismatches across all 305 ids.

    Applied via one migration script with THREE deliberately different
    replacement strategies, because a naive blanket replace would corrupt
    lookalike strings: (1) `app/topics/*.py` - ANCHORED `id=`/`topic_id=`
    replace only, so coincidental context strings are untouched (this
    matters: `"density"`/`"pressure"` appear as `rng.choice([...])` branch
    values in `compound_measures.py` AND are topic ids; the
    `"plans_and_elevations"` diagram kind and `"symmetry_lines"` param key
    also equal topic ids); (2) `topic_selection.py` (priority lists +
    `CALCULATOR_ONLY_TOPIC_IDS`) + the `data/*.json` `topic_id` fields +
    test files - exact-quoted-id replace; (3) JSON anchored to
    `"topic_id": "..."` so frozen diagram `"kind"` fields were never touched.
    `registry.py` needed NO change - it lists `TopicDefinition` constants, and
    each id lives on its definition inside the topic file.

    The full-suite run then caught the one class of thing the exact-quoted
    TEST replace got wrong (app files were safe via the anchored approach):
    the two ids that also serve as a diagram kind / param key -
    `plans_and_elevations` (a `DiagramSpec` kind) and `symmetry_lines` (a
    `draw_symmetry_shape` param key) - had their kind/param *usages* in test
    assertions wrongly suffixed; reverted those specific 4 lines while keeping
    the genuine `topic_id`/`.id`/GENERATORS-tuple id references suffixed
    (collision set confirmed to be exactly those two, via
    `topic_ids ∩ diagram_kinds` and `topic_ids ∩ param_keys`). Also updated
    three route-test download-filename assertions (the filename is
    `{topic_id}-{tier}-...pdf`, now correctly containing `_F`/`_H` - my
    exact-id replace correctly hadn't touched `"reverse_percentage-higher-..."`
    since the id was followed by `-`, not a closing quote). Frontend confirmed
    to have no hardcoded backend ids, so it was untouched.

    Verification: registry loads 305 topics all ending `_F`/`_H`; every
    generator's produced `topic_id` matches its registered `id`; all 30
    calculator-only ids and all 283 distinct frozen-paper `topic_id`s resolve;
    full backend suite 959/959. 193 tracked files changed (65 topic modules,
    ~60 test files, 60 JSON, `topic_selection.py`, `test_routes.py`,
    CLAUDE.md's architecture guidance). Review PDFs regenerated (now showing
    the new ids) and sent to the user. Committed and pushed as `9833db2`.

45. New session, a single focused user request (with a reference image): make
    **fractional powers render as raised powers** in the PDF. A fractional
    exponent like `x^(1/2)` was being drawn as a small vinculum fraction sitting
    LOW next to the base — reading like a coefficient/subscript rather than a
    power — while integer powers (`x^5`) correctly floated up. Root cause, found
    by rendering an actual `algebraic_indices_H` worksheet and looking closely
    (not by any test — the test asserted the old markup): `mathtext.py`'s
    fractional-exponent branch wrapped the fraction image in `<super>…</super>`
    with the image's own `valign="bottom"`, but a `<super>` wrapper only shifts
    *text* runs — an `<img>` with `valign="bottom"` stays pinned to the baseline
    regardless, so the fraction never actually rose. Fixed with a one-line change
    in `_replace_math`: drop the `<super>` wrapper and set `valign="super"` on the
    image itself, which lifts it into the same raised zone as an integer
    superscript and self-scales with font size (verified via a rendered-PDF spike
    comparing it against `x^5`/`(..)^2` at both 11pt prose and the 9pt practice-
    test mark-scheme size). Updated the one `test_mathtext.py` test that asserted
    the old `<super>`-wrapper structure; the compound `x^(¼+¾)` case (fractions
    inside `<super>` via `\frac` markers) was unaffected. No topic/count change;
    regenerated + sent both review PDFs. Backend suite 935→935 (one test updated,
    none added), frontend unaffected.

46. Same session, a large new feature: a **home-page PDF / Word download-format
    toggle** that makes every topic's Worksheet *and* Modelled Example
    downloadable as a real Word `.docx`, not just a PDF. Scoped up front via
    `AskUserQuestion` (Worksheet + Modelled Example only — Practice Tests stay
    PDF-only, Bell Tasks unchanged; **maths matches Bell Tasks exactly** — native
    equations for fractions/powers, plain Cambria Math text for rarer constructs;
    **full layout parity** with the PDF; Bell Tasks *font scheme* but the
    worksheet's own size hierarchy/colours, not Bell Tasks' 18pt purple), then
    planned in plan mode.

    Built a new `backend/app/docx/` package (added `python-docx==1.2.0`, absent
    before): `docx_omml.py` builds real native Word equations (fractions,
    superscripts, fractional-power superscripts, and — after a follow-up user
    request — native stacked **column vectors** via an `<m:d>` delimiter around an
    `<m:m>` matrix) as raw WordprocessingML `<m:oMath>` via lxml — the Word
    sibling of the existing PowerPoint `app/bell_tasks/omml.py`, but simpler
    (Word takes a bare `<m:oMath>` directly in a `<w:p>`, no `mc:AlternateContent`
    wrapper, no `endParaRPr` ordering trap). `render.py` provides
    `render_worksheet_docx` / `render_modelled_example_docx` mirroring the two PDF
    renderers element-for-element (title/meta/rule, numbered questions, embedded
    diagrams, Worked Solutions / answers-only, the modelled-example worked-example
    box + backward-fading practice page), reusing the pure `math_tokenizer.tokenize`
    and `diagram_raster.rasterize_drawing` from `bell_tasks/` and `render_diagram`
    from `pdf/diagrams.py` unchanged. The `format` field was added to
    `GenerateWorksheetRequest` (default `pdf`, so existing bodies are unchanged)
    and both routes branch on it.

    **Risk-first spikes, opened in real Microsoft Word via COM automation** (the
    same QA path Bell Tasks used for PowerPoint, since LibreOffice isn't installed
    here) before wiring anything: (1) a minimal fraction/superscript/fractional-
    exponent doc confirmed the bare-`<m:oMath>` mechanism and that font/size/colour
    on a `<w:rPr>` inside each math run genuinely take effect; (2) an **empty-base
    `<m:sSup>`** renders cleanly (no placeholder box) — which is what lets a
    bracketed/unattached power like `(25x^4)^(1/2)` or `(x^-2)^4` raise as a native
    superscript instead of printing a literal `^` caret. This last point is the one
    place the docx deliberately goes *beyond* Bell-Tasks-exact: Bell Tasks (which
    only renders prompts, rarely with bracketed powers) leaves those as literal
    carets, but on an index-laws worksheet — which renders steps too — that looked
    clearly worse than the PDF and against the step-45 "powers look like powers"
    intent, so `render._emit_segment` routes every exponent form through a native
    superscript (empty base when unattached). Genuinely compound nested-paren
    exponents in steps (`x^(6-(-4))`) stay literal, matching both the scope and the
    PDF's own behaviour there. The `\frac{}{}` and `\colvec{}{}` markers (which the
    tokenizer can't see, and which fill solution steps/answers) are handled in
    `_emit_segment` before tokenizing; `\recur`/`\plain`/surds/`x_n` fall back to
    plain Cambria Math text per the chosen scope.

    Frontend: a global `FormatContext` (`context/FormatContext.tsx`,
    localStorage-persisted) + `useFormat`, a `DownloadFormatToggle` segmented
    control rendered on the home page, and `format` threaded through
    `api/types.ts`/`client.ts` and both download hooks (choosing the `.docx`/`.pdf`
    filename extension). The choice is global so it applies from HomeScreen,
    SectionView and TopicSearch, not just where the control is shown. Existing
    component/hook tests that render `TopicCard` (whose hooks now read the context)
    were wrapped in `FormatProvider`.

    Verified end-to-end: full backend suite 959→971 (new `test_docx_render.py` —
    structural assertions incl. real `<m:oMath>`/`<m:f>`/`<m:sSup>`/`<m:d>` elements,
    embedded diagram images, answers-only, the docx route media-type/filename +
    default-still-PDF, and bold vector letters); frontend 61→65 (new
    `DownloadFormatToggle.test.tsx`); real `.docx` files for a fractions topic,
    `algebraic_indices_H` (native fractional powers), a diagram topic, a modelled
    example, `vectors_arithmetic_H` (native column vectors), and `geometric_vectors_H`
    (bold vector letters) all opened in real Word and eyeballed; and a live browser
    click-through (toggle → Word, download returns 200 with the `wordprocessingml`
    content-type and `PK` docx magic bytes, no console errors).

    Follow-up requests in the same session (all folded into this step): the native
    stacked column vector (`\colvec{}{}` → an `<m:d>` delimiter around a two-row
    `<m:m>` matrix, replacing an earlier plain-text `(a, b)` fallback), and **bold
    `\vec{a}`/`\vec{b}` vector letters** (handled in `_emit_segment` before the
    tokenizer, matching the PDF's own `<b>` treatment — the tokenizer would otherwise
    flatten them to plain Cambria Math). These closed the two Bell-Tasks-exact
    shortcuts the first pass had left; nothing docx-related is now knowingly below PDF
    parity.

47. New session (IN PROGRESS — Phases 0-3 of 6 done, committed WIP on branch
    `diagram-scale-overhaul`, NOT merged). A large user-requested overhaul of **every
    shape/angle & 3D-solid diagram** in `backend/app/pdf/diagrams.py`, driven by three
    asks: (1) diagrams big enough that each measurement is clearly associated with its
    own side/angle (first flagged example: `forming_equations_H` Q2's crammed
    quadrilateral, but "one of many"); (2) all diagram text one uniform size (~11pt);
    (3) shapes/angles drawn roughly to scale ("doesn't have to be exact; if every shape
    looks different, that's fine"). Scope confirmed via `AskUserQuestion`: 2D shapes &
    angles AND 3D solids (graphs/charts/number-lines/Venn/trees/loci/probability
    illustrations OUT); proportional where a value is given, plausible where it's the
    unknown being solved for; ~11pt everywhere; longer PDFs accepted. Planned in plan
    mode (`C:\Users\James\.claude\plans\zesty-yawning-blum.md` — its "STATUS (resume
    here)" section is the authoritative continue-guide) and phased 0-6, each phase
    verified by rendering every affected topic to a contact sheet (not unit tests — the
    project's standing "render and look closely" discipline) and sending regenerated
    `all_topics_review_*.pdf` as a checkpoint.

    Done so far: **Phase 0** (engine — canvas 200x130→290x190, `_LABEL_SIZE` 9→11 uniform
    with `_TRIANGLE_LABEL_SIZE` aliased, asymmetric fit margins `_MARGIN_X`/`_MARGIN_Y`,
    and shared helpers `_dimension_value`/`_plausible_length`/`_plausible_angle`/
    `_scale_to_fit`/`_fit_triangle`/`_orient`/`_legible_angles`/`_construct_triangle`);
    **Phase 1** (rectilinear — uniform text + asymmetric margins, which fixed a real
    outside-left height-label clipping bug that had rendered a trapezium's "10 cm" as
    "0 cm" on the wider canvas); **Phase 2** (triangles — right/trig triangles built to
    TRUE scale from real legs/marked-angle, general_triangle & triangle_angles built to
    true shape via `_construct_triangle` AAS/SAS/SSS so an obtuse angle is drawn obtuse,
    everything else scaled-to-fill + uniform); **Phase 3** (angles & polygons — the
    flagged `forming_equations_H` Q2 diamond fixed: `polygon_angles` now an irregular
    convex quad on a taller 250-tall canvas with one label per vertex, `triangle_angles`
    to true legibility-compressed angles on a 230-tall canvas, angle_line/parallel_lines/
    polygon/symmetry_shape bigger + uniform). Full backend suite **971/971** after each
    phase; frontend untouched; no topic-count change; diagram param schemas deliberately
    unchanged so the 60 frozen Practice Test papers still render with no rebuild.

    Remaining: **Phase 4** circles & sectors (`circle`, `sector`, six `circle_*` theorem
    diagrams — inherently schematic, so target plausible + clear + bigger + uniform, not
    true scale); **Phase 5** bearings (`draw_bearings` — draw true bearings to scale);
    **Phase 6** 3D solids (cuboid/prism/cylinder/cone/sphere/pyramid/frustum/net/
    compound_3d/plans_and_elevations — proportional edges where numeric, uniform text,
    clear labels; bump `SOLID_WIDTH/HEIGHT`/`NET_*` and unify the many per-function
    hardcoded label sizes). One accepted trade-off already made: very acute/obtuse
    triangle angles are compressed toward 60 for *drawing* legibility (`_legible_angles`)
    so three vertex labels don't collide — the labels still show the true values.

48. New session, a review-feedback batch covering pages 1–200 of the
    `all_topics_review_*.pdf` documents (7 named items) — a paginated continuation of the
    same review process (steps 34-43), the first such chunk after the step-47 diagram
    overhaul was merged. Two design decisions were locked with the user before this
    session (recorded in the plan file
    `C:\Users\James\.claude\plans\review-batch-pages-1-200.md`): ratio parts all distinct,
    and best-buys with no dominating option. Worked directly through the 7 items (no
    parallel subagents), verifying every visual change by rendering real PDFs, per this
    project's standing "render and look closely" discipline.

    1. **Triple brackets split** (`expand_factorise.py`): refactored
       `generate_expand_triple`/its modelled twin into shared helpers
       (`_expand_triple_cubic` doing both verifications, `_build_expand_triple_question`/
       `_build_expand_triple_modelled`). The existing `expand_triple_brackets_H` now
       guarantees ≥1 x-coefficient with magnitude >1 (`_triple_coeffs_with_coefficient`
       rerolls until so), and a NEW `expand_triple_brackets_no_coefficient_H` (all `(x±k)`
       brackets, `_triple_coeffs_no_coefficient`) was added — Higher, "Expanding Brackets"
       group, own modelled example + `TopicDefinition`, registered, added to
       `HOISTED_INSTRUCTIONS`. 312 → 313 topics; the four hardcoded `312` count assertions
       bumped to `313`; Algebra table 80 → 81. This is the only topic-count change this batch.
    2. **`kinematics_suvat_H` quantity letters** (`kinematics.py`): the SUVAT letter now
       follows EVERY quantity in the question prompt, not just the "Find …" phrase step 42
       already did — e.g. "initial velocity (u) of 5 m/s", "acceleration (a)",
       "a time (t) of 3 s", "displacement (s)", "final velocity (v)". Edited all prompt
       strings across `_prompt_and_steps_eq1/2/3` (question prompts only; steps unchanged).
    3. **Label every integer on small-range graph axes** (`diagrams.py`
       `_draw_scaled_axes`): the numbered ticks previously recomputed `_nice_tick_step`
       independently, so a square-unit graph with gridlines every 1 unit but a y-span >10
       (e.g. `plot_straight_line_F` y = -3x+4) numbered only every 2nd line. Changed the
       numbered-tick loops to follow the actual `grid_step_x`/`grid_step_y` — so whenever
       gridlines are at every integer, every integer is labelled (real squared-paper
       convention). Zero effect on wide/lopsided graphs (their rectangular fallback already
       sets grid_step = `_nice_tick_step`). Fixes `plot_straight_line_F`, `plot_quadratic_F`,
       `line_equation_from_graph_F`; confirmed `plot_cubic_H`/`trig_graph_H` unchanged.
    4. **`plot_reciprocal_H` domain wording** (`graphs.py`): prompt (and its modelled twin)
       now say "for x = -4 to 4" instead of listing the non-zero x values; the numeric table
       still uses only the 8 non-zero x (division by zero), with an added solution step that
       x = 0 is undefined and left out — "for the student to discover", per the user.
    5. **`graph_transformations_H` both curves visible** (`diagrams.py`
       `draw_graph_transformation`): the fixed x[-6,6]/y[-6,8] window clipped a curve flat
       whenever a translation of up to 8 pushed it off-screen. Now the window is computed
       from the actual extent of BOTH curves (+1.5-unit margin) so neither clips — this
       diagram is schematic, so exact scale doesn't matter. Also made the generic base curve
       asymmetric (`_transform_base_fn` = `0.5x^2 + 0.6x - 1.5`, was the symmetric
       `0.5x^2 - 1.5`) so `reflect_y` (y = f(-x)) produces a visibly DIFFERENT curve rather
       than one that lands exactly on top of the dashed original and hides it — a genuine
       "can't see both curves" case the fixed-window fix alone wouldn't have addressed.
    6. **best_buys no-dominance** (`best_buys.py`): new `_has_dominant_option` (an option
       that is BOTH the lowest total price AND the largest quantity — obviously best without
       computing unit prices); both `_build_scenario` (calculator) and `_build_scenario_noncalc`
       now reroll (bounded 200-attempt loop) until no option dominates, forcing a genuine
       unit-price comparison. Existing unit-price + cross-multiplication verification kept.
    7. **ratio all parts distinct** (`ratio.py`): new `_rand_distinct_parts(rng, n)` (via
       `rng.sample(range(1,10), n)`) applied to `generate_share_two`/`_share_three`/
       `_share_three_foundation`/`_combine_ratios` and their modelled twins (each of a
       combined-ratio's two pairs made distinct). `find_share`, `ratio_difference`,
       `ratio_difference_higher` already rerolled to distinct; `ratio_1_to_n` (n≠1) and
       `ratio_to_equation` (m≠n) were already safe — confirmed by a 1500-trial-per-generator
       scan finding zero equal-part ratios.

    No frontend changes. Practice Tests were NOT rebuilt — the changed generators keep
    backward-compatible output shapes and the frozen JSON is static (the determinism test
    compares build-vs-build, not against committed files), so the 60 papers still render.
    Backend suite grew 971 → 981 (new triple-bracket generator/modelled/topic tests; the
    other items were covered by existing tests). Review PDFs regenerated (313 question pages,
    up from 312; 323 answer pages) and sent to the user. Committed and pushed.

49. Same session as step 48, a follow-up on one review item: `area_composite_rectangles_F`
    "still hasn't changed" — the user linked Corbett Maths' "Area of Compound Shapes"
    worksheet (Q1-4, Q6 as prime targets) as the "significantly better" bar. Downloaded and
    read the PDF (via `fitz`; WebFetch can't parse PDF binaries), rendered the current app
    output, and diagnosed the real gap: the app labelled the **full bounding rectangle + a
    floating cut-out caption** (e.g. "24 cm × 12 cm" + "2 cm × 7 cm"), whereas Corbett labels
    the shape's **own boundary edges directly, with some deliberately omitted** so the student
    deduces the missing lengths (step 42's rework had added shape variety but kept the old
    labelling). Locked 3 decisions via `AskUserQuestion`: (a) switch to Corbett edge-labelling
    with some sides omitted; (b) rectilinear only — NO "house" (rectangle+triangle roof, Q6),
    which already lives in `area_mixed_compound_H`; (c) also fix the sibling compound topics.

    **Diagram engine** (`diagrams.py`): new `_place_edge_label` helper (labels an edge at its
    midpoint, pushed outward from the shape centroid) + an additive `edge_labels` dict mode on
    `draw_l_shape` (both corner orientations) and `draw_t_shape` — draws the shape to scale and
    labels each named boundary edge, omitting blanks. Old param path (outer_labels/inner_labels/
    right_labels) and `shade_frame` kept for backward compatibility. The T-shape's two notch
    edges are special-cased (label goes BELOW the overhang, beside the stem — the centroid
    heuristic points the wrong way for those concave edges; found by rendering).

    **`area_composite_rectangles_F`** (`area_perimeter.py`) fully reworked: 4 branches — L
    (top-right / top-left notch), T-shape, and a find-x step-shape (top-left notch, area given,
    x on an inner edge, matching Corbett Q4). Each labels a Corbett-style subset of edges (e.g.
    L gives bottom, full side, notch-across, and the notched side's remaining part; omits the
    top segment and notch depth) and the steps show deducing the missing sides before splitting/
    subtracting. Both existing two-decomposition verifications kept; find-x verified by solving
    A = top·H + x·lower via sympy. 2604 distinct dedup keys.

    **Siblings**: `area_subtract_compound_F/_H` — the hole's two dimensions were jammed together
    inside it ("6 cm 3 cm"); now the width sits on the hole's top edge and the height on its
    left edge (small-hole fallback to a combined caption kept). `area_mixed_compound_H` — the
    quarter-circle and semicircle-notch cut-radius labels were cramped against the shape edges;
    nudged clear (the semicircle-notch label moved to just above the notch, inside the body,
    after a first attempt collided with the centred width label — caught by rendering).

    No topic-count change (still 313). Rebuilt all 60 Practice Test papers (`area_composite`
    diagram param schema changed; also picks up topic #313 from step 48 in the selection pool) —
    all exactly 100 marks, non-calculator constraint intact. Backend suite 981/981 (+1 test:
    composite diagrams use edge_labels, find-x carries "x"). Review PDFs regenerated (313/323,
    unchanged counts) and sent. Committed and pushed. (The chronology line above says
    "981/981" for step 49; the composite-edge-labels test added there actually made it 982.)

50. Same review thread, feedback on `ratio_shape_similar_F`/`_H`: put the letter "A"/"B"
    INSIDE each shape (not "Shape A" outside); use multiple shape types in different
    orientations (was always two same-orientation rectangles, per step 38); and for the
    Foundation topic, draw the two shapes further apart with the unknown label closer to its
    shape. Reworked `draw_two_similar_rectangles` (`diagrams.py`, kept the registry kind name
    for frozen-paper compat) into a general two-similar-shapes renderer: a new
    `_similar_shape_geometry(kind, orient, ...)` returns the polygon + the two corresponding
    edges to label for `rectangle` / `right_triangle` (4 right-angle-corner orientations) /
    `parallelogram` (2 leans); both shapes in a question share one kind+orientation (so
    corresponding sides stay identifiable), bigger drawn left, each labelled with a bold letter
    inside (via the shape centroid) and its edge labels placed by the existing
    `_place_edge_label` helper (which sits them close to their own edge). Gap widened 48→74 so
    the height/unknown labels sit close to their shape without reaching the other one. New
    `_pick_similar_shape(rng)` in `ratio.py` chooses kind+orientation; wired into all four
    generators (F/H × practice/modelled), added to `shape_kind`/`orientation` diagram params
    and the dedup keys. All three shape kinds appear; ~1600-1800 distinct dedup keys per
    generator. No topic-count change (313). Rebuilt all 60 Practice Test papers (diagram param
    schema changed) — all 100 marks. Backend suite 982 → 983 (+1: similar-shapes diagrams vary
    shape_kind). Review PDFs regenerated (313/323) and sent. Committed and pushed.

51. Same review thread, feedback on `density_H`: when the student has to work out the volume
    themselves (the `from_dimensions` flavour), show a DIAGRAM of the solid and stop restating
    the dimensions in prose — e.g. "A block of alloy in the shape of a cuboid has dimensions
    6 cm × 2 cm × 4 cm and a mass of 2175 g. Find its density…" should read "The block of alloy
    below has a mass of 2175 g. Find its density, correct to 2 decimal places." Reworked
    `generate_density_higher`'s `from_dimensions` branch (+ modelled twin, `compound_measures.py`):
    new `_density_dimension_shape(rng)` picks a **cube / cuboid / triangular prism**, returns the
    volume + the volume-working step + a `DiagramSpec` (reusing `draw_cuboid` with `is_cube` for
    the cube, `draw_triangular_prism` for the prism — dimensions live on the diagram), with an
    independent repeated-addition volume cross-check kept. The prompt now says "The {obj} below
    has a mass/density of … Find its …" with the dimensions only on the shape. Solid-only context
    list (`_DENSITY_SOLID_CONTEXTS` — a "sample of liquid" has no shape to draw). The
    `unit_conversion` flavour is unchanged and stays diagram-less. (`pressure_H` got the same
    treatment next, step 52.) No topic-count change (313). Rebuilt all 60 Practice Test papers
    (density_H can now carry a diagram) — all 100 marks. Backend suite 983 → 984 (+1: density_H
    dimensions questions carry a shape diagram, three kinds, no prose dimensions). Review PDFs
    regenerated (313/323) and sent. Committed and pushed.

52. Same review thread — the user asked for `pressure_H` to get the same treatment as
    `density_H` (step 51). Reworked `generate_pressure_higher`'s `from_dimensions` branch (+
    modelled twin): new `_pressure_dimension_shape(rng)` picks a **rectangle / square /
    right-triangle** base, returns the contact area + area-working step + a `DiagramSpec`
    (`draw_rectangle` for rectangle/square, `draw_triangle_area` for the triangle — dimensions
    on the diagram, independent repeated-addition area cross-check kept). Prompt reworded to
    "The {obj} below exerts a pressure/force of … on its base. Find the …", dimensions only on
    the shape. `unit_conversion` flavour unchanged (no diagram). No topic-count change (313).
    Rebuilt all 60 Practice Test papers — all 100 marks. Backend suite 984 → 985 (+1: pressure_H
    dimensions questions carry a base-shape diagram, three kinds, no prose dimensions). Review
    PDFs regenerated (313/323) and sent. Committed and pushed.

53. Same review thread, a large batch on the whole **Transformations** group (reflect/rotate/
    translate/enlarge × complete/describe, plus combined). Global rules (all transformation
    diagrams): vertices are never dotted or labelled - each shape is identified by a single
    whole-shape letter (A original, B image) drawn at its centroid; prompts use just those
    letters ("Rotate shape A 180° about (0, -1)", not "shape ABCD"). Implemented in
    `draw_grid_transformation` (`diagrams.py`): removed the vertex `Circle` dots; added an
    `image_same_color` param so "describe" diagrams draw BOTH shapes black (distinguished only by
    the A/B label) while "complete" solution diagrams keep the image a distinct colour to
    highlight the answer. New helpers in `transformations.py`: `_transform_diagram` (builds the
    standard blank-vertex + A/B spec, never drawing a centre dot or translation arrow),
    `_image_coords` (coordinate-list answers, no vertex letters), `_polygons_intersect`
    (edge-cross + point-in-polygon), and `_fmt_vector` now returns a real `\colvec{}{}` column
    vector everywhere. Per-topic: all "complete" topics (reflect/rotate/translate/enlarge F+H)
    switched to shape labels + coordinate-list steps/answers, and rotate/enlarge complete no
    longer draw the centre on the diagram (the student plots it from the text);
    translate_complete's vector renders as a column vector. All "describe" topics dropped
    "shown on the grid" and draw both shapes black; `translate_describe` gained its missing A/B
    labels; `rotate_describe_H` rerolls until the two shapes don't overlap
    (`_random_rotate_describe_instance`, intersecting rate ~0%, well under the requested 5%).
    New topic **`transform_enlarge_describe_F`** (313→314): positive scale factors only
    (3/2, 5/2, 1/2, 1/3, 1/4), built by scaling a small base template by the factor's
    numerator/denominator so integer grid points are guaranteed (the general
    `_random_enlarge_instance` can't - it needs every vertex offset divisible by the
    denominator, which almost never happens with no integer factor to fall back on); wording is
    90% "maps A onto B" / 10% "maps B onto A" (the reverse answer is the reciprocal scale
    factor). **`combined_transformations_H` fully redesigned** from "describe the single
    equivalent transformation" to "apply 2-3 transformations yourself and draw the final image":
    `_random_combined_sequence` applies a random mix of reflect/rotate/translate/enlarge steps,
    checking every intermediate fits the grid and verifying each step via the existing
    `_verify_*` helpers; the question shows shape A only, the solution shows the final image B.
    The old single-equivalent-transformation machinery (`_ComboInstance`, `_random_combo_*`,
    `_ROTATE_COMBO_PAIRS`, `_build_combo_instance`) was removed. Rebuilt all 60 Practice Test
    papers (diagram schemas changed + topic #314 in the pool) - all 100 marks. Backend suite
    985 → 981 (the redesign replaced 7 combo-internal tests with 3 behavioural ones; the new
    topic is covered via the generic generator/modelled lists). Review PDFs regenerated (314/326)
    and sent. Symmetry topics (a separate Geometry group) were left untouched. Committed and pushed.

54. New session, a **coverage-gap audit against maths4everyone.com** (the user asked to read
    every GCSE Foundation & Higher worksheet topic on that site and advise on gaps), followed
    by "do all 5" - build the genuine gaps found. The site is JS-driven and its listing is
    virtualised, so the taxonomy was pulled cleanly by POSTing its own data endpoint directly
    (`/data/resources/r-worksheets.php`, params `sFilter` = f/h and `tFilter` = 1-9) from the
    in-app browser's `javascript_tool` and parsing the returned `.h-topic`/`.h-subtopic`/
    `.h-skill`/`.sub-skill` HTML fragments - all 18 tier×category combinations in two fetches.
    The site's GCSE collection turned out far thinner than this app; cross-referencing every
    listed topic against the 314-topic registry (verified against the actual code, not memory -
    e.g. `expand_single_bracket_F`/`factorise_common_factor_F`/`fractions_mixed_number_arithmetic_H`
    already existed, so were NOT gaps) left 5 genuine gaps, all built this step (314 → 320):
    - `collect_like_terms_F` (new `simplify_expressions.py`, Algebra "Expressions, Formulae,
      Equations & Identities" group): simplify by collecting like terms (single-var, with
      constants, two-var a/b, x^2+x). Answer built by summing coefficients per symbol; verified
      independently via `sp.expand(original - answer) == 0`. Uses a/b (upright) for two-var and
      x (italic) for the rest, since mathtext only italicises x/n - mixing would look inconsistent.
    - `midpoint_of_segment_F` + `distance_between_points_H` (new `coordinate_geometry.py`, new
      Algebra group "Coordinate Geometry"): midpoint by averaging coordinates (verified via the
      vector-equality definition M-A == B-M); distance via Pythagoras giving a simplified surd
      (points rerolled so d² is never a perfect square, verified against `math.hypot`). **Two
      cosmetic fixes were made after rendering, not caught by tests**: the generic formula line
      `(x2 - x1)²` rendered with x italic but y plain (mathtext quirk) - reworded to
      "horizontal/vertical gap"; and the "simplify the surd" step showed a silly "√(1² × 185)"
      when the surd was already simplest (k=1) - special-cased to "already in its simplest form".
    - `surds_add_subtract_H` (added to `powers_roots.py`, same "Powers, Roots & Indices" group):
      add/subtract like surds and simplify-then-combine (√8 + √18 = 5√2). Verified numerically
      via `math.sqrt` against the answer coeff×√root.
    - `circle_parts_F` (new `circle_parts.py` + new `circle_part` diagram kind in `diagrams.py`,
      new Geometry group "Parts of a Circle"): name the highlighted part (radius/diameter/chord/
      tangent/arc/sector/segment/circumference/centre). A recall topic - no verify() (like
      Constructions/3D-properties), `question_count=len(_PARTS)`=9. The diagram draws one feature
      in ACCENT with NO text labels (so nothing can overlap); segment uses the fill-then-erase
      trick (wedge minus centre-triangle). Rendered and eyeballed all 9 parts - clean.
    - `set_listing_F` (added to `data_handling.py`, "Sets and Counting" group): list a set from a
      property or set-builder notation (even/odd/multiple/square/factors), roster form. Distinct
      from `set_notation_F` (which is Venn set-operations). Verified via a closed-form count
      independent of the element-by-element scan; set-builder form carries the range so it's finite.
    Registry wired; the 4 hardcoded `314` count assertions bumped to `320`. New test files
    (`test_simplify_expressions.py`, `test_coordinate_geometry.py`, `test_circle_parts.py`) plus
    additions to `test_powers_roots.py`/`test_data_handling.py`. Backend suite 981 → **1000**;
    frontend unaffected (65/65 - new groups render generically). Practice Tests NOT rebuilt (no
    existing diagram schema changed). Review PDFs NOT regenerated (this wasn't a review batch).
    Committed in c6cce8f.

55. Same session, a review-feedback batch of 5 diagram/wording items (all fixed by rendering
    real PDFs and iterating, per the standing "render and look closely" discipline - no new
    tests added, backend stays 1000/1000):
    - `area_semicircle_compound_F`/`_H`: prompt was a verbose prose description of the shape's
      dimensions even though the diagram already shows them. Trimmed to "Find the total area of
      the following compound shape, ..." - F now also uses the shared dp/sf `rounding` engine
      ("correct to {phrase}", matching `area_mixed_compound`); H keeps its exact-in-terms-of-π
      form (that's the whole F/H distinction), just reworded to "...giving your answer in terms
      of π." Dimensions read off the diagram (semicircle diameter = the labelled rectangle width).
    - `area_subtract_compound_F`/`_H` (`draw_l_shape` shade_frame branch): the hole's height
      label floated in the middle of the white hole. Moved both hole dimension labels into the
      SHADED frame hugging their side (width just below the hole, height just right of it), with
      a fallback to just-inside-the-hole for a very thin frame (inner ≈ outer).
    - `arc_length_F`/`_H`, `area_sector_F`/`_H` (`draw_sector`): radius label moved from inside
      the wedge to just OUTSIDE it, left of the fixed vertical (90°) radius edge - that strip is
      always outside the wedge (a sector spans [90-angle, 90], never above 90°), so it never sits
      on the fill for any angle incl. reflex. Verified across 30/90/150/240/300°.
    - `angles_straight_line_H` (`draw_angle_line`): a wide algebraic label like "(5x - 30)°" in a
      moderately narrow wedge sat on top of the middle ray. Replaced the fixed radius-by-band
      rule with a width-aware analytic one: place the label at the radius where its measured
      half-width clears both rays (R = (half_w+6)/sin(v/2)), or just BEYOND the ray tips (open
      space) when the wedge is too narrow to fit it inside. Verified across seeds + around_point
      regression.
    - `angles_triangle_H`, `angles_exterior_H`: the algebraic angle label sat far from its own
      angle (the analytic clearance pushed a wide label ~120px down an edge to fully clear both
      sides). Added a `compact` mode to `_place_angle_label` (caps the push so the label sits just
      beyond the arc, near the angle - accepting a light touch of the sides, as exam papers do) for
      `draw_triangle_angles`/`draw_polygon_angles`; and reduced `draw_exterior_triangle`'s `_inset`
      factor cap (0.85 → 0.55) so the interior algebraic label sits by its vertex, not the centroid.
    Practice Tests NOT rebuilt (no diagram param SCHEMA changed - only label positions/prompt
    text, both backward-compatible; frozen papers still render). Committed in c6cce8f.

56. Same session, a review-feedback batch of 4 items on the 3D and triangle-rule diagrams (all
    verified by rendering real PDFs; no new tests, backend stays 1000/1000):
    - `pythagoras_3d_H`: the depth ("15 cm") label sat ON the slanting depth edge b->c. Fixed in
      `draw_cuboid` by offsetting the length label PERPENDICULAR to that edge (outward, down-right)
      so the edge line no longer runs through the number. Prompt trimmed to just
      "Find the length of ag, correct to {phrase}." (ag = the a<->g space diagonal, endpoints
      lettered on the diagram; dimensions read off the diagram).
    - `trig_3d_H`: prompt trimmed to "Find the angle gac, correct to 1 decimal place." (three-
      letter notation, vertex a in the middle). Added a `show_base_diagonal` param to `draw_cuboid`
      that draws the base diagonal a->c, so the right-angled triangle a-c-g for angle gac is fully
      visible (base diagonal ac + vertical edge cg + space diagonal ag).
    - `sine_rule_H`, `cosine_rule_H`: removed the "In triangle ABC, ... = ..." prose so the prompt
      reads only e.g. "Find the length of side b, correct to 3 significant figures." /
      "Find the size of angle A, ...". Values are now read off the diagram: added a `show_vertices`
      param to `draw_general_triangle` (letters the vertices A/B/C, grounding "side b"/"angle B"),
      the given sides/angles show their numbers, the unknown SIDE is left unmarked, and the unknown
      ANGLE is drawn as a BARE ARC (via passing angle_X_label="" - `draw_general_triangle`'s angle
      loop now draws an arc for any non-None label, empty string => arc with no text, so there's no
      letter clash with the vertex label). Both worksheet + modelled-example prompts updated.
    - `triangle_area_sine_rule_H`: a small included angle made `draw_general_triangle` a razor-thin
      sliver that crammed the labels. Since the figure is "not to scale", `draw_general_triangle`
      now falls back to a legible plausible scalene shape whenever the constructed triangle's
      smallest angle is < 28 deg (new `_triangle_min_angle` helper) - the true angle value still
      shows in its label. (This also benefits any sine/cosine case with a very acute angle.)
    Practice Tests NOT rebuilt (only optional new params + label/prompt changes, all backward-
    compatible - frozen papers still render). Committed in c6cce8f.

57. Same session, a review batch of 3 items on the 3D-solid diagrams/prompts (all verified by
    rendering real PDFs; no new tests, backend stays 1000/1000):
    - `plans_and_elevations_F`: the three blank grids (front/side elevation + plan) the student
      draws into were only ~6 squares - too few to draw an up-to-8 cm solid to scale. Enlarged
      `draw_plans_and_elevations_blank` to 10x10 squares at ~13pt each (real squared-paper size);
      `render_diagram` places the composed Drawing at natural size (no down-scaling while it fits
      the page width), so the bigger boxes actually render bigger. Also centred the solid sketch
      above the grid in `draw_plans_and_elevations_question`.
    - `volume_surface_area_cube_F`: the cube looked like a long box because `draw_cuboid` drew the
      receding depth at its full (equal) edge length. For `is_cube`, foreshorten the depth to
      ~0.55x the front edge (standard cabinet-projection convention) so it reads as a cube.
    - **Every volume/surface-area prompt standardised** to "Here is a {shape}. Find its
      {volume|surface area}[, correct to {phrase} | in terms of π]." with the dimensions read off
      the diagram (per the reviewer's rule "for all volume and surface area"). Covers cuboid, cube,
      triangular prism (+ a new `hyp_label` on `draw_triangular_prism` so the surface-area case can
      read the hypotenuse off the figure), cylinder F/H, cone, sphere/hemisphere, square-based
      pyramid, and frustum. The two `compound_3d_*` topics were left as-is (a compound of two
      solids has no single shape name, so "Here is a X" doesn't fit).
    Practice Tests NOT rebuilt (no diagram param SCHEMA changed - `hyp_label`/`is_cube` are
    optional params, the rest are prompt-text/label changes; frozen papers still render). Committed
    in 9ba81d8.

58. New session, a single review item on the two Histograms topics (`histogram_plot_H`,
    `histogram_interpret_H`): the user's complaint was that to answer an "interpret" question the
    student had to *estimate* the frequency density off the graph, because densities were messy
    `frequency ÷ width` values (e.g. 3.6, 0.8, 2.2) that landed between the coarse 0.5 gridlines -
    and asked for "smaller SQUARES", offering to be shown example ideas. Rendered the current
    diagram to confirm the diagnosis, then built three design mockups (fine 0.2 squares / coarse
    0.5 squares / very fine 0.1) and sent them via `AskUserQuestion`; the user picked the fine
    **0.2-square** option (real GCSE graph-paper look).
    - **Data** (`app/topics/histograms.py`, `_random_histogram_table`): frequencies are now
      constructed as `rng.randint(2, 13) * (width // 5)` so each class density (frequency ÷ width)
      is an exact multiple of **0.2** (density = k/5), while every frequency stays a whole number
      (every width is a multiple of 5). This guarantees every bar top lands exactly on a 0.2
      gridline - the density is read by *counting squares*, never estimated between lines. The
      existing independent `density × width == frequency` check still holds exactly.
    - **Diagram** (`app/pdf/diagrams.py`, `draw_histogram` - the one function behind the `histogram`
      interpret diagram, the `histogram_question` blank plotting grid, and the plotting solution):
      rebuilt from the generic `_draw_stats_axes(square_grid=True)` path (which used a `major/2`
      minor step, i.e. 0.5 squares) into a dedicated fine squared-paper grid drawn directly - each
      small square is **0.2** in frequency density (y) and **2.5** in the x quantity, drawn at a
      fixed 10px so cells are visually square; minor gridlines every square, darker major lines +
      numbered ticks every 1.0 (y) and every 10 (x). Also fixed the old clipped "Frequency density"
      / x-axis labels (the generic path anchored the y-label hard against the left edge, clipping it
      to "y density"). `_nice_tick_step`/`_grid_minor_step`/`square_grid` were left untouched - other
      stats charts (bar/box/scatter/cumulative-frequency) still use them; only `draw_histogram` opted
      out.
    - Verified by rendering real diagrams across several seeds, the full plotting-question composite
      (table + blank grid), and a full worksheet PDF (question + worked solutions) - every density on
      a gridline, arithmetic exact, labels uncropped. Added 1 regression test
      (`test_every_density_is_a_multiple_of_0_2_...`) guarding the invariant. Backend suite 1000 →
      1001; frontend unaffected (65/65); no topic-count change (still 320). **Practice Tests NOT
      rebuilt** - no frozen paper uses a histogram topic (confirmed via grep) and the diagram param
      schema is unchanged, so nothing to regenerate. Review PDFs regenerated (320 question / 331
      answer pages) and sent. Committed and pushed.

59. Same review thread, a broad user request to review **all graphs** with the same "can a student
    actually read/plot the values" lens as the histograms. Rendered a real example of every graph
    family first (function/plotting graphs, read-off-graph algebra, all stats charts) and found four
    recurring problems, reported with options + clarifying questions before touching code: (1) coarse
    gridlines on large/steep ranges (the fallback in `_draw_scaled_axes` drew lines only at the
    numbered nice-tick step - e.g. every 5, or every 50 on trig - with nothing between, so you
    couldn't plot y=-4 or read the `simultaneous_graphically` intersection); (2) a **flat-cap clamp
    bug** (curves/lines drawn flat where they ran past the window, via a per-point
    `max(min(f(x),y_max),y_min)` clamp); (3) axis-title clipping on almost every stats chart +
    distance/velocity-time ("Frequency"→"equency", "Velocity (m/s)"→"locity (m/s)", etc.); (4) coarse
    reading grids on cumulative-frequency & box plots. Planned in plan mode
    (`C:\Users\James\.claude\plans\graceful-giggling-cook.md`).

    **Mid-implementation the user interrupted, emphatically: cells must be SQUARE, never rectangles,
    even if that makes the graphs large.** A first attempt at the fallback (fill each axis
    independently → rectangular cells) was scrapped. The final `_draw_scaled_axes` rework guarantees
    **square pixel cells always**: a "nice" MAJOR step per axis (numbered, heavier line) + one shared
    `px_per_major` (so major cells are square) + a shared subdivision factor k for the fine MINOR grid
    (so minor cells stay square too). A lopsided range is absorbed by a larger major step on the long
    axis (cubic → square overall, numbered every 5 with a minor line every 1; trig → 1 square = 10°×0.2,
    still square pixels) rather than by stretching cells. Confirmed via `AskUserQuestion` (after showing
    compact-vs-grown mockups): **compact** size (square cells, keep the current ~210px footprint) and
    **different units per axis is fine** (square pixels, not literal 1:1 units - matching the histograms
    they'd already approved). This subsumed the planned "generator range-capping" phase - the engine now
    always yields a fine readable grid for any range (lines every 1-2 units even on big ranges, which is
    how real exam papers scale big graphs), so no generator ranges were changed.

    Other fixes: **flat-cap** replaced with true window clipping (`_clip_curve_segments` in
    `draw_function_graph` + `draw_linear_graph_pair` - splits the sampled curve into in-window segments
    with the exact boundary crossing inserted, so it stops cleanly at the edge). **Axis titles**: a new
    `_vertical_label` (rotated 90° Group) draws a long descriptive y-title up the widened left margin and
    the x-title centres below, in BOTH `_draw_scaled_axes` and `_draw_stats_axes` (a bare "x"/"y" keeps
    the old compact label, so pure coordinate graphs are untouched). **Stats reading grids**:
    `_grid_minor_step` gained a `divisor` param; `cumulative_frequency`/`box_plot` pass `fine_grid=True`
    (finer minor squares so median/quartiles read closer to a line).

    **Deliberately NOT done** (agreed scope + a deferred offer): the STATS charts keep their reading
    grid with rectangular cells - only the coordinate/plotting graphs were made square, since that's
    where the "never rectangles" instruction was aimed and the stats scope the user agreed earlier was
    labels + finer CF/box grids. Squaring cumulative-frequency/scatter/time-series is offered as a
    follow-up (see the deferred note near the top of this file); bar/box have a categorical axis so
    square cells don't apply.

    Verified by rendering every graph family across seeds (all square-celled, no flat caps, labels
    uncropped, small-range coordinate graphs like circle/inequality unchanged) and a real frozen
    Practice Test paper (function_graph + piecewise) to confirm backward-compat. Added 3 regression
    tests (`_clip_curve_segments`; a cubic curve never flatlines at the window edge; `_draw_scaled_axes`
    minor cells are square). Backend suite 1001 → 1004; frontend unaffected (65/65); no topic-count
    change (still 320). **Practice Tests NOT rebuilt** - all changes are rendering-only and
    backward-compatible (no new required diagram params), so the 60 frozen papers render on the new
    engine unchanged (verified). Review PDFs regenerated and sent. Committed and pushed.

## Environment gotchas (Windows, this machine specifically)

Python, Node, and GitHub CLI were **not** installed on this machine when this project
started. They were installed mid-session:

- **Python 3.12**: installed via `winget install Python.Python.3.12`, lives at
  `C:\Users\James\AppData\Local\Programs\Python\Python312`. A Windows Store alias
  shadows `python` on PATH, so the backend venv is the reliable way to get a working
  interpreter (see below).
- **Node.js**: winget's installer needed admin elevation that couldn't be granted
  non-interactively, so a **portable** Node zip is used instead, extracted to
  `C:\Users\James\AppData\Local\NodePortable\node-v22.14.0-win-x64\`. `npm`/`npx`
  work from there; `node`/`npm` are **not** on PATH by default in a fresh shell —
  prepend that dir to `$env:Path` first, e.g.:
  ```powershell
  $env:Path = "C:\Users\James\AppData\Local\NodePortable\node-v22.14.0-win-x64;" + $env:Path
  ```
- **GitHub CLI**: installed via winget (`winget install --id GitHub.cli`), but **not
  on PATH** in a fresh Bash/PowerShell tool session — `gh` alone gives "not
  recognized"/"command not found" even right after a successful install, and
  `winget list --id GitHub.cli` can even come back empty if it was reinstalled since
  (don't take that as proof it's missing; check the real path first). Call it via its
  full path instead: `& "C:\Program Files\GitHub CLI\gh.exe" <args>` in PowerShell, or
  the equivalent in Bash. Auth persists across reinstalls (keyring-backed), so
  `gh auth status` via the full path should already show logged in — no need to
  `gh auth login` again.
- **Console/terminal Unicode**: printing strings containing `⁻¹`, `°`, etc. straight to
  a PowerShell/cp1252 console can throw `UnicodeEncodeError` even though the *PDF*
  renders those characters fine (or, in the `⁻` case specifically, doesn't — see the
  Gotcha above). Use `PYTHONIOENCODING=utf-8` for ad hoc `python -c` debug prints, and
  don't take a console encoding error as evidence the PDF output is broken — always
  render an actual PDF and screenshot/inspect it to check.

## Running it

**Preferred**: use the Browser pane's `preview_start` tool with `{name: "backend"}` /
`{name: "frontend"}` — `.claude/launch.json` already has both configured with full
absolute paths (works around the PATH issues above, no manual env setup needed).
Neither server has `--reload`, so **restart the backend server** (`preview_stop` then
`preview_start` again) after editing any backend `.py` file before testing in the browser.

**Manual equivalent**, if needed:
```powershell
# Backend (from repo root)
backend\.venv\Scripts\python.exe -m uvicorn --app-dir backend app.main:app --port 8000

# Frontend (from repo root, after prepending NodePortable to PATH as above)
node "C:\Users\James\AppData\Local\NodePortable\node-v22.14.0-win-x64\node.exe" `
     frontend\node_modules\vite\bin\vite.js frontend --port 5173
```
Backend: http://localhost:8000 (docs at `/docs`, topics at `/api/topics`, sections at
`/api/sections`). Frontend: http://localhost:5173.

The backend venv (`backend/.venv`) already has all of `requirements.txt` installed
(includes `pymupdf`/`fitz`, handy for rendering a generated PDF to a PNG to visually
inspect it — see "Verifying new topics" below).
The frontend (`frontend/node_modules`) already has all deps installed including
Vitest + React Testing Library.

**Regenerating the Practice Tests data**: the 20 papers under
`backend/app/practice_tests/data/*.json` are committed, static content (see "Current
state") — the API serves them as-is, nothing is generated at request time. Only
re-run `backend\.venv\Scripts\python.exe -m app.practice_tests.build` (from `backend/`)
if you deliberately want to regenerate them (e.g. after editing `topic_selection.py`'s
weighting/priority tables or `mark_scheme.py`'s marking rules) — it overwrites all 20
files and is fully deterministic (re-running with no code changes reproduces
byte-identical output). Restart the backend afterward to pick up the new data (the
loader reads the JSON files once at import time).

**Regenerating the all-topics aesthetic-review PDFs** (chronology step 34): the user is
doing a broad aesthetic-review pass across every topic, working from two generated PDFs
(one question - and, in the answers version, its full worked solution - from every one of
the 296 topics, one per page, headed `Section › Group › Topic Name (Tier)`). Re-run
`backend\.venv\Scripts\python.exe -m scripts.generate_review_pdfs` (from `backend/`)
whenever a change should be reflected in a fresh comparison copy - it overwrites
`all_topics_review_questions.pdf`/`all_topics_review_answers.pdf` in `backend/` and is
fully deterministic (fixed seed `42` in `scripts/generate_review_pdfs.py`, so the same
questions reappear across reruns for a clean before/after comparison). The script reuses
`app/pdf/renderer.py`'s own `_question_block`/`_solution_block` and `app/pdf/styles.py`'s
`build_styles()` directly rather than reimplementing them, so it's always a true preview
of the app's actual current styling - no separate script logic to keep in sync if
`renderer.py`/`styles.py` change. The script itself is committed; the two generated PDFs
are deliberately left untracked (deliverables, not source).

## Testing

```powershell
# Backend — from backend/, with the venv
.\.venv\Scripts\python.exe -m pytest -v

# Frontend — from frontend/, with NodePortable on PATH
npx vitest run
```

### Verifying new topics visually (don't skip this)

Passing tests is not enough — this session found a real rendering bug (the `⁻` glyph
issue) that every test suite happily missed, because tests check *values*, not *how
they render as PDF glyphs*. After adding/changing a topic, render an actual worksheet
and look at it:

```python
import fitz
from app.core.registry import list_topics
from app.worksheet.builder import build_worksheet
from app.pdf.renderer import render_worksheet

t = {t.id: t for t in list_topics()}["some_topic_id"]
ws = build_worksheet(t.id, t.fixed_tier)
pdf = render_worksheet(ws)
doc = fitz.open(stream=pdf, filetype="pdf")
doc[0].get_pixmap(dpi=110, clip=fitz.Rect(0, 0, 595, 320)).save("scratch.png")
# also render the "Worked Solutions" page (search doc[i].get_text() for that string) -
# that's where inverse-trig / cos^-1 / f^-1 style text tends to live
```
Then `Read` the PNG. Do this for question *and* solutions pages for anything using
exponents, inverse notation, or a new diagram kind. Clean up scratch files afterward.

## Architecture patterns to follow when extending this

- **One topic = one `generate_xxx(tier, rng) -> Question` function + one
  `TopicDefinition`** in `backend/app/topics/<module>.py`. Register new topics in
  `backend/app/core/registry.py`'s `_TOPIC_LIST` (declared order = display order,
  not alphabetical). Each topic is tier-exclusive (`fixed_tier=Tier.FOUNDATION` or
  `.HIGHER`) — see `TopicDefinition.fixed_tier` in `app/topics/base.py` for the
  (currently unused) `None` = "supports both tiers via a toggle" escape hatch.
- **Every topic id ends in `_F` (Foundation) or `_H` (Higher)** — a streamlining
  done to all 305 ids (see chronology step 43): the id is `<base>_F`/`<base>_H`,
  matching `fixed_tier`, e.g. `bearings_cosine_rule_H`, `linear_two_step_F`. New
  topics MUST follow this. The suffix is the id's ONLY tier marker — don't also put
  `_foundation`/`_higher` in the base. NB the generator/modelled-example *function*
  names were deliberately NOT renamed (still `generate_bearings_cosine_rule`, etc.),
  and `dedup_key` prefixes keep their own short mnemonics — only `id=`/`topic_id=`
  strings carry the `_F`/`_H` scheme.
- **Foundation/Higher overlap content gets two separate topic IDs**, not one
  parameterised topic — e.g. `linear_both_sides_F` alongside `linear_both_sides_H`,
  `trig_missing_side_F` alongside `trig_missing_side_H`. The Foundation sibling is typically a positive-
  coefficients-only / no-rearranging-required variant of the same generator logic
  (mirrors the existing `pythagoras.py` triple-vs-surd pattern). When adding a new
  topic, check whether it's genuinely Foundation+Higher overlap content on the real
  AQA/Edexcel specs before making it single-tier — see the chronology's step 6 for
  the audit that was already done (there's more possibly worth doing, see "Ideas"
  below).
- **Always verify independently.** Every generator asserts its own answer is correct
  using a *different* computation path than the one used to build the steps. Patterns
  used across the codebase: `algebra_utils.solve_linear_with_steps` + substitution
  check (`linear_equations.py`); brute-force `itertools.product` sample-space
  enumeration (`probability.py`); stdlib `statistics`/`Decimal` cross-checks
  (`statistics.py`/`decimals.py`); coordinate-geometry cross-checks — build the shape
  from coordinates and re-measure with the distance formula / dot product / shoelace
  formula (`triangle_rules.py`, `vectors.py`); `sympy.solve`/`linsolve` as an
  independent solver (`simultaneous_equations.py`, `sequences.py`'s quadratic nth
  term via a 3×3 system). Raise `ValueError` on mismatch — never silently emit a
  wrong answer. If a generator has a nontrivial internal rejection rate (e.g. an
  edge case near a domain boundary), wrap it in a bounded retry loop
  (`for _ in range(N): ... else: raise`) rather than letting `ValueError` escape to
  the caller — see `pythagoras.py`'s `generate_surd_hypotenuse` or
  `triangle_rules.py`'s `generate_sine_rule` for the pattern. `build_worksheet`
  itself also retries on `ValueError`, but a topic with a high rejection rate should
  still self-heal internally, and a **test that calls the generator directly in a
  raw loop with no try/except will fail** if it doesn't (this happened once this
  session with `sine_rule` — 500-trial smoke test caught it before it reached tests).
- **Exact arithmetic only** — `sympy.Rational`, `fractions.Fraction`, or
  `decimal.Decimal`, never raw floats for anything that ends up in an answer.
  `sp.nsimplify` was tried early on and **removed** — it can hallucinate bogus
  irrational closed-forms for exact rationals; use `sp.Rational(x)` directly instead.
  Exception: genuinely irrational real-world results (trig ratios, `sqrt`) are fine
  as `float`/`math.sqrt`/`math.sin` etc., rounded via `Decimal.quantize` with
  `ROUND_HALF_UP` for display — see `pythagoras.generate_hypotenuse_decimal` or any
  `trigonometry.py` generator.
- **Math text convention** (see `mathtext.py` in the Current State section above):
  write plain ASCII in generator strings — bare `x`/`n` for variables, `^n` for
  exponents (including negative, e.g. `10^-3`), `^-1` for inverse-function/inverse-
  trig notation, `^(num/den)` for a fractional exponent (e.g. `x^(1/4)`, raised as
  one flat unit — see "Fractional exponents in mathtext.py" above), `num/den` for
  standalone fractions (e.g. `3/4`), `x_n`/`x_(n+1)` for a real subscript (parens
  stripped, not shown — see chronology step 37; currently only `iteration.py` uses
  this), `\plain{X}` to opt a bare letter OUT of the default x/n italics for the rare
  case it's a plain notational placeholder rather than a real variable (e.g.
  `ratio_1_to_n`'s "1:n" — see chronology step 38). Never hand-write Unicode
  `²`/`⁻¹`/italics in generator code (with the sole exception of `²`, which IS safe
  as a literal — see the Gotcha above for exactly what is/isn't). `x` and `n` are
  both italicised as of chronology step 16; `a`/`b` (vectors) are NOT — see the
  "Ideas" list for why that one's deliberately deferred, not just unimplemented.
- **Diagrams**: a topic that wants one sets `diagram=DiagramSpec(kind=..., params={...})`
  on its returned `Question`, using the exact same random values already used for the
  prompt (see any `area_perimeter.py`/`angles.py`/`pythagoras.py` generator). Add new
  diagram *kinds* as a `draw_xxx(params) -> Drawing` function in `app/pdf/diagrams.py`
  and register it in `_RENDERERS`. For triangles/circles/graphs that aren't drawn to
  actual scale (schematic only), add the `_not_to_scale(d)` "Diagram NOT accurately
  drawn" caption — matches real exam-paper convention and sidesteps needing exact
  proportional geometry for arbitrary random values (see `draw_general_triangle`,
  `draw_circle_angle_centre`, `draw_parabola`, `draw_linear_graph_pair`). A diagram
  whose answer would otherwise be visible in the picture (e.g. "solve graphically")
  should show a placeholder like `"?"` instead of the real value — see
  `simultaneous_equations.generate_simultaneous_graphically`. Always pass fully
  pre-formatted label strings (with units, and the real algebraic expression if the
  value is unknown-but-not-`x`) rather than bare numbers or a hardcoded `"x"` — see
  the "Algebraic expressions and units on diagrams" bullet above for two real bugs
  this caught. If a diagram kind's labels have only ever been short, adding a wider
  one can expose an untested overlap (anchor direction and/or vertex-inset distance
  may need to scale with `stringWidth`) — see the "Label-anchor-direction" bullet
  above; render and visually check, don't just trust the unit tests.
- **Frontend**: `useSections`/`fetchSections` is the single source of truth for the
  nested section→group→topic tree; `TopicCard` handles its own generate/download flow
  per-card via `useGenerateWorksheet`. No router library — view switching in `App.tsx`
  is plain `useState` (home / selected section / search results). Within a section,
  `SectionView.tsx` adds a Foundation/Higher tier-picker step before showing groups —
  filters `section.groups[].topics` by `fixedTier` client-side.
- **Tests**: one test file per topic module in `backend/tests/unit/topics/`, following
  the existing pattern — a `GENERATORS` list of `(function, tier)` pairs, a 200-to-400-
  trial "produces valid verified questions" test, a dedup-key-variance test, and a
  topic-metadata test. Geometry (and some Algebra) topic tests additionally assert
  `question.diagram` matches the expected kind/params. **Watch the dedup-key state
  space**: a topic whose dedup_key only depends on a handful of discrete choices (e.g.
  a small curated ratio/shape list) can fail to produce 20 unique questions for a real
  worksheet even though every individual generation is valid — this happened with
  `geometric_vectors` (only 9 ratio pairs → capped at 9 unique questions) and was
  fixed by widening the ratio list to 19 and adding a second "target vector" axis of
  variation (57 total combinations). When adding a topic with a bounded/curated choice
  set, sanity-check `len({distinct dedup_keys}) >> 20` (or `>> question_count` for a
  topic with a smaller override, e.g. the 5-question Plotting Graphs topics just need
  `>> 5`) before considering it done —
  `test_all_topics_produce_their_full_distinct_question_count_at_their_fixed_tier` in
  `test_worksheet_builder.py` will catch it, but better to catch it while writing the
  generator (a quick 300-trial loop counting `set()` size, as used throughout this
  session, works fine as a manual check).

## Ideas for a future session (not started, no commitment made)

- The entire user-supplied Geometry expansion (Phases 1-4b) is complete — see
  chronology steps 23-27 — and its one genuine loose end, compound-3D
  surface area, was built in step 29. One small loose end remains: Phase 3's
  congruent triangle proof topic covers SSS/SAS/ASA/RHS via an 18-entry
  curated bank (see step 25) — a Foundation `trig_mixed`-style sibling
  covering *identifying* similar (not congruent) triangles, or a "prove NOT
  congruent" variant, were not requested and are not built.
- The from-scratch Foundation/Higher curriculum audit (step 13) flagged a handful of
  **lower-confidence** candidates that were reported but deliberately *not* built,
  pending more research or a product decision: `velocity_time_interpret`
  (the gradient/acceleration reading might be Foundation-appropriate; only
  "area under graph = distance" is clearly Higher-only — could split rather than
  duplicate), `fractions_mixed_number_arithmetic` (a Foundation sibling with
  smaller/simpler mixed numbers), `ratio_combine` (a friendlier-number Foundation
  version), `trig_mixed` (a Foundation version combining the already-Foundation
  side/angle topics). Don't build these without discussing first — the audit's
  confidence in each was explicitly lower than the 11 that were built.
  (`probability_combined_dice`, also originally on this list, was confirmed
  in step 29 to already exist — not a gap, removed from this list.)
- Stem-and-leaf diagrams and standard deviation are real GCSE Statistics content not
  covered by the Probability/Statistics topic list the user supplied (chronology steps
  17–18) — never explicitly requested, so not built, but worth flagging if a future
  session wants to round out Statistics further. (Scatter graphs & correlation, also
  originally on this list, were built in step 31 — removed from here.)
- Step 31's full AQA-spec gap audit reported medium- and low-confidence gaps that were
  **not** built (only the 7 high-confidence ones were) — don't build these without
  discussing first, since the audit's confidence in each was explicitly lower than the
  7 that were built: box plots and IQR being Higher-only in this app despite AQA
  listing both as Foundation "additional content" too (a tier-placement gap, same
  pattern as the audits in steps 6/9/13/20); conditional probability specifically via
  Venn diagrams or two-way tables (only the "pick two without replacement" tree-style
  version exists); pictograms, vertical line charts, and frequency trees (all
  relatively minor/basic). (Several other items originally on this list — substitution
  into formulae, geometric/Fibonacci-type sequences, map scales/scale drawings,
  perpendicular from/at a point, combining multiple transformations — were confirmed
  as genuine gaps by step 32's independent OCR-spec audit and built then; removed from
  this list.)
- Step 32's full OCR J560-spec gap audit reported 5 medium-confidence gaps that were
  **not** built (only the 10 high-confidence ones were, per the user's explicit choice)
  — don't build these without discussing first: proving two triangles similar (via
  AA/SSS/SAS criteria, distinct from `ratio_shape_similar_foundation`/`_higher`, which
  only calculate a scale factor — a `congruent_triangle_proof.py`-style sibling would
  be the natural pattern); reverse-direction plans and elevations (`plans_elevations.py`
  currently only goes 3D-solid → 2D views; the spec also wants views → construct/
  identify the solid, e.g. on isometric paper — a genuinely new diagram engine, not a
  small extension); quadrilateral angle properties (finding angles via a kite/rhombus/
  parallelogram's own diagonal/side properties, distinct from the existing area/
  perimeter and symmetry topics for the same shapes); estimating the gradient of a
  genuinely curved graph via a tangent (`velocity_time_interpret` only handles
  straight-line segments — also flagged by the step-13/31 audits, still not built);
  reading approximate roots of a quadratic directly off its plotted graph (`plot_
  quadratic` only asks to build the table and plot the curve, never to read roots
  back off it).
- Saved worksheet history, mixed-topic revision papers, user accounts.
- Deploying this somewhere instead of local-only dev servers.
- Practice Tests (step 22) deliberately deferred a few things, per the user's choices
  at the time. Step 30 later resolved two of them by reading real OCR papers directly
  (revisionmaths.com): the real 3-paper-per-sitting structure was built, and the mark
  scheme/formulae sheet were calibrated against real papers spanning June 2017-June
  2024 — though step 30's own conclusion that OCR has calculator allowed on *all
  three* papers turned out to be wrong (right for the specific papers checked, but not
  the actual current spec), corrected in step 32 once the real spec PDF was read
  directly: Paper 2 (Foundation)/Paper 5 (Higher) are now genuinely non-calculator.
  Still genuinely not built: hand-authored multi-part exam questions (with sub-parts
  a/b/c combining several skills, the way real OCR questions are often structured)
  instead of frozen single-skill generator output — `mark_scheme.py`'s one-M1-per-step
  derivation is still a systematic approximation of a real per-question mark
  allocation, not a transcription of one, since this app's questions are still
  single-skill by design.

Don't start any of these without checking with the user first — this list is just
carried-over context, not a plan.
