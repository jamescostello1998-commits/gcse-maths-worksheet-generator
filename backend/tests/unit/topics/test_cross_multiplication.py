import random

from app.core.models import Tier
from app.topics import cross_multiplication as cm

TRIALS = 300

GENERATORS = [
    (cm.generate_cross_multiplication_F, Tier.FOUNDATION),
    (cm.generate_cross_multiplication_H, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(160)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer.startswith("x =")
            assert "\\frac" in q.prompt


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(161)
        keys = {generate(tier, rng).dedup_key for _ in range(120)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [cm.TOPIC_CROSS_MULTIPLICATION_F, cm.TOPIC_CROSS_MULTIPLICATION_H]
    assert len({t.id for t in topics}) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Solving Linear Equations"
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (cm.generate_modelled_example_cross_multiplication_F, Tier.FOUNDATION, "cross_multiplication_F"),
    (cm.generate_modelled_example_cross_multiplication_H, Tier.HIGHER, "cross_multiplication_H"),
]


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(260)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
