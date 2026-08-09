import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import functions

TRIALS = 200

GENERATORS = [
    (functions.generate_functions_evaluate, Tier.FOUNDATION),
    (functions.generate_functions_composite_inverse, Tier.HIGHER),
    (functions.generate_functions_inverse_evaluate, Tier.HIGHER),
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
        functions.TOPIC_FUNCTIONS_EVALUATE,
        functions.TOPIC_FUNCTIONS_COMPOSITE_INVERSE,
        functions.TOPIC_FUNCTIONS_INVERSE_EVALUATE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Functions"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_inverse_evaluate_answer_satisfies_the_original_function():
    # Independent check (beyond the generator's own internal verification):
    # substituting the claimed answer back into f(x) should reproduce the
    # numeric input k that f^-1 was evaluated at.
    rng = random.Random(124)
    for _ in range(TRIALS):
        q = functions.generate_functions_inverse_evaluate(Tier.HIGHER, rng)
        a, b, k = (int(x) for x in q.dedup_key.split(":")[1:])
        value = Fraction(q.final_answer)
        assert a * value + b == k


MODELLED_EXAMPLE_GENERATORS = [
    (functions.generate_modelled_example_functions_evaluate, Tier.FOUNDATION, "functions_evaluate_F"),
    (functions.generate_modelled_example_functions_composite_inverse, Tier.HIGHER, "functions_composite_inverse_H"),
    (functions.generate_modelled_example_functions_inverse_evaluate, Tier.HIGHER, "functions_inverse_evaluate_H"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        functions.TOPIC_FUNCTIONS_EVALUATE,
        functions.TOPIC_FUNCTIONS_COMPOSITE_INVERSE,
        functions.TOPIC_FUNCTIONS_INVERSE_EVALUATE,
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
