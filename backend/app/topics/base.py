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
    # Fixed reference lines (e.g. a set of formulae) shown in a boxed panel
    # at the very top of a topic's rendered PDF, before Q1 - for a topic
    # whose questions all rely on the same handful of formulae the student
    # needs to see every time, rather than repeating them per-question.
    preamble_lines: Optional[tuple[str, ...]] = None
