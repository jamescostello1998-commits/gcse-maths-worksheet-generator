import random

from app.core.models import Tier
from app.topics import pythagoras

TRIALS = 200


def test_foundation_generates_valid_questions():
    rng = random.Random(60)
    for _ in range(TRIALS):
        q = pythagoras.generate(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_higher_generates_valid_questions():
    rng = random.Random(61)
    for _ in range(TRIALS):
        q = pythagoras.generate(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_simplify_surd():
    assert pythagoras._simplify_surd(50) == (5, 2)
    assert pythagoras._simplify_surd(9) == (3, 1)
    assert pythagoras._simplify_surd(8) == (2, 2)
    assert pythagoras._simplify_surd(7) == (1, 7)


def test_dedup_keys_vary():
    rng = random.Random(62)
    keys = {pythagoras.generate(Tier.HIGHER, rng).dedup_key for _ in range(100)}
    assert len(keys) > 50
