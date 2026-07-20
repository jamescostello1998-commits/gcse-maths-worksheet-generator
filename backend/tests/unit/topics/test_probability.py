import random

from app.core.models import Tier
from app.topics import probability

TRIALS = 200

GENERATORS = [
    (probability.generate_single_event, Tier.FOUNDATION),
    (probability.generate_complement, Tier.FOUNDATION),
    (probability.generate_combined_dice, Tier.HIGHER),
    (probability.generate_conditional_without_replacement, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(70)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(72)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 20


def test_topic_definitions_have_expected_metadata():
    topics = [
        probability.TOPIC_SINGLE_EVENT,
        probability.TOPIC_COMPLEMENT,
        probability.TOPIC_COMBINED_DICE,
        probability.TOPIC_CONDITIONAL,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "probability"
        assert t.group == "Probability"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_modelled_example_pilot_scope():
    assert probability.TOPIC_SINGLE_EVENT.generate_modelled_example is not None
    for t in (probability.TOPIC_COMPLEMENT, probability.TOPIC_COMBINED_DICE, probability.TOPIC_CONDITIONAL):
        assert t.generate_modelled_example is None


def test_modelled_example_single_event_produces_verified_examples():
    rng = random.Random(204)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_single_event(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_single_event"
        assert example.prompt
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
