import random

import pytest

from app.core.errors import TopicNotFoundError, WorksheetGenerationError
from app.core.models import Question, Tier
from app.topics.base import TopicDefinition
from app.worksheet import builder


def test_happy_path_produces_20_distinct_questions():
    worksheet = builder.build_worksheet("linear_one_step_F", Tier.FOUNDATION, rng=random.Random(1))
    assert len(worksheet.questions) == 20
    assert len({q.dedup_key for q in worksheet.questions}) == 20
    assert worksheet.topic_id == "linear_one_step_F"
    assert worksheet.tier == Tier.FOUNDATION


def test_hoisted_instruction_topics_set_shared_instruction_and_item_text():
    # A topic in HOISTED_INSTRUCTIONS gets its repeated instruction lifted to
    # the worksheet level, with each question carrying just the bare item; the
    # full prompt is preserved and still begins with the instruction.
    from app.core.registry import get_topic

    for topic_id, instruction in builder.HOISTED_INSTRUCTIONS.items():
        topic = get_topic(topic_id)
        ws = builder.build_worksheet(topic_id, topic.fixed_tier, count=6, rng=random.Random(7))
        assert ws.shared_instruction == instruction, topic_id
        for q in ws.questions:
            assert q.shared_instruction == instruction, topic_id
            assert q.item_text, topic_id
            assert q.prompt.startswith(instruction), topic_id
            assert instruction not in q.item_text, topic_id


def test_non_hoisted_topic_has_no_shared_instruction():
    ws = builder.build_worksheet("linear_one_step_F", Tier.FOUNDATION, count=6, rng=random.Random(3))
    assert ws.shared_instruction is None
    assert all(q.item_text is None for q in ws.questions)


def test_all_topics_produce_their_full_distinct_question_count_at_their_fixed_tier():
    from app.core.registry import list_topics

    topics = list_topics()
    assert len(topics) == 313
    for topic in topics:
        tier = topic.fixed_tier or Tier.FOUNDATION
        count = topic.question_count or 20
        worksheet = builder.build_worksheet(topic.id, tier, count=count, rng=random.Random(42))
        assert len(worksheet.questions) == count, f"{topic.id}/{tier} failed to produce {count} questions"
        assert len({q.dedup_key for q in worksheet.questions}) == count


def test_unknown_topic_raises_topic_not_found():
    with pytest.raises(TopicNotFoundError):
        builder.build_worksheet("not_a_real_topic", Tier.FOUNDATION, rng=random.Random(1))


def test_exhaustion_raises_worksheet_generation_error(monkeypatch):
    call_count = {"n": 0}

    def limited_generate(tier, rng):
        call_count["n"] += 1
        key = call_count["n"] % 5  # only 5 distinct dedup_keys ever possible
        return Question(
            topic_id="fake",
            tier=tier,
            prompt="fake prompt",
            solution_steps=("step",),
            final_answer="1",
            dedup_key=str(key),
        )

    fake_topic = TopicDefinition(
        id="fake",
        display_name="Fake",
        description="",
        generate=limited_generate,
        section="algebra",
        group="Fake Group",
    )
    monkeypatch.setattr(builder, "get_topic", lambda topic_id: fake_topic)

    with pytest.raises(WorksheetGenerationError) as exc_info:
        builder.build_worksheet("fake", Tier.FOUNDATION, count=20, max_attempts=50, rng=random.Random(1))

    assert exc_info.value.produced == 5
    assert exc_info.value.attempts == 50
