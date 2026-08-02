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
from typing import NamedTuple, Optional

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
        return f"x_(n+1) = \\frac{{{a} - x_n^2}}{{{b}}}"
    if shape == "sqrt":
        coeff = "" if b == 1 else str(b)
        return f"x_(n+1) = sqrt({a} - {coeff}x_n)"
    return f"x_(n+1) = \\frac{{{a}}}{{x_n + {b}}}"


def _subst_expr(shape: str, a: int, b: int, prev_disp: str) -> str:
    # Parenthesise a negative previous value before squaring/multiplying it -
    # "-1^2" reads as -(1^2) = -1 by normal order of operations, not the
    # (-1)^2 = 1 actually being computed, so a bare negative substituted
    # straight after a caret or × is genuinely ambiguous/wrong-looking.
    squared_disp = f"({prev_disp})" if prev_disp.startswith("-") else prev_disp
    if shape == "quadratic":
        return f"\\frac{{{a} - {squared_disp}^2}}{{{b}}}"
    if shape == "sqrt":
        coeff = "" if b == 1 else f"{b}×"
        return f"sqrt({a} - {coeff}{squared_disp})"
    return f"\\frac{{{a}}}{{{prev_disp} + {b}}}"


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


# ---------------------------------------------------------------------------
# Trial and improvement: given f(x) = x^3 + ax - b, show a root lies between
# two consecutive integers, then narrow it down with a 0.1-step decimal
# search and a midpoint test to find the root correct to 1 decimal place.
# This is deliberately a genuinely different skill from generate_iteration
# above (a fixed x_(n+1) = g(x_n) recurrence formula) - here the student
# performs a systematic decimal search on a cubic, not repeated substitution
# into a given rearrangement.
#
# Getting the 1dp rounding right is the entire risk in this topic too, so
# every candidate (a, b) is verified two ways: the coarse 0.1-step table plus
# a midpoint test (the method shown to the student), and a fine step-0.001
# scan with linear interpolation (a completely different resolution/loop),
# and any (a, b) where these two disagree, or where the true root sits
# suspiciously close to a #.#5 rounding boundary, is rejected and retried -
# see _build_trial_improvement_example.
# ---------------------------------------------------------------------------

_TRIAL_A_RANGE = (-4, 4)
_TRIAL_B_RANGE = (10, 80)
_TRIAL_LO_RANGE = range(1, 9)


class _TrialData(NamedTuple):
    a: int
    b: int
    lo: int
    coarse_rows: tuple[tuple[str, str, str], ...]
    mid_x: str
    mid_val: str
    mid_side: str
    answer_1dp: str


def _f_cubic(x: Decimal, a: int, b: int) -> Decimal:
    return x**3 + a * x - b


def _sign_word(v: Decimal) -> str:
    return "positive" if v > 0 else "negative"


def _fmt_val(v: Decimal) -> str:
    return str(v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _find_bracket(a: int, b: int) -> Optional[int]:
    """Search for a small integer lo such that f(lo) and f(lo + 1) have
    opposite (nonzero) signs, i.e. a root of f lies strictly between them."""
    for lo in _TRIAL_LO_RANGE:
        f_lo = _f_cubic(Decimal(lo), a, b)
        f_hi = _f_cubic(Decimal(lo + 1), a, b)
        if f_lo == 0 or f_hi == 0:
            return None
        if (f_lo > 0) != (f_hi > 0):
            return lo
    return None


def _near_1dp_boundary(x: Decimal) -> bool:
    """True if x sits suspiciously close (within 0.001) to a #.#5 rounding
    boundary, where the true root's 1dp rounding could be ambiguous between
    the coarse table's midpoint test and this module's own fine-scan
    cross-check."""
    scaled = x * 10
    floor_val = scaled.to_integral_value(rounding=decimal.ROUND_FLOOR)
    frac = scaled - floor_val
    return abs(frac - Decimal("0.5")) < Decimal("0.01")


def _fine_scan_root(lo: int, a: int, b: int) -> Optional[Decimal]:
    """Independently locate the root to about 4 decimal places via a fine
    step-0.001 linear scan across [lo, lo + 1], linearly interpolating across
    the sign change it finds - a genuinely different resolution and loop
    structure from the coarse 0.1-step trial-and-improvement table shown to
    the student, used only to cross-check the final 1dp answer."""
    step = Decimal("0.001")
    x_prev = Decimal(lo)
    val_prev = _f_cubic(x_prev, a, b)
    for _ in range(1000):
        x = x_prev + step
        val = _f_cubic(x, a, b)
        if val == 0:
            return x
        if (val > 0) != (val_prev > 0):
            root = x_prev + (x - x_prev) * (-val_prev) / (val - val_prev)
            return root.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        x_prev, val_prev = x, val
    return None


def _build_trial_improvement_example(rng: random.Random) -> _TrialData:
    for _ in range(300):
        a = rng.randint(*_TRIAL_A_RANGE)
        b = rng.randint(*_TRIAL_B_RANGE)

        lo = _find_bracket(a, b)
        if lo is None:
            continue

        f_lo = _f_cubic(Decimal(lo), a, b)
        f_hi = _f_cubic(Decimal(lo + 1), a, b)
        lo_positive = f_lo > 0

        coarse_rows = [
            (str(lo), _fmt_val(f_lo), _sign_word(f_lo)),
            (str(lo + 1), _fmt_val(f_hi), _sign_word(f_hi)),
        ]
        flip_d = None
        for d in range(1, 10):
            x = Decimal(lo) + Decimal(d) / Decimal(10)
            val = _f_cubic(x, a, b)
            if val == 0:
                break
            coarse_rows.append((f"{x:.1f}", _fmt_val(val), _sign_word(val)))
            if (val > 0) != lo_positive:
                flip_d = d
                break
        if flip_d is None or flip_d == 1:
            # No decimal sign flip found (shouldn't happen given the lo/lo+1
            # bracket already found one), or the flip happened at the very
            # first 0.1 step, leaving no earlier decimal row to pair with it
            # for a meaningful midpoint test - reject and retry.
            continue

        low_bound = Decimal(lo) + Decimal(flip_d - 1) / Decimal(10)
        high_bound = Decimal(lo) + Decimal(flip_d) / Decimal(10)
        mid_x = (low_bound + high_bound) / 2

        val_low = _f_cubic(low_bound, a, b)
        val_mid = _f_cubic(mid_x, a, b)
        if val_mid == 0:
            continue

        if (val_mid > 0) == (val_low > 0):
            answer = high_bound
            mid_side = "above"
        else:
            answer = low_bound
            mid_side = "below"

        fine_root = _fine_scan_root(lo, a, b)
        if fine_root is None or _near_1dp_boundary(fine_root):
            continue
        fine_answer = fine_root.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if fine_answer != answer:
            continue

        return _TrialData(
            a=a,
            b=b,
            lo=lo,
            coarse_rows=tuple(coarse_rows),
            mid_x=f"{mid_x:.2f}",
            mid_val=_fmt_val(val_mid),
            mid_side=mid_side,
            answer_1dp=f"{answer:.1f}",
        )
    raise ValueError("trial_and_improvement: failed to find safe (a, b) parameters after 300 tries")


def _format_cubic(a: int, b: int) -> str:
    parts = ["x^3"]
    if a > 0:
        parts.append(f"+ {a}x")
    elif a < 0:
        parts.append(f"- {abs(a)}x")
    parts.append(f"- {b}")
    return " ".join(parts)


def generate_trial_and_improvement(tier: Tier, rng: random.Random) -> Question:
    data = _build_trial_improvement_example(rng)
    formula = _format_cubic(data.a, data.b)
    low_x, high_x = data.coarse_rows[-2][0], data.coarse_rows[-1][0]

    steps = [f"f(x) = {formula}"]
    for x_str, val_str, sign in data.coarse_rows:
        steps.append(f"f({x_str}) = {val_str} ({sign})")
    steps.append(
        f"The sign changes between x = {low_x} and x = {high_x}, so try the midpoint "
        f"x = {data.mid_x}: f({data.mid_x}) = {data.mid_val}."
    )
    if data.mid_side == "above":
        steps.append(
            f"f({data.mid_x}) has the same sign as f({low_x}), so the root lies between {data.mid_x} and "
            f"{high_x} - to 1 decimal place, this rounds up to {data.answer_1dp}."
        )
    else:
        steps.append(
            f"f({data.mid_x}) has the same sign as f({high_x}), so the root lies between {low_x} and "
            f"{data.mid_x} - to 1 decimal place, this rounds down to {data.answer_1dp}."
        )

    return Question(
        topic_id="trial_and_improvement",
        tier=Tier.HIGHER,
        prompt=(
            f"f(x) = {formula}. Show that f(x) = 0 has a root between x = {data.lo} and x = {data.lo + 1}, "
            "then use trial and improvement to find this root correct to 1 decimal place."
        ),
        solution_steps=tuple(steps),
        final_answer=f"x = {data.answer_1dp}",
        dedup_key=f"trial_improve:{data.a}:{data.b}",
    )


def generate_modelled_example_trial_and_improvement(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _build_trial_improvement_example(rng)
    formula = _format_cubic(data.a, data.b)
    low_x, high_x = data.coarse_rows[-2][0], data.coarse_rows[-1][0]

    worked_calculation = [f"f(x) = {formula}"]
    for x_str, val_str, sign in data.coarse_rows:
        worked_calculation.append(f"f({x_str}) = {val_str} ({sign})")
    worked_calculation.append(f"f({data.mid_x}) = {data.mid_val}")
    worked_calculation.append(f"Root = {data.answer_1dp} (1 d.p.)")

    if data.mid_side == "above":
        rounding_explanation = (
            f"f({data.mid_x}) turned out to be the same sign as f({low_x}), which means the root is "
            f"actually trapped between {data.mid_x} and {high_x} - since that whole interval rounds to "
            f"{data.answer_1dp} to 1 decimal place, that's the final answer."
        )
    else:
        rounding_explanation = (
            f"f({data.mid_x}) turned out to be the same sign as f({high_x}), which means the root is "
            f"actually trapped between {low_x} and {data.mid_x} - since that whole interval rounds to "
            f"{data.answer_1dp} to 1 decimal place, that's the final answer."
        )

    teaching_steps = [
        "Trial and improvement finds a root by repeatedly narrowing down the interval it must lie in: "
        "start by confirming the sign of f(x) changes between two whole numbers (which guarantees a root "
        "lies between them), then test values with more and more decimal places to close in on it.",
        f"f({data.lo}) is {data.coarse_rows[0][2]} and f({data.lo + 1}) is {data.coarse_rows[1][2]} - since "
        f"the sign changes, there's a root somewhere between x = {data.lo} and x = {data.lo + 1}.",
        f"Testing x = {low_x}, {high_x} to one decimal place narrows this down further: the sign changes "
        f"between these two values, so the root is trapped between x = {low_x} and x = {high_x}.",
        f"To decide which of these two values the root rounds to, test the midpoint x = {data.mid_x}: "
        f"f({data.mid_x}) = {data.mid_val}. {rounding_explanation}",
        "It's always the midpoint of the narrowed 1dp interval that settles a trial-and-improvement "
        "question - whichever side of the midpoint the sign change actually falls on tells you which of "
        "the two 1dp values the true root is closer to.",
    ]

    return ModelledExample(
        topic_id="trial_and_improvement",
        tier=Tier.HIGHER,
        prompt=(
            f"f(x) = {formula}. Show that f(x) = 0 has a root between x = {data.lo} and x = {data.lo + 1}, "
            "then use trial and improvement to find this root correct to 1 decimal place."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {data.answer_1dp}",
    )


TOPIC_TRIAL_AND_IMPROVEMENT = TopicDefinition(
    id="trial_and_improvement",
    display_name="Trial and Improvement",
    description="Use systematic trial and improvement to find a root of a cubic equation to 1 decimal place.",
    generate=generate_trial_and_improvement,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_trial_and_improvement,
)
