import random

import sympy as sp

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition
from app.topics.number_format import fmt_money, to_fraction

SECTION = "ratio_proportion"
GROUP = "Percentages"

FOUNDATION_PERCENTS = ["10", "20", "25", "50"]
HIGHER_PERCENTS = ["12", "15", "17.5", "24", "30", "35", "42.5", "60"]


def _multiplier(percent: sp.Rational, increase: bool) -> sp.Rational:
    return sp.Integer(1) + percent / 100 if increase else sp.Integer(1) - percent / 100


def generate_of_amount(tier: Tier, rng: random.Random) -> Question:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    amount = rng.randrange(20, 501, 20)
    value = percent / 100 * amount

    # Independent verification via Python's Fraction (separate implementation path).
    frac_check = (to_fraction(percent) / 100) * amount
    if frac_check != to_fraction(value):
        raise ValueError("Percentage-of-amount verification failed")

    steps = [
        f"Convert {percent}% to a fraction: {percent}/100",
        f"Multiply: {percent}/100 × {amount} = {fmt_money(value)}",
    ]
    return Question(
        topic_id="percentage_of_amount",
        tier=Tier.FOUNDATION,
        prompt=f"Find {percent}% of {amount}.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(value),
        dedup_key=f"of_amount:{percent}:{amount}",
    )


def generate_change(tier: Tier, rng: random.Random) -> Question:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    amount = rng.randrange(20, 501, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = amount * multiplier

    verb = "Increase" if increase else "Decrease"
    steps = [
        f"Convert {percent}% to a multiplier: {fmt_money(multiplier)}",
        f"Multiply: {amount} × {fmt_money(multiplier)} = {fmt_money(result)}",
    ]
    return Question(
        topic_id="percentage_change",
        tier=Tier.FOUNDATION,
        prompt=f"{verb} {amount} by {percent}%.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(result),
        dedup_key=f"change:{percent}:{amount}:{increase}",
    )


def generate_reverse(tier: Tier, rng: random.Random) -> Question:
    percent = sp.Rational(rng.choice(HIGHER_PERCENTS))
    original = rng.randrange(20, 401, 4)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = original * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    recovered = to_fraction(result) / to_fraction(multiplier)
    if recovered != to_fraction(sp.Integer(original)):
        raise ValueError("Reverse-percentage verification failed")

    verb = "increase" if increase else "decrease"
    steps = [
        f"Convert {percent}% to a multiplier: {fmt_money(multiplier)} (original × multiplier = new value)",
        f"Divide the new value by the multiplier: {fmt_money(result)} ÷ {fmt_money(multiplier)} = {fmt_money(original)}",
    ]
    return Question(
        topic_id="reverse_percentage",
        tier=Tier.HIGHER,
        prompt=f"After a {percent}% {verb}, an item costs £{fmt_money(result)}. Find the original price.",
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(original)}",
        dedup_key=f"reverse:{percent}:{original}:{increase}",
    )


def generate_compound(tier: Tier, rng: random.Random) -> Question:
    original = rng.randrange(20, 401, 4)
    percent1 = sp.Rational(rng.choice(HIGHER_PERCENTS))
    percent2 = sp.Rational(rng.choice(HIGHER_PERCENTS))
    increase1 = rng.choice([True, False])
    increase2 = rng.choice([True, False])
    mult1 = _multiplier(percent1, increase1)
    mult2 = _multiplier(percent2, increase2)
    intermediate = original * mult1
    final = intermediate * mult2

    expected = to_fraction(sp.Integer(original)) * to_fraction(mult1) * to_fraction(mult2)
    if expected != to_fraction(final):
        raise ValueError("Compound-percentage verification failed")

    verb1 = "increases" if increase1 else "decreases"
    verb2 = "increases" if increase2 else "decreases"
    steps = [
        f"After the first change: {original} × {fmt_money(mult1)} = {fmt_money(intermediate)}",
        f"After the second change: {fmt_money(intermediate)} × {fmt_money(mult2)} = {fmt_money(final)}",
    ]
    return Question(
        topic_id="compound_percentage",
        tier=Tier.HIGHER,
        prompt=(
            f"A price of £{original} {verb1} by {percent1}%, then {verb2} by {percent2}%. "
            "Find the final price."
        ),
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(final)}",
        dedup_key=f"compound:{original}:{percent1}:{increase1}:{percent2}:{increase2}",
    )


TOPIC_OF_AMOUNT = TopicDefinition(
    id="percentage_of_amount",
    display_name="Percentage of an Amount",
    description="Find a percentage of a given amount.",
    generate=generate_of_amount,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_CHANGE = TopicDefinition(
    id="percentage_change",
    display_name="Percentage Change",
    description="Increase or decrease an amount by a percentage.",
    generate=generate_change,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_REVERSE = TopicDefinition(
    id="reverse_percentage",
    display_name="Reverse Percentage",
    description="Find the original amount given a value after a percentage change.",
    generate=generate_reverse,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_COMPOUND = TopicDefinition(
    id="compound_percentage",
    display_name="Compound Percentage Change",
    description="Apply two successive percentage changes to an amount.",
    generate=generate_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
