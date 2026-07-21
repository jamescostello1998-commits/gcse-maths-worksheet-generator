import random

from app.core.models import Tier
from app.topics import proportion

TRIALS = 200

GENERATORS = [
    (proportion.generate_direct_proportion, Tier.FOUNDATION),
    (proportion.generate_inverse_proportion, Tier.FOUNDATION),
    (proportion.generate_algebraic_direct_proportion, Tier.HIGHER),
    (proportion.generate_algebraic_inverse_proportion, Tier.HIGHER),
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
        proportion.TOPIC_DIRECT_PROPORTION,
        proportion.TOPIC_INVERSE_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Proportion"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert proportion.TOPIC_DIRECT_PROPORTION.fixed_tier == Tier.FOUNDATION
    assert proportion.TOPIC_INVERSE_PROPORTION.fixed_tier == Tier.FOUNDATION
    assert proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION.fixed_tier == Tier.HIGHER
    assert proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_have_generator_wired():
    for t in (
        proportion.TOPIC_DIRECT_PROPORTION,
        proportion.TOPIC_INVERSE_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_direct_proportion_produces_verified_examples():
    rng = random.Random(402)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_direct_proportion(Tier.FOUNDATION, rng)
        assert example.topic_id == "direct_proportion"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_inverse_proportion_produces_verified_examples():
    rng = random.Random(403)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_inverse_proportion(Tier.FOUNDATION, rng)
        assert example.topic_id == "inverse_proportion"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_algebraic_direct_proportion_produces_verified_examples():
    rng = random.Random(404)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_algebraic_direct_proportion(
            Tier.HIGHER, rng
        )
        assert example.topic_id == "algebraic_direct_proportion"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_algebraic_inverse_proportion_produces_verified_examples():
    rng = random.Random(405)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_algebraic_inverse_proportion(
            Tier.HIGHER, rng
        )
        assert example.topic_id == "algebraic_inverse_proportion"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
