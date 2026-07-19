from app.core.errors import TopicNotFoundError
from app.topics import (
    angles,
    area_perimeter,
    expand_factorise,
    linear_equations,
    percentages,
    probability,
    pythagoras,
    ratio,
)
from app.topics.base import TopicDefinition

_TOPIC_LIST: list[TopicDefinition] = [
    linear_equations.TOPIC,
    expand_factorise.TOPIC,
    percentages.TOPIC,
    ratio.TOPIC,
    area_perimeter.TOPIC,
    angles.TOPIC,
    pythagoras.TOPIC,
    probability.TOPIC,
]

TOPICS: dict[str, TopicDefinition] = {t.id: t for t in _TOPIC_LIST}


def get_topic(topic_id: str) -> TopicDefinition:
    try:
        return TOPICS[topic_id]
    except KeyError:
        raise TopicNotFoundError(topic_id) from None


def list_topics() -> list[TopicDefinition]:
    return list(_TOPIC_LIST)
