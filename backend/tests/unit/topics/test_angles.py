import random

from app.core.models import Tier
from app.topics import angles

TRIALS = 200

GENERATORS = [
    (angles.generate_straight_line, Tier.FOUNDATION),
    (angles.generate_around_point, Tier.FOUNDATION),
    (angles.generate_triangle_angles, Tier.FOUNDATION),
    (angles.generate_parallel_lines_foundation, Tier.FOUNDATION),
    (angles.generate_parallel_lines, Tier.HIGHER),
    (angles.generate_exterior_foundation, Tier.FOUNDATION),
    (angles.generate_exterior_angle, Tier.HIGHER),
    (angles.generate_polygon_interior_foundation, Tier.FOUNDATION),
    (angles.generate_polygon_interior, Tier.HIGHER),
]


EXPECTED_DIAGRAM_KINDS = {
    angles.generate_straight_line: "angle_line",
    angles.generate_around_point: "angle_line",
    angles.generate_triangle_angles: "triangle_angles",
    angles.generate_parallel_lines_foundation: "parallel_lines",
    angles.generate_parallel_lines: "parallel_lines",
    angles.generate_exterior_foundation: "exterior_triangle",
    angles.generate_exterior_angle: "exterior_triangle",
    angles.generate_polygon_interior_foundation: "polygon",
    angles.generate_polygon_interior: "polygon",
}


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(50)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_all_generators_attach_a_matching_diagram():
    for generate, tier in GENERATORS:
        rng = random.Random(51)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == EXPECTED_DIAGRAM_KINDS[generate]


def test_straight_line_and_around_point_diagram_angles_sum_correctly():
    rng = random.Random(53)
    q = angles.generate_straight_line(Tier.FOUNDATION, rng)
    assert sum(q.diagram.params["angle_values"]) == 180
    assert q.diagram.params["around_point"] is False

    q2 = angles.generate_around_point(Tier.FOUNDATION, rng)
    assert sum(q2.diagram.params["angle_values"]) == 360
    assert q2.diagram.params["around_point"] is True


def test_dedup_keys_vary_per_generator():
    # generate_polygon_interior_foundation's parameter space is small (19 valid
    # side-counts x 3 question kinds = 57 max distinct keys), so it uses a
    # lower bar - see test_dedup_keys_vary_for_polygon_interior_foundation.
    for generate, tier in GENERATORS:
        if generate is angles.generate_polygon_interior_foundation:
            continue
        rng = random.Random(52)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_dedup_keys_vary_for_polygon_interior_foundation():
    rng = random.Random(54)
    keys = {angles.generate_polygon_interior_foundation(Tier.FOUNDATION, rng).dedup_key for _ in range(100)}
    assert len(keys) > 25


def test_topic_definitions_have_expected_metadata():
    topics = [
        angles.TOPIC_STRAIGHT_LINE,
        angles.TOPIC_AROUND_POINT,
        angles.TOPIC_TRIANGLE,
        angles.TOPIC_PARALLEL_LINES_FOUNDATION,
        angles.TOPIC_PARALLEL_LINES,
        angles.TOPIC_EXTERIOR_FOUNDATION,
        angles.TOPIC_EXTERIOR,
        angles.TOPIC_POLYGON_INTERIOR_FOUNDATION,
        angles.TOPIC_POLYGON_INTERIOR,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 9
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Angles"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_modelled_example_pilot_scope():
    assert angles.TOPIC_TRIANGLE.generate_modelled_example is not None
    other_topics = [
        angles.TOPIC_STRAIGHT_LINE, angles.TOPIC_AROUND_POINT,
        angles.TOPIC_PARALLEL_LINES_FOUNDATION, angles.TOPIC_PARALLEL_LINES,
        angles.TOPIC_EXTERIOR_FOUNDATION, angles.TOPIC_EXTERIOR,
        angles.TOPIC_POLYGON_INTERIOR_FOUNDATION, angles.TOPIC_POLYGON_INTERIOR,
    ]
    for t in other_topics:
        assert t.generate_modelled_example is None


def test_modelled_example_triangle_angles_produces_verified_examples():
    rng = random.Random(203)
    for _ in range(TRIALS):
        example = angles.generate_modelled_example_triangle_angles(Tier.FOUNDATION, rng)
        assert example.topic_id == "angles_triangle"
        assert example.prompt
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None
        assert example.diagram.kind == "triangle_angles"
