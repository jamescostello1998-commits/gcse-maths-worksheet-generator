import random

from app.core.models import Tier
from app.topics import fractional_equations as fe

TRIALS = 300

GENERATORS = [
    (fe.generate_fractional_equations_F, Tier.FOUNDATION),
    (fe.generate_fractional_equations_H, Tier.HIGHER),
    (fe.generate_fractional_equations_advanced, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(150)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer.startswith("x =")
            assert "\\frac" in q.prompt  # every question shows a real vinculum fraction


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(151)
        keys = {generate(tier, rng).dedup_key for _ in range(120)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        fe.TOPIC_FRACTIONAL_EQUATIONS_F,
        fe.TOPIC_FRACTIONAL_EQUATIONS_H,
        fe.TOPIC_FRACTIONAL_EQUATIONS_ADVANCED,
    ]
    assert len({t.id for t in topics}) == 3
    assert fe.TOPIC_FRACTIONAL_EQUATIONS_F.section == "algebra"
    assert fe.TOPIC_FRACTIONAL_EQUATIONS_F.group == "Solving Linear Equations"
    assert fe.TOPIC_FRACTIONAL_EQUATIONS_H.group == "Solving Linear Equations"
    assert fe.TOPIC_FRACTIONAL_EQUATIONS_ADVANCED.group == "Algebraic Fractions"
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (fe.generate_modelled_example_fractional_equations_F, Tier.FOUNDATION, "fractional_equations_F"),
    (fe.generate_modelled_example_fractional_equations_H, Tier.HIGHER, "fractional_equations_H"),
    (fe.generate_modelled_example_fractional_equations_advanced, Tier.HIGHER, "fractional_equations_advanced_H"),
]


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(250)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
