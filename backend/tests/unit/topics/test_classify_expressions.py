import random

from app.core.models import Tier
from app.topics import classify_expressions

TRIALS = 200

GENERATORS = [
    (classify_expressions.generate_classify_expressions, Tier.FOUNDATION),
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
            assert q.final_answer in ("expression", "equation", "formula", "identity")


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_all_four_categories_are_produced():
    rng = random.Random(99)
    categories = {classify_expressions.generate_classify_expressions(Tier.FOUNDATION, rng).final_answer for _ in range(200)}
    assert categories == {"expression", "equation", "formula", "identity"}


def test_expression_statements_have_no_equals_or_identity_sign():
    rng = random.Random(5)
    for _ in range(200):
        q = classify_expressions.generate_classify_expressions(Tier.FOUNDATION, rng)
        if q.final_answer == "expression":
            statement = q.prompt.split("\n")[-1]
            assert "=" not in statement
            assert "≡" not in statement


def test_equation_statements_have_equals_but_not_identity_sign():
    rng = random.Random(6)
    for _ in range(200):
        q = classify_expressions.generate_classify_expressions(Tier.FOUNDATION, rng)
        if q.final_answer == "equation":
            statement = q.prompt.split("\n")[-1]
            assert "=" in statement
            assert "≡" not in statement


def test_identity_statements_use_identity_sign():
    rng = random.Random(7)
    for _ in range(200):
        q = classify_expressions.generate_classify_expressions(Tier.FOUNDATION, rng)
        if q.final_answer == "identity":
            statement = q.prompt.split("\n")[-1]
            assert "≡" in statement


def test_formula_statements_come_from_the_curated_pool():
    rng = random.Random(8)
    pool_statements = {f for f, _ in classify_expressions._FORMULAE}
    for _ in range(200):
        q = classify_expressions.generate_classify_expressions(Tier.FOUNDATION, rng)
        if q.final_answer == "formula":
            statement = q.prompt.split("\n")[-1]
            assert statement in pool_statements


def test_formula_pool_has_at_least_eight_entries():
    assert len(classify_expressions._FORMULAE) >= 8


def test_topic_definitions_have_expected_metadata():
    topics = [classify_expressions.TOPIC_CLASSIFY_EXPRESSIONS]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Expressions, Formulae, Equations & Identities"
        assert t.fixed_tier == Tier.FOUNDATION


MODELLED_EXAMPLE_GENERATORS = [
    (classify_expressions.generate_modelled_example_classify_expressions, Tier.FOUNDATION, "classify_expressions"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (classify_expressions.TOPIC_CLASSIFY_EXPRESSIONS,):
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
            assert example.final_answer in ("expression", "equation", "formula", "identity")
