import random

from app.core.models import Tier
from app.topics import standard_form

TRIALS = 200

GENERATORS = [
    (standard_form.generate_to_standard_form, Tier.FOUNDATION),
    (standard_form.generate_from_standard_form, Tier.FOUNDATION),
    (standard_form.generate_multiply_divide_standard_form, Tier.HIGHER),
    (standard_form.generate_add_subtract_standard_form, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(110)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(112)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        standard_form.TOPIC_TO_STANDARD_FORM,
        standard_form.TOPIC_FROM_STANDARD_FORM,
        standard_form.TOPIC_MULTIPLY_DIVIDE,
        standard_form.TOPIC_ADD_SUBTRACT,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "number"
        assert t.group == "Standard Form"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (standard_form.generate_modelled_example_to_standard_form, Tier.FOUNDATION, "standard_form_to"),
    (standard_form.generate_modelled_example_from_standard_form, Tier.FOUNDATION, "standard_form_from"),
    (standard_form.generate_modelled_example_multiply_divide_standard_form, Tier.HIGHER, "standard_form_multiply_divide"),
    (standard_form.generate_modelled_example_add_subtract_standard_form, Tier.HIGHER, "standard_form_add_subtract"),
]


def test_topic_definitions_have_modelled_example_generator():
    topics = [
        standard_form.TOPIC_TO_STANDARD_FORM,
        standard_form.TOPIC_FROM_STANDARD_FORM,
        standard_form.TOPIC_MULTIPLY_DIVIDE,
        standard_form.TOPIC_ADD_SUBTRACT,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(910)
        for _ in range(200):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
