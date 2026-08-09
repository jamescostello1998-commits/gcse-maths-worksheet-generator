import random

from app.core.models import Tier
from app.topics import iteration

TRIALS = 200

GENERATORS = [
    (iteration.generate_iteration, Tier.HIGHER),
    (iteration.generate_trial_and_improvement, Tier.HIGHER),
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
    topics = [iteration.TOPIC_ITERATION, iteration.TOPIC_TRIAL_AND_IMPROVEMENT]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Iteration"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_sqrt_shape_uses_the_real_radical_symbol_not_the_word_sqrt():
    # The sqrt shape used to write the literal word "sqrt(...)" - swapped
    # for a real "√" symbol to match the rest of the app's convention (see
    # CLAUDE.md's iteration.py fix). Search across enough trials to
    # guarantee at least one "sqrt" shape question is generated.
    rng = random.Random(0)
    found_sqrt_shape = False
    for _ in range(TRIALS):
        q = iteration.generate_iteration(Tier.HIGHER, rng)
        if q.dedup_key.split(":")[1] == "sqrt":
            found_sqrt_shape = True
            assert "sqrt(" not in q.prompt
            assert "√(" in q.prompt
            for step in q.solution_steps:
                assert "sqrt(" not in step
    assert found_sqrt_shape


MODELLED_EXAMPLE_GENERATORS = [
    (iteration.generate_modelled_example_iteration, Tier.HIGHER, "iteration_H"),
    (
        iteration.generate_modelled_example_trial_and_improvement,
        Tier.HIGHER,
        "trial_and_improvement_H",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (iteration.TOPIC_ITERATION, iteration.TOPIC_TRIAL_AND_IMPROVEMENT):
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
