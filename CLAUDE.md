# GCSE Maths Worksheet Generator

A local web app that generates UK GCSE maths practice worksheets as PDFs with worked
solutions, searchable/browsable across 6 curriculum sections.

- **Backend**: `backend/` — Python 3.12, FastAPI, sympy (symbolic math), ReportLab (PDF + diagrams)
- **Frontend**: `frontend/` — React + Vite + TypeScript
- **Repo**: https://github.com/jamescostello1998-commits/gcse-maths-worksheet-generator (pushed, `master` up to date)

`first-pr-practice/` in this same folder is an **unrelated** git-practice repo (its own
`.git`) — ignored via the root `.gitignore`. Don't touch it when working on this app.

## Current state (as of this session)

**56 topics across 6 sections**, all procedurally generated with independent
correctness verification (never trust the generator's own arithmetic — always
cross-check via a second method: sympy substitution, stdlib `statistics`/`Decimal`,
brute-force sample-space enumeration, etc.). Full backend suite: **79/79 passing**.

| Section | Groups | Topics |
|---|---|---|
| Number | Fractions, Decimals, Standard Form | 13 |
| Algebra | Solving Linear Equations, Expanding Brackets, Factorising | 9 |
| Ratio & Proportion | Percentages, Ratio | 8 |
| Geometry | Area & Perimeter, Angles, Pythagoras' Theorem | 17 (all with diagrams) |
| Probability | Probability | 4 |
| Statistics | Averages from a List, Frequency Tables, Working Backwards | 5 |

All 17 Geometry topics render an actual ReportLab-drawn figure (rectangle, triangle,
angle diagram, right triangle, etc.) matching that question's real generated values —
see `backend/app/pdf/diagrams.py`.

Nothing is a stub/placeholder — every topic has real generation logic, a real
independent verification check, and a real test file with ~200-trial seeded runs.

## How this was built (chronology, for context)

1. Initial build: FastAPI backend + React frontend, 8 flat topics, PDF renderer, full test suite.
2. Restructured into the current 6-section/group/topic hierarchy (each old topic's
   internal random "shape" promoted to its own standalone, tier-exclusive subtopic).
   Added a new frontend nav: `HomeScreen` → `SectionView` → `TopicCard`, plus global search.
3. Added 13 new Number topics (Fractions/Decimals/Standard Form) and the Geometry
   diagram-rendering engine.

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

## Running it

**Preferred**: use the Browser pane's `preview_start` tool with `{name: "backend"}` /
`{name: "frontend"}` — `.claude/launch.json` already has both configured with full
absolute paths (works around the PATH issues above, no manual env setup needed).

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

The backend venv (`backend/.venv`) already has all of `requirements.txt` installed.
The frontend (`frontend/node_modules`) already has all deps installed including
Vitest + React Testing Library.

## Testing

```powershell
# Backend — from backend/, with the venv
.\.venv\Scripts\python.exe -m pytest -v

# Frontend — from frontend/, with NodePortable on PATH
npx vitest run
```

## Architecture patterns to follow when extending this

- **One topic = one `generate_xxx(tier, rng) -> Question` function + one
  `TopicDefinition`** in `backend/app/topics/<module>.py`. Register new topics in
  `backend/app/core/registry.py`'s `_TOPIC_LIST` (declared order = display order,
  not alphabetical). Each topic is tier-exclusive (`fixed_tier=Tier.FOUNDATION` or
  `.HIGHER`) — see `TopicDefinition.fixed_tier` in `app/topics/base.py` for the
  (currently unused) `None` = "supports both tiers via a toggle" escape hatch.
- **Always verify independently.** Every generator asserts its own answer is correct
  using a *different* computation path than the one used to build the steps
  (e.g. `algebra_utils.solve_linear_with_steps` + substitution check in
  `linear_equations.py`; brute-force `itertools.product` sample-space enumeration in
  `probability.py`; stdlib `statistics`/`Decimal` cross-checks in `statistics.py`/
  `decimals.py`). Raise `ValueError` on mismatch — never silently emit a wrong answer.
- **Exact arithmetic only** — `sympy.Rational`, `fractions.Fraction`, or
  `decimal.Decimal`, never raw floats for anything that ends up in an answer.
  `sp.nsimplify` was tried early on and **removed** — it can hallucinate bogus
  irrational closed-forms for exact rationals (see git history / commit messages
  if curious); use `sp.Rational(x)` directly instead.
- **Diagrams**: a topic that wants one sets `diagram=DiagramSpec(kind=..., params={...})`
  on its returned `Question`, using the exact same random values already used for the
  prompt (see any `area_perimeter.py`/`angles.py`/`pythagoras.py` generator). Add new
  diagram *kinds* as a `draw_xxx(params) -> Drawing` function in `app/pdf/diagrams.py`
  and register it in `_RENDERERS`.
- **Frontend**: `useSections`/`fetchSections` is the single source of truth for the
  nested section→group→topic tree; `TopicCard` handles its own generate/download flow
  per-card via `useGenerateWorksheet`. No router library — view switching in `App.tsx`
  is plain `useState` (home / selected section / search results).
- **Tests**: one test file per topic module in `backend/tests/unit/topics/`, following
  the existing pattern — a `GENERATORS` list of `(function, tier)` pairs, a 200-trial
  "produces valid verified questions" test, a dedup-key-variance test, and a
  topic-metadata test. Geometry topic tests additionally assert `question.diagram`
  matches the expected kind/params.

## Ideas for a future session (not started, no commitment made)

- Real Number-section content beyond Fractions/Decimals/Standard Form? (section is
  already populated now, so this is just "more of it" if wanted)
- Diagrams for Probability (dice/spinner/bag illustrations) — explicitly out of scope
  so far (user asked for Geometry diagrams specifically).
- Adjustable question count (currently fixed at 20), answer-only PDF mode, saved
  worksheet history, mixed-topic revision papers, user accounts.
- Deploying this somewhere instead of local-only dev servers.

Don't start any of these without checking with the user first — this list is just
carried-over context from earlier "what should we build next" conversation, not a plan.
