"""3D Shapes: properties of common solids (faces/edges/vertices) and their
nets (which 2D shapes fold up to make them).

Like algebraic_proof.py, these are curated fixed-question-bank topics rather
than infinite-random-numbers topics - there's no "random number" to generate,
only a fixed geometric fact to recall (how many faces a cylinder has doesn't
vary by seed). So each topic is a TEMPLATES list of real, independently
fact-checked solids, and the only randomisation is which template AND which
angle of question (which count, or which phrasing) gets asked.
`TopicDefinition.question_count` is set to each topic's own template-bank
length, per this app's established convention for curated-bank topics
(see algebraic_proof.py) - even though the two topics below also vary the
*angle* of question per template, giving a larger real dedup-key ceiling than
the template count alone (see the dedup-key-space comments below each
generator), the template bank itself is what "one distinct fact" means here.

Faces/edges/vertices counts were checked against Euler's formula
(F + V - E = 2) for every true polyhedron in the bank below (see the
module-level assertion) as a sanity check while writing the templates - this
is NOT a runtime verification of each generated question (there's no second
"computation path" for a hardcoded fact, unlike every other topic in this
app), it's a one-time check that the hardcoded numbers are internally
consistent. Cylinder and sphere are deliberately excluded from that check:
they aren't true polyhedra, and GCSE convention counts their curved surfaces
as a single "face" with no vertices, which doesn't satisfy Euler's formula
(3 + 0 - 2 = 1 for a cylinder, 1 + 0 - 0 = 1 for a sphere) - that's expected,
not a bug.
"""

import random
from typing import NamedTuple, Optional

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "3D Shapes"


# ---------------------------------------------------------------------------
# Topic 1: properties_3d_shapes (faces / edges / vertices)
# ---------------------------------------------------------------------------


class _ShapeTemplate(NamedTuple):
    id: str
    name: str  # used in prompts, e.g. "a cylinder"
    faces: int
    edges: int
    vertices: int
    note: str  # one sentence stating all three counts together, with the GCSE counting convention spelled out for curved solids
    breakdown: dict[str, str]  # quantity -> a short "components" phrase for the worked_calculation line
    diagram: Optional[DiagramSpec]


TEMPLATES: list[_ShapeTemplate] = [
    _ShapeTemplate(
        "cube", "cube", 6, 12, 8,
        "A cube has 6 square faces, 12 edges, and 8 vertices (corners).",
        {
            "faces": "6 identical square faces",
            "edges": "12 edges (4 on the top face, 4 on the bottom face, 4 vertical edges joining them)",
            "vertices": "8 vertices (4 top corners + 4 bottom corners)",
        },
        DiagramSpec(kind="cuboid", params={"width_label": "4 cm", "height_label": "4 cm", "length_label": "4 cm"}),
    ),
    _ShapeTemplate(
        "cuboid", "cuboid", 6, 12, 8,
        "A cuboid has 6 rectangular faces (3 congruent pairs), 12 edges, and 8 vertices (corners).",
        {
            "faces": "6 rectangular faces (3 congruent pairs)",
            "edges": "12 edges (4 lengths, 4 widths, 4 heights)",
            "vertices": "8 vertices (4 top corners + 4 bottom corners)",
        },
        DiagramSpec(kind="cuboid", params={"width_label": "6 cm", "height_label": "4 cm", "length_label": "5 cm"}),
    ),
    _ShapeTemplate(
        "triangular_prism", "triangular prism", 5, 9, 6,
        "A triangular prism has 5 faces (2 triangular ends + 3 rectangular sides), 9 edges, and 6 vertices (corners).",
        {
            "faces": "2 triangular end faces + 3 rectangular side faces",
            "edges": "3 edges on each triangular end (6 total) + 3 length edges joining them",
            "vertices": "3 corners on each triangular end (6 total)",
        },
        DiagramSpec(kind="triangular_prism", params={"base_label": "5 cm", "triangle_height_label": "4 cm", "length_label": "8 cm"}),
    ),
    _ShapeTemplate(
        "square_pyramid", "square-based pyramid", 5, 8, 5,
        "A square-based pyramid has 5 faces (1 square base + 4 triangular sides), 8 edges, and 5 vertices "
        "(4 base corners + 1 apex).",
        {
            "faces": "1 square base + 4 triangular side faces",
            "edges": "4 edges around the base + 4 sloped edges up to the apex",
            "vertices": "4 base corners + 1 apex",
        },
        DiagramSpec(kind="pyramid", params={"base_label": "5 cm", "height_label": "6 cm"}),
    ),
    _ShapeTemplate(
        "tetrahedron", "tetrahedron (triangular-based pyramid)", 4, 6, 4,
        "A tetrahedron has 4 triangular faces, 6 edges, and 4 vertices (corners) - every face is a "
        "triangle, including the base.",
        {
            "faces": "4 triangular faces (including the base)",
            "edges": "3 edges around the base + 3 sloped edges up to the apex",
            "vertices": "3 base corners + 1 apex",
        },
        # No existing diagram kind models a genuine 4-faced triangular-based pyramid -
        # draw_pyramid always sketches a SQUARE base (5 faces), which would actively
        # misrepresent a tetrahedron's face count rather than just being schematic, so
        # this template deliberately has no diagram at all rather than a misleading one.
        None,
    ),
    _ShapeTemplate(
        "cylinder", "cylinder", 3, 2, 0,
        "By GCSE convention, a cylinder has 3 faces (2 flat circular faces + 1 curved surface), 2 edges "
        "(where the curved surface meets each circular face), and 0 vertices (there are no sharp corners).",
        {
            "faces": "2 flat circular faces + 1 curved face",
            "edges": "1 edge where the curved surface meets the top circle + 1 where it meets the bottom circle",
            "vertices": "no sharp corners anywhere",
        },
        DiagramSpec(kind="cylinder", params={"radius_label": "3 cm", "height_label": "8 cm"}),
    ),
    _ShapeTemplate(
        "cone", "cone", 2, 1, 1,
        "By GCSE convention, a cone has 2 faces (1 flat circular base + 1 curved surface), 1 edge (where "
        "the curved surface meets the circular base), and 1 vertex (the apex point at the top).",
        {
            "faces": "1 flat circular base + 1 curved face",
            "edges": "1 edge where the curved surface meets the circular base",
            "vertices": "1 apex point",
        },
        DiagramSpec(kind="cone", params={"radius_label": "3 cm", "slant_label": "7 cm"}),
    ),
    _ShapeTemplate(
        "sphere", "sphere", 1, 0, 0,
        "A sphere has 1 face (the curved surface), 0 edges, and 0 vertices - there are no flat surfaces, "
        "corners, or edges anywhere on a sphere.",
        {
            "faces": "1 curved face and nothing else",
            "edges": "no edges anywhere",
            "vertices": "no corners anywhere",
        },
        DiagramSpec(kind="sphere", params={"radius_label": "5 cm"}),
    ),
    _ShapeTemplate(
        "hexagonal_prism", "hexagonal prism", 8, 18, 12,
        "A hexagonal prism has 8 faces (2 hexagonal ends + 6 rectangular sides), 18 edges, and 12 vertices "
        "(corners).",
        {
            "faces": "2 hexagonal end faces + 6 rectangular side faces",
            "edges": "6 edges on each hexagonal end (12 total) + 6 length edges joining them",
            "vertices": "6 corners on each hexagonal end (12 total)",
        },
        # No existing diagram kind models a hexagonal prism.
        None,
    ),
]

_ids = [t.id for t in TEMPLATES]
if len(_ids) != len(set(_ids)):
    raise ValueError("solids_properties: duplicate template id found in TEMPLATES")

# One-time sanity check while writing the templates: Euler's formula
# (F + V - E = 2) holds for every true polyhedron here. Cylinder and sphere
# are curved solids, not polyhedra, and are deliberately excluded - see the
# module docstring for why they fail this check under GCSE counting
# convention (and why that's expected, not a bug).
_POLYHEDRA_IDS = {"cube", "cuboid", "triangular_prism", "square_pyramid", "tetrahedron", "hexagonal_prism"}
for _t in TEMPLATES:
    if _t.id in _POLYHEDRA_IDS and _t.faces + _t.vertices - _t.edges != 2:
        raise ValueError(f"solids_properties: Euler's formula check failed for {_t.id!r}")

_QUANTITY_DEFINITIONS = {
    "faces": "A face is a flat or curved surface on the outside of a 3D shape.",
    "edges": "An edge is a line where two faces meet.",
    "vertices": "A vertex is a corner point where edges meet.",
}


def generate_properties_3d_shapes(tier: Tier, rng: random.Random) -> Question:
    template = rng.choice(TEMPLATES)
    quantity = rng.choice(["faces", "edges", "vertices"])
    value = {"faces": template.faces, "edges": template.edges, "vertices": template.vertices}[quantity]

    steps = [
        _QUANTITY_DEFINITIONS[quantity],
        template.note,
        f"So a {template.name} has {value} {quantity}.",
    ]
    return Question(
        topic_id="properties_3d_shapes",
        tier=Tier.FOUNDATION,
        prompt=f"How many {quantity} does a {template.name} have?",
        solution_steps=tuple(steps),
        final_answer=str(value),
        dedup_key=f"properties3d:{template.id}:{quantity}",
        diagram=template.diagram,
    )


def generate_modelled_example_properties_3d_shapes(tier: Tier, rng: random.Random) -> ModelledExample:
    template = rng.choice(TEMPLATES)
    quantity = rng.choice(["faces", "edges", "vertices"])
    value = {"faces": template.faces, "edges": template.edges, "vertices": template.vertices}[quantity]

    teaching_steps = [
        f"{_QUANTITY_DEFINITIONS[quantity]} To count them for any solid, it helps to picture the shape "
        "in your head (or look at a real object like a tin can or a dice) and count systematically, "
        "rather than guessing.",
        f"For a {template.name}: {template.note}",
        "Curved solids like cylinders, cones and spheres need a bit of care - GCSE convention treats "
        "a whole curved surface as ONE face (even though it's not flat), and a curved solid can have "
        "far fewer edges and vertices than a straight-edged solid with a similar shape, since there "
        "are no sharp corners where a curved surface meets itself.",
        f"Counting carefully for this shape gives {value} {quantity}.",
    ]
    worked_calculation = [
        f"{template.name.capitalize()}: {template.breakdown[quantity]}",
        f"= {value} {quantity}",
    ]
    return ModelledExample(
        topic_id="properties_3d_shapes",
        tier=Tier.FOUNDATION,
        prompt=f"How many {quantity} does a {template.name} have?",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(value),
        diagram=template.diagram,
    )


# ---------------------------------------------------------------------------
# Topic 2: nets_3d_shapes (which 2D shapes make up a solid's net)
# ---------------------------------------------------------------------------


class _NetTemplate(NamedTuple):
    id: str
    name: str  # used in prompts, e.g. "a cuboid"
    composition: dict[str, int]  # plural shape name -> count, e.g. {"rectangles": 6}
    description: str  # the full "describe the net" answer string
    diagram_shape: str  # the "shape" param passed to DiagramSpec(kind="net", ...)


NET_TEMPLATES: list[_NetTemplate] = [
    _NetTemplate(
        "cuboid", "cuboid",
        {"rectangles": 6},
        "6 rectangles (3 congruent pairs)",
        "cuboid",
    ),
    _NetTemplate(
        "cube", "cube",
        {"squares": 6},
        "6 squares",
        "cube",
    ),
    _NetTemplate(
        "triangular_prism", "triangular prism",
        {"triangles": 2, "rectangles": 3},
        "2 triangles and 3 rectangles",
        "triangular_prism",
    ),
    _NetTemplate(
        "cylinder", "cylinder",
        {"circles": 2, "rectangles": 1},
        "2 circles and 1 rectangle (the curved surface unrolled flat)",
        "cylinder",
    ),
    _NetTemplate(
        "cone", "cone",
        {"circles": 1, "sectors": 1},
        "1 circle and 1 sector (the curved surface unrolled flat)",
        "cone",
    ),
    _NetTemplate(
        "square_pyramid", "square-based pyramid",
        {"squares": 1, "triangles": 4},
        "1 square and 4 triangles",
        "pyramid",
    ),
]

_net_ids = [t.id for t in NET_TEMPLATES]
if len(_net_ids) != len(set(_net_ids)):
    raise ValueError("solids_properties: duplicate template id found in NET_TEMPLATES")


def _net_question_content(template: _NetTemplate, angle: str) -> tuple[str, str]:
    """Returns (prompt, final_answer) for a given template + angle key. Shared
    between generate_nets_3d_shapes and its modelled-example twin so the two
    stay in sync."""
    if angle == "describe_a":
        return f"Describe the net of a {template.name}.", template.description
    if angle == "describe_b":
        return f"What 2D shapes make up the net of a {template.name}?", template.description
    # angle is "count:<key>"
    _, key = angle.split(":")
    count = template.composition[key]
    return f"How many {key} does the net of a {template.name} contain?", str(count)


def _net_question_angles(template: _NetTemplate) -> list[str]:
    return ["describe_a", "describe_b"] + [f"count:{key}" for key in template.composition]


def generate_nets_3d_shapes(tier: Tier, rng: random.Random) -> Question:
    template = rng.choice(NET_TEMPLATES)
    angle = rng.choice(_net_question_angles(template))
    prompt, final_answer = _net_question_content(template, angle)

    steps = [
        f"Imagine unfolding a {template.name} flat, so every one of its faces lies in the same plane "
        "with none overlapping - this flattened-out shape is called its net.",
        f"A {template.name}'s net is made up of: {template.description}.",
        f"So the answer is: {final_answer}.",
    ]
    return Question(
        topic_id="nets_3d_shapes",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"nets3d:{template.id}:{angle}",
        diagram=DiagramSpec(kind="net", params={"shape": template.diagram_shape}),
    )


def generate_modelled_example_nets_3d_shapes(tier: Tier, rng: random.Random) -> ModelledExample:
    template = rng.choice(NET_TEMPLATES)
    angle = rng.choice(_net_question_angles(template))
    prompt, final_answer = _net_question_content(template, angle)

    teaching_steps = [
        "To find a solid's net, imagine carefully unfolding every face outward along its edges until "
        "the whole surface lies completely flat, like flattening out a cardboard box - nothing is "
        "added or removed, just unfolded.",
        f"A {template.name} unfolds into: {template.description}.",
        f"Counting (or listing) these flat pieces answers this particular question: {final_answer}.",
        "A good way to check a net is correct is to picture folding it back up along each edge - if "
        "it would close up into the solid with no gaps and no overlaps, it's a valid net.",
    ]
    worked_calculation = [
        f"{template.name.capitalize()} net = {template.description}",
        f"Answer: {final_answer}",
    ]
    return ModelledExample(
        topic_id="nets_3d_shapes",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(kind="net", params={"shape": template.diagram_shape}),
    )


# ---------------------------------------------------------------------------
# Topic definitions
# ---------------------------------------------------------------------------

# question_count is set to each topic's own template-bank length, per this
# app's established curated-bank convention (see algebraic_proof.py) - even
# though the real dedup-key ceiling is larger (9 shapes x 3 quantities = 27
# for properties_3d_shapes; up to 22 for nets_3d_shapes, see each generator's
# own dedup-key comment), the template bank is what "one distinct fact" means
# for this topic, matching the spirit of algebraic_proof's TEMPLATES-length
# convention.
TOPIC_PROPERTIES_3D_SHAPES = TopicDefinition(
    id="properties_3d_shapes",
    display_name="Properties of 3D Shapes",
    description="Identify the number of faces, edges, or vertices of common 3D solids.",
    generate=generate_properties_3d_shapes,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(TEMPLATES),
    generate_modelled_example=generate_modelled_example_properties_3d_shapes,
)

TOPIC_NETS_3D_SHAPES = TopicDefinition(
    id="nets_3d_shapes",
    display_name="Nets of 3D Shapes",
    description="Identify the 2D shapes that make up the net of a 3D solid.",
    generate=generate_nets_3d_shapes,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(NET_TEMPLATES),
    generate_modelled_example=generate_modelled_example_nets_3d_shapes,
)
