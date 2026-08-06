import random

from app.core.models import Tier
from app.topics import algebraic_fractions

TRIALS = 200

GENERATORS = [
    (algebraic_fractions.generate_algebraic_fractions_add_subtract, Tier.HIGHER),
    (algebraic_fractions.generate_algebraic_fractions_multiply_divide, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(400)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(401)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_add_subtract_answer_is_single_fraction_with_factorised_denominator():
    rng = random.Random(402)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_add_subtract(Tier.HIGHER, rng)
        # The answer is a real stacked-vinculum fraction via the \frac{}{}
        # marker (see mathtext.py), not a raw "num/den" string - so it has
        # no bare "/" at all, and the denominator's two factorised brackets
        # are the only "(" in the string.
        assert q.final_answer.startswith("\\frac{")
        assert "/" not in q.final_answer
        assert q.final_answer.count("(") >= 2  # two denominator factors


def test_multiply_divide_answer_is_a_simplified_linear_expression():
    rng = random.Random(403)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_multiply_divide(Tier.HIGHER, rng)
        assert "/" not in q.final_answer
        assert "x" in q.final_answer


def test_add_subtract_prompt_has_no_redundant_brackets_around_lone_denominators():
    # Each prompt fraction's denominator is a single linear factor standing
    # alone in its own \frac{}{} marker - the vinculum bar already groups it,
    # so it should render bare ("x + a"), not self-wrapped ("(x + a)").
    rng = random.Random(404)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_add_subtract(Tier.HIGHER, rng)
        # Everything up to the first "}" of the second \frac{}{}'s denominator
        # is the prompt's own fraction content - neither of its two
        # standalone denominators should contain a bracket.
        prompt_fracs = q.prompt.split(", giving")[0]
        for piece in prompt_fracs.split("\\frac{")[1:]:
            den = piece.split("}{")[1].split("}")[0]
            assert "(" not in den and ")" not in den


def test_multiply_divide_prompt_has_no_redundant_brackets_around_lone_fraction_content():
    rng = random.Random(405)
    for _ in range(TRIALS):
        q = algebraic_fractions.generate_algebraic_fractions_multiply_divide(Tier.HIGHER, rng)
        prompt_fracs = q.prompt.split(", giving")[0]
        for piece in prompt_fracs.split("\\frac{")[1:]:
            num, den = piece.split("}{")[0], piece.split("}{")[1].split("}")[0]
            assert "(" not in num and ")" not in num
            assert "(" not in den and ")" not in den


def test_topic_definitions_have_expected_metadata():
    topics = [
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_ADD_SUBTRACT,
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_MULTIPLY_DIVIDE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Algebraic Fractions"
        assert t.fixed_tier == Tier.HIGHER


MODELLED_EXAMPLE_GENERATORS = [
    (
        algebraic_fractions.generate_modelled_example_algebraic_fractions_add_subtract,
        Tier.HIGHER,
        "algebraic_fractions_add_subtract",
    ),
    (
        algebraic_fractions.generate_modelled_example_algebraic_fractions_multiply_divide,
        Tier.HIGHER,
        "algebraic_fractions_multiply_divide",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_ADD_SUBTRACT,
        algebraic_fractions.TOPIC_ALGEBRAIC_FRACTIONS_MULTIPLY_DIVIDE,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(420)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
