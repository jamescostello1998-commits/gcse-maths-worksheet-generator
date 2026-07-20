import random

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Negative Numbers"

_NONZERO = [x for x in range(-12, 13) if x != 0]

_FLOAT_OPS = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "×": lambda x, y: x * y,
    "÷": lambda x, y: x / y,
}


def generate_negative_number_arithmetic(tier: Tier, rng: random.Random) -> Question:
    op = rng.choice(["+", "-", "×", "÷"])

    if op in ("+", "-"):
        a = rng.randint(-20, 20)
        b = rng.randint(-20, 20)
        result = a + b if op == "+" else a - b
    elif op == "×":
        a, b = rng.choice(_NONZERO), rng.choice(_NONZERO)
        result = a * b
    else:
        b = rng.choice(_NONZERO)
        result = rng.choice(_NONZERO)
        a = b * result

    # Independent check via plain float arithmetic (a different code path than
    # the integer operators used above).
    if abs(_FLOAT_OPS[op](a, b) - result) > 1e-9:
        raise ValueError("negative_number_arithmetic verification failed")

    b_display = f"({b})" if b < 0 else str(b)
    steps = [f"{a} {op} {b_display} = {result}"]
    return Question(
        topic_id="negative_numbers",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"negnum:{a}:{b}:{op}",
    )


TOPIC_NEGATIVE_NUMBERS = TopicDefinition(
    id="negative_numbers",
    display_name="Negative Number Arithmetic",
    description="Add, subtract, multiply, and divide with negative numbers.",
    generate=generate_negative_number_arithmetic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)
