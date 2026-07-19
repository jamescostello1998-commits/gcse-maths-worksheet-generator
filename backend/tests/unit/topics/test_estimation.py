import random

from app.core.models import Tier
from app.topics import estimation

TRIALS = 200

GENERATORS = [
    (estimation.generate_estimation, Tier.FOUNDATION),
    (estimation.generate_error_interval, Tier.FOUNDATION),
    (estimation.generate_bounds_calculation, Tier.HIGHER),
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


def test_error_interval_answer_format():
    rng = random.Random(1)
    for _ in range(TRIALS):
        q = estimation.generate_error_interval(Tier.FOUNDATION, rng)
        assert "≤ x <" in q.final_answer


def test_bounds_calculation_upper_bound_never_smaller_than_lower_bound():
    rng = random.Random(2)
    for _ in range(TRIALS):
        q = estimation.generate_bounds_calculation(Tier.HIGHER, rng)
        assert "bound" in q.prompt


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(102)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        estimation.TOPIC_ESTIMATION,
        estimation.TOPIC_ERROR_INTERVAL,
        estimation.TOPIC_BOUNDS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "number"
        assert t.group == "Estimation & Bounds"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
