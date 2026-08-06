"""Geometry Phase 4b (part 2 of 3): ruler-and-compass constructions
(angle bisector, perpendicular bisector, triangle given SSS/SAS/ASA).

These are "describe the method" text questions - there is no way to
numerically check a described construction, so unlike every other topic in
this app, these have **no independent `verify()` at all** (confirmed with
the user; author-review only). Variety instead comes from randomised
numbers/labels embedded in fixed per-scenario method text - a large
combinatorial state space - rather than a curated `TEMPLATES` bank (which
would be thinner than any existing precedent in this app for a topic with no
question_count override).
"""

import random
import string

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_CONSTRUCTIONS = "Constructions"

_SIDE_RANGE = (4, 14)


def _labels(rng: random.Random, count: int) -> list:
    return rng.sample(string.ascii_uppercase, count)


# ---------------------------------------------------------------------------
# Angle bisector
# ---------------------------------------------------------------------------

def _angle_bisector_content(X: str, Y: str, Z: str, angle_deg: int) -> dict:
    prompt = (
        f"Angle {X}{Y}{Z} = {angle_deg}°. Describe, step by step, how to construct the bisector of "
        f"angle {X}{Y}{Z} using only a ruler and a pair of compasses."
    )
    steps = [
        f"Open the compasses to any radius and place the point on {Y} (the vertex of the angle).",
        f"Draw an arc that crosses both arms of the angle, at a point on {Y}{X} and a point on {Y}{Z}.",
        "Without changing the compass radius, place the point on each of these two crossing points in "
        "turn and draw two more arcs so that they intersect each other.",
        f"Draw a straight line from {Y} through the point where the two arcs intersect. This line is "
        f"the bisector of angle {X}{Y}{Z}.",
    ]
    answer = f"The straight line from {Y} through the intersection of the two equal-radius arcs bisects angle {X}{Y}{Z} into two equal angles."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def generate_construction_angle_bisector(tier: Tier, rng: random.Random) -> Question:
    X, Y, Z = _labels(rng, 3)
    angle_deg = rng.randint(20, 160)
    c = _angle_bisector_content(X, Y, Z, angle_deg)
    return Question(
        topic_id="construction_angle_bisector",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        solution_steps=tuple(c["steps"]),
        final_answer=c["answer"],
        dedup_key=f"bisector_angle:{X}{Y}{Z}:{angle_deg}",
    )


def generate_modelled_example_construction_angle_bisector(tier: Tier, rng: random.Random) -> ModelledExample:
    X, Y, Z = _labels(rng, 3)
    angle_deg = rng.randint(20, 160)
    c = _angle_bisector_content(X, Y, Z, angle_deg)
    teaching_steps = [
        "An angle bisector is the line that splits an angle into two exactly equal halves - every point "
        "on it is the same perpendicular distance from both arms of the angle.",
        f"Start by placing the compass point at the vertex {Y}, since the bisector always starts there. "
        "Any radius works, as long as the arc is big enough to cross both arms of the angle - this gives "
        "two points that are exactly the same distance from the vertex.",
        "Keeping the compasses open to the same radius is the key step: drawing two more arcs, one from "
        "each of those crossing points, guarantees the new intersection point is equally far from both "
        "arms too - which is exactly the property that defines the bisector.",
        f"Joining {Y} to that intersection point gives a line every point of which is equidistant from "
        f"both arms of angle {X}{Y}{Z} - the bisector itself.",
    ]
    return ModelledExample(
        topic_id="construction_angle_bisector",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        worked_calculation=tuple(c["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=c["answer"],
    )


# ---------------------------------------------------------------------------
# Perpendicular bisector
# ---------------------------------------------------------------------------

def _perpendicular_bisector_content(P: str, Q: str, length_cm: int) -> dict:
    prompt = (
        f"Line segment {P}{Q} has length {length_cm} cm. Describe, step by step, how to construct the "
        f"perpendicular bisector of {P}{Q} using only a ruler and a pair of compasses."
    )
    steps = [
        f"Open the compasses to a radius more than half of {length_cm} cm (more than half the length of {P}{Q}).",
        f"With the compass point on {P}, draw an arc above and below the line.",
        f"Without changing the compass radius, place the point on {Q} and draw two more arcs, crossing "
        "the first two.",
        f"Draw a straight line through the two points where the arcs intersect. This line is the "
        f"perpendicular bisector of {P}{Q}.",
    ]
    answer = f"A straight line through the two arc intersections, crossing {P}{Q} at its midpoint at a right angle."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def generate_construction_perpendicular_bisector(tier: Tier, rng: random.Random) -> Question:
    P, Q = _labels(rng, 2)
    length_cm = rng.randint(4, 14)
    c = _perpendicular_bisector_content(P, Q, length_cm)
    return Question(
        topic_id="construction_perpendicular_bisector",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        solution_steps=tuple(c["steps"]),
        final_answer=c["answer"],
        dedup_key=f"bisector_perp:{P}{Q}:{length_cm}",
    )


def generate_modelled_example_construction_perpendicular_bisector(tier: Tier, rng: random.Random) -> ModelledExample:
    P, Q = _labels(rng, 2)
    length_cm = rng.randint(4, 14)
    c = _perpendicular_bisector_content(P, Q, length_cm)
    teaching_steps = [
        "The perpendicular bisector of a line segment is the set of all points that are exactly the same "
        f"distance from {P} as they are from {Q}.",
        f"The radius must be more than half of {length_cm} cm - if it were any smaller, the two arcs from "
        f"{P} and {Q} would never reach far enough to cross each other at all.",
        f"Each arc marks out points a fixed distance from {P} (or from {Q}). Where an arc from {P} and an "
        f"arc from {Q} of the *same* radius cross, that point is automatically equidistant from both - "
        "exactly the defining property of the bisector.",
        f"Drawing the line through both crossing points (one above {P}{Q}, one below) gives the whole "
        f"bisector - and it always meets {P}{Q} at a right angle, exactly at its midpoint.",
    ]
    return ModelledExample(
        topic_id="construction_perpendicular_bisector",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        worked_calculation=tuple(c["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=c["answer"],
    )


# ---------------------------------------------------------------------------
# Triangle given SSS / SAS / ASA
# ---------------------------------------------------------------------------

def _sss_sides(rng: random.Random) -> tuple:
    for _ in range(200):
        a, b, c = (rng.randint(*_SIDE_RANGE) for _ in range(3))
        if a + b > c and a + c > b and b + c > a:
            return a, b, c
    raise ValueError("construction_triangle could not find a valid SSS triangle")


def _asa_angles(rng: random.Random) -> tuple:
    for _ in range(200):
        angle1, angle2 = rng.randint(20, 130), rng.randint(20, 130)
        if angle1 + angle2 <= 150:
            return angle1, angle2
    raise ValueError("construction_triangle could not find a valid ASA angle pair")


def _sss_content(X: str, Y: str, Z: str, xy: int, yz: int, xz: int) -> dict:
    prompt = (
        f"Triangle {X}{Y}{Z} has {X}{Y} = {xy} cm, {Y}{Z} = {yz} cm, and {X}{Z} = {xz} cm. Describe, "
        f"step by step, how to construct triangle {X}{Y}{Z} using only a ruler and a pair of compasses."
    )
    steps = [
        f"Draw the line segment {X}{Y} = {xy} cm using a ruler.",
        f"Open the compasses to {xz} cm. With the point on {X}, draw an arc above the line.",
        f"Open the compasses to {yz} cm. With the point on {Y}, draw a second arc that crosses the first.",
        f"Label the point where the two arcs cross as {Z}, then draw straight lines from {X} to {Z} and "
        f"from {Y} to {Z} to complete the triangle.",
    ]
    answer = f"Triangle {X}{Y}{Z}, with {Z} located at the intersection of the two compass arcs."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def _sas_content(X: str, Y: str, Z: str, xy: int, angle_deg: int, yz: int) -> dict:
    prompt = (
        f"Triangle {X}{Y}{Z} has {X}{Y} = {xy} cm, the angle at {Y} equal to {angle_deg}°, and "
        f"{Y}{Z} = {yz} cm. Describe, step by step, how to construct triangle {X}{Y}{Z} using a ruler, "
        "a protractor, and a pair of compasses."
    )
    steps = [
        f"Draw the line segment {X}{Y} = {xy} cm using a ruler.",
        f"At {Y}, use a protractor to draw a ray at {angle_deg}° from the line {Y}{X}.",
        f"Along this new ray, measure {yz} cm from {Y} using a ruler and mark the point {Z}.",
        f"Draw a straight line from {X} to {Z} to complete the triangle.",
    ]
    answer = f"Triangle {X}{Y}{Z}, with {Z} marked {yz} cm from {Y} along the {angle_deg}° ray at {Y}."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def _asa_content(X: str, Y: str, Z: str, xy: int, angle_x: int, angle_y: int) -> dict:
    prompt = (
        f"Triangle {X}{Y}{Z} has {X}{Y} = {xy} cm, the angle at {X} equal to {angle_x}°, and the angle "
        f"at {Y} equal to {angle_y}°. Describe, step by step, how to construct triangle {X}{Y}{Z} using "
        "a ruler and a protractor."
    )
    steps = [
        f"Draw the line segment {X}{Y} = {xy} cm using a ruler.",
        f"At {X}, use a protractor to draw a ray at {angle_x}° from the line {X}{Y}.",
        f"At {Y}, use a protractor to draw a ray at {angle_y}° from the line {Y}{X}.",
        f"Label the point where the two new rays cross as {Z}. This completes triangle {X}{Y}{Z}.",
    ]
    answer = f"Triangle {X}{Y}{Z}, with {Z} located where the two angle rays from {X} and {Y} cross."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def _random_triangle_content(rng: random.Random) -> tuple:
    """Returns (content dict, dedup_key). Shared by the real generator and
    the modelled example so both stay in sync with the same three
    per-criterion method texts."""
    criterion = rng.choice(["SSS", "SAS", "ASA"])
    X, Y, Z = _labels(rng, 3)
    if criterion == "SSS":
        xy, yz, xz = _sss_sides(rng)
        content = _sss_content(X, Y, Z, xy, yz, xz)
        dedup_key = f"construct_triangle:SSS:{X}{Y}{Z}:{xy}:{yz}:{xz}"
    elif criterion == "SAS":
        xy, yz = rng.randint(*_SIDE_RANGE), rng.randint(*_SIDE_RANGE)
        angle_deg = rng.randint(20, 150)
        content = _sas_content(X, Y, Z, xy, angle_deg, yz)
        dedup_key = f"construct_triangle:SAS:{X}{Y}{Z}:{xy}:{angle_deg}:{yz}"
    else:
        xy = rng.randint(*_SIDE_RANGE)
        angle_x, angle_y = _asa_angles(rng)
        content = _asa_content(X, Y, Z, xy, angle_x, angle_y)
        dedup_key = f"construct_triangle:ASA:{X}{Y}{Z}:{xy}:{angle_x}:{angle_y}"
    return content, dedup_key


def generate_construction_triangle(tier: Tier, rng: random.Random) -> Question:
    content, dedup_key = _random_triangle_content(rng)
    return Question(
        topic_id="construction_triangle",
        tier=Tier.FOUNDATION,
        prompt=content["prompt"],
        solution_steps=tuple(content["steps"]),
        final_answer=content["answer"],
        dedup_key=dedup_key,
    )


def generate_modelled_example_construction_triangle(tier: Tier, rng: random.Random) -> ModelledExample:
    content, _ = _random_triangle_content(rng)
    teaching_steps = [
        "A triangle is only rigid - meaning there is exactly one triangle that fits the given information "
        "- if you are told enough to fully pin it down: three sides (SSS), two sides and the angle "
        "trapped between them (SAS), or two angles and the side between them (ASA).",
        "Always draw the one fully-known side first - it fixes two of the three vertices in place before "
        "anything else is added.",
        "Compasses are for transferring a fixed *length* (they mark every point a set distance from a "
        "centre); a protractor is for transferring a fixed *angle*. Which tool you reach for at each step "
        "depends on whether you were given a length or an angle at that point.",
        "The final vertex is wherever the last two conditions meet - either where two compass arcs cross "
        "(a length from each known vertex), or where two protractor rays cross (an angle from each known "
        "vertex).",
    ]
    return ModelledExample(
        topic_id="construction_triangle",
        tier=Tier.FOUNDATION,
        prompt=content["prompt"],
        worked_calculation=tuple(content["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=content["answer"],
    )


# ---------------------------------------------------------------------------
# Perpendicular from a point to a line / at a point on a line
# ---------------------------------------------------------------------------

def _perpendicular_from_point_content(P: str, A: str, B: str, length_cm: int) -> dict:
    prompt = (
        f"Point {P} is not on line segment {A}{B} (length {length_cm} cm). Describe, step by step, how "
        f"to construct the perpendicular from {P} to the line {A}{B} using only a ruler and a pair of "
        "compasses."
    )
    steps = [
        f"Open the compasses to a radius large enough to reach the line {A}{B} from {P}.",
        f"With the compass point on {P}, draw an arc that crosses {A}{B} at two points.",
        "Without changing the compass radius, place the point on each of these two crossing points in "
        f"turn and draw two more arcs on the far side of {A}{B} from {P}, so that they intersect each "
        "other.",
        f"Draw a straight line from {P} through the point where these two arcs intersect. This line is "
        f"the perpendicular from {P} to {A}{B}, crossing it at the foot of the perpendicular.",
    ]
    answer = f"The straight line from {P} through the intersection of the two far-side arcs is perpendicular to {A}{B}."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def _perpendicular_at_point_content(P: str, A: str, B: str, length_cm: int) -> dict:
    prompt = (
        f"Point {P} lies on line segment {A}{B} (length {length_cm} cm). Describe, step by step, how to "
        f"construct the perpendicular to {A}{B} at {P} using only a ruler and a pair of compasses."
    )
    steps = [
        f"With the compass point on {P}, draw two arcs of equal radius along the line {A}{B}, one on "
        f"each side of {P}, marking two new points that are the same distance from {P}.",
        "Open the compasses to a larger radius than before.",
        "With the point on each of the two new points in turn, draw two arcs above (or below) the line "
        "so that they intersect each other.",
        f"Draw a straight line from {P} through the point where these two arcs intersect. This line is "
        f"perpendicular to {A}{B} at {P}.",
    ]
    answer = f"The straight line from {P} through the intersection of the two larger-radius arcs is perpendicular to {A}{B} at {P}."
    return {"prompt": prompt, "steps": steps, "answer": answer}


def _random_perpendicular_from_point_content(rng: random.Random) -> tuple:
    """Returns (content dict, dedup_key, scenario). Shared by the real generator and
    the modelled example so both stay in sync with the same two per-scenario method
    texts."""
    scenario = rng.choice(["from_point", "at_point"])
    A, B, P = _labels(rng, 3)
    length_cm = rng.randint(*_SIDE_RANGE)
    if scenario == "from_point":
        content = _perpendicular_from_point_content(P, A, B, length_cm)
    else:
        content = _perpendicular_at_point_content(P, A, B, length_cm)
    dedup_key = f"perp_point:{scenario}:{P}{A}{B}:{length_cm}"
    return content, dedup_key, scenario


def generate_construction_perpendicular_from_point(tier: Tier, rng: random.Random) -> Question:
    content, dedup_key, _ = _random_perpendicular_from_point_content(rng)
    return Question(
        topic_id="construction_perpendicular_from_point",
        tier=Tier.FOUNDATION,
        prompt=content["prompt"],
        solution_steps=tuple(content["steps"]),
        final_answer=content["answer"],
        dedup_key=dedup_key,
    )


def generate_modelled_example_construction_perpendicular_from_point(tier: Tier, rng: random.Random) -> ModelledExample:
    content, _, scenario = _random_perpendicular_from_point_content(rng)
    if scenario == "from_point":
        teaching_steps = [
            "The perpendicular from a point to a line is the shortest possible path from that point to "
            "the line, and it always meets the line at a right angle.",
            "Since the point isn't on the line, the first arc needs a radius big enough to actually "
            "reach across and cross the line - it crosses at two points that are both the same "
            "distance from the point you started at.",
            "Swinging two more equal-radius arcs from those two crossing points - on the far side of "
            "the line from the original point - finds a new point that is, by construction, "
            "equidistant from both of them too.",
            "Joining the original point to that new intersection gives the perpendicular: it crosses "
            "the line at a right angle, at what's called the foot of the perpendicular.",
        ]
    else:
        teaching_steps = [
            "This time the point already lies on the line, so the goal is different: constructing a "
            "right angle exactly at that point, rather than dropping a line in from outside.",
            "Marking two points an equal distance from the given point, one on each side of it along "
            "the line, gives two points that any true perpendicular through the given point must be "
            "equidistant from as well.",
            "Using a bigger radius from each of those two new points in turn finds an intersection "
            "point equidistant from both of them - which places it directly above (or below) the "
            "midpoint between them, and that midpoint is the original point itself.",
            "Joining the original point to that intersection gives the perpendicular to the line at "
            "that point.",
        ]
    return ModelledExample(
        topic_id="construction_perpendicular_from_point",
        tier=Tier.FOUNDATION,
        prompt=content["prompt"],
        worked_calculation=tuple(content["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=content["answer"],
    )


TOPIC_CONSTRUCTION_ANGLE_BISECTOR = TopicDefinition(
    id="construction_angle_bisector",
    display_name="Constructing an Angle Bisector",
    description="Describe how to construct the bisector of a given angle using a ruler and compasses.",
    generate=generate_construction_angle_bisector,
    section=SECTION,
    group=GROUP_CONSTRUCTIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_construction_angle_bisector,
)

TOPIC_CONSTRUCTION_PERPENDICULAR_BISECTOR = TopicDefinition(
    id="construction_perpendicular_bisector",
    display_name="Constructing a Perpendicular Bisector",
    description="Describe how to construct the perpendicular bisector of a line segment using a ruler and compasses.",
    generate=generate_construction_perpendicular_bisector,
    section=SECTION,
    group=GROUP_CONSTRUCTIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_construction_perpendicular_bisector,
)

TOPIC_CONSTRUCTION_TRIANGLE = TopicDefinition(
    id="construction_triangle",
    display_name="Constructing a Triangle",
    description="Describe how to construct a triangle given SSS, SAS, or ASA information.",
    generate=generate_construction_triangle,
    section=SECTION,
    group=GROUP_CONSTRUCTIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_construction_triangle,
)

TOPIC_CONSTRUCTION_PERPENDICULAR_FROM_POINT = TopicDefinition(
    id="construction_perpendicular_from_point",
    display_name="Constructing a Perpendicular From/At a Point",
    description="Describe how to construct the perpendicular from a point to a line, or at a point on a line, using a ruler and compasses.",
    generate=generate_construction_perpendicular_from_point,
    section=SECTION,
    group=GROUP_CONSTRUCTIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_construction_perpendicular_from_point,
)
