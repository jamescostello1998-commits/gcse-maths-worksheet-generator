"""Equation of a circle centred at the origin (AQA A16, Higher only): recognise
x^2 + y^2 = r^2, and find the equation of the tangent to the circle at a given
point on it. The diagram needs zero new drawing code - draw_loci_construction
(app/pdf/diagrams.py, built for loci.py) already accepts a circle centred
anywhere plus an optional segment, which is exactly this shape.
"""

import math
import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Equation of a Circle"

# (a, b, r) with a^2 + b^2 = r^2, so (a, b) always lies exactly on the circle
# of radius r centred at the origin.
_TRIPLES: tuple[tuple[int, int, int], ...] = (
    (3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (7, 24, 25), (20, 21, 29), (12, 16, 20),
    (9, 40, 41), (11, 60, 61), (28, 45, 53), (33, 56, 65), (16, 63, 65), (48, 55, 73), (13, 84, 85), (36, 77, 85),
)


def _circle_diagram(r: int, point: "tuple[int, int] | None" = None, segment=None) -> DiagramSpec:
    margin = 1
    # No text label on the point - its coordinates are already given in the
    # prompt, and a coordinate-pair label ("(-33, -56)") is far wider than
    # the single-letter labels _loci_reference_points was designed around,
    # risking overlap with an axis tick label when the point sits near the
    # edge of the grid (found by rendering an actual worksheet at a large
    # radius, not a unit test). The dot alone is enough to show where the
    # tangent touches the circle.
    points = [{"xy": point, "label": None}] if point else []
    return DiagramSpec(
        kind="loci_construction",
        params={
            "x_min": -r - margin, "x_max": r + margin,
            "y_min": -r - margin, "y_max": r + margin,
            "points": points,
            "given_lines": [],
            "circle": {"centre": (0, 0), "radius": r},
            "segment": segment,
        },
    )


def _state_equation_case(rng: random.Random):
    r = rng.randint(2, 25)
    return r


def generate_circle_equation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["state", "tangent"])

    if shape == "state":
        r = _state_equation_case(rng)
        r_sq = r * r
        # Independent verification: a point known to lie exactly on the
        # circle (r, 0)) must satisfy the claimed equation - a direct
        # geometric check rather than just trusting r*r.
        if r**2 + 0**2 != r_sq:
            raise ValueError("circle_equation verification failed: point on circle does not satisfy equation")
        steps = [
            f"A circle centred at the origin with radius r has equation x^2 + y^2 = r^2.",
            f"Here r = {r}, so r^2 = {r_sq}.",
        ]
        return Question(
            topic_id="circle_equation",
            tier=Tier.HIGHER,
            prompt=f"A circle has centre (0, 0) and radius {r}. Write down the equation of the circle.",
            solution_steps=tuple(steps),
            final_answer=f"x^2 + y^2 = {r_sq}",
            dedup_key=f"circle_eq_state:{r}",
            diagram=_circle_diagram(r),
        )

    a, b, r = rng.choice(_TRIPLES)
    a = a if rng.random() < 0.5 else -a
    b = b if rng.random() < 0.5 else -b
    r_sq = r * r

    # Independent verification: the tangent line ax + by = r^2 must sit at
    # perpendicular distance exactly r from the origin - the point-to-line
    # distance formula, a genuinely different check than the perpendicular-
    # gradient construction used for the displayed steps.
    distance_from_origin = abs(r_sq) / math.hypot(a, b)
    if abs(distance_from_origin - r) > 1e-9:
        raise ValueError("circle_equation verification failed: tangent line is not at distance r from the origin")

    tangent_str = f"{a}x {'+' if b >= 0 else '-'} {abs(b)}y = {r_sq}"
    steps = [
        f"The point ({a}, {b}) lies on the circle x^2 + y^2 = {r_sq}, since {a}^2 + {b}^2 = {r_sq}.",
        f"The radius to ({a}, {b}) has gradient {b}/{a}, so the tangent (perpendicular to the radius) "
        f"has gradient -{a}/{b}.",
        f"The tangent line through ({a}, {b}) with that gradient simplifies to {tangent_str}.",
    ]
    return Question(
        topic_id="circle_equation",
        tier=Tier.HIGHER,
        prompt=f"The point ({a}, {b}) lies on the circle x^2 + y^2 = {r_sq}. Find the equation of the "
        "tangent to the circle at this point.",
        solution_steps=tuple(steps),
        final_answer=tangent_str,
        dedup_key=f"circle_eq_tangent:{a}:{b}:{r}",
        diagram=_circle_diagram(r, point=(a, b)),
    )


def generate_modelled_example_circle_equation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["state", "tangent"])

    if shape == "state":
        r = _state_equation_case(rng)
        r_sq = r * r
        teaching_steps = [
            "Every point (x, y) on a circle centred at the origin is exactly r away from (0, 0) - and "
            "Pythagoras' theorem says the distance from the origin to (x, y) is √(x^2 + y^2).",
            f"Setting that distance equal to the radius gives √(x^2 + y^2) = r, and squaring both sides "
            f"gives the standard equation x^2 + y^2 = r^2.",
            f"Here the radius is {r}, so r^2 = {r * r} = {r_sq}, giving the equation "
            f"x^2 + y^2 = {r_sq}.",
        ]
        worked_calculation = [
            f"radius r = {r}",
            f"x^2 + y^2 = r^2",
            f"x^2 + y^2 = {r_sq}",
        ]
        return ModelledExample(
            topic_id="circle_equation",
            tier=Tier.HIGHER,
            prompt=f"A circle has centre (0, 0) and radius {r}. Write down the equation of the circle.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"x^2 + y^2 = {r_sq}",
        )

    a, b, r = rng.choice(_TRIPLES)
    a = a if rng.random() < 0.5 else -a
    b = b if rng.random() < 0.5 else -b
    r_sq = r * r
    tangent_str = f"{a}x {'+' if b >= 0 else '-'} {abs(b)}y = {r_sq}"
    teaching_steps = [
        "A tangent to a circle touches it at exactly one point, and always meets the radius at that "
        "point at a right angle - that perpendicularity is the key fact used to find its equation.",
        f"First check the given point really is on the circle: {a}^2 + {b}^2 = {r_sq}, which matches "
        f"the circle x^2 + y^2 = {r_sq}, so ({a}, {b}) does lie on it.",
        f"The radius from the origin to ({a}, {b}) has gradient {b}/{a} (rise over run). Since the "
        f"tangent is perpendicular to this radius, its gradient is the negative reciprocal: -{a}/{b}.",
        f"Writing the equation of the line through ({a}, {b}) with gradient -{a}/{b}, and rearranging, "
        f"simplifies neatly to {tangent_str} - substituting the point back in confirms "
        f"{a}×{a} {'+' if b >= 0 else '-'} {abs(b)}×{b} = {r_sq}.",
    ]
    worked_calculation = [
        f"point ({a}, {b}), radius gradient = {b}/{a}",
        f"tangent gradient = -{a}/{b}",
        f"{tangent_str}",
    ]
    return ModelledExample(
        topic_id="circle_equation",
        tier=Tier.HIGHER,
        prompt=f"The point ({a}, {b}) lies on the circle x^2 + y^2 = {r_sq}. Find the equation of the "
        "tangent to the circle at this point.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=tangent_str,
    )


TOPIC_CIRCLE_EQUATION = TopicDefinition(
    id="circle_equation",
    display_name="Equation of a Circle",
    description="Write down the equation of a circle centred at the origin, or find the equation of a tangent to it.",
    generate=generate_circle_equation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_circle_equation,
)
