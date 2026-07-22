import math
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition
from app.topics.powers_roots import _SQUARE_FREE_FACTORS

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


def _fmt_surd_answer(nc: int, k: int, m: int, denom: int) -> str:
    """Render (nc + k*sqrt(m))/denom, using +/- for both roots at once."""
    surd = f"{k}√{m}" if k != 1 else f"√{m}"
    core = f"±{surd}" if nc == 0 else f"{nc} ± {surd}"
    return core if denom == 1 else f"({core})/{denom}"


def _decimal_case(rng: random.Random):
    """Pick a, b, c (a in 2-5) with a positive, non-square discriminant.

    Returns (a, b, c, D, x1, x2) where x1/x2 are the two roots, rounded to
    2dp (x1 is the '+' root, x2 is the '-' root).
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
    x1 = Decimal(str((-b + sqrt_D) / (2 * a))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    x2 = Decimal(str((-b - sqrt_D) / (2 * a))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if x1 == 0:
        x1 = Decimal("0.00")
    if x2 == 0:
        x2 = Decimal("0.00")

    # Independent verification: solve the equation exactly with sympy (a
    # different method than the manual quadratic-formula arithmetic above)
    # and confirm the exact roots round to the same 2dp values.
    exact = sorted(sp.N(root) for root in sp.solve(sp.Eq(a * X**2 + b * X + c, 0), X))
    mine = sorted([float(x1), float(x2)])
    for e_, m_ in zip(exact, mine):
        if abs(float(e_) - m_) > 0.006:
            raise ValueError("quadratic_formula decimal verification failed")

    return a, b, c, D, x1, x2


def _surd_case(rng: random.Random):
    """Pick a, b, c (a in 2-5) so the discriminant is exactly k^2*m for a
    square-free m > 1, giving an exact surd answer.

    Returns (a, b, c, D, k, m, nc, denom, g, nc2, k2, denom2), where the
    fully simplified roots are (nc2 +/- k2*sqrt(m)) / denom2.
    """
    for _ in range(500):
        a = rng.randint(2, 5)
        b = rng.randint(-14, 14)
        k = rng.randint(1, 4)
        m = rng.choice(_SQUARE_FREE_FACTORS)
        D = k * k * m
        num = b * b - D
        denom_check = 4 * a
        if num % denom_check != 0:
            continue
        c = num // denom_check
        break
    else:
        raise ValueError("quadratic_formula: could not construct surd-shape coefficients")

    # Independent check that m is genuinely square-free - a different check
    # than the curated _SQUARE_FREE_FACTORS list it was drawn from.
    for p in range(2, int(m**0.5) + 1):
        if m % (p * p) == 0:
            raise ValueError("quadratic_formula surd verification failed: m is not square-free")

    nc = -b
    denom = 2 * a
    g = math.gcd(math.gcd(abs(nc), k), denom)
    nc2, k2, denom2 = nc // g, k // g, denom // g

    # Independent verification of the simplification: sympy Rational
    # equality auto-reduces fractions on its own, a different check than the
    # gcd division above.
    if sp.Rational(nc, denom) != sp.Rational(nc2, denom2) or sp.Rational(k, denom) != sp.Rational(k2, denom2):
        raise ValueError("quadratic_formula surd simplification verification failed")

    # Independent verification that the claimed roots actually solve the
    # equation, substituting the exact symbolic expression back in - a
    # different check from the formula derivation above.
    sqrt_m = sp.sqrt(m)
    for sign in (1, -1):
        root = sp.Rational(nc2, denom2) + sign * sp.Rational(k2, denom2) * sqrt_m
        residual = sp.simplify(a * root**2 + b * root + c)
        if residual != 0:
            raise ValueError("quadratic_formula surd root verification failed")

    return a, b, c, D, k, m, nc, denom, g, nc2, k2, denom2


def generate_quadratic_formula(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["decimal", "surd"])

    if shape == "decimal":
        a, b, c, D, x1, x2 = _decimal_case(rng)
        steps = [
            "x = (-b ± √(b^2 - 4ac)) / 2a",
            f"a = {a}, b = {b}, c = {c}",
            f"x = ({-b} ± √({b}^2 - 4×{a}×{c})) / (2×{a})",
            f"x = ({-b} ± √{D}) / {2 * a}",
            f"x = {x1} or x = {x2}",
        ]
        return Question(
            topic_id="quadratic_formula",
            tier=Tier.HIGHER,
            prompt=f"Solve {_fmt_quadratic(a, b, c)} using the quadratic formula, "
            "giving your answers to 2 decimal places.",
            solution_steps=tuple(steps),
            final_answer=f"x = {x1} or x = {x2}",
            dedup_key=f"quad_dec:{a}:{b}:{c}",
        )

    a, b, c, D, k, m, nc, denom, g, nc2, k2, denom2 = _surd_case(rng)
    surd_term = f"{k}√{m}" if k != 1 else f"√{m}"
    answer = _fmt_surd_answer(nc2, k2, m, denom2)
    steps = [
        "x = (-b ± √(b^2 - 4ac)) / 2a",
        f"a = {a}, b = {b}, c = {c}",
        f"x = ({nc} ± √({b}^2 - 4×{a}×{c})) / {denom}",
        f"x = ({nc} ± √{D}) / {denom}",
        f"√{D} = √({k}^2 × {m}) = {surd_term}",
    ]
    if g > 1:
        steps.append(f"x = ({nc} ± {surd_term}) / {denom} = {answer} (dividing numerator and denominator by {g})")
    else:
        steps.append(f"x = ({nc} ± {surd_term}) / {denom}")
    return Question(
        topic_id="quadratic_formula",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(a, b, c)}, giving your answer in the form x = (-b ± k√m)/2a, "
        "fully simplified.",
        solution_steps=tuple(steps),
        final_answer=f"x = {answer}",
        dedup_key=f"quad_surd:{a}:{b}:{c}",
    )


def generate_modelled_example_quadratic_formula(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["decimal", "surd"])

    if shape == "decimal":
        a, b, c, D, x1, x2 = _decimal_case(rng)
        teaching_steps = [
            "Not every quadratic factorises nicely, so the quadratic formula gives a method that always "
            f"works: for ax^2 + bx + c = 0, the two solutions are x = (-b ± √(b^2 - 4ac)) / 2a.",
            f"Read off the coefficients from {_fmt_quadratic(a, b, c)}: a = {a}, b = {b}, c = {c}.",
            f"Substitute them into the formula: x = ({-b} ± √({b}^2 - 4×{a}×{c})) / (2×{a}), which works "
            f"out to x = ({-b} ± √{D}) / {2 * a}.",
            f"Since {D} isn't a perfect square, √{D} doesn't simplify to a whole number - a calculator is "
            "used here, and each root is rounded to 2 decimal places exactly as the question asks.",
            f"This gives the two solutions x = {x1} and x = {x2}.",
        ]
        worked_calculation = [
            f"a = {a}, b = {b}, c = {c}",
            f"x = ({-b} ± √{D}) / {2 * a}",
            f"x = {x1} or x = {x2}",
        ]
        return ModelledExample(
            topic_id="quadratic_formula",
            tier=Tier.HIGHER,
            prompt=f"Solve {_fmt_quadratic(a, b, c)} using the quadratic formula, "
            "giving your answers to 2 decimal places.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"x = {x1} or x = {x2}",
        )

    a, b, c, D, k, m, nc, denom, g, nc2, k2, denom2 = _surd_case(rng)
    surd_term = f"{k}√{m}" if k != 1 else f"√{m}"
    answer = _fmt_surd_answer(nc2, k2, m, denom2)
    teaching_steps = [
        "The quadratic formula, x = (-b ± √(b^2 - 4ac)) / 2a, always works for solving ax^2 + bx + c = 0 "
        "- and sometimes the number under the root simplifies to an exact surd instead of needing a "
        "decimal approximation.",
        f"Read off the coefficients from {_fmt_quadratic(a, b, c)}: a = {a}, b = {b}, c = {c}, then "
        f"substitute into the formula: x = ({nc} ± √({b}^2 - 4×{a}×{c})) / {denom} = ({nc} ± √{D}) / {denom}.",
        f"{D} has a square number hiding inside it: {D} = {k}^2 × {m}, so the root can be pulled apart "
        f"just like simplifying any other surd: √{D} = √({k}^2 × {m}) = {surd_term}.",
        (
            f"The fraction ({nc} ± {surd_term}) / {denom} can be simplified further, since {nc}, {k} and "
            f"{denom} share a common factor of {g} - dividing all three by it gives the fully simplified "
            f"answer {answer}."
            if g > 1
            else f"Here {nc}, {k} and {denom} share no common factor, so ({nc} ± {surd_term}) / {denom} is "
            "already fully simplified."
        ),
        f"So the exact solutions are x = {answer}.",
    ]
    worked_calculation = [
        f"a = {a}, b = {b}, c = {c}",
        f"x = ({nc} ± √{D}) / {denom}",
        f"x = {answer}",
    ]
    return ModelledExample(
        topic_id="quadratic_formula",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(a, b, c)}, giving your answer in the form x = (-b ± k√m)/2a, "
        "fully simplified.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {answer}",
    )


TOPIC_QUADRATIC_FORMULA = TopicDefinition(
    id="quadratic_formula",
    display_name="The Quadratic Formula",
    description="Solve a quadratic equation using the quadratic formula, giving decimal or exact surd answers.",
    generate=generate_quadratic_formula,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_quadratic_formula,
)
