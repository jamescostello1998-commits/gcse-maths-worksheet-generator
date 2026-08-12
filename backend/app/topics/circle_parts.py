"""Name the parts of a circle (radius, diameter, chord, tangent, arc, sector,
segment, circumference, centre) from a diagram.

This is a vocabulary/recall topic: each question shows a circle with one part
highlighted and asks for its name. Like the Constructions and 3D-properties
topics, there is nothing numeric to verify - the answer is fixed by which part
the diagram draws - so there is no verify() step; correctness rests on the
curated definitions below and the diagram matching the chosen part exactly.
"""

import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Parts of a Circle"

# (part-key == the expected answer, definition used in the solution steps).
_PARTS: list[tuple[str, str]] = [
    ("radius", "a straight line from the centre of the circle to any point on the circumference"),
    ("diameter", "a straight line right across the circle, from one side to the other, passing through the centre"),
    ("chord", "a straight line joining two points on the circumference that does NOT pass through the centre"),
    ("tangent", "a straight line that touches the circle at exactly one point"),
    ("arc", "part of the circumference - a section of the curved edge of the circle"),
    ("sector", "a region enclosed by two radii and an arc (a 'slice' of the circle)"),
    ("segment", "a region enclosed by a chord and an arc"),
    ("circumference", "the whole distance all the way around the outside of the circle"),
    ("centre", "the point in the middle, the same distance from every point on the circumference"),
]

_ARTICLE = {
    "radius": "the radius",
    "diameter": "the diameter",
    "chord": "a chord",
    "tangent": "a tangent",
    "arc": "an arc",
    "sector": "a sector",
    "segment": "a segment",
    "circumference": "the circumference",
    "centre": "the centre",
}

_PROMPT = "Name the part of the circle that is highlighted."


def _diagram(part: str) -> DiagramSpec:
    return DiagramSpec(kind="circle_part", params={"part": part})


def generate_circle_parts(tier: Tier, rng: random.Random) -> Question:
    part, definition = rng.choice(_PARTS)
    if part not in _ARTICLE:
        raise ValueError("circle_parts: unknown part")
    steps = [
        f"Look at which feature of the circle is highlighted.",
        f"It is {definition}.",
        f"This part of a circle is called {_ARTICLE[part]}.",
    ]
    return Question(
        topic_id="circle_parts_F",
        tier=Tier.FOUNDATION,
        prompt=_PROMPT,
        solution_steps=tuple(steps),
        final_answer=part,
        dedup_key=f"circlepart:{part}",
        diagram=_diagram(part),
    )


def generate_modelled_example_circle_parts(tier: Tier, rng: random.Random) -> ModelledExample:
    part, definition = rng.choice(_PARTS)
    teaching_steps = [
        "Learning the names of the parts of a circle is about matching each name to what it looks "
        "like. Start by noticing whether the highlighted feature is a straight line, a piece of the "
        "curved edge, or a whole region shaded in.",
        f"Here the highlighted feature is {definition}.",
        "A couple of the pairs are easy to mix up, so it helps to hold the differences in mind: a "
        "radius goes centre-to-edge while a diameter goes edge-to-edge through the centre; a chord "
        "joins two edge points but misses the centre; a tangent only touches the outside at one "
        "point. An arc is part of the curved edge, whereas a sector and a segment are whole regions "
        "(a sector is bounded by two radii, a segment by a chord).",
        f"Matching the highlighted feature to its definition, this is {_ARTICLE[part]}.",
    ]
    worked_calculation = [f"Highlighted: {definition}", f"Name: {part}"]
    return ModelledExample(
        topic_id="circle_parts_F",
        tier=Tier.FOUNDATION,
        prompt=_PROMPT,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=part,
        diagram=_diagram(part),
    )


TOPIC_CIRCLE_PARTS = TopicDefinition(
    id="circle_parts_F",
    display_name="Parts of a Circle",
    description="Name the parts of a circle: radius, diameter, chord, tangent, arc, sector, segment, circumference.",
    generate=generate_circle_parts,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(_PARTS),
    generate_modelled_example=generate_modelled_example_circle_parts,
)
