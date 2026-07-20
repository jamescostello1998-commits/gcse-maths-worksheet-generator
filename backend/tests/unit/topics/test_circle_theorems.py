import random

from app.core.models import Tier
from app.topics import circle_theorems

TRIALS = 400

GENERATORS = [
    (circle_theorems.generate_circle_theorem, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(110)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None


def test_all_four_theorem_shapes_appear():
    rng = random.Random(111)
    kinds = {circle_theorems.generate_circle_theorem(Tier.HIGHER, rng).diagram.kind for _ in range(TRIALS)}
    assert kinds == {
        "circle_angle_centre",
        "circle_semicircle",
        "circle_cyclic_quad",
        "circle_two_tangents",
    }


def test_dedup_keys_vary():
    rng = random.Random(112)
    keys = {circle_theorems.generate_circle_theorem(Tier.HIGHER, rng).dedup_key for _ in range(200)}
    assert len(keys) > 60


def test_topic_definition_has_expected_metadata():
    t = circle_theorems.TOPIC_CIRCLE_THEOREMS
    assert t.section == "geometry"
    assert t.group == "Circle Theorems"
    assert t.fixed_tier == Tier.HIGHER


def test_topic_has_a_modelled_example_generator_wired_up():
    assert circle_theorems.TOPIC_CIRCLE_THEOREMS.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(210)
    for _ in range(TRIALS):
        ex = circle_theorems.generate_modelled_example_circle_theorem(Tier.HIGHER, rng)
        assert ex.topic_id == "circle_theorems"
        assert ex.tier == Tier.HIGHER
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None


def test_modelled_example_all_four_theorem_shapes_appear():
    rng = random.Random(211)
    kinds = {circle_theorems.generate_modelled_example_circle_theorem(Tier.HIGHER, rng).diagram.kind for _ in range(TRIALS)}
    assert kinds == {
        "circle_angle_centre",
        "circle_semicircle",
        "circle_cyclic_quad",
        "circle_two_tangents",
    }
