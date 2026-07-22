import random

from app.core.models import Tier
from app.topics import order_of_operations

TRIALS = 200

GENERATORS = [
    (order_of_operations.generate_bidmas, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(150)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(151)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [order_of_operations.TOPIC_BIDMAS]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "number"
        assert t.group == "Order of Operations (BIDMAS)"
        assert t.fixed_tier == Tier.FOUNDATION


def test_all_topics_have_modelled_example_wired():
    for t in (order_of_operations.TOPIC_BIDMAS,):
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (order_of_operations.generate_modelled_example_bidmas, Tier.FOUNDATION, "bidmas"),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(250)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
