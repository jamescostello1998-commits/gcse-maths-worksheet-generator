import random

import sympy as sp

from app.core.models import DiagramSpec, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP_SQUARE = "Completing the Square"
GROUP_TURNING_POINT = "Turning Point of a Graph"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_quadratic(b: int, c: int) -> str:
    parts = ["x^2"]
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    if c != 0:
        parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
    return " ".join(parts)


def _fmt_square_term(p: int) -> str:
    if p > 0:
        return f"(x + {p})"
    if p < 0:
        return f"(x - {abs(p)})"
    return "x"


def _fmt_completed_square(p: int, q: int) -> str:
    square = f"{_fmt_square_term(p)}^2"
    if q == 0:
        return square
    return f"{square} {'+' if q > 0 else '-'} {abs(q)}"


def generate_completing_the_square(tier: Tier, rng: random.Random) -> Question:
    p = _rand_nonzero(rng, -9, 9)
    b = 2 * p
    c = rng.randint(-15, 15)
    q = c - p * p

    residual = sp.expand((X + p) ** 2 + q - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("completing_the_square verification failed")

    answer = _fmt_completed_square(p, q)
    steps = [
        f"Half the coefficient of x: {b} ÷ 2 = {p}",
        f"{_fmt_square_term(p)}^2 = x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {p * p}",
        f"x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {c} = {_fmt_square_term(p)}^2 + ({c} - {p * p}) = {answer}",
    ]
    return Question(
        topic_id="completing_the_square",
        tier=Tier.HIGHER,
        prompt=f"Write {_fmt_quadratic(b, c)} in the form (x + p)^2 + q.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"complete_square:{p}:{c}",
    )


def generate_turning_point(tier: Tier, rng: random.Random) -> Question:
    p = _rand_nonzero(rng, -9, 9)
    b = 2 * p
    c = rng.randint(-15, 15)
    q = c - p * p
    vertex_x, vertex_y = -p, q

    residual = sp.expand((X - vertex_x) ** 2 + vertex_y - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("turning_point verification failed: completed-square identity")

    # Independent verification via symmetry: the curve's value one step either side of
    # the claimed turning point must be equal (and no smaller), a different check than
    # the completing-the-square algebra above.
    def y_at(x_val: int) -> int:
        return x_val * x_val + b * x_val + c

    left, centre, right = y_at(vertex_x - 1), y_at(vertex_x), y_at(vertex_x + 1)
    if left != right or centre != vertex_y or centre > left:
        raise ValueError("turning_point verification failed: symmetry cross-check")

    answer = f"({vertex_x}, {vertex_y})"
    steps = [
        f"Complete the square: x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {c} = {_fmt_completed_square(p, q)}",
        f"The turning point of y = (x + p)^2 + q is (-p, q).",
        f"Turning point = {answer}",
    ]
    return Question(
        topic_id="turning_point_of_graph",
        tier=Tier.HIGHER,
        prompt=f"Find the coordinates of the turning point of the curve y = {_fmt_quadratic(b, c)}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"turning_point:{p}:{c}",
        diagram=DiagramSpec(kind="parabola", params={"vertex_label": answer}),
    )


TOPIC_COMPLETING_THE_SQUARE = TopicDefinition(
    id="completing_the_square",
    display_name="Completing the Square",
    description="Write a quadratic expression in completed-square form (x + p)^2 + q.",
    generate=generate_completing_the_square,
    section=SECTION,
    group=GROUP_SQUARE,
    fixed_tier=Tier.HIGHER,
)

TOPIC_TURNING_POINT = TopicDefinition(
    id="turning_point_of_graph",
    display_name="Turning Point of a Graph",
    description="Use completing the square to find the turning point of a quadratic graph.",
    generate=generate_turning_point,
    section=SECTION,
    group=GROUP_TURNING_POINT,
    fixed_tier=Tier.HIGHER,
)
