import random
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.units import display_qty

SECTION = "ratio_proportion"
GROUP = "Proportion"


def _format_money(value_in_pence: int) -> str:
    """Format an integer number of pence/cents as a 2dp amount string (no currency symbol)."""
    pounds, pence = divmod(value_in_pence, 100)
    return f"{pounds}.{pence:02d}"


# ---------------------------------------------------------------------------
# direct_proportion
# ---------------------------------------------------------------------------

_SHOPPING_ITEMS = ["pens", "notebooks", "pencils", "rulers", "exercise books"]
_INGREDIENTS = ["flour", "sugar", "rice", "butter", "oats"]


def _direct_shopping(x1: int, x2: int, rng: random.Random) -> dict:
    item = rng.choice(_SHOPPING_ITEMS)
    singular = item[:-1] if item.endswith("s") else item
    unit_value = rng.randint(10, 500)  # pence per item
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": f"shopping:{item}",
        "prompt": f"If {x1} {item} cost £{_format_money(y1)}, how much would {x2} {item} cost?",
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": f"the number of {item}",
        "unit_phrase": f"one {singular}",
        "amount_noun": "cost",
        "format_amount": lambda v: f"£{_format_money(v)}",
    }


def _direct_recipe(x1: int, x2: int, rng: random.Random) -> dict:
    ingredient = rng.choice(_INGREDIENTS)
    unit_value = rng.randint(20, 300)  # grams per person
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": f"recipe:{ingredient}",
        "prompt": (
            f"If a recipe for {x1} people uses {display_qty(y1, 'g')} of {ingredient}, how much "
            f"{ingredient} is needed for {x2} people?"
        ),
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": "the number of people",
        "unit_phrase": "one person's share",
        "amount_noun": f"amount of {ingredient} needed",
        "format_amount": lambda v: f"{v}g",
        "narrate_amount": lambda v: display_qty(v, "g"),
    }


def _direct_map(x1: int, x2: int, rng: random.Random) -> dict:
    unit_value = rng.randint(5, 80)  # km per cm
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": "map",
        "prompt": (
            f"If {x1} cm on a map represents {y1} km in real life, how many km does "
            f"{x2} cm represent?"
        ),
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": "the length on the map (in cm)",
        "unit_phrase": "1 cm on the map",
        "amount_noun": "real-life distance",
        "format_amount": lambda v: f"{v} km",
    }


def _direct_currency(x1: int, x2: int, rng: random.Random) -> dict:
    unit_value = rng.randint(100, 300)  # cents (dollars, in cents) per pound
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": "currency",
        "prompt": f"If £{x1} exchanges for ${_format_money(y1)}, how much is £{x2} worth in dollars ($)?",
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": "the amount exchanged (in £)",
        "unit_phrase": "£1",
        "amount_noun": "value in dollars ($)",
        "format_amount": lambda v: f"${_format_money(v)}",
    }


_DIRECT_TEMPLATES = [_direct_shopping, _direct_recipe, _direct_map, _direct_currency]


def _pick_direct_context(rng: random.Random) -> dict:
    x1 = rng.randint(2, 12)
    x2 = rng.randint(2, 20)
    while x2 == x1:
        x2 = rng.randint(2, 20)
    template = rng.choice(_DIRECT_TEMPLATES)
    return template(x1, x2, rng)


def generate_direct_proportion(tier: Tier, rng: random.Random) -> Question:
    ctx = _pick_direct_context(rng)
    x1, x2, y1, y2, unit_value = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"], ctx["unit_value"]
    format_amount = ctx["format_amount"]
    narrate_amount = ctx.get("narrate_amount", format_amount)

    # Independent verification via cross-multiplication (a different computation path
    # than the divide-then-multiply used to build the steps below).
    if Fraction(y2, x2) != Fraction(y1, x1):
        raise ValueError("direct_proportion verification failed")

    steps = []
    if narrate_amount(y1) != format_amount(y1):
        steps.append(f"{narrate_amount(y1)} = {format_amount(y1)}")
    steps.append(f"Unit value = {format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}")
    steps.append(f"Answer = {format_amount(unit_value)} × {x2} = {format_amount(y2)}")
    if narrate_amount(y2) != format_amount(y2):
        steps.append(f"{format_amount(y2)} = {narrate_amount(y2)}")

    return Question(
        topic_id="direct_proportion",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        solution_steps=tuple(steps),
        final_answer=narrate_amount(y2),
        dedup_key=f"direct:{ctx['name']}:{x1}:{x2}:{unit_value}",
    )


def generate_modelled_example_direct_proportion(tier: Tier, rng: random.Random) -> ModelledExample:
    ctx = _pick_direct_context(rng)
    x1, x2, y1, y2, unit_value = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"], ctx["unit_value"]
    format_amount = ctx["format_amount"]
    narrate_amount = ctx.get("narrate_amount", format_amount)

    # Independent verification via cross-multiplication (a different computation path
    # than the divide-then-multiply used to build the working below).
    if Fraction(y2, x2) != Fraction(y1, x1):
        raise ValueError("modelled example direct_proportion verification failed")

    teaching_steps = [
        f"This is direct proportion: as {ctx['quantity_phrase']} increases, the "
        f"{ctx['amount_noun']} increases in the same ratio, so the first job is to work out "
        f"what {ctx['unit_phrase']} is worth.",
    ]
    if narrate_amount(y1) != format_amount(y1):
        teaching_steps.append(
            f"The given amount, {narrate_amount(y1)}, is the same as {format_amount(y1)} - "
            "converting to that unit makes the division below straightforward."
        )
    teaching_steps.append(
        f"Divide the known {ctx['amount_noun']} by the known number to find that: "
        f"{format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}."
    )
    teaching_steps.append(
        f"Now scale that unit value up (or down) to the new number, {x2}, by multiplying: "
        f"{format_amount(unit_value)} × {x2} = {format_amount(y2)}."
    )
    teaching_steps.append(f"So the {ctx['amount_noun']} works out as {narrate_amount(y2)}.")

    worked_calculation = [ctx["prompt"]]
    if narrate_amount(y1) != format_amount(y1):
        worked_calculation.append(f"{narrate_amount(y1)} = {format_amount(y1)}")
    worked_calculation.append(f"{format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}")
    worked_calculation.append(f"{format_amount(unit_value)} × {x2} = {format_amount(y2)}")
    if narrate_amount(y2) != format_amount(y2):
        worked_calculation.append(f"{format_amount(y2)} = {narrate_amount(y2)}")

    return ModelledExample(
        topic_id="direct_proportion",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=narrate_amount(y2),
    )


# ---------------------------------------------------------------------------
# direct_proportion_noncalculator - a genuinely non-calculator-friendly
# sibling. generate_direct_proportion's unit rate is already an exact
# integer by construction, but x1/x2 are otherwise unrelated (2-12 vs
# 2-20), so the final scaling step is an arbitrary multiplication a student
# can't easily do in their head. Here x1 and x2 are always a small "clean"
# multiple of one another (double, triple, etc.) with a small unit value, so
# every step is a simple times-table fact - not just exact, but genuinely
# quick without a calculator.
# ---------------------------------------------------------------------------


def _direct_shopping_noncalc(x1: int, x2: int, rng: random.Random) -> dict:
    item = rng.choice(_SHOPPING_ITEMS)
    singular = item[:-1] if item.endswith("s") else item
    unit_value = rng.randint(2, 20)  # pence per item - small and mental-maths friendly
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": f"shopping_nc:{item}",
        "prompt": f"If {x1} {item} cost {y1}p, how much would {x2} {item} cost?",
        "x1": x1, "x2": x2, "y1": y1, "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": f"the number of {item}",
        "unit_phrase": f"one {singular}",
        "amount_noun": "cost",
        "format_amount": lambda v: f"{v}p",
    }


def _direct_recipe_noncalc(x1: int, x2: int, rng: random.Random) -> dict:
    ingredient = rng.choice(_INGREDIENTS)
    unit_value = rng.randint(2, 20)  # grams per person - small and mental-maths friendly
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": f"recipe_nc:{ingredient}",
        "prompt": (
            f"If a recipe for {x1} people uses {y1}g of {ingredient}, how much "
            f"{ingredient} is needed for {x2} people?"
        ),
        "x1": x1, "x2": x2, "y1": y1, "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": "the number of people",
        "unit_phrase": "one person's share",
        "amount_noun": f"amount of {ingredient} needed",
        "format_amount": lambda v: f"{v}g",
    }


def _direct_map_noncalc(x1: int, x2: int, rng: random.Random) -> dict:
    unit_value = rng.randint(2, 20)  # km per cm - small and mental-maths friendly
    y1, y2 = unit_value * x1, unit_value * x2
    return {
        "name": "map_nc",
        "prompt": (
            f"If {x1} cm on a map represents {y1} km in real life, how many km does "
            f"{x2} cm represent?"
        ),
        "x1": x1, "x2": x2, "y1": y1, "y2": y2,
        "unit_value": unit_value,
        "quantity_phrase": "the length on the map (in cm)",
        "unit_phrase": "1 cm on the map",
        "amount_noun": "real-life distance",
        "format_amount": lambda v: f"{v} km",
    }


_DIRECT_TEMPLATES_NONCALC = [_direct_shopping_noncalc, _direct_recipe_noncalc, _direct_map_noncalc]


def _pick_direct_noncalc_context(rng: random.Random) -> dict:
    x_small = rng.randint(2, 6)
    factor = rng.randint(2, 5)
    x_big = x_small * factor
    x1, x2 = (x_small, x_big) if rng.random() < 0.5 else (x_big, x_small)
    template = rng.choice(_DIRECT_TEMPLATES_NONCALC)
    return template(x1, x2, rng)


def generate_direct_proportion_noncalculator(tier: Tier, rng: random.Random) -> Question:
    ctx = _pick_direct_noncalc_context(rng)
    x1, x2, y1, y2, unit_value = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"], ctx["unit_value"]
    format_amount = ctx["format_amount"]

    if Fraction(y2, x2) != Fraction(y1, x1):
        raise ValueError("direct_proportion_noncalculator verification failed")

    steps = [
        f"Unit value = {format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}",
        f"Answer = {format_amount(unit_value)} × {x2} = {format_amount(y2)}",
    ]
    return Question(
        topic_id="direct_proportion_noncalculator",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        solution_steps=tuple(steps),
        final_answer=format_amount(y2),
        dedup_key=f"direct_nc:{ctx['name']}:{x1}:{x2}:{unit_value}",
    )


def generate_modelled_example_direct_proportion_noncalculator(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    ctx = _pick_direct_noncalc_context(rng)
    x1, x2, y1, y2, unit_value = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"], ctx["unit_value"]
    format_amount = ctx["format_amount"]

    if Fraction(y2, x2) != Fraction(y1, x1):
        raise ValueError("modelled example direct_proportion_noncalculator verification failed")

    teaching_steps = [
        f"This is direct proportion: as {ctx['quantity_phrase']} increases, the "
        f"{ctx['amount_noun']} increases in the same ratio, so the first job is to work out "
        f"what {ctx['unit_phrase']} is worth.",
        f"Divide the known {ctx['amount_noun']} by the known number to find that: "
        f"{format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}.",
        f"Now scale that unit value up (or down) to the new number, {x2}, by multiplying: "
        f"{format_amount(unit_value)} × {x2} = {format_amount(y2)}. Every number here was chosen "
        "to keep this a simple times-table fact, not a calculator calculation.",
        f"So the {ctx['amount_noun']} works out as {format_amount(y2)}.",
    ]
    worked_calculation = [
        ctx["prompt"],
        f"{format_amount(y1)} ÷ {x1} = {format_amount(unit_value)}",
        f"{format_amount(unit_value)} × {x2} = {format_amount(y2)}",
    ]
    return ModelledExample(
        topic_id="direct_proportion_noncalculator",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=format_amount(y2),
    )


# ---------------------------------------------------------------------------
# inverse_proportion
# ---------------------------------------------------------------------------

_INVERSE_CONTEXTS = [
    ("workers", "build a wall"),
    ("pipes", "fill a tank"),
    ("machines", "complete a production run"),
    ("painters", "paint a fence"),
]


def _pick_inverse_context(rng: random.Random) -> dict:
    x1 = rng.randint(2, 12)
    x2 = rng.randint(2, 12)
    while x2 == x1:
        x2 = rng.randint(2, 12)
    m = rng.randint(1, 8)
    # Constructed so that x1*y1 == x2*y2 == m*x1*x2 exactly, by construction.
    y1 = m * x2
    y2 = m * x1
    noun_plural, task = rng.choice(_INVERSE_CONTEXTS)
    prompt = (
        f"It takes {x1} {noun_plural} {y1} hours to {task}. Working at the same rate, "
        f"how long would it take {x2} {noun_plural}?"
    )
    return {
        "x1": x1,
        "x2": x2,
        "y1": y1,
        "y2": y2,
        "m": m,
        "noun_plural": noun_plural,
        "task": task,
        "prompt": prompt,
    }


def generate_inverse_proportion(tier: Tier, rng: random.Random) -> Question:
    ctx = _pick_inverse_context(rng)
    x1, x2, y1, y2 = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"]

    # Independent verification via the constant-product property, checked by direct
    # multiplication of both pairs (a different path than the division used to build y2).
    if x1 * y1 != x2 * y2:
        raise ValueError("inverse_proportion verification failed")

    k = x1 * y1
    steps = [
        f"Constant = {x1} × {y1} = {k}",
        f"Time for {x2} {ctx['noun_plural']} = {k} ÷ {x2} = {y2}",
    ]
    return Question(
        topic_id="inverse_proportion",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        solution_steps=tuple(steps),
        final_answer=f"{y2} hours",
        dedup_key=f"inverse:{ctx['noun_plural']}:{x1}:{x2}:{ctx['m']}",
    )


def generate_modelled_example_inverse_proportion(tier: Tier, rng: random.Random) -> ModelledExample:
    ctx = _pick_inverse_context(rng)
    x1, x2, y1, y2 = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"]

    # Independent verification via the constant-product property, checked by direct
    # multiplication of both pairs (a different path than the division used to build y2).
    if x1 * y1 != x2 * y2:
        raise ValueError("modelled example inverse_proportion verification failed")

    k = x1 * y1
    teaching_steps = [
        f"This is inverse proportion: as the number of {ctx['noun_plural']} increases, the "
        "time taken decreases (and vice versa) — because it's the PRODUCT of the two "
        "quantities that stays constant, not their ratio.",
        f"Find that constant product using the pair we know: {x1} × {y1} = {k}.",
        f"To find the time for {x2} {ctx['noun_plural']}, divide the constant by the new "
        f"number instead of multiplying: {k} ÷ {x2} = {y2}.",
        f"So it would take {y2} hours.",
    ]
    worked_calculation = [
        ctx["prompt"],
        f"{x1} × {y1} = {k}",
        f"{k} ÷ {x2} = {y2}",
    ]
    return ModelledExample(
        topic_id="inverse_proportion",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{y2} hours",
    )


# ---------------------------------------------------------------------------
# inverse_proportion_noncalculator - a genuinely non-calculator-friendly
# sibling. generate_inverse_proportion's constant k = x1*y1 can already be
# computed exactly, but its own division step (k ÷ x2) is otherwise an
# arbitrary computation - here x1 and x2 are always small and k is kept
# small too, so k ÷ x2 is a simple times-table fact rather than a
# calculator-scale division.
# ---------------------------------------------------------------------------


def _pick_inverse_noncalc_context(rng: random.Random) -> dict:
    x1 = rng.randint(2, 6)
    x2 = rng.randint(2, 6)
    while x2 == x1:
        x2 = rng.randint(2, 6)
    m = rng.randint(1, 4)
    y1 = m * x2
    y2 = m * x1
    noun_plural, task = rng.choice(_INVERSE_CONTEXTS)
    prompt = (
        f"It takes {x1} {noun_plural} {y1} hours to {task}. Working at the same rate, "
        f"how long would it take {x2} {noun_plural}?"
    )
    return {
        "x1": x1, "x2": x2, "y1": y1, "y2": y2, "m": m,
        "noun_plural": noun_plural, "task": task, "prompt": prompt,
    }


def generate_inverse_proportion_noncalculator(tier: Tier, rng: random.Random) -> Question:
    ctx = _pick_inverse_noncalc_context(rng)
    x1, x2, y1, y2 = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"]

    if x1 * y1 != x2 * y2:
        raise ValueError("inverse_proportion_noncalculator verification failed")

    k = x1 * y1
    steps = [
        f"Constant = {x1} × {y1} = {k}",
        f"Time for {x2} {ctx['noun_plural']} = {k} ÷ {x2} = {y2}",
    ]
    return Question(
        topic_id="inverse_proportion_noncalculator",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        solution_steps=tuple(steps),
        final_answer=f"{y2} hours",
        dedup_key=f"inverse_nc:{ctx['noun_plural']}:{x1}:{x2}:{ctx['m']}",
    )


def generate_modelled_example_inverse_proportion_noncalculator(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    ctx = _pick_inverse_noncalc_context(rng)
    x1, x2, y1, y2 = ctx["x1"], ctx["x2"], ctx["y1"], ctx["y2"]

    if x1 * y1 != x2 * y2:
        raise ValueError("modelled example inverse_proportion_noncalculator verification failed")

    k = x1 * y1
    teaching_steps = [
        f"This is inverse proportion: as the number of {ctx['noun_plural']} increases, the "
        "time taken decreases (and vice versa) — because it's the PRODUCT of the two "
        "quantities that stays constant, not their ratio.",
        f"Find that constant product using the pair we know: {x1} × {y1} = {k}.",
        f"To find the time for {x2} {ctx['noun_plural']}, divide the constant by the new "
        f"number instead of multiplying: {k} ÷ {x2} = {y2}. Every number here is small "
        "enough to work out without a calculator.",
        f"So it would take {y2} hours.",
    ]
    worked_calculation = [
        ctx["prompt"],
        f"{x1} × {y1} = {k}",
        f"{k} ÷ {x2} = {y2}",
    ]
    return ModelledExample(
        topic_id="inverse_proportion_noncalculator",
        tier=Tier.FOUNDATION,
        prompt=ctx["prompt"],
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{y2} hours",
    )


# ---------------------------------------------------------------------------
# algebraic_direct_proportion
# ---------------------------------------------------------------------------


def _pick_algebraic_direct_values(rng: random.Random) -> dict:
    n = rng.choice([2, 3])
    x1 = rng.randint(2, 9)
    x2 = rng.randint(2, 9)
    while x2 == x1:
        x2 = rng.randint(2, 9)
    k = rng.randint(2, 12)
    y1 = k * (x1 ** n)
    y2 = k * (x2 ** n)
    return {"n": n, "x1": x1, "x2": x2, "k": k, "y1": y1, "y2": y2}


def generate_algebraic_direct_proportion(tier: Tier, rng: random.Random) -> Question:
    v = _pick_algebraic_direct_values(rng)
    n, x1, x2, k, y1, y2 = v["n"], v["x1"], v["x2"], v["k"], v["y1"], v["y2"]

    # Independent verification: recompute the constant from BOTH pairs via Fraction and
    # confirm they agree (a different check than the single division used to build y2).
    if Fraction(y2, x2 ** n) != Fraction(y1, x1 ** n):
        raise ValueError("algebraic_direct_proportion verification failed")

    prompt = (
        f"y is directly proportional to x^{n}. When x = {x1}, y = {y1}. "
        f"Find the value of y when x = {x2}."
    )
    steps = [
        f"y = kx^{n}",
        f"{y1} = k × {x1}^{n} = k × {x1 ** n}",
        f"k = {y1} ÷ {x1 ** n} = {k}",
        f"y = {k} × {x2}^{n} = {k} × {x2 ** n} = {y2}",
    ]
    return Question(
        topic_id="algebraic_direct_proportion",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(y2),
        dedup_key=f"alg_direct:{n}:{x1}:{x2}:{k}",
    )


def generate_modelled_example_algebraic_direct_proportion(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    v = _pick_algebraic_direct_values(rng)
    n, x1, x2, k, y1, y2 = v["n"], v["x1"], v["x2"], v["k"], v["y1"], v["y2"]

    # Independent verification: recompute the constant from BOTH pairs via Fraction and
    # confirm they agree (a different check than the single division used to build y2).
    if Fraction(y2, x2 ** n) != Fraction(y1, x1 ** n):
        raise ValueError("modelled example algebraic_direct_proportion verification failed")

    prompt = (
        f"y is directly proportional to x^{n}. When x = {x1}, y = {y1}. "
        f"Find the value of y when x = {x2}."
    )
    teaching_steps = [
        f"'y is directly proportional to x^{n}' means y = k × x^{n} for some fixed constant "
        "k — whatever the actual relationship is, our first job is always to pin down k "
        "using the pair of values we're already given.",
        f"Substitute x = {x1}, y = {y1} into y = kx^{n}: {y1} = k × {x1}^{n} = k × {x1 ** n}. "
        f"Dividing both sides by {x1 ** n} gives k = {y1} ÷ {x1 ** n} = {k}.",
        f"Now that we know k = {k}, the full relationship is y = {k}x^{n}. Substitute the new "
        f"value x = {x2}: y = {k} × {x2}^{n} = {k} × {x2 ** n} = {y2}.",
        f"So when x = {x2}, y = {y2}.",
    ]
    worked_calculation = [
        f"y proportional to x^{n}; x = {x1}, y = {y1}; find y when x = {x2}",
        f"k = {y1} ÷ {x1}^{n} = {k}",
        f"y = {k} × {x2}^{n} = {y2}",
    ]
    return ModelledExample(
        topic_id="algebraic_direct_proportion",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(y2),
    )


# ---------------------------------------------------------------------------
# algebraic_inverse_proportion
# ---------------------------------------------------------------------------


def _pow_expr(base: str, n: int) -> str:
    """`base^n`, or bare `base` when n == 1 - an exponent of 1 is invisible
    in real notation, so printing "x^1" literally (the unconditional
    f"x^{n}" this replaces) was a genuine bug, not a stylistic choice."""
    return base if n == 1 else f"{base}^{n}"


def _pick_algebraic_inverse_values(rng: random.Random) -> dict:
    n = rng.choice([1, 2, 3])
    x1 = rng.randint(2, 6)
    x2 = rng.randint(2, 6)
    while x2 == x1:
        x2 = rng.randint(2, 6)
    m = rng.randint(1, 6)
    # Constructed so that y1*x1^n == y2*x2^n == m*x1^n*x2^n exactly, by construction.
    y1 = m * (x2 ** n)
    y2 = m * (x1 ** n)
    k = y1 * (x1 ** n)
    return {"n": n, "x1": x1, "x2": x2, "y1": y1, "y2": y2, "k": k}


def generate_algebraic_inverse_proportion(tier: Tier, rng: random.Random) -> Question:
    v = _pick_algebraic_inverse_values(rng)
    n, x1, x2, y1, y2, k = v["n"], v["x1"], v["x2"], v["y1"], v["y2"], v["k"]

    # Independent verification via the constant-product property, checked across both
    # pairs (a different path than the division used to build y2 above).
    if y1 * (x1 ** n) != y2 * (x2 ** n):
        raise ValueError("algebraic_inverse_proportion verification failed")

    x_n, x1_n, x2_n = _pow_expr("x", n), _pow_expr(str(x1), n), _pow_expr(str(x2), n)
    prompt = (
        f"y is inversely proportional to {x_n}. When x = {x1}, y = {y1}. "
        f"Find the value of y when x = {x2}."
    )
    steps = [
        f"y = k ÷ {x_n}",
        f"k = y × {x_n} = {y1} × {x1_n} = {y1} × {x1 ** n} = {k}",
        f"y = k ÷ {x_n} = {k} ÷ {x2_n} = {k} ÷ {x2 ** n} = {y2}",
    ]
    return Question(
        topic_id="algebraic_inverse_proportion",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(y2),
        dedup_key=f"alg_inverse:{n}:{x1}:{x2}:{y1}:{y2}",
    )


def generate_modelled_example_algebraic_inverse_proportion(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    v = _pick_algebraic_inverse_values(rng)
    n, x1, x2, y1, y2, k = v["n"], v["x1"], v["x2"], v["y1"], v["y2"], v["k"]

    # Independent verification via the constant-product property, checked across both
    # pairs (a different path than the division used to build y2 above).
    if y1 * (x1 ** n) != y2 * (x2 ** n):
        raise ValueError("modelled example algebraic_inverse_proportion verification failed")

    x_n, x1_n, x2_n = _pow_expr("x", n), _pow_expr(str(x1), n), _pow_expr(str(x2), n)
    prompt = (
        f"y is inversely proportional to {x_n}. When x = {x1}, y = {y1}. "
        f"Find the value of y when x = {x2}."
    )
    teaching_steps = [
        f"'y is inversely proportional to {x_n}' means y = k ÷ {x_n} for some fixed constant "
        f"k, so as {x_n} gets bigger, y gets smaller (and vice versa) — first we pin down k "
        "using the pair of values we're already given.",
        f"Rearranging y = k ÷ {x_n} gives k = y × {x_n}. Substitute x = {x1}, y = {y1}: "
        f"k = {y1} × {x1_n} = {y1} × {x1 ** n} = {k}.",
        f"Now that we know k = {k}, use it with the new x-value: "
        f"y = k ÷ {x_n} = {k} ÷ {x2_n} = {k} ÷ {x2 ** n} = {y2}.",
        f"So when x = {x2}, y = {y2}.",
    ]
    worked_calculation = [
        f"y inversely proportional to {x_n}; x = {x1}, y = {y1}; find y when x = {x2}",
        f"k = {y1} × {x1_n} = {k}",
        f"y = {k} ÷ {x2_n} = {y2}",
    ]
    return ModelledExample(
        topic_id="algebraic_inverse_proportion",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(y2),
    )


TOPIC_DIRECT_PROPORTION = TopicDefinition(
    id="direct_proportion",
    display_name="Direct Proportion",
    description="Use the unitary method to scale a directly proportional quantity up or down.",
    generate=generate_direct_proportion,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_direct_proportion,
)

TOPIC_INVERSE_PROPORTION = TopicDefinition(
    id="inverse_proportion",
    display_name="Inverse Proportion",
    description="Use the constant-product property to solve an inverse proportion word problem.",
    generate=generate_inverse_proportion,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_inverse_proportion,
)

TOPIC_DIRECT_PROPORTION_NONCALCULATOR = TopicDefinition(
    id="direct_proportion_noncalculator",
    display_name="Direct Proportion (Non-Calculator)",
    description=(
        "Use the unitary method to scale a directly proportional quantity, using small "
        "numbers chosen to keep every step a simple times-table fact."
    ),
    generate=generate_direct_proportion_noncalculator,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_direct_proportion_noncalculator,
)

TOPIC_INVERSE_PROPORTION_NONCALCULATOR = TopicDefinition(
    id="inverse_proportion_noncalculator",
    display_name="Inverse Proportion (Non-Calculator)",
    description=(
        "Use the constant-product property to solve an inverse proportion word problem, "
        "using small numbers chosen to keep every step a simple times-table fact."
    ),
    generate=generate_inverse_proportion_noncalculator,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_inverse_proportion_noncalculator,
)

TOPIC_ALGEBRAIC_DIRECT_PROPORTION = TopicDefinition(
    id="algebraic_direct_proportion",
    display_name="Direct Proportion with Powers",
    description=(
        "Find the constant of proportionality when y is directly proportional to a power of x."
    ),
    generate=generate_algebraic_direct_proportion,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_direct_proportion,
)

TOPIC_ALGEBRAIC_INVERSE_PROPORTION = TopicDefinition(
    id="algebraic_inverse_proportion",
    display_name="Inverse Proportion with Powers",
    description=(
        "Find the constant of proportionality when y is inversely proportional to a power of x."
    ),
    generate=generate_algebraic_inverse_proportion,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_inverse_proportion,
)
