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
