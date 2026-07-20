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


def test_all_fraction_topics_have_modelled_examples():
    topics = [
        fractions.TOPIC_SIMPLIFY,
        fractions.TOPIC_ADD_SUBTRACT,
        fractions.TOPIC_MULTIPLY,
        fractions.TOPIC_DIVIDE,
        fractions.TOPIC_MIXED_NUMBER_ARITHMETIC,
        fractions.TOPIC_OF_AMOUNT,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (fractions.generate_modelled_example_simplify_fraction, Tier.FOUNDATION, "fractions_simplify"),
    (fractions.generate_modelled_example_add_subtract, Tier.FOUNDATION, "fractions_add_subtract"),
    (fractions.generate_modelled_example_multiply_fractions, Tier.FOUNDATION, "fractions_multiply"),
    (fractions.generate_modelled_example_divide_fractions, Tier.HIGHER, "fractions_divide"),
    (fractions.generate_modelled_example_mixed_number_arithmetic, Tier.HIGHER, "fractions_mixed_number_arithmetic"),
    (fractions.generate_modelled_example_fraction_of_amount, Tier.FOUNDATION, "fractions_of_amount"),
]


def test_modelled_examples_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(200)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
