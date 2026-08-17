import math
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Solving Quadratic Equations"


def _fmt_quadratic(a, b, c) -> str:
    """Render ax^2 + bx + c = 0."""
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x^2")
        elif a == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{a}x^2")
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        if parts:
            parts.append(f"{'+' if b > 0 else '-'} {term}")
        else:
            parts.append(f"-{term}" if b < 0 else term)
    if c != 0 or not parts:
        if parts:
            parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
        else:
            parts.append(str(c))
    return " ".join(parts) + " = 0"


def _decimal_case(rng: random.Random):
    """Pick a, b, c (a in 2-5) with a positive, non-square discriminant.

    Returns (a, b, c, D, x1, x2) where x1/x2 are the two roots, rounded to
    4dp (x1 is the '+' root, x2 is the '-' root). Rounded to 4dp rather than
    the number of decimal places actually asked for (the prompt no longer
    states one at all - the student picks a sensible precision themselves),
    so the stored answer is precise enough to check a student's answer at
    whatever reasonable precision they chose.
    """
    for _ in range(300):
        a = rng.randint(2, 5)
        b = rng.randint(-14, 14)
        c = rng.randint(-14, 14)
        D = b * b - 4 * a * c
        if D <= 0:
            continue
        r = math.isqrt(D)
        if r * r == D:
            continue
        break
    else:
        raise ValueError("quadratic_formula: could not construct decimal-shape coefficients")

    sqrt_D = math.sqrt(D)
    x1 = Decimal(str((-b + sqrt_D) / (2 * a))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    x2 = Decimal(str((-b - sqrt_D) / (2 * a))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    if x1 == 0:
        x1 = Decimal("0.0000")
    if x2 == 0:
        x2 = Decimal("0.0000")

    # Independent verification: solve the equation exactly with sympy (a
    # different method than the manual quadratic-formula arithmetic above)
    # and confirm the exact roots round to the same 4dp values.
    exact = sorted(sp.N(root) for root in sp.solve(sp.Eq(a * X**2 + b * X + c, 0), X))
    mine = sorted([float(x1), float(x2)])
    for e_, m_ in zip(exact, mine):
        if abs(float(e_) - m_) > 0.00006:
            raise ValueError("quadratic_formula decimal verification failed")

    return a, b, c, D, x1, x2


def generate_quadratic_formula(tier: Tier, rng: random.Random) -> Question:
    a, b, c, D, x1, x2 = _decimal_case(rng)
    steps = [
        "x = (-b ± √(b^2 - 4ac)) / 2a",
        f"a = {a}, b = {b}, c = {c}",
        f"x = \\frac{{{-b} ± √({b}^2 - 4×{a}×{c})}}{{2×{a}}}",
        f"x = \\frac{{{-b} ± √{D}}}{{{2 * a}}}",
        f"x = {x1} or x = {x2}",
    ]
    return Question(
        topic_id="quadratic_formula_H",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(a, b, c)}",
        solution_steps=tuple(steps),
        final_answer=f"x = {x1} or x = {x2}",
        dedup_key=f"quad_dec:{a}:{b}:{c}",
    )


def generate_modelled_example_quadratic_formula(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c, D, x1, x2 = _decimal_case(rng)
    teaching_steps = [
        "Not every quadratic factorises nicely, so the quadratic formula gives a method that always "
        f"works: for ax^2 + bx + c = 0, the two solutions are x = (-b ± √(b^2 - 4ac)) / 2a.",
        f"Read off the coefficients from {_fmt_quadratic(a, b, c)}: a = {a}, b = {b}, c = {c}.",
        f"Substitute them into the formula: x = \\frac{{{-b} ± √({b}^2 - 4×{a}×{c})}}{{2×{a}}}, which "
        f"works out to x = \\frac{{{-b} ± √{D}}}{{{2 * a}}}.",
        f"Since {D} isn't a perfect square, √{D} doesn't simplify to a whole number - a calculator is "
        "used here. The question doesn't state how many decimal places to round to, so pick a sensible "
        "precision (2 or 3 decimal places is typical) and say what you rounded to.",
        f"This gives the two solutions x = {x1} and x = {x2} (shown here to 4 decimal places).",
    ]
    worked_calculation = [
        f"a = {a}, b = {b}, c = {c}",
        f"x = \\frac{{{-b} ± √{D}}}{{{2 * a}}}",
        f"x = {x1} or x = {x2}",
    ]
    return ModelledExample(
        topic_id="quadratic_formula_H",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(a, b, c)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {x1} or x = {x2}",
    )


TOPIC_QUADRATIC_FORMULA = TopicDefinition(
    id="quadratic_formula_H",
    display_name="The Quadratic Formula",
    description="Solve a quadratic equation using the quadratic formula, giving decimal answers.",
    generate=generate_quadratic_formula,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_quadratic_formula,
)
