import random

from app.core.models import Tier
from app.topics import negative_numbers

TRIALS = 200

GENERATORS = [
    (negative_numbers.generate_negative_number_arithmetic, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(500)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_all_four_operations_appear():
    rng = random.Random(501)
    ops = {negative_numbers.generate_negative_number_arithmetic(Tier.FOUNDATION, rng).dedup_key.rsplit(":", 1)[1] for _ in range(200)}
    assert ops == {"+", "-", "×", "÷"}


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(502)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [negative_numbers.TOPIC_NEGATIVE_NUMBERS]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "number"
        assert t.group == "Negative Numbers"
        assert t.fixed_tier == Tier.FOUNDATION


MODELLED_EXAMPLE_GENERATORS = [
    (negative_numbers.generate_modelled_example_negative_number_arithmetic, Tier.FOUNDATION, "negative_numbers"),
]


def test_topic_definitions_have_modelled_example_generator():
    assert negative_numbers.TOPIC_NEGATIVE_NUMBERS.generate_modelled_example is not None


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(930)
        for _ in range(200):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
