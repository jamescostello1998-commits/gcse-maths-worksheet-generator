import random

from app.core.models import Tier
from app.topics import fractions

TRIALS = 200

GENERATORS = [
    (fractions.generate_simplify_fraction, Tier.FOUNDATION),
    (fractions.generate_add_subtract_fractions, Tier.FOUNDATION),
    (fractions.generate_multiply_fractions, Tier.FOUNDATION),
    (fractions.generate_divide_fractions, Tier.HIGHER),
    (fractions.generate_mixed_number_arithmetic, Tier.HIGHER),
    (fractions.generate_fraction_of_amount, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(90)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(92)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        fractions.TOPIC_SIMPLIFY,
        fractions.TOPIC_ADD_SUBTRACT,
        fractions.TOPIC_MULTIPLY,
        fractions.TOPIC_DIVIDE,
        fractions.TOPIC_MIXED_NUMBER_ARITHMETIC,
        fractions.TOPIC_OF_AMOUNT,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 6
    for t in topics:
        assert t.section == "number"
        assert t.group == "Fractions"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
