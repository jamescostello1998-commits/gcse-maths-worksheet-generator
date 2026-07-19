import random

import sympy as sp

from app.core.models import Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Solving Linear Equations"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def generate_one_step(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, 2, 9)
    sol = rng.randint(1, 12)
    c = a * sol

    orig_lhs = a * X
    orig_rhs = sp.Integer(c)
    steps, solution = solve_linear_with_steps(a, 0, 0, c)
    _verify(orig_lhs, orig_rhs, solution, "one_step")

    return Question(
        topic_id="linear_one_step",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {fmt_linear(a, 0)} = {fmt_num(c)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"one_step:{a}:{c}",
    )


def generate_two_step(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, 2, 9)
    b = rng.randint(1, 15)
    sol = rng.randint(1, 12)
    c = a * sol + b

    orig_lhs = a * X + b
    orig_rhs = sp.Integer(c)
    steps, solution = solve_linear_with_steps(a, b, 0, c)
    _verify(orig_lhs, orig_rhs, solution, "two_step")

    return Question(
        topic_id="linear_two_step",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_num(c)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"two_step:{a}:{b}:{c}",
    )


def generate_multi_step(tier: Tier, rng: random.Random) -> Question:
    coeff1 = _rand_nonzero(rng, 2, 6)
    coeff2 = _rand_nonzero(rng, 2, 6)
    const1 = rng.randint(1, 15)
    const2 = _rand_nonzero(rng, -10, 10)
    sol = rng.randint(1, 12)
    combined_coeff = coeff1 + coeff2
    combined_const = const1 + const2
    c = combined_coeff * sol + combined_const

    orig_lhs = coeff1 * X + const1 + coeff2 * X + const2
    orig_rhs = sp.Integer(c)

    const2_sign = "+" if const2 >= 0 else "-"
    collect_step = (
        f"Collect like terms: {coeff1}x + {coeff2}x = {combined_coeff}x, "
        f"{fmt_num(const1)} {const2_sign} {fmt_num(abs(const2))} = {fmt_num(combined_const)}"
    )
    solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, c)
    steps = [collect_step] + solve_steps
    _verify(orig_lhs, orig_rhs, solution, "multi_step")

    prompt = f"Solve: {coeff1}x + {const1} + {coeff2}x {const2_sign} {abs(const2)} = {c}"
    return Question(
        topic_id="linear_multi_step",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"multi_step:{coeff1}:{const1}:{coeff2}:{const2}:{c}",
    )


def generate_both_sides(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, -9, 9)
    c = _rand_nonzero(rng, -9, 9)
    while c == a:
        c = _rand_nonzero(rng, -9, 9)
    sol = _rand_nonzero(rng, -10, 10)
    b = rng.randint(-15, 15)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    steps, solution = solve_linear_with_steps(a, b, c, d)
    _verify(orig_lhs, orig_rhs, solution, "both_sides")

    return Question(
        topic_id="linear_both_sides",
        tier=Tier.HIGHER,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"both_sides:{a}:{b}:{c}:{d}",
    )


def generate_both_sides_foundation(tier: Tier, rng: random.Random) -> Question:
    # Same shape as generate_both_sides but with positive coefficients and a
    # positive solution, so a Foundation student never has to juggle a negative
    # coefficient of x - this is Foundation-tier content on the real GCSE specs,
    # just with friendlier numbers than the Higher version above.
    a = rng.randint(2, 6)
    c = rng.randint(2, 6)
    while c == a:
        c = rng.randint(2, 6)
    sol = rng.randint(1, 10)
    b = rng.randint(0, 12)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    steps, solution = solve_linear_with_steps(a, b, c, d)
    _verify(orig_lhs, orig_rhs, solution, "both_sides_foundation")

    return Question(
        topic_id="linear_both_sides_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"both_sides_f:{a}:{b}:{c}:{d}",
    )


def generate_brackets(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, 2, 6)
    b = _rand_nonzero(rng, 2, 6)
    c = rng.randint(-8, 8)
    sol = _rand_nonzero(rng, -8, 8)
    d = a * (b * sol + c)

    orig_lhs = a * (b * X + c)
    orig_rhs = sp.Integer(d)
    expand_step = f"Expand the bracket: {a}({fmt_linear(b, c)}) = {fmt_linear(a * b, a * c)}"
    solve_steps, solution = solve_linear_with_steps(a * b, a * c, 0, d)
    steps = [expand_step] + solve_steps
    _verify(orig_lhs, orig_rhs, solution, "brackets")

    return Question(
        topic_id="linear_brackets",
        tier=Tier.HIGHER,
        prompt=f"Solve: {a}({fmt_linear(b, c)}) = {fmt_num(d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"brackets:{a}:{b}:{c}:{d}",
    )


def generate_brackets_foundation(tier: Tier, rng: random.Random) -> Question:
    # Same shape as generate_brackets but c and the solution are restricted to
    # non-negative, so expanding the bracket never introduces a negative term -
    # Foundation-tier content on the real GCSE specs, friendlier than Higher above.
    a = rng.randint(2, 5)
    b = rng.randint(2, 5)
    c = rng.randint(0, 8)
    sol = rng.randint(1, 8)
    d = a * (b * sol + c)

    orig_lhs = a * (b * X + c)
    orig_rhs = sp.Integer(d)
    expand_step = f"Expand the bracket: {a}({fmt_linear(b, c)}) = {fmt_linear(a * b, a * c)}"
    solve_steps, solution = solve_linear_with_steps(a * b, a * c, 0, d)
    steps = [expand_step] + solve_steps
    _verify(orig_lhs, orig_rhs, solution, "brackets_foundation")

    return Question(
        topic_id="linear_brackets_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {a}({fmt_linear(b, c)}) = {fmt_num(d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"brackets_f:{a}:{b}:{c}:{d}",
    )


def _verify(orig_lhs, orig_rhs, solution, shape: str) -> None:
    residual = sp.simplify(orig_lhs.subs(X, solution) - orig_rhs.subs(X, solution))
    if residual != 0:
        raise ValueError(
            f"Generated linear equation failed verification (shape={shape}, residual={residual})."
        )


TOPIC_ONE_STEP = TopicDefinition(
    id="linear_one_step",
    display_name="One-Step Equations",
    description="Solve simple equations of the form ax = c.",
    generate=generate_one_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_TWO_STEP = TopicDefinition(
    id="linear_two_step",
    display_name="Two-Step Equations",
    description="Solve equations of the form ax + b = c.",
    generate=generate_two_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_MULTI_STEP = TopicDefinition(
    id="linear_multi_step",
    display_name="Multi-Step Equations",
    description="Collect like terms on one side before solving.",
    generate=generate_multi_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_BOTH_SIDES_FOUNDATION = TopicDefinition(
    id="linear_both_sides_foundation",
    display_name="Unknowns on Both Sides",
    description="Solve equations with the unknown appearing on both sides.",
    generate=generate_both_sides_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_BOTH_SIDES = TopicDefinition(
    id="linear_both_sides",
    display_name="Unknowns on Both Sides",
    description="Solve equations with the unknown appearing on both sides, including negative coefficients.",
    generate=generate_both_sides,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_BRACKETS_FOUNDATION = TopicDefinition(
    id="linear_brackets_foundation",
    display_name="Equations with Brackets",
    description="Expand a bracket before solving the equation.",
    generate=generate_brackets_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_BRACKETS = TopicDefinition(
    id="linear_brackets",
    display_name="Equations with Brackets",
    description="Expand a bracket before solving the equation, including negative terms.",
    generate=generate_brackets,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
