import random

from app.core.models import Tier
from app.topics import probability

TRIALS = 200


def test_foundation_generates_valid_questions():
    rng = random.Random(70)
    for _ in range(TRIALS):
        q = probability.generate(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_higher_generates_valid_questions():
    rng = random.Random(71)
    for _ in range(TRIALS):
        q = probability.generate(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer


def test_dedup_keys_vary():
    rng = random.Random(72)
    keys = {probability.generate(Tier.HIGHER, rng).dedup_key for _ in range(100)}
    assert len(keys) > 20
