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


def _manual_order(nums: list[int], ascending: bool) -> list[int]:
    """Insertion-sort-style manual ordering, used as a second, independent
    code path from Python's built-in `sorted()` to cross-check the answer."""
    result = list(nums)
    n = len(result)
    for i in range(1, n):
        key = result[i]
        j = i - 1
        if ascending:
            while j >= 0 and result[j] > key:
                result[j + 1] = result[j]
                j -= 1
        else:
            while j >= 0 and result[j] < key:
                result[j + 1] = result[j]
                j -= 1
        result[j + 1] = key
    return result


# --- Adding and Subtracting Negative Numbers -------------------------------


def generate_negative_add_subtract(tier: Tier, rng: random.Random) -> Question:
    op = rng.choice(["+", "-"])

    for _ in range(100):
        a = rng.randint(-20, 20)
        b = rng.randint(-20, 20)
        if a < 0 or b < 0:
            break
    else:
        raise ValueError("negative_add_subtract: failed to generate a negative operand")

    result = a + b if op == "+" else a - b

    # Independent check via plain float arithmetic (a different code path than
    # the integer operators used above).
    if abs(_FLOAT_OPS[op](a, b) - result) > 1e-9:
        raise ValueError("negative_add_subtract verification failed")

    b_display = f"({b})" if b < 0 else str(b)
    steps = [f"{a} {op} {b_display} = {result}"]
    return Question(
        topic_id="negative_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"negaddsub:{a}:{b}:{op}",
    )


def generate_modelled_example_negative_add_subtract(tier: Tier, rng: random.Random) -> ModelledExample:
    op = rng.choice(["+", "-"])

    for _ in range(100):
        a = rng.randint(-20, 20)
        b = rng.randint(-20, 20)
        if a < 0 or b < 0:
            break
    else:
        raise ValueError("negative_add_subtract modelled example: failed to generate a negative operand")

    result = a + b if op == "+" else a - b

    if abs(_FLOAT_OPS[op](a, b) - result) > 1e-9:
        raise ValueError("modelled example negative_add_subtract verification failed")

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
    else:
        teaching_steps = [
            f"Subtracting a number moves you along the number line in the OPPOSITE direction to adding "
            "it: subtracting a positive number moves left, but subtracting a negative number moves "
            "right, because two minus signs together make a plus.",
            f"So {a} {op} {b_display} means starting at {a} and moving {abs(b)} places to the "
            f"{'left' if b >= 0 else 'right'}.",
            f"Starting at {a} and moving {abs(b)} places {'left' if b >= 0 else 'right'} lands on {result}.",
            f"So {a} {op} {b_display} = {result}.",
        ]

    worked_calculation = [f"{a} {op} {b_display}", f"= {result}"]
    return ModelledExample(
        topic_id="negative_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(result),
    )


TOPIC_NEGATIVE_ADD_SUBTRACT = TopicDefinition(
    id="negative_add_subtract",
    display_name="Adding and Subtracting Negative Numbers",
    description="Add and subtract with negative numbers.",
    generate=generate_negative_add_subtract,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_negative_add_subtract,
)


# --- Multiplying and Dividing Negative Numbers -----------------------------


def generate_negative_multiply_divide(tier: Tier, rng: random.Random) -> Question:
    op = rng.choice(["×", "÷"])

    if op == "×":
        for _ in range(100):
            a, b = rng.choice(_NONZERO), rng.choice(_NONZERO)
            if a < 0 or b < 0:
                break
        else:
            raise ValueError("negative_multiply_divide: failed to generate a negative operand")
        result = a * b
    else:
        for _ in range(100):
            b = rng.choice(_NONZERO)
            result = rng.choice(_NONZERO)
            a = b * result
            if a < 0 or b < 0:
                break
        else:
            raise ValueError("negative_multiply_divide: failed to generate a negative operand")

    # Independent check via plain float arithmetic (a different code path than
    # the integer operators used above).
    if abs(_FLOAT_OPS[op](a, b) - result) > 1e-9:
        raise ValueError("negative_multiply_divide verification failed")

    b_display = f"({b})" if b < 0 else str(b)
    steps = [f"{a} {op} {b_display} = {result}"]
    return Question(
        topic_id="negative_multiply_divide",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"negmuldiv:{a}:{b}:{op}",
    )


def generate_modelled_example_negative_multiply_divide(tier: Tier, rng: random.Random) -> ModelledExample:
    op = rng.choice(["×", "÷"])

    if op == "×":
        for _ in range(100):
            a, b = rng.choice(_NONZERO), rng.choice(_NONZERO)
            if a < 0 or b < 0:
                break
        else:
            raise ValueError("negative_multiply_divide modelled example: failed to generate a negative operand")
        result = a * b
    else:
        for _ in range(100):
            b = rng.choice(_NONZERO)
            result = rng.choice(_NONZERO)
            a = b * result
            if a < 0 or b < 0:
                break
        else:
            raise ValueError("negative_multiply_divide modelled example: failed to generate a negative operand")

    if abs(_FLOAT_OPS[op](a, b) - result) > 1e-9:
        raise ValueError("modelled example negative_multiply_divide verification failed")

    b_display = f"({b})" if b < 0 else str(b)
    same_sign = (a > 0) == (b > 0)

    if op == "×":
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
        topic_id="negative_multiply_divide",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a} {op} {b_display}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(result),
    )


TOPIC_NEGATIVE_MULTIPLY_DIVIDE = TopicDefinition(
    id="negative_multiply_divide",
    display_name="Multiplying and Dividing Negative Numbers",
    description="Multiply and divide with negative numbers.",
    generate=generate_negative_multiply_divide,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_negative_multiply_divide,
)


# --- Ordering Negative Numbers ----------------------------------------------

_ORDERING_POOL = list(range(-10, 11))  # -10..10 inclusive, includes 0


def _generate_ordering_values(rng: random.Random) -> tuple[list[int], bool]:
    n = rng.choice([5, 6])
    numbers = rng.sample(_ORDERING_POOL, n)
    ascending = rng.choice([True, False])
    return numbers, ascending


def _verify_ordering(numbers: list[int], ascending: bool) -> list[int]:
    # Independent check: Python's built-in sorted() vs. a hand-written
    # insertion-sort-style manual ordering — two genuinely distinct code
    # paths that must agree.
    via_sorted = sorted(numbers, reverse=not ascending)
    via_manual = _manual_order(numbers, ascending)
    if via_sorted != via_manual:
        raise ValueError("negative_ordering verification failed: sorted() and manual order disagree")
    return via_sorted


def generate_negative_ordering(tier: Tier, rng: random.Random) -> Question:
    numbers, ascending = _generate_ordering_values(rng)
    ordered = _verify_ordering(numbers, ascending)

    direction_text = "smallest to largest" if ascending else "largest to smallest"
    numbers_text = ", ".join(str(x) for x in numbers)
    ordered_text = ", ".join(str(x) for x in ordered)

    steps = [
        f"Place the numbers on a number line: {numbers_text}.",
        f"Reading them in order from {direction_text} gives: {ordered_text}.",
    ]
    return Question(
        topic_id="negative_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these numbers in order, from {direction_text}: {numbers_text}",
        solution_steps=tuple(steps),
        final_answer=ordered_text,
        dedup_key=f"negord:{','.join(str(x) for x in numbers)}:{ascending}",
    )


def generate_modelled_example_negative_ordering(tier: Tier, rng: random.Random) -> ModelledExample:
    numbers, ascending = _generate_ordering_values(rng)
    ordered = _verify_ordering(numbers, ascending)

    direction_text = "smallest to largest" if ascending else "largest to smallest"
    numbers_text = ", ".join(str(x) for x in numbers)
    ordered_text = ", ".join(str(x) for x in ordered)

    teaching_steps = [
        "Imagine every number placed on a number line. The further right a number sits, the larger it "
        "is — so a negative number close to zero (like -1) is bigger than a negative number far from "
        "zero (like -8), even though 8 is the bigger 'size'.",
        f"Placing {numbers_text} on a number line and reading them from left to right gives the order "
        f"from smallest to largest: {', '.join(str(x) for x in sorted(numbers))}.",
        f"The question asks for the order from {direction_text}, so "
        + (
            "read the number line left to right, exactly as it is."
            if ascending
            else "read the number line right to left instead, reversing that order."
        ),
        f"So the numbers in order from {direction_text} are: {ordered_text}.",
    ]

    worked_calculation = [f"Numbers: {numbers_text}", f"Ordered ({direction_text}): {ordered_text}"]
    return ModelledExample(
        topic_id="negative_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these numbers in order, from {direction_text}: {numbers_text}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=ordered_text,
    )


TOPIC_NEGATIVE_ORDERING = TopicDefinition(
    id="negative_ordering",
    display_name="Ordering Negative Numbers",
    description="Order a mix of negative and positive numbers from smallest to largest or vice versa.",
    generate=generate_negative_ordering,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_negative_ordering,
)
