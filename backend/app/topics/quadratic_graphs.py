import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
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


def generate_modelled_example_completing_the_square(tier: Tier, rng: random.Random) -> ModelledExample:
    p = _rand_nonzero(rng, -9, 9)
    b = 2 * p
    c = rng.randint(-15, 15)
    q = c - p * p

    residual = sp.expand((X + p) ** 2 + q - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("modelled example completing_the_square verification failed")

    answer = _fmt_completed_square(p, q)
    teaching_steps = [
        f"Any quadratic x^2 + bx + c can be rewritten in the form (x + p)^2 + q - this is called "
        "completing the square, and it works because (x + p)^2 always expands to give back the same "
        "x^2 and bx terms, as long as p is chosen correctly.",
        f"Expanding (x + p)^2 gives x^2 + 2px + p^2, so matching the x term to our {b}x tells us "
        f"2p = {b}, meaning p = {p} (half of {b}).",
        f"Now check what (x {'+' if p >= 0 else '-'} {abs(p)})^2 actually expands to: "
        f"x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {p * p}. Our original expression has {c} as the "
        f"constant, not {p * p}, so we need to add on the difference: {c} - {p * p} = {q}.",
        f"Putting it together: x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {c} = {answer}.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(b, c)}",
        f"p = {b} ÷ 2 = {p}",
        f"= {_fmt_square_term(p)}^2 + ({c} - {p * p})",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="completing_the_square",
        tier=Tier.HIGHER,
        prompt=f"Write {_fmt_quadratic(b, c)} in the form (x + p)^2 + q.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_turning_point(tier: Tier, rng: random.Random) -> ModelledExample:
    p = _rand_nonzero(rng, -9, 9)
    b = 2 * p
    c = rng.randint(-15, 15)
    q = c - p * p
    vertex_x, vertex_y = -p, q

    def y_at(x_val: int) -> int:
        return x_val * x_val + b * x_val + c

    left, centre, right = y_at(vertex_x - 1), y_at(vertex_x), y_at(vertex_x + 1)
    if left != right or centre != vertex_y or centre > left:
        raise ValueError("modelled example turning_point verification failed")

    answer = f"({vertex_x}, {vertex_y})"
    teaching_steps = [
        "A quadratic graph y = x^2 + bx + c is a symmetric U-shape, and its turning point (the very "
        "bottom of the U) sits exactly on the graph's line of symmetry. Completing the square finds "
        "that point directly.",
        f"Write the quadratic in completed-square form: x^2 {'+' if b >= 0 else '-'} {abs(b)}x + {c} "
        f"= {_fmt_completed_square(p, q)}.",
        f"In the form (x + p)^2 + q, the squared term (x + p)^2 can never be negative, so the smallest "
        f"it can ever be is 0 - and that happens exactly when x = {vertex_x}. At that point, "
        f"y = 0 + {q} = {q}.",
        f"So the turning point is where x = {vertex_x} and y = {q}, giving {answer}.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(b, c)}",
        f"= {_fmt_completed_square(p, q)}",
        f"Turning point = (-p, q) = {answer}",
    ]
    return ModelledExample(
        topic_id="turning_point_of_graph",
        tier=Tier.HIGHER,
        prompt=f"Find the coordinates of the turning point of the curve y = {_fmt_quadratic(b, c)}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
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
    generate_modelled_example=generate_modelled_example_completing_the_square,
)

TOPIC_TURNING_POINT = TopicDefinition(
    id="turning_point_of_graph",
    display_name="Turning Point of a Graph",
    description="Use completing the square to find the turning point of a quadratic graph.",
    generate=generate_turning_point,
    section=SECTION,
    group=GROUP_TURNING_POINT,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_turning_point,
)
