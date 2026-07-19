import random

from app.core.models import Tier
from app.topics import ratio

TRIALS = 200

GENERATORS = [
    (ratio.generate_share_two, Tier.FOUNDATION),
    (ratio.generate_find_share, Tier.FOUNDATION),
    (ratio.generate_share_three, Tier.HIGHER),
    (ratio.generate_combine_ratios, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(30)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(32)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        ratio.TOPIC_SHARE_TWO,
        ratio.TOPIC_FIND_SHARE,
        ratio.TOPIC_SHARE_THREE,
        ratio.TOPIC_COMBINE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Ratio"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
