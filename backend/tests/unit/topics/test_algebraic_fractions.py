import random

from app.core.models import Tier
from app.topics import algebraic_fractions

TRIALS = 200

GENERATORS = [
    (algebraic_fractions.generate_algebraic_fractions_add_subtract, Tier.HIGHER),
    (algebraic_fractions.generate_algebraic_fractions_multiply_divide, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(400)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(401)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_add_subtract_answer_is_single_fraction_with_factorised_denominator():
    rng = random.Random(402)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_add_subtract(Tier.HIGHER, rng)
        assert q.final_answer.count("(") >= 3  # numerator bracket + two denominator factors
        assert "/" in q.final_answer


def test_multiply_divide_answer_is_a_simplified_linear_expression():
    rng = random.Random(403)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_multiply_divide(Tier.HIGHER, rng)
        assert "/" not in q.final_answer
        assert "x" in q.final_answer


def test_topic_definitions_have_expected_metadata():
    topics = [
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_ADD_SUBTRACT,
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_MULTIPLY_DIVIDE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Algebraic Fractions"
        assert t.fixed_tier == Tier.HIGHER


MODELLED_EXAMPLE_GENERATORS = [
    (
        algebraic_fractions.generate_modelled_example_algebraic_fractions_add_subtract,
        Tier.HIGHER,
        "algebraic_fractions_add_subtract",
    ),
    (
        algebraic_fractions.generate_modelled_example_algebraic_fractions_multiply_divide,
        Tier.HIGHER,
        "algebraic_fractions_multiply_divide",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_ADD_SUBTRACT,
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_MULTIPLY_DIVIDE,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(420)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
