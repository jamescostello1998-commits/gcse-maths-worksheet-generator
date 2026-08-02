"""Shading (or reading) a two-inequality region on a coordinate grid - the
2D-region sibling of inequalities_number_line.py's 1D number-line topics.
Shares the "Inequalities" group with app/topics/inequalities.py and
app/topics/inequalities_number_line.py (both different modules, same
display group)."""

import operator
import random
from fractions import Fraction

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Inequalities"

_X_MIN, _X_MAX, _Y_MIN, _Y_MAX = -8, 8, -8, 8
_MARGIN = 2  # keep the two lines' intersection point away from the grid edge

_M_CHOICES = [Fraction(-2), Fraction(-1), Fraction(-1, 2), Fraction(1, 2), Fraction(1), Fraction(2)]
_C_RANGE = range(-4, 5)

_SYM = {"<": "<", "<=": "≤", ">": ">", ">=": "≥"}
_REL = {"<": sp.Lt, "<=": sp.Le, ">": sp.Gt, ">=": sp.Ge}
_OP = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}

_X, _Y = sp.symbols("x y")


def _fmt_coeff_x(m: Fraction) -> str:
    if m == 1:
        return "x"
    if m == -1:
        return "-x"
    if m.denominator == 1:
        return f"{m.numerator}x"
    if abs(m.numerator) == 1:
        sign = "-" if m.numerator < 0 else ""
        return f"{sign}\\frac{{x}}{{{m.denominator}}}"
    return f"\\frac{{{m.numerator}x}}{{{m.denominator}}}"


def _fmt_line_expr(m: Fraction, c: int) -> str:
    coeff_part = _fmt_coeff_x(m)
    if c == 0:
        return coeff_part
    sign = "+" if c > 0 else "-"
    return f"{coeff_part} {sign} {abs(c)}"


def _random_line(rng: random.Random) -> dict:
    return {"m": rng.choice(_M_CHOICES), "c": rng.choice(_C_RANGE), "op": rng.choice(["<", "<=", ">", ">="])}


def _lines_intersect_in_window(line1: dict, line2: dict, x_lo, x_hi, y_lo, y_hi) -> bool:
    m1, c1 = line1["m"], line1["c"]
    m2, c2 = line2["m"], line2["c"]
    if m1 == m2:
        return False  # parallel lines never meet - would give a degenerate/unbounded-only region
    x = Fraction(c2 - c1, m1 - m2)
    y = m1 * x + c1
    return x_lo <= x <= x_hi and y_lo <= y <= y_hi


def _sample_points(line1: dict, line2: dict) -> list:
    """A handful of grid points to sanity-check membership against - the
    four window corners, the centre, the two lines' intersection point
    (rounded to the nearest grid point), and several points offset from it
    in each direction, giving a mix of points clearly inside and clearly
    outside the eventual shaded region."""
    m1, c1, m2, c2 = line1["m"], line1["c"], line2["m"], line2["c"]
    ix = Fraction(c2 - c1, m1 - m2)
    iy = m1 * ix + c1
    icx = max(_X_MIN, min(_X_MAX, round(float(ix))))
    icy = max(_Y_MIN, min(_Y_MAX, round(float(iy))))

    points = {
        (_X_MIN, _Y_MIN), (_X_MIN, _Y_MAX), (_X_MAX, _Y_MIN), (_X_MAX, _Y_MAX),
        (0, 0), (icx, icy),
    }
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
        px = max(_X_MIN, min(_X_MAX, icx + dx))
        py = max(_Y_MIN, min(_Y_MAX, icy + dy))
        points.add((px, py))
    return list(points)


def _check_region(lines: list, samples: list) -> None:
    """For every sample point and every line, evaluate membership two
    genuinely different ways: a plain Python comparison against
    y <op> m*x + c (the ground truth the diagram itself is built from - not
    independent of anything, but asserted anyway as a sanity check that
    catches a transcription slip between a line's stored (m, c, op) and the
    displayed inequality text), and a sympy relational built from the same
    (m, c, op) and evaluated via symbolic substitution (a genuinely
    different code path, mirroring inequalities_number_line.py's
    _check_single). Both must agree at every sample point."""
    for gx, gy in samples:
        for ln in lines:
            m, c, op = ln["m"], ln["c"], ln["op"]
            plain_result = _OP[op](Fraction(gy), m * gx + c)
            rel = _REL[op](_Y, m * _X + c)
            sym_result = bool(rel.subs({_X: gx, _Y: gy}))
            if plain_result != sym_result:
                raise ValueError("inequalities_region_higher verification failed: membership mismatch")


def _build_lines(rng: random.Random) -> tuple:
    for _ in range(200):
        line1 = _random_line(rng)
        line2 = _random_line(rng)
        if _lines_intersect_in_window(
            line1, line2, _X_MIN + _MARGIN, _X_MAX - _MARGIN, _Y_MIN + _MARGIN, _Y_MAX - _MARGIN
        ):
            break
    else:
        raise ValueError("inequalities_region_higher: could not construct two lines intersecting within the window")

    samples = _sample_points(line1, line2)
    _check_region([line1, line2], samples)
    return line1, line2


def _boundary_desc(line: dict) -> str:
    strict = line["op"] in ("<", ">")
    return "dashed" if strict else "solid", "not included" if strict else "included"


def _shading_side(op: str) -> str:
    return "lower" if op in ("<", "<=") else "upper"


def generate_inequalities_region_higher(tier: Tier, rng: random.Random) -> Question:
    line1, line2 = _build_lines(rng)
    lines = [line1, line2]

    expr1 = f"y {_SYM[line1['op']]} {_fmt_line_expr(line1['m'], line1['c'])}"
    expr2 = f"y {_SYM[line2['op']]} {_fmt_line_expr(line2['m'], line2['c'])}"
    boundary1 = f"y = {_fmt_line_expr(line1['m'], line1['c'])}"
    boundary2 = f"y = {_fmt_line_expr(line2['m'], line2['c'])}"
    final_answer = f"{expr1} and {expr2}"

    diagram_lines = [
        {"m": float(line1["m"]), "c": line1["c"], "op": line1["op"]},
        {"m": float(line2["m"]), "c": line2["c"], "op": line2["op"]},
    ]
    marked = DiagramSpec(
        kind="inequality_region",
        params={"x_min": _X_MIN, "x_max": _X_MAX, "y_min": _Y_MIN, "y_max": _Y_MAX, "lines": diagram_lines},
    )
    blank = DiagramSpec(
        kind="inequality_region",
        params={"x_min": _X_MIN, "x_max": _X_MAX, "y_min": _Y_MIN, "y_max": _Y_MAX, "blank": True},
    )

    shape = rng.choice(["draw", "read"])
    dashed1, included1 = _boundary_desc(line1)
    dashed2, included2 = _boundary_desc(line2)

    if shape == "draw":
        prompt = f"On the grid, shade the region that satisfies both {expr1} and {expr2}."
        steps = [
            f"Draw the line {boundary1} ({dashed1} - the line itself is {included1} in the region).",
            f"Draw the line {boundary2} ({dashed2} - the line itself is {included2} in the region).",
            f"Shade the region where both {expr1} and {expr2} are true at the same time.",
        ]
        return Question(
            topic_id="inequalities_region_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=final_answer,
            dedup_key=(
                f"ineq_region:draw:{line1['m']}:{line1['c']}:{line1['op']}:"
                f"{line2['m']}:{line2['c']}:{line2['op']}"
            ),
            diagram=blank,
            solution_diagram=marked,
        )
    else:
        prompt = "The shaded region on the grid satisfies two inequalities. State both inequalities."
        steps = [
            f"The boundary line {boundary1} is {dashed1}, and the shading lies on the "
            f"{_shading_side(line1['op'])} side of it, giving {expr1}.",
            f"The boundary line {boundary2} is {dashed2}, and the shading lies on the "
            f"{_shading_side(line2['op'])} side of it, giving {expr2}.",
        ]
        return Question(
            topic_id="inequalities_region_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=final_answer,
            dedup_key=(
                f"ineq_region:read:{line1['m']}:{line1['c']}:{line1['op']}:"
                f"{line2['m']}:{line2['c']}:{line2['op']}"
            ),
            diagram=marked,
        )


def generate_modelled_example_inequalities_region_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    line1, line2 = _build_lines(rng)

    expr1 = f"y {_SYM[line1['op']]} {_fmt_line_expr(line1['m'], line1['c'])}"
    expr2 = f"y {_SYM[line2['op']]} {_fmt_line_expr(line2['m'], line2['c'])}"
    boundary1 = f"y = {_fmt_line_expr(line1['m'], line1['c'])}"
    boundary2 = f"y = {_fmt_line_expr(line2['m'], line2['c'])}"
    final_answer = f"{expr1} and {expr2}"

    diagram_lines = [
        {"m": float(line1["m"]), "c": line1["c"], "op": line1["op"]},
        {"m": float(line2["m"]), "c": line2["c"], "op": line2["op"]},
    ]
    marked = DiagramSpec(
        kind="inequality_region",
        params={"x_min": _X_MIN, "x_max": _X_MAX, "y_min": _Y_MIN, "y_max": _Y_MAX, "lines": diagram_lines},
    )
    blank = DiagramSpec(
        kind="inequality_region",
        params={"x_min": _X_MIN, "x_max": _X_MAX, "y_min": _Y_MIN, "y_max": _Y_MAX, "blank": True},
    )

    dashed1, included1 = _boundary_desc(line1)
    dashed2, included2 = _boundary_desc(line2)

    shape = rng.choice(["draw", "read"])
    if shape == "draw":
        prompt = f"On the grid, shade the region that satisfies both {expr1} and {expr2}."
        teaching_steps = [
            "Shading a region for two inequalities at once means drawing both boundary lines first, then "
            "shading only where BOTH conditions hold together, not either one on its own.",
            f"For {expr1}, draw the line {boundary1} - {dashed1}, because the inequality is "
            f"{'strict, so points exactly on the line are' if dashed1 == 'dashed' else 'not strict, so points exactly on the line are'} "
            f"{included1}.",
            f"For {expr2}, draw the line {boundary2} - {dashed2} for the same reason ({included2}).",
            f"Finally, shade wherever both {expr1} AND {expr2} are true - this overlap is usually a single "
            "wedge-shaped region bounded by the two lines.",
        ]
        worked_calculation = [expr1, expr2, f"Boundaries: {boundary1} ({dashed1}), {boundary2} ({dashed2})"]
        return ModelledExample(
            topic_id="inequalities_region_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=final_answer,
            diagram=blank,
        )
    else:
        prompt = "The shaded region on the grid satisfies two inequalities. State both inequalities."
        teaching_steps = [
            "Reading a shaded region backwards into inequalities means examining each boundary line in "
            "turn: its equation, whether it's dashed or solid, and which side the shading sits on.",
            f"The line {boundary1} is {dashed1} ({'strict' if dashed1 == 'dashed' else 'not strict'} "
            f"inequality), and the shading lies on its {_shading_side(line1['op'])} side, giving {expr1}.",
            f"The line {boundary2} is {dashed2}, and the shading lies on its {_shading_side(line2['op'])} "
            f"side, giving {expr2}.",
            f"Together, the shaded region satisfies both {expr1} and {expr2} at the same time.",
        ]
        worked_calculation = [f"Boundary 1: {boundary1} ({dashed1}) -> {expr1}", f"Boundary 2: {boundary2} ({dashed2}) -> {expr2}"]
        return ModelledExample(
            topic_id="inequalities_region_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=final_answer,
            diagram=marked,
        )


TOPIC_INEQUALITIES_REGION_HIGHER = TopicDefinition(
    id="inequalities_region_higher",
    display_name="Shading Inequality Regions",
    description="Shade (or read off) the region on a coordinate grid that satisfies two linear inequalities at once.",
    generate=generate_inequalities_region_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_inequalities_region_higher,
)
