# GCSE Maths Worksheet Generator

A local web app that generates UK GCSE maths practice worksheets as PDFs with worked
solutions, searchable/browsable across 6 curriculum sections.

- **Backend**: `backend/` — Python 3.12, FastAPI, sympy (symbolic math), ReportLab (PDF + diagrams)
- **Frontend**: `frontend/` — React + Vite + TypeScript
- **Repo**: https://github.com/jamescostello1998-commits/gcse-maths-worksheet-generator (pushed, `master` up to date as of this session)

`first-pr-practice/` in this same folder is an **unrelated** git-practice repo (its own
`.git`) — ignored via the root `.gitignore`. Don't touch it when working on this app.

## Current state (as of this session)

**89 topics across 6 sections**, all procedurally generated with independent
correctness verification (never trust the generator's own arithmetic — always
cross-check via a second method: sympy substitution/solve, coordinate geometry,
stdlib `statistics`/`Decimal`, brute-force sample-space enumeration, etc.).
Full backend suite: **114/114 passing**. Frontend suite: **23/23 passing**
(unaffected this session).

| Section | Groups | Topics |
|---|---|---|
| Number | Fractions, Decimals, Standard Form, Estimation & Bounds | 16 |
| Algebra | Solving Linear Equations, Expanding Brackets, Factorising, Completing the Square, Turning Point of a Graph, Functions, Simultaneous Equations, Sequences | 27 |
| Ratio & Proportion | Percentages, Ratio | 8 |
| Geometry | Area & Perimeter, Angles, Pythagoras' Theorem, Trigonometry, Sine Rule, Cosine Rule, Area of a Triangle, Vectors, Geometric Vectors, Circle Theorems | 29 |
| Probability | Probability | 4 |
| Statistics | Averages from a List, Frequency Tables, Working Backwards | 5 |

Every Geometry topic and a handful of Algebra topics (parabola for turning point,
line-pair for simultaneous-graphically) render an actual ReportLab-drawn figure
matching that question's real generated values — see `backend/app/pdf/diagrams.py`.

Nothing is a stub/placeholder — every topic has real generation logic, a real
independent verification check, and a real test file with ~200–400-trial seeded runs.

**Frontend**: each section now has a Foundation/Higher tier-picker sub-menu (added
this session) before showing its topic groups — see `SectionView.tsx`. Topics with
`fixed_tier=None` (currently unused) would show under both.

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
  `simultaneous_equations.generate_simultaneous_graphically`.
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
  set, sanity-check `len({distinct dedup_keys}) >> 20` before considering it done —
  `test_all_topics_produce_20_distinct_questions_at_their_fixed_tier` in
  `test_worksheet_builder.py` will catch it, but better to catch it while writing the
  generator (a quick 300-trial loop counting `set()` size, as used throughout this
  session, works fine as a manual check).

## Ideas for a future session (not started, no commitment made)

- Further curriculum-audit dual-tier candidates identified but **not yet built**
  (flagged during this session's audit, deliberately left for later so as not to keep
  expanding scope unprompted): `percentages.generate_reverse` — Foundation version
  with friendlier numbers; `angles.py`'s `parallel_lines`/`exterior`/`polygon_interior`
  — a pure-numeric (no algebra/no solving-for-x) Foundation version of each, since the
  existing ones embed an algebraic solve which is more Higher-flavoured;
  `area_perimeter.generate_circle` — a Foundation version giving a decimal answer
  (calculator π) rather than the current "exact form in terms of π".
  If asked to continue the audit, start there.
- Extend `mathtext.py`/`diagrams.py` italics beyond `x` to other single-letter
  variables (`n` in sequences, `a`/`b` in vectors) for full standard-typesetting
  consistency — noted above as a reasonable but currently out-of-scope enhancement.
- Diagrams for Probability (dice/spinner/bag illustrations) — explicitly out of scope
  so far (user asked for Geometry diagrams specifically, then later Algebra graphs).
- Adjustable question count (currently fixed at 20), answer-only PDF mode, saved
  worksheet history, mixed-topic revision papers, user accounts.
- Deploying this somewhere instead of local-only dev servers.

Don't start any of these without checking with the user first — this list is just
carried-over context, not a plan.
