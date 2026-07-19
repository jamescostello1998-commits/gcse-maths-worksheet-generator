import random

import pytest

from app.core.errors import TopicNotFoundError, WorksheetGenerationError
from app.core.models import Question, Tier
from app.topics.base import TopicDefinition
from app.worksheet import builder


def test_happy_path_produces_20_distinct_questions():
    worksheet = builder.build_worksheet("linear_one_step", Tier.FOUNDATION, rng=random.Random(1))
    assert len(worksheet.questions) == 20
    assert len({q.dedup_key for q in worksheet.questions}) == 20
    assert worksheet.topic_id == "linear_one_step"
    assert worksheet.tier == Tier.FOUNDATION


def test_all_topics_produce_20_distinct_questions_at_their_fixed_tier():
    from app.core.registry import list_topics

    topics = list_topics()
    assert len(topics) == 89
    for topic in topics:
        tier = topic.fixed_tier or Tier.FOUNDATION
        worksheet = builder.build_worksheet(topic.id, tier, rng=random.Random(42))
        assert len(worksheet.questions) == 20, f"{topic.id}/{tier} failed to produce 20 questions"
        assert len({q.dedup_key for q in worksheet.questions}) == 20


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
