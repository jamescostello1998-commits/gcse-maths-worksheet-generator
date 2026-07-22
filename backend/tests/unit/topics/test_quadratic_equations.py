import random

from app.core.models import Tier
from app.topics import quadratic_equations

TRIALS = 200

GENERATORS = [
    (quadratic_equations.generate_quadratic_formula, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(300)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(301)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [quadratic_equations.TOPIC_QUADRATIC_FORMULA]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Solving Quadratic Equations"
        assert t.fixed_tier == Tier.HIGHER


def test_both_shapes_are_produced():
    rng = random.Random(302)
    seen_decimal = False
    seen_surd = False
    for _ in range(TRIALS):
        q = quadratic_equations.generate_quadratic_formula(Tier.HIGHER, rng)
        if q.dedup_key.startswith("quad_dec:"):
            seen_decimal = True
            assert "decimal places" in q.prompt
        elif q.dedup_key.startswith("quad_surd:"):
            seen_surd = True
            assert "√" in q.final_answer
    assert seen_decimal and seen_surd


MODELLED_EXAMPLE_GENERATORS = [
    (quadratic_equations.generate_modelled_example_quadratic_formula, Tier.HIGHER, "quadratic_formula"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (quadratic_equations.TOPIC_QUADRATIC_FORMULA,):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(320)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
