"""Solving equations by cross-multiplication (Corbett V112).

Both tiers reduce a "fraction = fraction" equation to a LINEAR equation by
cross-multiplying, then finish with algebra_utils.solve_linear_with_steps:

- cross_multiplication_F : a single unknown against a numeric fraction
  (x/a = c/d, b/x = c/d, mx/a = c/d, (x+p)/a = c/d) - integer answers.
- cross_multiplication_H : linear expressions on both sides
  ((px+q)/a = (rx+s)/b).

Every fraction is emitted with the \\frac{}{} marker so mathtext.py renders a
true vinculum. Each answer is cross-checked independently with sympy.
"""

import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Solving Linear Equations"
INSTRUCTION = "Solve the following equation."


def _frac(num, den) -> str:
    return f"\\frac{{{num}}}{{{den}}}"


def _signed(p: int) -> str:
    return f"+ {p}" if p >= 0 else f"- {abs(p)}"


def _verify(lhs, rhs, expected) -> bool:
    sols = sp.solve(sp.Eq(lhs, rhs), X)
    return len(sols) == 1 and sp.Rational(sols[0]) == sp.Rational(expected)


# ---------------------------------------------------------------------------
# Foundation: single unknown = numeric fraction -> linear (integer answers)
# ---------------------------------------------------------------------------


def _build_cross_F(rng: random.Random):
    shape = rng.choice(["x_over_a", "b_over_x", "coeff", "bracket"])
    a = rng.randint(2, 12)
    c = rng.randint(2, 12)
    d = rng.randint(2, 12)
    if c % d == 0:  # the numeric fraction must be a genuine fraction, not a whole number
        return None
    if shape == "x_over_a":  # x/a = c/d
        lhs, rhs = X / a, sp.Rational(c, d)
        disp = f"{_frac('x', a)} = {_frac(c, d)}"
        cross = f"Cross-multiply: x × {d} = {a} × {c}"
    elif shape == "b_over_x":  # b/x = c/d
        b = rng.randint(2, 12)
        lhs, rhs = sp.Rational(b) / X, sp.Rational(c, d)
        disp = f"{_frac(b, 'x')} = {_frac(c, d)}"
        cross = f"Cross-multiply: {b} × {d} = {c} × x"
    elif shape == "coeff":  # mx/a = c/d
        m = rng.randint(2, 6)
        lhs, rhs = (m * X) / a, sp.Rational(c, d)
        disp = f"{_frac(f'{m}x', a)} = {_frac(c, d)}"
        cross = f"Cross-multiply: {m}x × {d} = {a} × {c}"
    else:  # (x + p)/a = c/d
        p = rng.choice([n for n in range(-9, 10) if n != 0])
        lhs, rhs = (X + p) / a, sp.Rational(c, d)
        disp = f"{_frac(f'x {_signed(p)}', a)} = {_frac(c, d)}"
        cross = f"Cross-multiply: (x {_signed(p)}) × {d} = {a} × {c}"

    sols = sp.solve(sp.Eq(lhs, rhs), X)
    if len(sols) != 1:
        return None
    x_sol = sp.Rational(sols[0])
    if not x_sol.is_Integer or x_sol <= 0:  # keep Foundation answers clean positive integers
        return None
    steps = [cross, f"x = {fmt_num(x_sol)}"]
    return disp, steps, x_sol, lhs, rhs, shape


def generate_cross_multiplication_F(tier: Tier, rng: random.Random) -> Question:
    for _ in range(80):
        built = _build_cross_F(rng)
        if built and _verify(built[3], built[4], built[2]):
            disp, steps, x_sol, lhs, rhs, shape = built
            break
    else:
        raise ValueError("cross_multiplication_F could not build a verified equation")
    return Question(
        topic_id="cross_multiplication_F",
        tier=Tier.FOUNDATION,
        prompt=f"{INSTRUCTION}\n{disp}",
        solution_steps=tuple(steps),
        final_answer=f"x = {fmt_num(x_sol)}",
        dedup_key=f"cross_f:{shape}:{disp}",
    )


def generate_modelled_example_cross_multiplication_F(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(80):
        built = _build_cross_F(rng)
        if built and _verify(built[3], built[4], built[2]):
            disp, steps, x_sol, lhs, rhs, shape = built
            break
    else:
        raise ValueError("cross_multiplication_F modelled example could not build a verified equation")
    teaching_steps = [
        "When one fraction equals another fraction, you can 'cross-multiply': multiply the numerator of "
        "each side by the denominator of the OTHER side. This clears both denominators in a single step "
        "and leaves an equation with no fractions.",
        "The two products it produces are equal, so set them equal to each other - that gives an ordinary "
        "equation you can solve for x.",
        f"Here that gives: {steps[0].replace('Cross-multiply: ', '')}, and solving gives x = {fmt_num(x_sol)}.",
    ]
    worked_calculation = [disp] + list(steps)
    return ModelledExample(
        topic_id="cross_multiplication_F",
        tier=Tier.FOUNDATION,
        prompt=f"{INSTRUCTION}\n{disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {fmt_num(x_sol)}",
    )


# ---------------------------------------------------------------------------
# Higher: linear expression = linear expression -> cross-multiply -> linear
# ---------------------------------------------------------------------------


def _x_coeff(rng: random.Random) -> int:
    """A non-zero x-coefficient, biased positive (mostly 1-6) so a worksheet
    isn't dominated by negative-leading numerators."""
    v = rng.randint(1, 6)
    return v if rng.random() < 0.75 else -v


def _build_cross_H(rng: random.Random):
    a = rng.randint(2, 6)
    b = rng.choice([n for n in range(2, 7) if n != a])  # different denominators -> genuine cross-multiplication
    p = _x_coeff(rng)
    q = rng.randint(-9, 9)
    r = _x_coeff(rng)
    s = rng.randint(-9, 9)
    # Cross-multiplying (px+q)/a = (rx+s)/b gives b(px+q) = a(rx+s).
    lin_l_coeff, lin_l_const = b * p, b * q
    lin_r_coeff, lin_r_const = a * r, a * s
    if lin_l_coeff == lin_r_coeff:  # no unique solution
        return None
    tail_steps, x_sol = solve_linear_with_steps(lin_l_coeff, lin_l_const, lin_r_coeff, lin_r_const)
    if x_sol.q > 6:  # avoid ugly fractional answers
        return None
    lhs, rhs = (p * X + q) / a, (r * X + s) / b
    disp = f"{_frac(fmt_linear(p, q), a)} = {_frac(fmt_linear(r, s), b)}"
    cross = f"Cross-multiply: {b}({fmt_linear(p, q)}) = {a}({fmt_linear(r, s)})"
    steps = [cross] + tail_steps
    return disp, steps, x_sol, lhs, rhs


def generate_cross_multiplication_H(tier: Tier, rng: random.Random) -> Question:
    for _ in range(120):
        built = _build_cross_H(rng)
        if built and _verify(built[3], built[4], built[2]):
            disp, steps, x_sol, lhs, rhs = built
            break
    else:
        raise ValueError("cross_multiplication_H could not build a verified equation")
    return Question(
        topic_id="cross_multiplication_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION}\n{disp}",
        solution_steps=tuple(steps),
        final_answer=f"x = {fmt_num(x_sol)}",
        dedup_key=f"cross_h:{disp}",
    )


def generate_modelled_example_cross_multiplication_H(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(120):
        built = _build_cross_H(rng)
        if built and _verify(built[3], built[4], built[2]):
            disp, steps, x_sol, lhs, rhs = built
            break
    else:
        raise ValueError("cross_multiplication_H modelled example could not build a verified equation")
    teaching_steps = [
        "With a linear expression over a number on each side, cross-multiply: multiply each numerator by "
        "the denominator on the other side. This removes both fractions in one move.",
        "Remember to multiply the WHOLE numerator - keep it in brackets and expand carefully, since every "
        "term inside is multiplied by the number outside.",
        "That leaves a linear equation with the unknown on both sides; collect the x-terms on one side and "
        "the numbers on the other, then solve. The steps: " + "  ".join(steps),
    ]
    worked_calculation = [disp] + list(steps)
    return ModelledExample(
        topic_id="cross_multiplication_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION}\n{disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {fmt_num(x_sol)}",
    )


TOPIC_CROSS_MULTIPLICATION_F = TopicDefinition(
    id="cross_multiplication_F",
    display_name="Cross Multiplication",
    description="Solve a 'fraction = fraction' equation by cross-multiplying to a linear equation.",
    generate=generate_cross_multiplication_F,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_cross_multiplication_F,
)

TOPIC_CROSS_MULTIPLICATION_H = TopicDefinition(
    id="cross_multiplication_H",
    display_name="Cross Multiplication (Higher)",
    description="Solve an equation with a linear expression over a number on each side by cross-multiplying.",
    generate=generate_cross_multiplication_H,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_cross_multiplication_H,
)
