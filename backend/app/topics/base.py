import random
from typing import Callable, NamedTuple, Optional

from app.core.models import ModelledExample, Question, Tier

GenerateFn = Callable[[Tier, random.Random], Question]
GenerateModelledExampleFn = Callable[[Tier, random.Random], ModelledExample]


class TopicDefinition(NamedTuple):
    id: str
    display_name: str
    description: str
    generate: GenerateFn
    section: str
    group: str
    fixed_tier: Optional[Tier] = None
    question_count: Optional[int] = None
    generate_modelled_example: Optional[GenerateModelledExampleFn] = None
