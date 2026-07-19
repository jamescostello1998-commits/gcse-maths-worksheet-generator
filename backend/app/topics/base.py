import random
from typing import Callable, NamedTuple, Optional

from app.core.models import Question, Tier

GenerateFn = Callable[[Tier, random.Random], Question]


class TopicDefinition(NamedTuple):
    id: str
    display_name: str
    description: str
    generate: GenerateFn
    section: str
    group: str
    fixed_tier: Optional[Tier] = None
    question_count: Optional[int] = None
