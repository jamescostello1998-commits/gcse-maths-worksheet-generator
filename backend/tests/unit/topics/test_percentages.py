import random

from app.core.models import Tier
from app.topics import percentages

TRIALS = 200


def test_foundation_generates_valid_questions():
    rng = random.Random(20)
    for _ in range(TRIALS):
        q = percentages.generate(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_higher_generates_valid_questions():
    rng = random.Random(21)
    for _ in range(TRIALS):
        q = percentages.generate(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_fmt_money_formats_cleanly():
    import sympy as sp

    assert percentages.fmt_money(sp.Integer(46)) == "46"
    assert percentages.fmt_money(sp.Rational("47.5")) == "47.50"


def test_dedup_keys_vary():
    rng = random.Random(22)
    keys = {percentages.generate(Tier.HIGHER, rng).dedup_key for _ in range(100)}
    assert len(keys) > 50
