"""Numerical iteration: given an iterative formula x_(n+1) = g(x_n) and a
starting value x_0, find x_1, x_2, x_3 to 3 decimal places. This generator
deliberately only covers that numerical-evaluation half of the classic GCSE
two-part iteration question - the formula is always given outright, mirroring
how real exam papers often hand over the iterative formula for the final part
rather than asking the student to derive the rearrangement themselves.

Getting the rounding right is the entire risk in this topic, so every
candidate set of random parameters is computed at high (40 significant
figure) decimal precision first, rejected if it diverges, hits a domain
error, or lands ambiguously close to a 3dp rounding boundary, and then
cross-checked against an entirely separate ordinary-float computation before
being accepted - see _build_iteration_example.
"""

import decimal
import math
import random
from decimal import Decimal, ROUND_HALF_UP
from typing import NamedTuple

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Iteration"

_PREC = 40
_BOUND = Decimal(1000)
# A value is "near a rounding boundary" if x*1000's fractional part sits
# within this tolerance of exactly 0.5 - i.e. x itself is within roughly
# 1e-9 of a #.###5 boundary point, where ROUND_HALF_UP behaviour computed at
# two different precisions/methods might not agree.
_BOUNDARY_TOL = Decimal("1e-6")


class _IterationData(NamedTuple):
    shape: str
    a: int
    b: int
    x0: int
    x_display: tuple[str, str, str]


def _quantize3(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def _near_rounding_boundary(x: Decimal) -> bool:
    scaled = x * 1000
    floor_val = scaled.to_integral_value(rounding=decimal.ROUND_FLOOR)
    frac = scaled - floor_val
    return abs(frac - Decimal("0.5")) < _BOUNDARY_TOL


def _decimal_step(shape: str, x: Decimal, a: Decimal, b: Decimal) -> Decimal:
    if shape == "quadratic":
        return (a - x * x) / b
    if shape == "sqrt":
        arg = a - b * x
        if arg < 0:
            raise ValueError("iteration: negative under the square root")
        return arg.sqrt()
    if shape == "reciprocal":
        denom = x + b
        if abs(denom) < Decimal("1e-6"):
            raise ValueError("iteration: division by (near) zero")
        return a / denom
    raise AssertionError(shape)


def _float_step(shape: str, x: float, a: float, b: float) -> float:
    if shape == "quadratic":
        return (a - x * x) / b
    if shape == "sqrt":
        arg = a - b * x
        if arg < 0:
            raise ValueError("iteration: negative under the square root (float)")
        return math.sqrt(arg)
    if shape == "reciprocal":
        denom = x + b
        if abs(denom) < 1e-6:
            raise ValueError("iteration: division by (near) zero (float)")
        return a / denom
    raise AssertionError(shape)


def _rand_params(shape: str, rng: random.Random) -> tuple[Decimal, Decimal, Decimal]:
    if shape == "quadratic":
        a, b, x0 = rng.randint(2, 25), rng.randint(3, 9), rng.randint(-3, 3)
    elif shape == "sqrt":
        a, b, x0 = rng.randint(8, 40), rng.randint(1, 3), rng.randint(0, 4)
    else:  # reciprocal
        a, b, x0 = rng.randint(3, 24), rng.randint(2, 7), rng.randint(0, 4)
    return Decimal(a), Decimal(b), Decimal(x0)


def _build_iteration_example(rng: random.Random) -> _IterationData:
    for _ in range(200):
        shape = rng.choice(["quadratic", "sqrt", "reciprocal"])
        a, b, x0 = _rand_params(shape, rng)

        try:
            with decimal.localcontext() as ctx:
                ctx.prec = _PREC
                values: list[Decimal] = []
                x = x0
                for _ in range(4):  # x_1..x_4 - the 4th is only a guard
                    x = _decimal_step(shape, x, a, b)
                    values.append(x)
        except ValueError:
            continue

        if any(abs(v) > _BOUND or _near_rounding_boundary(v) for v in values):
            continue

        x1, x2, x3, _x4 = values

        # Independent verification: recompute x_1, x_2, x_3 completely
        # separately using ordinary double-precision float/math, and require
        # them to round to the exact same 3dp values as the high-precision
        # decimal computation above. A disagreement means this parameter
        # choice is precision-sensitive, not a genuinely reproducible answer.
        try:
            fx = float(x0)
            fvals = []
            for _ in range(3):
                fx = _float_step(shape, fx, float(a), float(b))
                fvals.append(fx)
        except ValueError:
            continue

        decimal_display = [_quantize3(v) for v in (x1, x2, x3)]
        float_display = [_quantize3(Decimal(str(v))) for v in fvals]
        if decimal_display != float_display:
            continue

        return _IterationData(
            shape=shape,
            a=int(a),
            b=int(b),
            x0=int(x0),
            x_display=tuple(f"{d:.3f}" for d in decimal_display),
        )
    else:
        raise ValueError("iteration: failed to find safely convergent parameters after 200 tries")


def _formula_str(shape: str, a: int, b: int) -> str:
    if shape == "quadratic":
        return f"x_(n+1) = ({a} - x_n^2) / {b}"
    if shape == "sqrt":
        coeff = "" if b == 1 else str(b)
        return f"x_(n+1) = sqrt({a} - {coeff}x_n)"
    return f"x_(n+1) = {a} / (x_n + {b})"


def _subst_expr(shape: str, a: int, b: int, prev_disp: str) -> str:
    # Parenthesise a negative previous value before squaring/multiplying it -
    # "-1^2" reads as -(1^2) = -1 by normal order of operations, not the
    # (-1)^2 = 1 actually being computed, so a bare negative substituted
    # straight after a caret or × is genuinely ambiguous/wrong-looking.
    squared_disp = f"({prev_disp})" if prev_disp.startswith("-") else prev_disp
    if shape == "quadratic":
        return f"({a} - {squared_disp}^2) / {b}"
    if shape == "sqrt":
        coeff = "" if b == 1 else f"{b}×"
        return f"sqrt({a} - {coeff}{squared_disp})"
    return f"{a} / ({prev_disp} + {b})"


def generate_iteration(tier: Tier, rng: random.Random) -> Question:
    data = _build_iteration_example(rng)
    formula = _formula_str(data.shape, data.a, data.b)
    x0_disp = str(data.x0)

    step_lines = []
    prev_disp = x0_disp
    for i, val_disp in enumerate(data.x_display, start=1):
        expr = _subst_expr(data.shape, data.a, data.b, prev_disp)
        step_lines.append(f"x_{i} = g(x_{i - 1}) = {expr} = {val_disp}")
        prev_disp = val_disp

    steps = [f"Iterative formula: {formula}", f"x_0 = {x0_disp}"] + step_lines
    final_answer = f"x_1 = {data.x_display[0]}, x_2 = {data.x_display[1]}, x_3 = {data.x_display[2]}"

    return Question(
        topic_id="iteration",
        tier=Tier.HIGHER,
        prompt=(
            f"The iterative formula {formula} is used with x_0 = {x0_disp}. "
            "Find the values of x_1, x_2 and x_3, giving each answer to 3 decimal places."
        ),
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"iteration:{data.shape}:{data.a}:{data.b}:{data.x0}",
    )


def generate_modelled_example_iteration(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _build_iteration_example(rng)
    formula = _formula_str(data.shape, data.a, data.b)
    x0_disp = str(data.x0)

    subst_exprs = []
    prev_disp = x0_disp
    for val_disp in data.x_display:
        subst_exprs.append(_subst_expr(data.shape, data.a, data.b, prev_disp))
        prev_disp = val_disp

    worked_calculation = [
        formula,
        f"x_0 = {x0_disp}",
        f"x_1 = {subst_exprs[0]} = {data.x_display[0]}",
        f"x_2 = {subst_exprs[1]} = {data.x_display[1]}",
        f"x_3 = {subst_exprs[2]} = {data.x_display[2]}",
    ]

    if data.shape == "quadratic":
        domain_note = (
            "This particular formula squares x_n, so it's always defined whatever value comes out of the "
            "previous step - there's no square root or fraction here to worry about going wrong."
        )
    elif data.shape == "sqrt":
        domain_note = (
            "Because this formula has a square root in it, always check the expression underneath hasn't "
            "gone negative before you evaluate it - a negative number under a square root would mean the "
            "iteration has broken down."
        )
    else:
        domain_note = (
            "Because this formula divides by an expression involving x_n, check that expression never "
            "comes out as zero - dividing by zero would mean the iteration has broken down."
        )

    teaching_steps = [
        "An iterative formula tells you how to generate the next term of a sequence from the current one: "
        "start with the given x_0, substitute it into the formula to get x_1, then substitute x_1 back in "
        "to get x_2, and so on - each new value depends only on the one immediately before it.",
        f"The formula here is {formula}. Substitute the starting value x_0 = {x0_disp} in place of x_n to "
        f"find x_1: {subst_exprs[0]} = {data.x_display[0]}.",
        "Keep going the same way: feed the most recently found value back into the formula in place of "
        f"x_n to get the next one. This gives x_2 = {subst_exprs[1]} = {data.x_display[1]}, then "
        f"x_3 = {subst_exprs[2]} = {data.x_display[2]}.",
        "Use the full, unrounded value from your calculator at each step rather than the rounded 3dp "
        "display - only round right at the end, when writing down the final answer for each x_n, "
        "otherwise small rounding errors can build up across the three steps.",
        domain_note,
    ]

    return ModelledExample(
        topic_id="iteration",
        tier=Tier.HIGHER,
        prompt=(
            f"The iterative formula {formula} is used with x_0 = {x0_disp}. "
            "Find the values of x_1, x_2 and x_3, giving each answer to 3 decimal places."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x_1 = {data.x_display[0]}, x_2 = {data.x_display[1]}, x_3 = {data.x_display[2]}",
    )


TOPIC_ITERATION = TopicDefinition(
    id="iteration",
    display_name="Iteration",
    description="Use a given iterative formula x_(n+1) = g(x_n) to find x_1, x_2 and x_3 to 3 decimal places.",
    generate=generate_iteration,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_iteration,
)
