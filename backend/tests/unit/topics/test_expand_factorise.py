import random

from app.core.models import Tier
from app.topics import expand_factorise

TRIALS = 200


def test_foundation_generates_valid_questions():
    rng = random.Random(10)
    for _ in range(TRIALS):
        q = expand_factorise.generate(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_higher_generates_valid_questions():
    rng = random.Random(11)
    for _ in range(TRIALS):
        q = expand_factorise.generate(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_factorise_quadratic_pair_search_matches_roots():
    assert expand_factorise._find_factor_pair(1, -12) in {(4, -3), (-3, 4)}
    assert expand_factorise._find_factor_pair(-7, 12) in {(-3, -4), (-4, -3)}
    assert expand_factorise._find_factor_pair(5, 0) == (0, 5)


def test_dedup_keys_vary():
    rng = random.Random(12)
    keys = {expand_factorise.generate(Tier.HIGHER, rng).dedup_key for _ in range(100)}
    assert len(keys) > 50
