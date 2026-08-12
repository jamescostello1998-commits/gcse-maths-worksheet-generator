import random

from app.core.models import Tier
from app.topics import circle_parts

TRIALS = 300

_VALID = {name for name, _ in circle_parts._PARTS}


def test_generator_produces_valid_questions_with_diagram():
    rng = random.Random(530)
    for _ in range(TRIALS):
        q = circle_parts.generate_circle_parts(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.topic_id == "circle_parts_F"
        assert q.final_answer in _VALID
        assert q.diagram is not None and q.diagram.kind == "circle_part"
        # The drawn part always matches the expected answer.
        assert q.diagram.params["part"] == q.final_answer


def test_every_part_can_be_produced():
    rng = random.Random(531)
    seen = {circle_parts.generate_circle_parts(Tier.FOUNDATION, rng).final_answer for _ in range(400)}
    assert seen == _VALID


def test_question_count_matches_the_bank_size():
    assert circle_parts.TOPIC_CIRCLE_PARTS.question_count == len(circle_parts._PARTS)
    assert len(circle_parts._PARTS) >= 8


def test_modelled_example_is_verified():
    rng = random.Random(532)
    for _ in range(TRIALS):
        ex = circle_parts.generate_modelled_example_circle_parts(Tier.FOUNDATION, rng)
        assert ex.topic_id == "circle_parts_F"
        assert ex.final_answer in _VALID
        assert ex.diagram is not None and ex.diagram.params["part"] == ex.final_answer
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3


def test_topic_metadata():
    t = circle_parts.TOPIC_CIRCLE_PARTS
    assert t.section == "geometry"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None
