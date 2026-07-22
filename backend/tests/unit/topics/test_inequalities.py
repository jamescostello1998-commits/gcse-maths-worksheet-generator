import random

from app.core.models import Tier
from app.topics import inequalities

TRIALS = 200

GENERATORS = [
    (inequalities.generate_solving_inequalities_foundation, Tier.FOUNDATION),
    (inequalities.generate_solving_inequalities_higher, Tier.HIGHER),
    (inequalities.generate_satisfying_inequalities_foundation, Tier.FOUNDATION),
    (inequalities.generate_satisfying_inequalities_higher, Tier.HIGHER),
    (inequalities.generate_quadratic_inequalities, Tier.HIGHER),
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


TOPICS = [
    inequalities.TOPIC_SOLVING_INEQUALITIES_FOUNDATION,
    inequalities.TOPIC_SOLVING_INEQUALITIES_HIGHER,
    inequalities.TOPIC_SATISFYING_INEQUALITIES_FOUNDATION,
    inequalities.TOPIC_SATISFYING_INEQUALITIES_HIGHER,
    inequalities.TOPIC_QUADRATIC_INEQUALITIES,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in TOPICS}
    assert len(ids) == len(TOPICS)
    for t in TOPICS:
        assert t.section == "algebra"
        assert t.group == "Inequalities"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_all_topics_have_modelled_example_wired():
    for t in TOPICS:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (
        inequalities.generate_modelled_example_solving_inequalities_foundation,
        Tier.FOUNDATION,
        "solving_inequalities_foundation",
    ),
    (
        inequalities.generate_modelled_example_solving_inequalities_higher,
        Tier.HIGHER,
        "solving_inequalities_higher",
    ),
    (
        inequalities.generate_modelled_example_satisfying_inequalities_foundation,
        Tier.FOUNDATION,
        "satisfying_inequalities_foundation",
    ),
    (
        inequalities.generate_modelled_example_satisfying_inequalities_higher,
        Tier.HIGHER,
        "satisfying_inequalities_higher",
    ),
    (
        inequalities.generate_modelled_example_quadratic_inequalities,
        Tier.HIGHER,
        "quadratic_inequalities",
    ),
]


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


def test_solving_inequalities_foundation_never_flips_sign():
    # Foundation content is defined by keeping the coefficient of x positive
    # throughout, so the displayed symbol should never need to change.
    rng = random.Random(55)
    for _ in range(TRIALS):
        q = inequalities.generate_solving_inequalities_foundation(Tier.FOUNDATION, rng)
        prompt_symbol = next(
            s for s in ("<=", ">=", "<", ">") if f" {inequalities.SYM_DISPLAY[s]} " in q.prompt
        )
        answer_symbol = next(
            s for s in ("<=", ">=", "<", ">") if f" {inequalities.SYM_DISPLAY[s]} " in q.final_answer
        )
        assert prompt_symbol == answer_symbol


def test_satisfying_inequalities_answers_are_comma_separated_integers():
    for generate, tier in (
        (inequalities.generate_satisfying_inequalities_foundation, Tier.FOUNDATION),
        (inequalities.generate_satisfying_inequalities_higher, Tier.HIGHER),
    ):
        rng = random.Random(99)
        for _ in range(50):
            q = generate(tier, rng)
            values = [int(v.strip()) for v in q.final_answer.split(",")]
            assert len(values) >= 1
            # Strictly increasing, confirming a clean sorted integer list.
            assert values == sorted(values)
            assert len(set(values)) == len(values)


def test_quadratic_inequalities_answer_format():
    rng = random.Random(31)
    for _ in range(100):
        q = inequalities.generate_quadratic_inequalities(Tier.HIGHER, rng)
        assert ("or" in q.final_answer) or (q.final_answer.count("x") == 1)
