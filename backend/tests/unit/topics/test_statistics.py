import random

from app.core.models import Tier
from app.topics import statistics as stats_topic

TRIALS = 200

GENERATORS = [
    (stats_topic.generate_mean_and_range, Tier.FOUNDATION),
    (stats_topic.generate_median_and_mode, Tier.FOUNDATION),
    (stats_topic.generate_mean_frequency_table, Tier.FOUNDATION),
    (stats_topic.generate_mean_grouped_frequency_table, Tier.HIGHER),
    (stats_topic.generate_reverse_mean, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(80)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(82)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        stats_topic.TOPIC_MEAN_AND_RANGE,
        stats_topic.TOPIC_MEDIAN_AND_MODE,
        stats_topic.TOPIC_MEAN_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE,
        stats_topic.TOPIC_REVERSE_MEAN,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "statistics"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
