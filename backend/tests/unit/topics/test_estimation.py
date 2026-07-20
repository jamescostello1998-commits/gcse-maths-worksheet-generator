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


MODELLED_EXAMPLE_GENERATORS = [
    (estimation.generate_modelled_example_estimation, Tier.FOUNDATION, "estimation_rounding"),
    (estimation.generate_modelled_example_error_interval, Tier.FOUNDATION, "error_interval"),
    (estimation.generate_modelled_example_bounds_calculation, Tier.HIGHER, "bounds_calculation"),
]


def test_topic_definitions_have_modelled_example_generator():
    topics = [
        estimation.TOPIC_ESTIMATION,
        estimation.TOPIC_ERROR_INTERVAL,
        estimation.TOPIC_BOUNDS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(920)
        for _ in range(200):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
