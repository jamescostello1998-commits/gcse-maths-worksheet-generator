import random

import sympy as sp

from app.core.models import Tier
from app.topics import linear_equations

TRIALS = 200

GENERATORS = [
    (linear_equations.generate_one_step, Tier.FOUNDATION),
    (linear_equations.generate_two_step, Tier.FOUNDATION),
    (linear_equations.generate_multi_step, Tier.FOUNDATION),
    (linear_equations.generate_both_sides_foundation, Tier.FOUNDATION),
    (linear_equations.generate_brackets_foundation, Tier.FOUNDATION),
    (linear_equations.generate_both_sides, Tier.HIGHER),
    (linear_equations.generate_brackets, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(1)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert len(q.solution_steps) >= 2
            assert q.final_answer


def test_final_answer_always_parses_as_rational():
    rng = random.Random(3)
    for generate, tier in GENERATORS:
        for _ in range(TRIALS):
            q = generate(tier, rng)
            parsed = sp.Rational(q.final_answer) if "/" in q.final_answer else sp.Integer(q.final_answer)
            assert parsed.is_rational


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(4)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_foundation_generators_never_produce_negative_coefficient():
    rng = random.Random(5)
    for generate in (linear_equations.generate_one_step, linear_equations.generate_two_step):
        for _ in range(TRIALS):
            q = generate(Tier.FOUNDATION, rng)
            assert "-" not in q.prompt.split("=")[0]


def test_topic_definitions_have_expected_metadata():
    topics = [
        linear_equations.TOPIC_ONE_STEP,
        linear_equations.TOPIC_TWO_STEP,
        linear_equations.TOPIC_MULTI_STEP,
        linear_equations.TOPIC_BOTH_SIDES_FOUNDATION,
        linear_equations.TOPIC_BRACKETS_FOUNDATION,
        linear_equations.TOPIC_BOTH_SIDES,
        linear_equations.TOPIC_BRACKETS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 7
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Solving Linear Equations"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_all_topics_have_modelled_example_wired():
    topics = [
        linear_equations.TOPIC_ONE_STEP,
        linear_equations.TOPIC_TWO_STEP,
        linear_equations.TOPIC_MULTI_STEP,
        linear_equations.TOPIC_BOTH_SIDES_FOUNDATION,
        linear_equations.TOPIC_BRACKETS_FOUNDATION,
        linear_equations.TOPIC_BOTH_SIDES,
        linear_equations.TOPIC_BRACKETS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (linear_equations.generate_modelled_example_one_step, Tier.FOUNDATION, "linear_one_step"),
    (linear_equations.generate_modelled_example_two_step, Tier.FOUNDATION, "linear_two_step"),
    (linear_equations.generate_modelled_example_multi_step, Tier.FOUNDATION, "linear_multi_step"),
    (
        linear_equations.generate_modelled_example_both_sides_foundation,
        Tier.FOUNDATION,
        "linear_both_sides_foundation",
    ),
    (
        linear_equations.generate_modelled_example_brackets_foundation,
        Tier.FOUNDATION,
        "linear_brackets_foundation",
    ),
    (linear_equations.generate_modelled_example_both_sides, Tier.HIGHER, "linear_both_sides"),
    (linear_equations.generate_modelled_example_brackets, Tier.HIGHER, "linear_brackets"),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate_modelled_example, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(201)
        for _ in range(TRIALS):
            example = generate_modelled_example(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
