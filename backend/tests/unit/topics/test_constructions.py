import random

from app.core.models import Tier
from app.topics import constructions

TRIALS = 300

GENERATORS = [
    (constructions.generate_construction_angle_bisector, Tier.FOUNDATION),
    (constructions.generate_construction_perpendicular_bisector, Tier.FOUNDATION),
    (constructions.generate_construction_triangle, Tier.FOUNDATION),
    (constructions.generate_construction_perpendicular_from_point, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_questions_with_no_diagram():
    # These topics have no verify() (author-review only, confirmed with the
    # user - see constructions.py's module docstring) and no diagram, unlike
    # every other topic in this app.
    for generate, tier in GENERATORS:
        rng = random.Random(900)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert len(q.solution_steps) == 4
            assert q.final_answer
            assert q.diagram is None


def test_dedup_keys_vary_widely():
    for generate, tier in GENERATORS:
        rng = random.Random(901)
        keys = {generate(tier, rng).dedup_key for _ in range(TRIALS)}
        assert len(keys) > TRIALS * 0.9


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
    (constructions.generate_modelled_example_construction_angle_bisector, "construction_angle_bisector"),
    (constructions.generate_modelled_example_construction_perpendicular_bisector, "construction_perpendicular_bisector"),
    (constructions.generate_modelled_example_construction_triangle, "construction_triangle"),
    (constructions.generate_modelled_example_construction_perpendicular_from_point, "construction_perpendicular_from_point"),
]


def test_modelled_examples_are_valid():
    for generate, topic_id in MODELLED_GENERATORS:
        rng = random.Random(905)
        for _ in range(TRIALS):
            ex = generate(Tier.FOUNDATION, rng)
            assert ex.topic_id == topic_id
            assert ex.tier == Tier.FOUNDATION
            assert ex.prompt
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3
            assert ex.final_answer
            assert ex.diagram is None
