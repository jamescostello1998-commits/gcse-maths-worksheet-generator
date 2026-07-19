import random

import sympy as sp

from app.core.models import Tier
from app.topics import percentages
from app.topics.number_format import fmt_money

TRIALS = 200

GENERATORS = [
    (percentages.generate_of_amount, Tier.FOUNDATION),
    (percentages.generate_change, Tier.FOUNDATION),
    (percentages.generate_reverse, Tier.HIGHER),
    (percentages.generate_compound, Tier.HIGHER),
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
        percentages.TOPIC_REVERSE,
        percentages.TOPIC_COMPOUND,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Percentages"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
