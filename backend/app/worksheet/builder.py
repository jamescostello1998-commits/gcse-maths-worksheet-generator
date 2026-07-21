import random
from datetime import datetime, timezone

from app.core.errors import WorksheetGenerationError
from app.core.models import Question, Tier, Worksheet
from app.core.registry import get_topic

DEFAULT_COUNT = 20
DEFAULT_MAX_ATTEMPTS = 400
MIN_COUNT = 5
MAX_COUNT = 40


def build_worksheet(
    topic_id: str,
    tier: Tier,
    count: int = DEFAULT_COUNT,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    rng: random.Random | None = None,
) -> Worksheet:
    topic = get_topic(topic_id)
    rng = rng or random.Random()

    seen_keys: set[str] = set()
    questions: list[Question] = []
    attempts = 0

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        question = topic.generate(tier, rng)
        if question.dedup_key in seen_keys:
            continue
        seen_keys.add(question.dedup_key)
        questions.append(question)

    if len(questions) < count:
        raise WorksheetGenerationError(
            topic_id=topic_id,
            tier=tier.value,
            attempts=attempts,
            produced=len(questions),
        )

    return Worksheet(
        topic_id=topic.id,
        topic_name=topic.display_name,
        tier=tier,
        questions=tuple(questions),
        generated_at=datetime.now(timezone.utc),
    )
