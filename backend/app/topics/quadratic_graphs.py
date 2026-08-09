import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition
from app.topics.powers_roots import _SQUARE_FREE_FACTORS

SECTION = "algebra"
GROUP_SQUARE = "Completing the Square"
GROUP_TURNING_POINT = "Turning Point of a Graph"
GROUP_SOLVE_QUADRATIC = "Solving Quadratic Equations"


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
        f"{_fmt_quadratic(b, c)} = {_fmt_square_term(p)}^2 + ({c} - {p * p}) = {answer}",
    ]
    return Question(
        topic_id="completing_the_square_H",
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
        f"Complete the square: {_fmt_quadratic(b, c)} = {_fmt_completed_square(p, q)}",
        f"The turning point of y = (x + p)^2 + q is (-p, q).",
        f"Turning point = {answer}",
    ]
    return Question(
        topic_id="turning_point_of_graph_H",
        tier=Tier.HIGHER,
        prompt=f"Find the coordinates of the turning point of the curve y = {_fmt_quadratic(b, c)}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"turning_point:{p}:{c}",
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
        f"Putting it together: {_fmt_quadratic(b, c)} = {answer}.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(b, c)}",
        f"p = {b} ÷ 2 = {p}",
        f"= {_fmt_square_term(p)}^2 + ({c} - {p * p})",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="completing_the_square_H",
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
        f"Write the quadratic in completed-square form: {_fmt_quadratic(b, c)} "
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
        topic_id="turning_point_of_graph_H",
        tier=Tier.HIGHER,
        prompt=f"Find the coordinates of the turning point of the curve y = {_fmt_quadratic(b, c)}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def _fmt_surd_root(neg_p: int, k: int, m: int, sign: str) -> str:
    surd = f"{k}√{m}" if k != 1 else f"√{m}"
    op = "+" if sign == "+" else "-"
    if neg_p == 0:
        return f"{op}{surd}" if op == "-" else surd
    return f"{neg_p} {op} {surd}"


def _solve_completing_square_case(rng: random.Random):
    """Pick p, k, m so that x^2 + bx + c = (x+p)^2 + q has q = -(k^2 * m) for a
    square-free m > 1 - i.e. a quadratic that completes the square to give an
    exact surd root, x = -p +/- k*sqrt(m) (the classic reason completing the
    square is used to solve, rather than just rewrite, a quadratic)."""
    p = 0
    while p == 0:
        p = rng.randint(-9, 9)
    k = rng.randint(1, 3)
    m = rng.choice(_SQUARE_FREE_FACTORS)
    q = -(k * k * m)
    b = 2 * p
    c = p * p + q
    return p, k, m, q, b, c


def generate_solve_quadratic_completing_square(tier: Tier, rng: random.Random) -> Question:
    p, k, m, q, b, c = _solve_completing_square_case(rng)

    residual = sp.expand((X + p) ** 2 + q - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("solve_quadratic_completing_square verification failed: completed-square identity")

    # Independent check that m is genuinely square-free.
    for d in range(2, int(m**0.5) + 1):
        if m % (d * d) == 0:
            raise ValueError("solve_quadratic_completing_square verification failed: m not square-free")

    # Independent verification: substitute the two claimed roots back into the
    # original quadratic symbolically - a different path than the completing-
    # the-square algebra used to derive them.
    sqrt_m = sp.sqrt(m)
    for sign in (1, -1):
        root = -p + sign * k * sqrt_m
        if sp.simplify(root**2 + b * root + c) != 0:
            raise ValueError("solve_quadratic_completing_square verification failed: root substitution")

    root_plus = _fmt_surd_root(-p, k, m, "+")
    root_minus = _fmt_surd_root(-p, k, m, "-")
    answer = f"x = {root_plus} or x = {root_minus}"
    steps = [
        f"Half the coefficient of x: {b} ÷ 2 = {p}",
        f"Complete the square: {_fmt_quadratic(b, c)} = {_fmt_completed_square(p, q)}",
        f"Set {_fmt_completed_square(p, q)} = 0, so {_fmt_square_term(p)}^2 = {-q}",
        f"{_fmt_square_term(p)} = ±√{-q} = ±{k}√{m}" if k != 1 else f"{_fmt_square_term(p)} = ±√{-q}",
        f"x = {root_plus} or x = {root_minus}",
    ]
    return Question(
        topic_id="solve_quadratic_completing_square_H",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(b, c)} = 0 by completing the square, "
        "giving your answers in exact surd form.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"solve_complete_square:{p}:{k}:{m}",
    )


def generate_modelled_example_solve_quadratic_completing_square(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    p, k, m, q, b, c = _solve_completing_square_case(rng)

    residual = sp.expand((X + p) ** 2 + q - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("modelled example solve_quadratic_completing_square verification failed (symbolic)")
    sqrt_m = sp.sqrt(m)
    for sign in (1, -1):
        root = -p + sign * k * sqrt_m
        if sp.simplify(root**2 + b * root + c) != 0:
            raise ValueError("modelled example solve_quadratic_completing_square verification failed (root check)")

    root_plus = _fmt_surd_root(-p, k, m, "+")
    root_minus = _fmt_surd_root(-p, k, m, "-")
    answer = f"x = {root_plus} or x = {root_minus}"
    teaching_steps = [
        f"Not every quadratic factorises with nice whole numbers - {_fmt_quadratic(b, c)} doesn't, so "
        "completing the square gives a reliable way to solve it exactly, using surds where needed.",
        f"Complete the square as usual: half the coefficient of x ({b} ÷ 2 = {p}), which gives "
        f"{_fmt_quadratic(b, c)} = {_fmt_completed_square(p, q)}.",
        f"Setting the equation to 0 means {_fmt_completed_square(p, q)} = 0, so "
        f"{_fmt_square_term(p)}^2 = {-q}.",
        f"Take the square root of both sides - remembering both the positive and negative root - to get "
        f"{_fmt_square_term(p)} = ±√{-q}, which simplifies to ±{k}√{m}." if k != 1 else
        f"Take the square root of both sides - remembering both the positive and negative root - to get "
        f"{_fmt_square_term(p)} = ±√{-q}.",
        f"Finally, rearrange to make x the subject: x = {root_plus} or x = {root_minus}. Check by "
        f"substituting either root back into the original quadratic - it evaluates to exactly 0.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(b, c)} = 0",
        f"{_fmt_completed_square(p, q)} = 0",
        f"{_fmt_square_term(p)} = ±√{-q}",
        f"x = {root_plus} or x = {root_minus}",
    ]
    return ModelledExample(
        topic_id="solve_quadratic_completing_square_H",
        tier=Tier.HIGHER,
        prompt=f"Solve {_fmt_quadratic(b, c)} = 0 by completing the square, "
        "giving your answers in exact surd form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_COMPLETING_THE_SQUARE = TopicDefinition(
    id="completing_the_square_H",
    display_name="Completing the Square",
    description="Write a quadratic expression in completed-square form (x + p)^2 + q.",
    generate=generate_completing_the_square,
    section=SECTION,
    group=GROUP_SQUARE,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_completing_the_square,
)

TOPIC_TURNING_POINT = TopicDefinition(
    id="turning_point_of_graph_H",
    display_name="Turning Point of a Graph",
    description="Use completing the square to find the turning point of a quadratic graph.",
    generate=generate_turning_point,
    section=SECTION,
    group=GROUP_TURNING_POINT,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_turning_point,
)

TOPIC_SOLVE_QUADRATIC_COMPLETING_SQUARE = TopicDefinition(
    id="solve_quadratic_completing_square_H",
    display_name="Solving by Completing the Square",
    description="Solve a quadratic equation by completing the square, giving exact surd answers.",
    generate=generate_solve_quadratic_completing_square,
    section=SECTION,
    group=GROUP_SOLVE_QUADRATIC,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_solve_quadratic_completing_square,
)
