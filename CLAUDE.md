# GCSE Maths Worksheet Generator

A local web app that generates UK GCSE maths practice worksheets as PDFs with worked
solutions, searchable/browsable across 6 curriculum sections.

- **Backend**: `backend/` — Python 3.12, FastAPI, sympy (symbolic math), ReportLab (PDF + diagrams)
- **Frontend**: `frontend/` — React + Vite + TypeScript
- **Repo**: https://github.com/jamescostello1998-commits/gcse-maths-worksheet-generator (`master` is up to date — every session's work has been committed and pushed before ending)

`first-pr-practice/` in this same folder is an **unrelated** git-practice repo (its own
`.git`) — ignored via the root `.gitignore`. Don't touch it when working on this app.

## Current state

*(For a session-by-session history of how it got here, see the Chronology section below.)*

**142 topics across 6 sections**, all procedurally generated with independent
correctness verification (never trust the generator's own arithmetic — always
cross-check via a second method: sympy substitution/solve, coordinate geometry,
stdlib `statistics`/`Decimal`, brute-force sample-space enumeration, etc.).
Full backend suite: **253/253 passing**. Frontend suite: **26/26 passing**.

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
| Number | Fractions, Decimals, Standard Form, Estimation & Bounds, Negative Numbers, Multiplying & Dividing by Powers of 10, Factors/Multiples & Primes, Powers/Roots & Indices | 34 |
| Algebra | Solving Linear Equations, Expanding Brackets, Factorising, Completing the Square, Turning Point of a Graph, Functions, Simultaneous Equations, Sequences, Plotting Graphs, Equation of a Line, Real-Life Graphs, Transformations of Graphs | 38 |
| Ratio & Proportion | Percentages, Ratio | 11 |
| Geometry | Area & Perimeter, Angles, Pythagoras' Theorem, Trigonometry, Sine Rule, Cosine Rule, Area of a Triangle, Vectors, Geometric Vectors, Circle Theorems | 39 |
| Probability | Probability, Tree Diagrams, Sets and Counting, Tables and Diagrams | 13 |
| Statistics | Averages from a List, Frequency Tables, Working Backwards | 7 |

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
`topic.question_count or DEFAULT_COUNT` when calling `build_worksheet`.

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

Every Geometry topic and a handful of Algebra topics (parabola for turning point,
line-pair for simultaneous-graphically) render an actual ReportLab-drawn figure
matching that question's real generated values — see `backend/app/pdf/diagrams.py`.

Nothing is a stub/placeholder — every topic has real generation logic, a real
independent verification check, and a real test file with ~200–400-trial seeded runs.

**Frontend**: each section has a Foundation/Higher tier-picker sub-menu before showing
its topic groups — see `SectionView.tsx`. Topics with `fixed_tier=None` (currently
unused) would show under both.

**Typesetting**: `backend/app/pdf/mathtext.py` centrally converts plain-ASCII math in
generator output (`x`, `x^2`, `10^-3`) into real PDF typesetting — the variable `x` is
italicised, and `^n` becomes a real superscript — applied once at render time in
`renderer.py`, so any topic that follows the ASCII convention gets this for free.
Diagram labels get the equivalent treatment via `diagrams.py`'s `_label()`/`_math_runs()`.

**⚠️ Gotcha (bit us once, see below)**: never use the literal Unicode superscript-minus
character `⁻` (e.g. in `f⁻¹`, `cos⁻¹`) — Helvetica has no glyph for it in ReportLab and
it renders as a missing-glyph box. Always write `f^-1(x)`, `cos^-1(...)` etc. and let
`mathtext.py` superscript it properly. (`²`, `√`, `π`, `≤`, `°`, `×`, `÷`, `£` are all
fine as literal Unicode — only `⁻` specifically is the problem.)

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

Everything above is committed and pushed (see `git log`).

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
- **GitHub CLI**: installed via winget, works normally (`gh auth status` to check).
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
- **Foundation/Higher overlap content gets two separate topic IDs**, not one
  parameterised topic — e.g. `linear_both_sides_foundation` (id) alongside
  `linear_both_sides`, `trig_missing_side_foundation` alongside
  `trig_missing_side_higher`. The Foundation sibling is typically a positive-
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
  write plain ASCII in generator strings — bare `x` for the variable, `^n` for
  exponents (including negative, e.g. `10^-3`), `^-1` for inverse-function/inverse-
  trig notation. Never hand-write Unicode `²`/`⁻¹`/italics in generator code (with
  the sole exception of `²`, which IS safe as a literal — see the Gotcha above for
  exactly what is/isn't). Only `x` gets italicised (not `n`, `a`, `b`, etc. — those
  are used elsewhere, e.g. `sequences.py`'s `n`, `vectors.py`'s `a`/`b`, and are left
  upright; extending italics to other variables would be a reasonable but
  out-of-scope-so-far enhancement to `mathtext.py`/`diagrams.py`).
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

- The from-scratch Foundation/Higher curriculum audit (step 13) flagged a handful of
  **lower-confidence** candidates that were reported but deliberately *not* built,
  pending more research or a product decision: `probability_combined_dice` (may
  overlap with the existing Foundation `sample_space_diagrams` — worth checking
  whether a distinct Foundation sibling adds anything), `velocity_time_interpret`
  (the gradient/acceleration reading might be Foundation-appropriate; only
  "area under graph = distance" is clearly Higher-only — could split rather than
  duplicate), `fractions_mixed_number_arithmetic` (a Foundation sibling with
  smaller/simpler mixed numbers), `ratio_combine` (a friendlier-number Foundation
  version), `trig_mixed` (a Foundation version combining the already-Foundation
  side/angle topics). Don't build these without discussing first — the audit's
  confidence in each was explicitly lower than the 11 that were built.
- Extend `mathtext.py`/`diagrams.py` italics beyond `x` to other single-letter
  variables (`n` in sequences, `a`/`b` in vectors) for full standard-typesetting
  consistency — noted above as a reasonable but currently out-of-scope enhancement.
- Dice/spinner/bag *illustrations* (actual pictures of a die or spinner, as opposed to
  the tree/table/sample-space diagrams added this session) are still out of scope.
- User-facing adjustable question count (the backend now supports a per-topic fixed
  override via `question_count`, but there's no UI control for the user to pick their
  own count), answer-only PDF mode, saved worksheet history, mixed-topic revision
  papers, user accounts.
- Deploying this somewhere instead of local-only dev servers.

Don't start any of these without checking with the user first — this list is just
carried-over context, not a plan.
