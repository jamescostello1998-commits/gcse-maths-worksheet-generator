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


def test_prompt_states_no_rounding_and_answer_is_to_4dp():
    # The surd-answer shape was removed (decimal-only now); the prompt no
    # longer states a rounding instruction at all (left to the student), but
    # the stored answer is always rounded to 4dp so it stays checkable
    # against whatever reasonable precision a student picks.
    rng = random.Random(302)
    for _ in range(TRIALS):
        q = quadratic_equations.generate_quadratic_formula(Tier.HIGHER, rng)
        assert q.dedup_key.startswith("quad_dec:")
        assert "decimal places" not in q.prompt
        assert "√" not in q.prompt
        for part in q.final_answer.split(" or "):
            root = part.replace("x = ", "")
            assert len(root.split(".")[1]) == 4


MODELLED_EXAMPLE_GENERATORS = [
    (quadratic_equations.generate_modelled_example_quadratic_formula, Tier.HIGHER, "quadratic_formula_H"),
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
