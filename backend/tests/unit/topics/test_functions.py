import random

from app.core.models import Tier
from app.topics import functions

TRIALS = 200

GENERATORS = [
    (functions.generate_functions_evaluate, Tier.FOUNDATION),
    (functions.generate_functions_composite_inverse, Tier.HIGHER),
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


def test_topic_definitions_have_expected_metadata():
    topics = [functions.TOPIC_FUNCTIONS_EVALUATE, functions.TOPIC_FUNCTIONS_COMPOSITE_INVERSE]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Functions"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
