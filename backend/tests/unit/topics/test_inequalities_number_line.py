import random

from app.core.models import Tier
from app.topics import inequalities_number_line as inl

TRIALS = 200

GENERATORS = [
    (inl.generate_inequalities_number_line_foundation, Tier.FOUNDATION),
    (inl.generate_inequalities_number_line_higher, Tier.HIGHER),
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
            assert q.diagram is not None
            # Exactly one of diagram/solution_diagram should be the "blank" question-side
            # diagram for the "draw" shape, or diagram alone carries the marks for "read".
            if q.solution_diagram is not None:
                assert q.diagram.params.get("blank") is True
                assert q.solution_diagram.params.get("blank", False) is False
            else:
                assert q.diagram.params.get("blank", False) is False


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(301)
        keys = {generate(tier, rng).dedup_key for _ in range(150)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        inl.TOPIC_INEQUALITIES_NUMBER_LINE_FOUNDATION,
        inl.TOPIC_INEQUALITIES_NUMBER_LINE_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Inequalities"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (
        inl.generate_modelled_example_inequalities_number_line_foundation,
        Tier.FOUNDATION,
        "inequalities_number_line_foundation",
    ),
    (
        inl.generate_modelled_example_inequalities_number_line_higher,
        Tier.HIGHER,
        "inequalities_number_line_higher",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        inl.TOPIC_INEQUALITIES_NUMBER_LINE_FOUNDATION,
        inl.TOPIC_INEQUALITIES_NUMBER_LINE_HIGHER,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(302)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            assert example.diagram is not None
