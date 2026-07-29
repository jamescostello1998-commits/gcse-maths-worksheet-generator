"""Plans and elevations of 3D solids (AQA 3.4.1 G13): the question page shows
the familiar oblique 3D sketch (reusing the existing draw_cuboid/
draw_triangular_prism diagram kinds unchanged, with dimensions labelled),
and the solution page shows all three orthographic views via the new
draw_plans_and_elevations diagram (app/pdf/diagrams.py) - genuinely new
drawing code, since every other 3D diagram in this file uses oblique
projection, not true orthographic views. Scoped to two solids (cuboid,
triangular prism) rather than every 3D shape in the app, reusing
solids_prisms.py's own validated dimension generation as the data source.
"""

import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.solids_prisms import _triangular_prism_values

SECTION = "geometry"
GROUP = "3D Shapes"


def _cuboid_case(rng: random.Random) -> dict:
    length, width, height = rng.randint(3, 12), rng.randint(3, 12), rng.randint(3, 12)
    return {
        "shape": "cuboid",
        "length": length, "width": width, "height": height,
        "front": f"a rectangle, {length} cm by {height} cm",
        "side": f"a rectangle, {width} cm by {height} cm",
        "plan": f"a rectangle, {length} cm by {width} cm",
        "dedup_key": f"plans_cuboid:{length}:{width}:{height}",
        "question_diagram": DiagramSpec(
            kind="cuboid",
            params={"length_label": f"{length} cm", "width_label": f"{width} cm", "height_label": f"{height} cm"},
        ),
        "solution_diagram": DiagramSpec(
            kind="plans_and_elevations",
            params={
                "shape": "cuboid", "length": length, "width": width, "height": height,
                "length_label": f"{length} cm", "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
        ),
    }


def _triangular_prism_case(rng: random.Random) -> dict:
    p, q, hyp, length, _measure = _triangular_prism_values(rng)
    # Independent check: the cross-section really is right-angled (the same
    # constraint solids_prisms.py's own generator checks), since the "front
    # elevation is a right-angled triangle" framing depends on it.
    if hyp**2 != p**2 + q**2:
        raise ValueError("plans_elevations (triangular_prism) verification failed: cross-section not right-angled")
    return {
        "shape": "triangular_prism",
        "base": p, "tri_height": q, "length": length,
        "front": f"a right-angled triangle, base {p} cm and height {q} cm",
        "side": f"a rectangle, {length} cm by {q} cm",
        "plan": f"a rectangle, {p} cm by {length} cm",
        "dedup_key": f"plans_tri_prism:{p}:{q}:{length}",
        "question_diagram": DiagramSpec(
            kind="triangular_prism",
            params={"base_label": f"{p} cm", "triangle_height_label": f"{q} cm", "length_label": f"{length} cm"},
        ),
        "solution_diagram": DiagramSpec(
            kind="plans_and_elevations",
            params={
                "shape": "triangular_prism", "base": p, "tri_height": q, "length": length,
                "base_label": f"{p} cm", "tri_height_label": f"{q} cm", "length_label": f"{length} cm",
            },
        ),
    }


def _plans_case(rng: random.Random) -> dict:
    build = rng.choice([_cuboid_case, _triangular_prism_case])
    return build(rng)


def generate_plans_and_elevations(tier: Tier, rng: random.Random) -> Question:
    c = _plans_case(rng)
    steps = [
        "The front elevation is what you see looking at the solid straight on from the front.",
        f"Front elevation: {c['front']}.",
        "The side elevation is what you see looking at the solid straight on from the side.",
        f"Side elevation: {c['side']}.",
        "The plan view is what you see looking straight down at the solid from above.",
        f"Plan view: {c['plan']}.",
    ]
    answer = f"Front elevation: {c['front']}. Side elevation: {c['side']}. Plan view: {c['plan']}."
    return Question(
        topic_id="plans_and_elevations",
        tier=Tier.FOUNDATION,
        prompt="The diagram shows a solid with its dimensions labelled. Draw and label the front "
        "elevation, side elevation, and plan view of the solid.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=c["dedup_key"],
        diagram=c["question_diagram"],
        solution_diagram=c["solution_diagram"],
    )


def generate_modelled_example_plans_and_elevations(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _plans_case(rng)
    teaching_steps = [
        "Plans and elevations are just three different 'straight-on' views of the same solid - imagine "
        "walking around it and looking directly from the front, then the side, then straight down from "
        "above, without any perspective or angle to the view.",
        f"Looking from the front: {c['front']}.",
        f"Looking from the side: {c['side']}.",
        f"Looking straight down from above (the plan view): {c['plan']}.",
        "A useful check: the front elevation and the plan view should always share the same width, and "
        "the front elevation and the side elevation should always share the same height - since they're "
        "views of the same solid, seen from directions at right angles to each other.",
    ]
    worked_calculation = [
        f"Front elevation: {c['front']}",
        f"Side elevation: {c['side']}",
        f"Plan view: {c['plan']}",
    ]
    answer = f"Front elevation: {c['front']}. Side elevation: {c['side']}. Plan view: {c['plan']}."
    return ModelledExample(
        topic_id="plans_and_elevations",
        tier=Tier.FOUNDATION,
        prompt="The diagram shows a solid with its dimensions labelled. Draw and label the front "
        "elevation, side elevation, and plan view of the solid.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=c["solution_diagram"],
    )


TOPIC_PLANS_AND_ELEVATIONS = TopicDefinition(
    id="plans_and_elevations",
    display_name="Plans and Elevations",
    description="Draw the front elevation, side elevation, and plan view of a cuboid or triangular prism.",
    generate=generate_plans_and_elevations,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_plans_and_elevations,
)
