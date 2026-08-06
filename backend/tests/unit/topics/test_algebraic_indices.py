import random

from app.core.models import Tier
from app.topics import algebraic_indices

TRIALS = 200

GENERATORS = [
    (algebraic_indices.generate_algebraic_indices_foundation, Tier.FOUNDATION),
    (algebraic_indices.generate_algebraic_indices_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(120)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_algebraic_indices_higher_shows_a_fractional_exponent_often():
    # Reweighted towards "fractional" (40%, up from an even 25% split) since
    # a genuine fractional exponent is this topic's own distinguishing
    # content - over enough trials it should appear noticeably more than a
    # quarter of the time.
    rng = random.Random(122)
    fractional_count = 0
    for _ in range(200):
        q = algebraic_indices.generate_algebraic_indices_higher(Tier.HIGHER, rng)
        if "^(" in q.prompt:
            fractional_count += 1
    assert fractional_count > 200 * 0.3


def test_topic_definitions_have_expected_metadata():
    topics = [
        algebraic_indices.TOPIC_ALGEBRAIC_INDICES_FOUNDATION,
        algebraic_indices.TOPIC_ALGEBRAIC_INDICES_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Algebraic Indices"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (
        algebraic_indices.generate_modelled_example_algebraic_indices_foundation,
        Tier.FOUNDATION,
        "algebraic_indices_foundation",
    ),
    (
        algebraic_indices.generate_modelled_example_algebraic_indices_higher,
        Tier.HIGHER,
        "algebraic_indices_higher",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        algebraic_indices.TOPIC_ALGEBRAIC_INDICES_FOUNDATION,
        algebraic_indices.TOPIC_ALGEBRAIC_INDICES_HIGHER,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(220)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
