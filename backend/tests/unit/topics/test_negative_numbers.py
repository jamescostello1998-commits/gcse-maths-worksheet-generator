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
