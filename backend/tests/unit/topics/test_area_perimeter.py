import random

from app.core.models import Tier
from app.topics import area_perimeter

TRIALS = 200

GENERATORS = [
    (area_perimeter.generate_rectangle, Tier.FOUNDATION),
    (area_perimeter.generate_triangle, Tier.FOUNDATION),
    (area_perimeter.generate_composite_rectangles, Tier.FOUNDATION),
    (area_perimeter.generate_circle_foundation, Tier.FOUNDATION),
    (area_perimeter.generate_circle, Tier.HIGHER),
    (area_perimeter.generate_semicircle_compound, Tier.HIGHER),
    (area_perimeter.generate_subtract_compound, Tier.HIGHER),
]


EXPECTED_DIAGRAM_KINDS = {
    area_perimeter.generate_rectangle: "rectangle",
    area_perimeter.generate_triangle: "triangle_area",
    area_perimeter.generate_composite_rectangles: "l_shape",
    area_perimeter.generate_circle_foundation: "circle",
    area_perimeter.generate_circle: "circle",
    area_perimeter.generate_semicircle_compound: "rectangle_semicircle",
    area_perimeter.generate_subtract_compound: "l_shape",
}


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(40)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_all_generators_attach_a_matching_diagram():
    for generate, tier in GENERATORS:
        rng = random.Random(41)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == EXPECTED_DIAGRAM_KINDS[generate]


def test_rectangle_diagram_params_match_generated_values():
    rng = random.Random(43)
    q = area_perimeter.generate_rectangle(Tier.FOUNDATION, rng)
    length, width = q.dedup_key.split(":")[1:3]
    assert q.diagram.params["width"] == int(length)
    assert q.diagram.params["height"] == int(width)


def test_dedup_keys_vary_per_generator():
    # generate_circle's parameter space is small (13 radii x 2 measures = 26 max
    # distinct keys), so this uses a lower bar than other topic files' equivalent test.
    for generate, tier in GENERATORS:
        rng = random.Random(42)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 15


def test_topic_definitions_have_expected_metadata():
    topics = [
        area_perimeter.TOPIC_RECTANGLE,
        area_perimeter.TOPIC_TRIANGLE,
        area_perimeter.TOPIC_COMPOSITE_RECTANGLES,
        area_perimeter.TOPIC_CIRCLE_FOUNDATION,
        area_perimeter.TOPIC_CIRCLE,
        area_perimeter.TOPIC_SEMICIRCLE_COMPOUND,
        area_perimeter.TOPIC_SUBTRACT_COMPOUND,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 7
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Area & Perimeter"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
