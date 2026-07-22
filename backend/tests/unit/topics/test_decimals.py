import random

from app.core.models import Tier
from app.topics import decimals

TRIALS = 200

GENERATORS = [
    (decimals.generate_round_to_decimal_places, Tier.FOUNDATION),
    (decimals.generate_round_to_significant_figures, Tier.FOUNDATION),
    (decimals.generate_ordering, Tier.FOUNDATION),
    (decimals.generate_recurring_decimal_to_fraction, Tier.HIGHER),
    (decimals.generate_dividing_decimals, Tier.FOUNDATION),
    (decimals.generate_powers_of_ten, Tier.FOUNDATION),
    (decimals.generate_decimals_add_subtract, Tier.FOUNDATION),
    (decimals.generate_decimals_multiply, Tier.FOUNDATION),
    (decimals.generate_recurring_decimal_two_digit, Tier.HIGHER),
]

# recurring_decimal_single_digit is deliberately excluded from GENERATORS above: a purely
# recurring single-digit decimal with no non-recurring prefix only has 8 possible distinct
# (numerator, denominator) pairs (the reduced denominator must divide 9), so it can never
# clear the same >30-unique-keys-in-100-trials bar the other generators comfortably clear -
# see its own dedicated full-state-space-coverage test below instead.


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(100)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_recurring_decimal_single_digit_produces_valid_verified_questions():
    rng = random.Random(100)
    for _ in range(TRIALS):
        q = decimals.generate_recurring_decimal_single_digit(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_recurring_decimal_single_digit_dedup_keys_cover_the_full_state_space():
    # Only 8 distinct (p, q) pairs are mathematically possible for a purely-recurring
    # single-digit decimal with no non-recurring prefix (reduced denominator must divide
    # 9): q=3 with p in {1, 2}, and q=9 with p in {1, 2, 4, 5, 7, 8} (p=3, 6 reduce to
    # denominator 3 instead). Over enough trials, every one of those 8 should appear.
    expected_keys = {f"recurring_1d:{p}:3" for p in (1, 2)} | {
        f"recurring_1d:{p}:9" for p in (1, 2, 4, 5, 7, 8)
    }
    rng = random.Random(103)
    keys = {decimals.generate_recurring_decimal_single_digit(Tier.FOUNDATION, rng).dedup_key for _ in range(300)}
    assert keys == expected_keys


def test_round_to_decimal_places_keeps_trailing_zeros():
    from decimal import Decimal

    rng = random.Random(1)
    found_trailing_zero_case = False
    for _ in range(200):
        q = decimals.generate_round_to_decimal_places(Tier.FOUNDATION, rng)
        dp = int(q.prompt.split(" to ")[1].split(" decimal")[0])
        assert len(q.final_answer.split(".")[-1]) == dp if "." in q.final_answer else dp == 0
        if q.final_answer.endswith("0") and "." in q.final_answer:
            found_trailing_zero_case = True
    assert found_trailing_zero_case


def test_decimal_expansion_detects_recurring_and_terminating():
    non_recurring, recurring = decimals._decimal_expansion(1, 6)
    assert non_recurring == [1]
    assert recurring == [6]

    non_recurring, recurring = decimals._decimal_expansion(1, 4)
    assert recurring is None  # 1/4 = 0.25 terminates


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(102)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        decimals.TOPIC_ROUND_DP,
        decimals.TOPIC_ROUND_SF,
        decimals.TOPIC_ORDERING,
        decimals.TOPIC_RECURRING_TO_FRACTION,
        decimals.TOPIC_DIVIDE,
        decimals.TOPIC_POWERS_OF_TEN,
        decimals.TOPIC_ADD_SUBTRACT,
        decimals.TOPIC_MULTIPLY,
        decimals.TOPIC_RECURRING_SINGLE_DIGIT,
        decimals.TOPIC_RECURRING_TWO_DIGIT,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 10
    for t in topics:
        assert t.section == "number"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert decimals.TOPIC_DIVIDE.group == "Decimals"
    assert decimals.TOPIC_POWERS_OF_TEN.group == "Multiplying & Dividing by Powers of 10"
    assert decimals.TOPIC_RECURRING_SINGLE_DIGIT.question_count == 6


def test_all_decimal_topics_have_modelled_examples():
    topics = [
        decimals.TOPIC_ROUND_DP,
        decimals.TOPIC_ROUND_SF,
        decimals.TOPIC_ORDERING,
        decimals.TOPIC_RECURRING_TO_FRACTION,
        decimals.TOPIC_DIVIDE,
        decimals.TOPIC_POWERS_OF_TEN,
        decimals.TOPIC_ADD_SUBTRACT,
        decimals.TOPIC_MULTIPLY,
        decimals.TOPIC_RECURRING_SINGLE_DIGIT,
        decimals.TOPIC_RECURRING_TWO_DIGIT,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (decimals.generate_modelled_example_round_to_decimal_places, Tier.FOUNDATION, "decimals_round_dp"),
    (decimals.generate_modelled_example_round_to_significant_figures, Tier.FOUNDATION, "decimals_round_sf"),
    (decimals.generate_modelled_example_ordering, Tier.FOUNDATION, "decimals_ordering"),
    (decimals.generate_modelled_example_recurring_decimal_to_fraction, Tier.HIGHER, "decimals_recurring_to_fraction"),
    (decimals.generate_modelled_example_dividing_decimals, Tier.FOUNDATION, "decimals_divide"),
    (decimals.generate_modelled_example_powers_of_ten, Tier.FOUNDATION, "number_powers_of_ten"),
    (decimals.generate_modelled_example_decimals_add_subtract, Tier.FOUNDATION, "decimals_add_subtract"),
    (decimals.generate_modelled_example_decimals_multiply, Tier.FOUNDATION, "decimals_multiply"),
    (
        decimals.generate_modelled_example_recurring_decimal_single_digit,
        Tier.FOUNDATION,
        "recurring_decimal_single_digit",
    ),
    (
        decimals.generate_modelled_example_recurring_decimal_two_digit,
        Tier.HIGHER,
        "recurring_decimal_two_digit",
    ),
]


def test_modelled_examples_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(300)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
