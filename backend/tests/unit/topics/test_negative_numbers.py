import random

from app.core.models import Tier
from app.topics import negative_numbers

TRIALS = 200

GENERATORS = [
    (negative_numbers.generate_negative_add_subtract, Tier.FOUNDATION),
    (negative_numbers.generate_negative_multiply_divide, Tier.FOUNDATION),
    (negative_numbers.generate_negative_ordering, Tier.FOUNDATION),
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


def test_add_subtract_both_operations_appear():
    rng = random.Random(501)
    ops = {
        negative_numbers.generate_negative_add_subtract(Tier.FOUNDATION, rng).dedup_key.rsplit(":", 1)[1]
        for _ in range(200)
    }
    assert ops == {"+", "-"}


def test_multiply_divide_both_operations_appear():
    rng = random.Random(503)
    ops = {
        negative_numbers.generate_negative_multiply_divide(Tier.FOUNDATION, rng).dedup_key.rsplit(":", 1)[1]
        for _ in range(200)
    }
    assert ops == {"×", "÷"}


def test_add_subtract_always_involves_a_negative_operand():
    rng = random.Random(504)
    for _ in range(TRIALS):
        q = negative_numbers.generate_negative_add_subtract(Tier.FOUNDATION, rng)
        _, a, b, _op = q.dedup_key.split(":")
        assert int(a) < 0 or int(b) < 0


def test_multiply_divide_always_involves_a_negative_operand():
    rng = random.Random(505)
    for _ in range(TRIALS):
        q = negative_numbers.generate_negative_multiply_divide(Tier.FOUNDATION, rng)
        _, a, b, _op = q.dedup_key.split(":")
        assert int(a) < 0 or int(b) < 0


def test_ordering_answer_matches_number_of_values_given():
    rng = random.Random(506)
    for _ in range(TRIALS):
        q = negative_numbers.generate_negative_ordering(Tier.FOUNDATION, rng)
        given = [x.strip() for x in q.prompt.rsplit(":", 1)[1].split(",")]
        answer = [x.strip() for x in q.final_answer.split(",")]
        assert sorted(given) == sorted(answer)


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(502)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        negative_numbers.TOPIC_NEGATIVE_ADD_SUBTRACT,
        negative_numbers.TOPIC_NEGATIVE_MULTIPLY_DIVIDE,
        negative_numbers.TOPIC_NEGATIVE_ORDERING,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "number"
        assert t.group == "Negative Numbers"
        assert t.fixed_tier == Tier.FOUNDATION


MODELLED_EXAMPLE_GENERATORS = [
    (negative_numbers.generate_modelled_example_negative_add_subtract, Tier.FOUNDATION, "negative_add_subtract"),
    (
        negative_numbers.generate_modelled_example_negative_multiply_divide,
        Tier.FOUNDATION,
        "negative_multiply_divide",
    ),
    (negative_numbers.generate_modelled_example_negative_ordering, Tier.FOUNDATION, "negative_ordering"),
]


def test_topic_definitions_have_modelled_example_generator():
    assert negative_numbers.TOPIC_NEGATIVE_ADD_SUBTRACT.generate_modelled_example is not None
    assert negative_numbers.TOPIC_NEGATIVE_MULTIPLY_DIVIDE.generate_modelled_example is not None
    assert negative_numbers.TOPIC_NEGATIVE_ORDERING.generate_modelled_example is not None


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
