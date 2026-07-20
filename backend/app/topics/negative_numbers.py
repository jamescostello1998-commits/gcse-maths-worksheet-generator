import random

from app.core.models import ModelledExample, Question, Tier
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


def generate_modelled_example_negative_number_arithmetic(tier: Tier, rng: random.Random) -> ModelledExample:
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
        raise ValueError("modelled example negative_number_arithmetic verification failed")

    b_display = f"({b})" if b < 0 else str(b)

    if op == "+":
        teaching_steps = [
            f"Adding a number moves you along the number line: adding a positive number moves right, "
            f"adding a negative number moves left. So {a} {op} {b_display} means starting at {a} and "
            f"moving {abs(b)} places to the {'right' if b >= 0 else 'left'}.",
            f"Starting at {a} and moving {abs(b)} places {'right' if b >= 0 else 'left'} lands on {result}.",
            f"So {a} {op} {b_display} = {result}. Notice that adding a negative number has the same "
            "effect as subtracting the equivalent positive number would.",
        ]
    elif op == "-":
        teaching_steps = [
            f"Subtracting a number moves you along the number line in the OPPOSITE direction to adding "
            "it: subtracting a positive number moves left, but subtracting a negative number moves "
            "right, because two minus signs together make a plus.",
            f"So {a} {op} {b_display} means starting at {a} and moving {abs(b)} places to the "
            f"{'left' if b >= 0 else 'right'}.",
            f"Starting at {a} and moving {abs(b)} places {'left' if b >= 0 else 'right'} lands on {result}.",
            f"So {a} {op} {b_display} = {result}.",
        ]
    elif op == "×":
        same_sign = (a > 0) == (b > 0)
        teaching_steps = [
            "When multiplying two numbers, first multiply their sizes as normal (ignoring the signs), "
            "then work out the sign of the answer separately using the rule: same signs give a positive "
            "answer, different signs give a negative answer.",
            f"{a} and {b_display} have {'the same sign' if same_sign else 'different signs'}, so the "
            f"answer will be {'positive' if same_sign else 'negative'}.",
            f"Multiplying the sizes (ignoring signs): {abs(a)} × {abs(b)} = {abs(result)}.",
            f"Applying the sign rule gives {a} {op} {b_display} = {result}.",
        ]
    else:
        same_sign = (a > 0) == (b > 0)
        teaching_steps = [
            "Just like multiplying, dividing two numbers means dividing their sizes as normal and then "
            "applying the same sign rule: same signs give a positive answer, different signs give a "
            "negative answer.",
            f"{a} and {b_display} have {'the same sign' if same_sign else 'different signs'}, so the "
            f"answer will be {'positive' if same_sign else 'negative'}.",
            f"Dividing the sizes (ignoring signs): {abs(a)} ÷ {abs(b)} = {abs(result)}.",
            f"Applying the sign rule gives {a} {op} {b_display} = {result}.",
        ]

    worked_calculation = [f"{a} {op} {b_display}", f"= {result}"]
    return ModelledExample(
        topic_id="negative_numbers",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(result),
    )


TOPIC_NEGATIVE_NUMBERS = TopicDefinition(
    id="negative_numbers",
    display_name="Negative Number Arithmetic",
    description="Add, subtract, multiply, and divide with negative numbers.",
    generate=generate_negative_number_arithmetic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_negative_number_arithmetic,
)
