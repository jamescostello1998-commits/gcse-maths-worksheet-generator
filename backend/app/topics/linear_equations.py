import random

import sympy as sp

from app.core.models import Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

TOPIC_ID = "linear_equations"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _generate_one_step(rng: random.Random):
    a = _rand_nonzero(rng, 2, 9)
    sol = rng.randint(1, 12)
    c = a * sol
    return (a, 0, 0, c), f"one_step:{a}:{c}"


def _generate_two_step(rng: random.Random):
    a = _rand_nonzero(rng, 2, 9)
    b = rng.randint(1, 15)
    sol = rng.randint(1, 12)
    c = a * sol + b
    return (a, b, 0, c), f"two_step:{a}:{b}:{c}"


def _generate_both_sides(rng: random.Random):
    a = _rand_nonzero(rng, -9, 9)
    c = _rand_nonzero(rng, -9, 9)
    while c == a:
        c = _rand_nonzero(rng, -9, 9)
    sol = _rand_nonzero(rng, -10, 10)
    b = rng.randint(-15, 15)
    d = a * sol + b - c * sol
    return (a, b, c, d), f"both_sides:{a}:{b}:{c}:{d}"


def _generate_bracket(rng: random.Random):
    a = _rand_nonzero(rng, 2, 6)
    b = _rand_nonzero(rng, 2, 6)
    c = rng.randint(-8, 8)
    sol = _rand_nonzero(rng, -8, 8)
    d = a * (b * sol + c)
    return a, b, c, d, f"bracket:{a}:{b}:{c}:{d}"


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["one_step", "two_step"])
        if shape == "one_step":
            (lhs_coeff, lhs_const, rhs_coeff, rhs_const), key = _generate_one_step(rng)
        else:
            (lhs_coeff, lhs_const, rhs_coeff, rhs_const), key = _generate_two_step(rng)
        orig_lhs = lhs_coeff * X + lhs_const
        orig_rhs = rhs_coeff * X + rhs_const
        prompt = f"Solve: {fmt_linear(lhs_coeff, lhs_const)} = {fmt_num(rhs_const)}"
        steps, solution = solve_linear_with_steps(lhs_coeff, lhs_const, rhs_coeff, rhs_const)
    else:
        shape = rng.choice(["both_sides", "bracket"])
        if shape == "both_sides":
            (lhs_coeff, lhs_const, rhs_coeff, rhs_const), key = _generate_both_sides(rng)
            orig_lhs = lhs_coeff * X + lhs_const
            orig_rhs = rhs_coeff * X + rhs_const
            prompt = f"Solve: {fmt_linear(lhs_coeff, lhs_const)} = {fmt_linear(rhs_coeff, rhs_const)}"
            steps, solution = solve_linear_with_steps(lhs_coeff, lhs_const, rhs_coeff, rhs_const)
        else:
            a, b, c, d, key = _generate_bracket(rng)
            orig_lhs = a * (b * X + c)
            orig_rhs = sp.Integer(d)
            prompt = f"Solve: {a}({fmt_linear(b, c)}) = {fmt_num(d)}"
            expand_step = f"Expand the bracket: {a}({fmt_linear(b, c)}) = {fmt_linear(a * b, a * c)}"
            steps, solution = solve_linear_with_steps(a * b, a * c, 0, d)
            steps = [expand_step] + steps

    residual = sp.simplify(orig_lhs.subs(X, solution) - orig_rhs.subs(X, solution))
    if residual != 0:
        raise ValueError(
            f"Generated linear equation failed verification (shape={shape}, "
            f"residual={residual}). This indicates a bug in the generator."
        )

    return Question(
        topic_id=TOPIC_ID,
        tier=tier,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"{shape}:{key}",
    )


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Solving Linear Equations",
    description="Solve equations for x, from one-step equations to equations with unknowns on both sides and brackets.",
    generate=generate,
)
