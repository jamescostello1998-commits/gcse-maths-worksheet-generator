import random

from app.core.models import Tier
from app.topics import forming_equations

TRIALS = 200

GENERATORS = [
    (forming_equations.generate_forming_equations_foundation, Tier.FOUNDATION),
    (forming_equations.generate_forming_equations_higher, Tier.HIGHER),
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
    topics = [
        forming_equations.TOPIC_FORMING_EQUATIONS_FOUNDATION,
        forming_equations.TOPIC_FORMING_EQUATIONS_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Forming and Solving Equations"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (
        forming_equations.generate_modelled_example_forming_equations_foundation,
        Tier.FOUNDATION,
        "forming_equations_foundation",
    ),
    (
        forming_equations.generate_modelled_example_forming_equations_higher,
        Tier.HIGHER,
        "forming_equations_higher",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        forming_equations.TOPIC_FORMING_EQUATIONS_FOUNDATION,
        forming_equations.TOPIC_FORMING_EQUATIONS_HIGHER,
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
