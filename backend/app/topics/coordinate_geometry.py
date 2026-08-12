"""Coordinate geometry of a line segment: the midpoint of two points
(Foundation) and the length/distance between two points (Higher).

Midpoint is built by averaging the coordinates, then independently verified by
the vector-equality definition (M - A must equal B - M). Distance is built with
Pythagoras and independently verified against math.hypot (a floating-point path
entirely separate from the exact integer/surd arithmetic used for the answer).
"""

import math
import random
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Coordinate Geometry"


def _fmt_half(value: Fraction) -> str:
    """A midpoint coordinate is always a whole number or a half; show it as an
    integer or a one-decimal-place decimal (never an ugly fraction)."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.1f}"


def _largest_square_factor(n: int) -> tuple[int, int]:
    """Return (k, m) with k*k*m == n and m square-free, k maximal."""
    k = math.isqrt(n)
    while k > 1:
        if n % (k * k) == 0:
            return k, n // (k * k)
        k -= 1
    return 1, n


def _fmt_surd(k: int, m: int) -> str:
    return f"√{m}" if k == 1 else f"{k}√{m}"


def _two_points(rng: random.Random) -> tuple[int, int, int, int]:
    while True:
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        x2, y2 = rng.randint(-8, 8), rng.randint(-8, 8)
        if (x1, y1) != (x2, y2):
            return x1, y1, x2, y2


# --------------------------------------------------------------------------
# Midpoint (Foundation)
# --------------------------------------------------------------------------


def _build_midpoint(rng: random.Random) -> tuple[int, int, int, int, Fraction, Fraction]:
    x1, y1, x2, y2 = _two_points(rng)
    mx = Fraction(x1 + x2, 2)
    my = Fraction(y1 + y2, 2)

    # Independent verification via the defining property of a midpoint: the
    # step from A to M must be identical to the step from M to B.
    if (mx - x1, my - y1) != (x2 - mx, y2 - my):
        raise ValueError("midpoint verification failed")

    return x1, y1, x2, y2, mx, my


def generate_midpoint_of_segment(tier: Tier, rng: random.Random) -> Question:
    x1, y1, x2, y2, mx, my = _build_midpoint(rng)
    answer = f"({_fmt_half(mx)}, {_fmt_half(my)})"
    steps = [
        "The midpoint of a line segment is the average of its two end points: average the two "
        "x-coordinates, then average the two y-coordinates.",
        f"x-coordinate of midpoint: ({x1} + {x2})/2 = {_fmt_half(mx)}",
        f"y-coordinate of midpoint: ({y1} + {y2})/2 = {_fmt_half(my)}",
        f"Midpoint = {answer}",
    ]
    return Question(
        topic_id="midpoint_of_segment_F",
        tier=Tier.FOUNDATION,
        prompt=f"Find the midpoint of the line segment joining A({x1}, {y1}) and B({x2}, {y2}).",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"midpoint:{x1}:{y1}:{x2}:{y2}",
    )


def generate_modelled_example_midpoint_of_segment(tier: Tier, rng: random.Random) -> ModelledExample:
    x1, y1, x2, y2, mx, my = _build_midpoint(rng)
    answer = f"({_fmt_half(mx)}, {_fmt_half(my)})"
    teaching_steps = [
        f"We want the point exactly halfway along the line segment from A({x1}, {y1}) to "
        f"B({x2}, {y2}). Because 'halfway' means the average position, the midpoint's coordinates "
        "are just the averages of the two end points' coordinates - you handle the x's and the y's "
        "completely separately.",
        f"Average the x-coordinates: ({x1} + {x2})/2 = {_fmt_half(mx)}. It is fine for a midpoint "
        "coordinate to come out as a decimal ending in .5 - that simply means the midpoint lies "
        "between two grid lines.",
        f"Average the y-coordinates the same way: ({y1} + {y2})/2 = {_fmt_half(my)}.",
        f"Put the two averaged coordinates together to get the midpoint: {answer}.",
    ]
    worked_calculation = [
        f"x: ({x1} + {x2})/2 = {_fmt_half(mx)}",
        f"y: ({y1} + {y2})/2 = {_fmt_half(my)}",
        f"Midpoint = {answer}",
    ]
    return ModelledExample(
        topic_id="midpoint_of_segment_F",
        tier=Tier.FOUNDATION,
        prompt=f"Find the midpoint of the line segment joining A({x1}, {y1}) and B({x2}, {y2}).",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# --------------------------------------------------------------------------
# Distance between two points (Higher)
# --------------------------------------------------------------------------


def _build_distance(rng: random.Random) -> tuple[int, int, int, int, int, int, int, int, int]:
    """Return (x1, y1, x2, y2, dx, dy, d2, k, m) with d2 = dx^2 + dy^2 NOT a
    perfect square, so the answer is always a genuine simplified surd."""
    for _ in range(200):
        x1, y1, x2, y2 = _two_points(rng)
        dx, dy = x2 - x1, y2 - y1
        d2 = dx * dx + dy * dy
        if d2 == 0:
            continue
        root = math.isqrt(d2)
        if root * root == d2:
            continue  # perfect square -> not a surd, skip
        k, m = _largest_square_factor(d2)
        if m == 1:
            continue

        # Independent verification: the exact surd k√m must match the direct
        # floating-point distance math.hypot(dx, dy) to high precision, and the
        # square-factorisation must reconstruct d2.
        if k * k * m != d2:
            raise ValueError("distance verification failed: bad factorisation")
        if abs(k * math.sqrt(m) - math.hypot(dx, dy)) > 1e-9:
            raise ValueError("distance verification failed: surd != hypot")

        return x1, y1, x2, y2, dx, dy, d2, k, m
    raise ValueError("distance could not find a surd-valued pair")


def generate_distance_between_points(tier: Tier, rng: random.Random) -> Question:
    x1, y1, x2, y2, dx, dy, d2, k, m = _build_distance(rng)
    answer = _fmt_surd(k, m)
    steps = [
        "The distance between two points is found with Pythagoras: the square root of "
        "((horizontal gap)^2 + (vertical gap)^2).",
        f"Horizontal gap: {x2} - ({x1}) = {dx}. Vertical gap: {y2} - ({y1}) = {dy}.",
        f"Distance = √(({dx})^2 + ({dy})^2) = √{d2}",
        (f"√{d2} is already in its simplest form."
         if k == 1 else f"Simplify the surd: √{d2} = √({k}^2 × {m}) = {answer}"),
    ]
    return Question(
        topic_id="distance_between_points_H",
        tier=Tier.HIGHER,
        prompt=(
            f"Find the length of the line segment joining A({x1}, {y1}) and B({x2}, {y2}). "
            "Give your answer as a surd in its simplest form."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"distance:{x1}:{y1}:{x2}:{y2}",
    )


def generate_modelled_example_distance_between_points(tier: Tier, rng: random.Random) -> ModelledExample:
    x1, y1, x2, y2, dx, dy, d2, k, m = _build_distance(rng)
    answer = _fmt_surd(k, m)
    teaching_steps = [
        f"To find the straight-line distance from A({x1}, {y1}) to B({x2}, {y2}), picture a "
        "right-angled triangle whose hypotenuse is the segment AB and whose other two sides are "
        "the horizontal and vertical gaps between the points. The distance is then just Pythagoras "
        "applied to that triangle: the square root of ((horizontal gap)^2 + (vertical gap)^2).",
        f"Work out the two shorter sides: the horizontal change is {x2} - ({x1}) = {dx}, and the "
        f"vertical change is {y2} - ({y1}) = {dy}. Squaring removes any minus signs, so the "
        "direction of travel doesn't matter here.",
        f"Substitute in: √(({dx})^2 + ({dy})^2) = √({dx * dx} + {dy * dy}) = √{d2}.",
        (f"√{d2} has no square factor bigger than 1, so it is already in its simplest surd form: {answer}."
         if k == 1 else
         f"Finally simplify the surd by taking out the largest square factor: "
         f"√{d2} = √({k}^2 × {m}) = {answer}."),
    ]
    worked_calculation = [f"√(({dx})^2 + ({dy})^2)", f"= √{d2}"]
    if k != 1:
        worked_calculation.append(f"= {answer}")
    return ModelledExample(
        topic_id="distance_between_points_H",
        tier=Tier.HIGHER,
        prompt=(
            f"Find the length of the line segment joining A({x1}, {y1}) and B({x2}, {y2}). "
            "Give your answer as a surd in its simplest form."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_MIDPOINT_OF_SEGMENT = TopicDefinition(
    id="midpoint_of_segment_F",
    display_name="Midpoint of a Line Segment",
    description="Find the midpoint of the line segment joining two points.",
    generate=generate_midpoint_of_segment,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_midpoint_of_segment,
)

TOPIC_DISTANCE_BETWEEN_POINTS = TopicDefinition(
    id="distance_between_points_H",
    display_name="Length of a Line Segment",
    description="Find the distance between two points, giving the answer as a simplified surd.",
    generate=generate_distance_between_points,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_distance_between_points,
)
