import random

from app.core.models import Tier
from app.topics import decimals

TRIALS = 200

GENERATORS = [
    (decimals.generate_round_to_decimal_places, Tier.FOUNDATION),
    (decimals.generate_round_to_significant_figures, Tier.FOUNDATION),
    (decimals.generate_ordering, Tier.FOUNDATION),
    (decimals.generate_recurring_decimal_to_fraction, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(100)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


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
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "number"
        assert t.group == "Decimals"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
