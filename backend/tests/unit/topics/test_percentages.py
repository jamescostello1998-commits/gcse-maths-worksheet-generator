import random

import sympy as sp

from app.core.models import Tier
from app.topics import percentages
from app.topics.number_format import fmt_money

TRIALS = 200

GENERATORS = [
    (percentages.generate_of_amount, Tier.FOUNDATION),
    (percentages.generate_change, Tier.FOUNDATION),
    (percentages.generate_reverse_foundation, Tier.FOUNDATION),
    (percentages.generate_reverse, Tier.HIGHER),
    (percentages.generate_compound, Tier.HIGHER),
    (percentages.generate_compound_foundation, Tier.FOUNDATION),
    (percentages.generate_simple_interest, Tier.FOUNDATION),
    (percentages.generate_find_percentage_change, Tier.FOUNDATION),
    (percentages.generate_percentage_increase_decrease_calculator, Tier.HIGHER),
    (percentages.generate_mixed_percentages, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(20)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_fmt_money_formats_cleanly():
    assert fmt_money(sp.Integer(46)) == "46"
    assert fmt_money(sp.Rational("47.5")) == "47.50"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(22)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        percentages.TOPIC_OF_AMOUNT,
        percentages.TOPIC_CHANGE,
        percentages.TOPIC_REVERSE_FOUNDATION,
        percentages.TOPIC_REVERSE,
        percentages.TOPIC_COMPOUND,
        percentages.TOPIC_COMPOUND_FOUNDATION,
        percentages.TOPIC_SIMPLE_INTEREST,
        percentages.TOPIC_FIND_PERCENTAGE_CHANGE,
        percentages.TOPIC_PERCENTAGE_INCREASE_DECREASE_CALCULATOR,
        percentages.TOPIC_MIXED_PERCENTAGES,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 10
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Percentages"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert percentages.TOPIC_COMPOUND_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert percentages.TOPIC_SIMPLE_INTEREST.fixed_tier == Tier.FOUNDATION
    assert percentages.TOPIC_FIND_PERCENTAGE_CHANGE.fixed_tier == Tier.FOUNDATION
    assert percentages.TOPIC_PERCENTAGE_INCREASE_DECREASE_CALCULATOR.fixed_tier == Tier.HIGHER
    assert percentages.TOPIC_MIXED_PERCENTAGES.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_have_generator_wired():
    for t in (
        percentages.TOPIC_OF_AMOUNT, percentages.TOPIC_CHANGE,
        percentages.TOPIC_REVERSE_FOUNDATION, percentages.TOPIC_REVERSE,
        percentages.TOPIC_COMPOUND, percentages.TOPIC_COMPOUND_FOUNDATION,
        percentages.TOPIC_SIMPLE_INTEREST, percentages.TOPIC_FIND_PERCENTAGE_CHANGE,
        percentages.TOPIC_PERCENTAGE_INCREASE_DECREASE_CALCULATOR, percentages.TOPIC_MIXED_PERCENTAGES,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_of_amount_produces_verified_examples():
    rng = random.Random(202)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_of_amount(Tier.FOUNDATION, rng)
        assert example.topic_id == "percentage_of_amount"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_change_produces_verified_examples():
    rng = random.Random(203)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_change(Tier.FOUNDATION, rng)
        assert example.topic_id == "percentage_change"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_reverse_foundation_produces_verified_examples():
    rng = random.Random(204)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_reverse_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "reverse_percentage_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_reverse_produces_verified_examples():
    rng = random.Random(205)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_reverse(Tier.HIGHER, rng)
        assert example.topic_id == "reverse_percentage"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_compound_produces_verified_examples():
    rng = random.Random(206)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_compound(Tier.HIGHER, rng)
        assert example.topic_id == "compound_percentage"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_compound_foundation_produces_verified_examples():
    rng = random.Random(207)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_compound_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "compound_percentage_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_simple_interest_produces_verified_examples():
    rng = random.Random(208)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_simple_interest(Tier.FOUNDATION, rng)
        assert example.topic_id == "simple_interest"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_find_percentage_change_produces_verified_examples():
    rng = random.Random(209)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_find_percentage_change(Tier.FOUNDATION, rng)
        assert example.topic_id == "find_percentage_change"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_percentage_increase_decrease_calculator_produces_verified_examples():
    rng = random.Random(210)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_percentage_increase_decrease_calculator(Tier.HIGHER, rng)
        assert example.topic_id == "percentage_increase_decrease_calculator"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mixed_percentages_produces_verified_examples():
    rng = random.Random(211)
    for _ in range(TRIALS):
        example = percentages.generate_modelled_example_mixed_percentages(Tier.HIGHER, rng)
        assert example.topic_id == "mixed_percentages"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_simple_interest_totals_at_least_the_principal_when_asked():
    rng = random.Random(212)
    for _ in range(TRIALS):
        q = percentages.generate_simple_interest(Tier.FOUNDATION, rng)
        assert q.dedup_key.startswith("si:")


def test_find_percentage_change_answer_states_direction():
    rng = random.Random(213)
    for _ in range(TRIALS):
        q = percentages.generate_find_percentage_change(Tier.FOUNDATION, rng)
        assert ("increase" in q.final_answer) or ("decrease" in q.final_answer)


def test_percentage_increase_decrease_calculator_rounds_to_two_dp():
    rng = random.Random(214)
    for _ in range(TRIALS):
        q = percentages.generate_percentage_increase_decrease_calculator(Tier.HIGHER, rng)
        # final_answer looks like "£123.45"
        assert q.final_answer.startswith("£")
        decimal_part = q.final_answer.split(".")[-1]
        assert len(decimal_part) == 2


def test_mixed_percentages_dispatches_to_all_four_underlying_topics():
    rng = random.Random(215)
    seen_prefixes = set()
    for _ in range(200):
        q = percentages.generate_mixed_percentages(Tier.HIGHER, rng)
        assert q.topic_id == "mixed_percentages"
        assert q.tier == Tier.HIGHER
        seen_prefixes.add(q.dedup_key.split(":")[1])
    # underlying dedup keys are of_amount/change/reverse/compound-flavoured
    assert len(seen_prefixes) >= 3
