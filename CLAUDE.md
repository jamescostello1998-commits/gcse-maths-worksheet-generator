# GCSE Maths Worksheet Generator

A local web app that generates UK GCSE maths practice worksheets as PDFs with worked
solutions, searchable/browsable across 6 curriculum sections.

- **Backend**: `backend/` — Python 3.12, FastAPI, sympy (symbolic math), ReportLab (PDF + diagrams)
- **Frontend**: `frontend/` — React + Vite + TypeScript
- **Repo**: https://github.com/jamescostello1998-commits/gcse-maths-worksheet-generator (`master` is up to date — every session's work has been committed and pushed before ending)

`first-pr-practice/` in this same folder is an **unrelated** git-practice repo (its own
`.git`) — ignored via the root `.gitignore`. Don't touch it when working on this app.

## Where to pick up next

Phases 1-3 of a large user-supplied Geometry expansion (chronology steps 23-25)
and **Phase 4a (chronology step 26, Symmetry + Transformations) are all
complete and pushed**. 268 topics total, backend suite 638/638, frontend
45/45 (unaffected), no known bugs.

**Phase 4b (bearings, constructions, loci — the last remaining piece of the
original Phase 4 scope) is FULLY PLANNED but NOT YET CODED.** The user
confirmed Phase 4b should be one single pass (not split further). A full
plan-mode research pass (3 parallel Explore agents + 1 Plan agent, plus two
technical claims independently re-verified directly — ReportLab's `ArcPath`
sweep direction, and that `fillOpacity` genuinely renders in real PDF output)
was completed, and every open design decision was confirmed with the user.
**The complete plan (exact topic list, diagram-kind param shapes, verification
design, registry insertion points, test plan, build order) is preserved at
`C:\Users\James\.claude\plans\tidy-crafting-shore.md`** (machine-local, not in
this repo) — resume by writing/confirming the final plan from that file's
findings (do not re-run the research) and proceeding straight to
implementation. This CLAUDE.md section is a summary in case that file is ever
lost; the plan file is the durable detailed copy.

**Net effect once built: 6 new topics (268 → 274)** — `bearings_cosine_rule`
(Higher, new `bearings.py`, reframes `triangle_rules.py`'s existing SAS
cosine-rule maths as a two-leg bearings word problem, deriving the included
angle from the two given bearings before applying the cosine rule); a new
"Bearings" group. `construction_angle_bisector` /
`construction_perpendicular_bisector` / `construction_triangle` (all
Foundation, new `constructions.py`, new "Constructions" group) — confirmed
**no `verify()` at all** (author-review only) and confirmed to use randomised
numbers/labels embedded in fixed per-scenario method text (large combinatorial
state space) rather than a curated `TEMPLATES` bank, since a fixed 3-entry
bank would be thinner than any existing precedent in this app.
`loci_constructions` (Foundation) / `loci_regions` (Higher), new `loci.py`,
new "Loci" group — confirmed as 2 separate tier-split topics, not one
combined topic; needs 2 new diagram kinds (`draw_bearings`;
`draw_loci_construction`/`draw_loci_region`, the latter sharing a
`_scaled_circle` helper that always uses `Ellipse` with separately-computed
x/y radii rather than `Circle`, since `_draw_scaled_axes`'s pixel scaling is
never exactly uniform even with a square data window) — confirmed to use a
rasterized dot-mesh for shaded regions, not hand-built boolean `ArcPath`
geometry.

If the user wants something else entirely instead of continuing Phase 4b,
check "Ideas for a future session" (bottom of this file) for other candidate
follow-ups, or ask directly what they'd like to work on.

## Current state

*(For a session-by-session history of how it got here, see the Chronology section below.)*

**268 topics across 6 sections**, all procedurally generated with independent
correctness verification (never trust the generator's own arithmetic — always
cross-check via a second method: sympy substitution/solve, coordinate geometry,
stdlib `statistics`/`Decimal`, brute-force sample-space enumeration, etc.).
Full backend suite: **638/638 passing**. Frontend suite: **45/45 passing**.

**Practice Tests (fixed/static content, not procedural — the one deliberate exception
to the paragraph above)**: a 7th homepage section, `backend/app/practice_tests/`,
holds 20 committed papers (`data/*.json`, `foundation-01`..`10`, `higher-01`..`10`),
each a 100-mark, OCR-GCSE-styled paper assembled by *freezing* real output from the
existing 232 generators rather than writing new exam-style content by hand. Built via
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
byte-identical JSON every time, verified by a test. Every paper's marks sum to
**exactly 100**, enforced by `topic_selection.select_paper_topics`'s fill-then-close
algorithm (self-restarts with a perturbed seed if it paints itself into a corner) plus
a `build.py`-level repair pass (`_repair_to_target`) for the handful of topics whose
`solution_steps` length varies by branch, occasionally drifting the real total from
the "typical" total the selection was planned against — and a whole-paper retry
(`MAX_PAPER_RETRIES`) as the final safety net.

The OCR-style mark scheme (`app/practice_tests/mark_scheme.py`) is a **systematic
approximation**, not lifted from a real OCR mark scheme (no reference papers were
available to calibrate against — built from general exam-board convention instead,
per the user's choice): a question's own `solution_steps` become M1 method marks
(1 per step, capped at 4, with any overflow folded into the last one) followed by one
A1 accuracy mark quoting the question's own `final_answer` (e.g. `"30 oe (cao)"`);
a multiple-choice-style `final_answer` (matches `^[A-D]\)`, e.g. `"B) 3/4"`, this app's
convention for "identify the correct one" questions) gets a single independent B1
instead, since there's no method to mark. **`PracticeQuestion`/`PracticeTestPaper`
(`practice_tests/models.py`) are deliberately separate from `core/models.py`'s
`Question`/`TopicDefinition`** — none of the 232 existing generators or their tests
were touched to build this feature. Two new PDF renderers
(`app/pdf/practice_test_renderer.py`) follow the existing `SimpleDocTemplate` +
flowable-list idiom: `render_practice_test_paper` (an original-wording — not copied
from any real OCR paper — cover page with candidate-detail boxes and an instructions
box, then numbered questions with marks shown as `[n]` in a right-aligned column) and
`render_mark_scheme` (a `Question | Answer | Marks | Guidance` table, one row per
question, each M1/A1/B1 point stacked in the Guidance cell). Three new GET routes
(`GET /api/practice-tests`, `.../{id}/paper`, `.../{id}/mark-scheme`) since content is
fully static per id — no request body needed, unlike the POST-based worksheet/modelled-
example endpoints. Frontend: `PracticeTestsView`/`PracticeTestCard` mirror
`SectionView`/`TopicCard`'s two-level tier-picker and two-independent-download-button
patterns exactly, rendered as a distinct block **underneath** `HomeScreen` in
`App.tsx` (not folded into the 6-section grid, since a static paper list is
structurally different from the procedural topic tree).

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
| Number | Fractions, Decimals, Order of Operations (BIDMAS), Standard Form, Estimation & Bounds, Negative Numbers, Multiplying & Dividing by Powers of 10, Factors/Multiples & Primes, Powers/Roots & Indices | 54 |
| Algebra | Expressions/Formulae/Equations/Identities, Solving Linear Equations, Forming and Solving Equations, Changing the Subject of a Formula, Expanding Brackets, Factorising, Algebraic Indices, Completing the Square, Turning Point of a Graph, Solving Quadratic Equations, Functions, Algebraic Fractions, Simultaneous Equations, Inequalities, Algebraic Proof, Sequences, Iteration, Plotting Graphs, Equation of a Line, Real-Life Graphs, Transformations of Graphs | 57 |
| Ratio & Proportion | Percentages, Best Buys, Ratio, Proportion, Compound Measures | 34 |
| Geometry | Area & Perimeter, Angles, Pythagoras' Theorem, Trigonometry, Sine Rule, Cosine Rule, Area of a Triangle, Vectors, Geometric Vectors, Circle Theorems, 3D Shapes, Congruence Proof, Symmetry, Transformations | 75 |
| Probability | Probability, Tree Diagrams, Sets and Counting, Tables and Diagrams, Venn Diagrams | 22 |
| Statistics | Averages from a List, Frequency Tables, Working Backwards, Charts and Graphs, Cumulative Frequency & Box Plots, Histograms | 26 |

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
variables `x` and `n` are italicised, `^n` becomes a real superscript, and a fraction
gets its numerator raised/denominator lowered (`<super>`/`<sub>`, e.g. `3/4` →
3-raised/4-lowered) — applied once at render time in `renderer.py` (and
`modelled_example_renderer.py`, which shares the same `to_markup`), so any topic that
follows the ASCII convention gets this for free. Only `x`/`n` are italicised, not
`a`/`b` or other letters — see the "Italicising more variables" bullet below for why a
blanket rule can't safely cover every single letter (e.g. `a` collides constantly with
the English indefinite article). The fraction markup is a super/sub approximation, not
a true stacked vinculum (horizontal bar) — ReportLab's inline `<img>` tag only accepts
a file-path string and this environment has no working image-rasterisation backend
(`renderPM` needs Cairo bindings that aren't installed), so a real vinculum in prose
text would need PNGs rendered via PIL to temp files using a hardcoded font path
(`C:\Windows\Fonts\arial.ttf`) — judged too fragile for the payoff and deliberately
not built (see chronology step 16). Diagram labels get the *real* vinculum treatment
via `diagrams.py`'s `_label()`/`_math_runs()`/`_draw_fraction()`, since diagrams are
already drawn as vector shapes (`String`/`Line` in a `Group`) and don't need the
Paragraph-markup workaround — italics there also cover `x` and `n`. No current topic's
diagram actually shows a fraction label yet, so this path is unexercised by real
content today; it's built and unit-tested for when one eventually does.

**⚠️ Gotchas (bit us, see below)**:
- Never use the literal Unicode superscript-minus character `⁻` (e.g. in `f⁻¹`,
  `cos⁻¹`) — Helvetica has no glyph for it in ReportLab and it renders as a
  missing-glyph box. Always write `f^-1(x)`, `cos^-1(...)` etc. and let `mathtext.py`
  superscript it properly. (`²`, `√`, `π`, `≤`, `°`, `×`, `÷`, `£` are all fine as
  literal Unicode — only `⁻` specifically is the problem.)
- ReportLab renders a comma **glued and raised** to the preceding digit when it
  immediately follows a closing `</sub>` with no space in between (verified in
  isolation with a throwaway script — periods, colons, semicolons, question marks and
  closing parens in the same position are all fine, and so is a comma after
  `</super>`; only sub+comma with zero gap breaks). Since every fraction here ends in
  `</sub>`, and prose text very often follows a fraction straight with a comma (e.g.
  `"...= 20/90, 2/9..."`), `mathtext.py`'s `_replace_fraction` inserts a non-breaking
  space before such a comma to dodge it. If a future change ever hand-writes
  `<sub>...</sub>` markup directly (bypassing `to_markup`), watch for this.

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

**Regenerating the Practice Tests data**: the 20 papers under
`backend/app/practice_tests/data/*.json` are committed, static content (see "Current
state") — the API serves them as-is, nothing is generated at request time. Only
re-run `backend\.venv\Scripts\python.exe -m app.practice_tests.build` (from `backend/`)
if you deliberately want to regenerate them (e.g. after editing `topic_selection.py`'s
weighting/priority tables or `mark_scheme.py`'s marking rules) — it overwrites all 20
files and is fully deterministic (re-running with no code changes reproduces
byte-identical output). Restart the backend afterward to pick up the new data (the
loader reads the JSON files once at import time).

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
  write plain ASCII in generator strings — bare `x`/`n` for variables, `^n` for
  exponents (including negative, e.g. `10^-3`), `^-1` for inverse-function/inverse-
  trig notation, `^(num/den)` for a fractional exponent (e.g. `x^(1/4)`, raised as
  one flat unit — see "Fractional exponents in mathtext.py" above), `num/den` for
  standalone fractions (e.g. `3/4`). Never hand-write Unicode
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

- **Geometry expansion Phase 4b** (agreed with the user in chronology step 23;
  Phases 1-3 and Phase 4a are built — see steps 24-26 for 3D Shapes, the trig/
  Pythagoras/congruence-proof topics, and Symmetry/Transformations): bearings
  & constructions/loci — cosine rule in bearings, constructing angle
  bisectors/perpendicular bisectors/triangles (describe-the-method text
  questions, per the user's choice — not diagram-based, since there's no way
  to "solve" a construction numerically, and confirmed in step 26 to need no
  `verify()` either — author-review only), and loci and regions. Not started —
  confirm with the user before starting, per the "Where to pick up next" note
  above.
  - Compound 3D shapes' **surface area** was deliberately left out of Phase 2's
    `compound_3d_volume` topic (volume only) — excluding a compound solid's internal
    shared face correctly was judged too much added risk for that session's first
    pass. Could be added as its own topic later if wanted.
  - Phase 3's congruent triangle proof topic covers SSS/SAS/ASA/RHS via an
    18-entry curated bank (see step 25) — a Foundation `trig_mixed`-style
    sibling covering *identifying* similar (not congruent) triangles, or a
    "prove NOT congruent" variant, were not requested and are not built.
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
- Bold (not italic) `a`/`b` vector labels in `vectors.py`/`diagrams.py`, matching real
  exam typesetting convention — deliberately deferred (see chronology step 16): needs
  every vector prompt/step string marked at the source (not a blanket regex, which
  can't tell a genuine vector mention from the English article "a" in the same
  sentence). `n` (sequences, angles, ratio) is already done as of step 16.
- Stem-and-leaf diagrams, scatter graphs & correlation, and standard deviation are all
  real GCSE Statistics content not covered by the Probability/Statistics topic list
  the user supplied (chronology steps 17–18) — never explicitly requested, so not
  built, but worth flagging if a future session wants to round out Statistics further.
- Saved worksheet history, mixed-topic revision papers, user accounts.
- Deploying this somewhere instead of local-only dev servers.
- `probability_expectation`'s `spinner` context and `relative_frequency`'s `spinner`
  context both have no side-count in their generators, so step 21 deliberately left
  them without a spinner diagram rather than inventing one — could be built by first
  adding a real side-count to those generators (a small, genuine change to the
  question content itself, not just a diagram retrofit). Similarly,
  `probability_listing_outcomes`'s two-spinner scenarios (`two_spinner3`/
  `spinner3_spinner4`) have no diagram since `draw_spinner` only draws one spinner at
  a time — would need a second diagram kind (or a `draw_spinner` extension) that lays
  out two spinners side by side.
- Practice Tests (step 22) deliberately deferred a few things, per the user's choices
  at the time: mimicking OCR's real 3-paper-per-sitting structure (non-calculator +
  2 calculator papers) instead of one combined 100-mark paper; hand-authored genuine
  multi-part exam questions (with sub-parts a/b/c combining several skills) instead of
  frozen single-skill generator output; and calibrating the mark scheme against real
  OCR specimen papers, which weren't available this session — if the user obtains
  some later, `mark_scheme.py`'s marks-per-step default rule could be replaced with
  real per-question-type mark allocations.

Don't start any of these without checking with the user first — this list is just
carried-over context, not a plan.
