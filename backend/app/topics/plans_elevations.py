"""Plans and elevations of 3D solids (AQA 3.4.1 G13): the question page shows
the familiar oblique 3D sketch (reusing the existing draw_cuboid/
draw_triangular_prism diagram kinds unchanged, with dimensions labelled)
stacked above a blank squared grid for the student to sketch their own
answer into (draw_plans_and_elevations_question - one composed Drawing,
since a Question only carries a single question-page diagram slot), and the
solution page shows all three orthographic views via the new
draw_plans_and_elevations diagram (app/pdf/diagrams.py) - genuinely new
drawing code, since every other 3D diagram in this file uses oblique
projection, not true orthographic views. Scoped to two solids (cuboid,
triangular prism) rather than every 3D shape in the app.

All dimensions are capped at 8 (both here and via a locally-scoped triple
pool for the triangular prism, NOT solids_prisms.py's own shared
`_triangular_prism_values`, which legitimately goes larger for its own
volume/surface-area topic and must stay untouched) - a small, legible
solid is more important here than a wide numeric range, since the point of
this topic is reading off a shape's views, not practising arithmetic.
"""

import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "3D Shapes"

# Right-angled triples with both legs <= 8 (the base (3, 4, 5) triple, plus
# its x2 scaling) - deliberately not reusing solids_prisms.py's own
# `_TRIPLES`/scale-up-to-x3 approach, which allows legs as large as (8, 15,
# 17) x3, well past this topic's own 8-max cap.
_PLANS_TRIANGLE_TRIPLES = [(3, 4, 5), (6, 8, 10)]


def _plans_triangular_prism_dims(rng: random.Random) -> tuple[int, int, int, int]:
    p, q, hyp = rng.choice(_PLANS_TRIANGLE_TRIPLES)
    length = rng.randint(3, 8)
    return p, q, hyp, length


def _cuboid_case(rng: random.Random) -> dict:
    length, width, height = rng.randint(3, 8), rng.randint(3, 8), rng.randint(3, 8)
    return {
        "shape": "cuboid",
        "length": length, "width": width, "height": height,
        "front": f"a rectangle, {length} cm by {height} cm",
        "side": f"a rectangle, {width} cm by {height} cm",
        "plan": f"a rectangle, {length} cm by {width} cm",
        "dedup_key": f"plans_cuboid:{length}:{width}:{height}",
        "question_diagram": DiagramSpec(
            kind="plans_and_elevations_question",
            params={
                "shape": "cuboid",
                "length_label": f"{length} cm", "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
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
    p, q, hyp, length = _plans_triangular_prism_dims(rng)
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
            kind="plans_and_elevations_question",
            params={
                "shape": "triangular_prism",
                "base_label": f"{p} cm", "triangle_height_label": f"{q} cm", "length_label": f"{length} cm",
            },
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
