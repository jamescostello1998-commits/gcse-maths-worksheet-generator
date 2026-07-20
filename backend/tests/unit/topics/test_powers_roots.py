import random

from app.core.models import Tier
from app.topics import powers_roots

TRIALS = 200

GENERATORS = [
    (powers_roots.generate_powers_foundation, Tier.FOUNDATION),
    (powers_roots.generate_powers_higher, Tier.HIGHER),
    (powers_roots.generate_roots_foundation, Tier.FOUNDATION),
    (powers_roots.generate_roots_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(700)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_roots_higher_answer_is_in_a_root_b_form():
    rng = random.Random(701)
    for _ in range(TRIALS):
        q = powers_roots.generate_roots_higher(Tier.HIGHER, rng)
        assert "√" in q.final_answer
        coeff, radicand = q.final_answer.split("√")
        assert int(coeff) > 1
        assert int(radicand) > 1


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(702)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "number"
        assert t.group == "Powers, Roots & Indices"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (powers_roots.generate_modelled_example_powers_foundation, Tier.FOUNDATION, "powers_foundation"),
    (powers_roots.generate_modelled_example_powers_higher, Tier.HIGHER, "powers_higher"),
    (powers_roots.generate_modelled_example_roots_foundation, Tier.FOUNDATION, "roots_foundation"),
    (powers_roots.generate_modelled_example_roots_higher, Tier.HIGHER, "roots_higher"),
]


def test_topic_definitions_have_modelled_example_generator():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(940)
        for _ in range(200):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
