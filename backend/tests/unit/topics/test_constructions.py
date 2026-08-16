import random

from app.core.models import Tier
from app.topics import constructions

TRIALS = 300

GENERATORS = [
    (constructions.generate_construction_angle_bisector, Tier.FOUNDATION, False),
    (constructions.generate_construction_perpendicular_bisector, Tier.FOUNDATION, True),
    (constructions.generate_construction_triangle, Tier.FOUNDATION, True),
    (constructions.generate_construction_perpendicular_from_point, Tier.FOUNDATION, False),
]


def test_all_generators_produce_valid_questions():
    # These topics have no verify() (author-review only, confirmed with the
    # user - see constructions.py's module docstring), unlike every other
    # topic in this app. angle_bisector and perpendicular_from_point stay
    # text-only (no diagram); perpendicular_bisector and triangle each show
    # a not-to-scale diagram of what's given, for the student to actually
    # construct into (rather than just describing the method in words).
    for generate, tier, has_diagram in GENERATORS:
        rng = random.Random(900)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert len(q.solution_steps) == 4
            assert q.final_answer
            assert (q.diagram is not None) == has_diagram


def test_dedup_keys_vary_widely():
    for generate, tier, _has_diagram in GENERATORS:
        rng = random.Random(901)
        keys = {generate(tier, rng).dedup_key for _ in range(TRIALS)}
        assert len(keys) > TRIALS * 0.9


def test_perpendicular_bisector_diagram_shows_both_points_and_the_segment_no_grid():
    rng = random.Random(907)
    for _ in range(TRIALS):
        q = constructions.generate_construction_perpendicular_bisector(Tier.FOUNDATION, rng)
        assert q.diagram.kind == "loci_construction"
        params = q.diagram.params
        assert params["show_grid"] is False
        assert len(params["points"]) == 2
        assert len(params["given_lines"]) == 1
        # No circle/segment leaking the constructed bisector itself onto the
        # question page - only the given points and segment.
        assert "circle" not in params
        assert "segment" not in params


def test_triangle_diagram_shows_the_actual_vertex_labels_and_given_values():
    rng = random.Random(908)
    for _ in range(TRIALS):
        q = constructions.generate_construction_triangle(Tier.FOUNDATION, rng)
        assert q.diagram.kind == "general_triangle"
        params = q.diagram.params
        assert params["show_vertices"] is True
        assert len(params["vertex_labels"]) == 3
        # Every vertex letter used in the prompt also appears on the diagram.
        for letter in params["vertex_labels"]:
            assert letter in q.prompt
        # At least one side is always labelled with a given length.
        assert any(k.startswith("side_") for k in params)


def test_triangle_generator_covers_all_three_criteria():
    rng = random.Random(902)
    criteria = {q.dedup_key.split(":")[1] for q in (
        constructions.generate_construction_triangle(Tier.FOUNDATION, rng) for _ in range(TRIALS)
    )}
    assert criteria == {"SSS", "SAS", "ASA"}


def test_sss_sides_always_satisfy_the_triangle_inequality():
    rng = random.Random(903)
    for _ in range(TRIALS):
        a, b, c = constructions._sss_sides(rng)
        assert a + b > c
        assert a + c > b
        assert b + c > a


def test_asa_angles_always_leave_room_for_a_third_angle():
    rng = random.Random(904)
    for _ in range(TRIALS):
        angle1, angle2 = constructions._asa_angles(rng)
        assert angle1 + angle2 < 180


def test_perpendicular_from_point_covers_both_scenarios():
    rng = random.Random(906)
    scenarios = {
        constructions._random_perpendicular_from_point_content(rng)[2] for _ in range(TRIALS)
    }
    assert scenarios == {"from_point", "at_point"}


def test_topic_definitions_have_expected_metadata():
    topics = [
        constructions.TOPIC_CONSTRUCTION_ANGLE_BISECTOR,
        constructions.TOPIC_CONSTRUCTION_PERPENDICULAR_BISECTOR,
        constructions.TOPIC_CONSTRUCTION_TRIANGLE,
        constructions.TOPIC_CONSTRUCTION_PERPENDICULAR_FROM_POINT,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Constructions"
        assert t.fixed_tier == Tier.FOUNDATION
        assert t.generate_modelled_example is not None


MODELLED_GENERATORS = [
    (constructions.generate_modelled_example_construction_angle_bisector, "construction_angle_bisector_F", False),
    (
        constructions.generate_modelled_example_construction_perpendicular_bisector,
        "construction_perpendicular_bisector_F", True,
    ),
    (constructions.generate_modelled_example_construction_triangle, "construction_triangle_F", True),
    (
        constructions.generate_modelled_example_construction_perpendicular_from_point,
        "construction_perpendicular_from_point_F", False,
    ),
]


def test_modelled_examples_are_valid():
    for generate, topic_id, has_diagram in MODELLED_GENERATORS:
        rng = random.Random(905)
        for _ in range(TRIALS):
            ex = generate(Tier.FOUNDATION, rng)
            assert ex.topic_id == topic_id
            assert ex.tier == Tier.FOUNDATION
            assert ex.prompt
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3
            assert ex.final_answer
            assert (ex.diagram is not None) == has_diagram
