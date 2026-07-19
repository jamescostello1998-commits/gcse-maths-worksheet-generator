import random

from app.core.models import Tier
from app.topics import expand_factorise

TRIALS = 200

GENERATORS = [
    (expand_factorise.generate_expand_single, Tier.FOUNDATION),
    (expand_factorise.generate_factorise_common, Tier.FOUNDATION),
    (expand_factorise.generate_expand_double_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_factorise_quadratic_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_expand_double, Tier.HIGHER),
    (expand_factorise.generate_factorise_quadratic, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(10)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_factorise_quadratic_pair_search_matches_roots():
    assert expand_factorise._find_factor_pair(1, -12) in {(4, -3), (-3, 4)}
    assert expand_factorise._find_factor_pair(-7, 12) in {(-3, -4), (-4, -3)}
    assert expand_factorise._find_factor_pair(5, 0) == (0, 5)


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(12)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        expand_factorise.TOPIC_EXPAND_SINGLE,
        expand_factorise.TOPIC_EXPAND_DOUBLE_FOUNDATION,
        expand_factorise.TOPIC_EXPAND_DOUBLE,
        expand_factorise.TOPIC_FACTORISE_COMMON,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC_FOUNDATION,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 6
    for t in topics:
        assert t.section == "algebra"
        assert t.group in ("Expanding Brackets", "Factorising")
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
