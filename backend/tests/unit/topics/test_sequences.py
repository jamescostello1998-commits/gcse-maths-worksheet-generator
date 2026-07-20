import random

from app.core.models import Tier
from app.topics import sequences

TRIALS = 200

GENERATORS = [
    (sequences.generate_next_term, Tier.FOUNDATION),
    (sequences.generate_term_to_term_rule, Tier.FOUNDATION),
    (sequences.generate_nth_term, Tier.FOUNDATION),
    (sequences.generate_quadratic_nth_term, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(150)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(151)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        sequences.TOPIC_NEXT_TERM,
        sequences.TOPIC_TERM_TO_TERM_RULE,
        sequences.TOPIC_NTH_TERM,
        sequences.TOPIC_QUADRATIC_NTH_TERM,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Sequences"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (sequences.generate_modelled_example_next_term, Tier.FOUNDATION, "sequences_next_term"),
    (sequences.generate_modelled_example_term_to_term_rule, Tier.FOUNDATION, "sequences_term_to_term_rule"),
    (sequences.generate_modelled_example_nth_term, Tier.FOUNDATION, "sequences_nth_term"),
    (sequences.generate_modelled_example_quadratic_nth_term, Tier.HIGHER, "sequences_quadratic_nth_term"),
]


def test_all_topics_have_modelled_example_wired():
    topics = [
        sequences.TOPIC_NEXT_TERM,
        sequences.TOPIC_TERM_TO_TERM_RULE,
        sequences.TOPIC_NTH_TERM,
        sequences.TOPIC_QUADRATIC_NTH_TERM,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(250)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
