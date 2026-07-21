import random

from app.core.models import Tier
from app.topics import ratio

TRIALS = 200

GENERATORS = [
    (ratio.generate_share_two, Tier.FOUNDATION),
    (ratio.generate_find_share, Tier.FOUNDATION),
    (ratio.generate_share_three, Tier.HIGHER),
    (ratio.generate_share_three_foundation, Tier.FOUNDATION),
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
        ratio.TOPIC_SHARE_THREE_FOUNDATION,
        ratio.TOPIC_COMBINE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Ratio"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert ratio.TOPIC_SHARE_THREE_FOUNDATION.fixed_tier == Tier.FOUNDATION


def test_modelled_example_topics_have_generator_wired():
    for t in (
        ratio.TOPIC_SHARE_TWO, ratio.TOPIC_FIND_SHARE,
        ratio.TOPIC_SHARE_THREE, ratio.TOPIC_SHARE_THREE_FOUNDATION, ratio.TOPIC_COMBINE,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_share_two_produces_verified_examples():
    rng = random.Random(302)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_two(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_share_two_part"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_find_share_produces_verified_examples():
    rng = random.Random(303)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_find_share(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_find_missing_share"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_share_three_produces_verified_examples():
    rng = random.Random(304)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_three(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_share_three_part"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_share_three_foundation_produces_verified_examples():
    rng = random.Random(306)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_three_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_share_three_part_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_combine_ratios_produces_verified_examples():
    rng = random.Random(305)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_combine_ratios(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_combine"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
