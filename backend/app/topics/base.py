import random
from typing import Callable, NamedTuple

from app.core.models import Question, Tier

GenerateFn = Callable[[Tier, random.Random], Question]


class TopicDefinition(NamedTuple):
    id: str
    display_name: str
    description: str
    generate: GenerateFn
