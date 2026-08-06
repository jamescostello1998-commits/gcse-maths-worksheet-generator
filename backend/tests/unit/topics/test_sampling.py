import random

from app.core.models import Tier
from app.topics import sampling

TRIALS = 300

GENERATORS = [
    (sampling.generate_sampling_methods, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(800)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_stratified_branch_answer_is_within_the_sample_size():
    rng = random.Random(801)
    seen_stratified = False
    for _ in range(TRIALS):
        q = sampling.generate_sampling_methods(Tier.FOUNDATION, rng)
        if "stratified sample of" not in q.prompt:
            continue
        seen_stratified = True
        answer = int(q.final_answer)
        assert answer >= 0
    assert seen_stratified


def test_dedup_keys_vary_widely():
    rng = random.Random(802)
    keys = {sampling.generate_sampling_methods(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.8


def test_topic_definition_metadata():
    t = sampling.TOPIC_SAMPLING_METHODS
    assert t.id == "sampling_methods"
    assert t.section == "statistics"
    assert t.group == "Sampling and Populations"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(803)
    for _ in range(TRIALS):
        ex = sampling.generate_modelled_example_sampling_methods(Tier.FOUNDATION, rng)
        assert ex.topic_id == "sampling_methods"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
