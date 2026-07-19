import random
from fractions import Fraction

import sympy as sp

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

TOPIC_ID = "percentages"

FOUNDATION_PERCENTS = ["10", "20", "25", "50"]
HIGHER_PERCENTS = ["12", "15", "17.5", "24", "30", "35", "42.5", "60"]


def _to_fraction(value: sp.Rational) -> Fraction:
    r = sp.Rational(value)
    return Fraction(int(r.p), int(r.q))


def fmt_money(value) -> str:
    r = sp.Rational(value)
    if r.is_Integer:
        return str(int(r))
    denom = int(sp.fraction(r)[1])
    while denom % 2 == 0:
        denom //= 2
    while denom % 5 == 0:
        denom //= 5
    if denom == 1:
        return f"{float(r):.2f}"
    return f"{r.p}/{r.q}"


def _multiplier(percent: sp.Rational, increase: bool) -> sp.Rational:
    return sp.Integer(1) + percent / 100 if increase else sp.Integer(1) - percent / 100


def _generate_of_amount(rng: random.Random):
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    amount = rng.randrange(20, 501, 20)
    value = percent / 100 * amount

    # Independent verification via Python's Fraction (separate implementation path).
    frac_check = (_to_fraction(percent) / 100) * amount
    if frac_check != _to_fraction(value):
        raise ValueError("Percentage-of-amount verification failed")

    steps = [
        f"Convert {percent}% to a fraction: {percent}/100",
        f"Multiply: {percent}/100 × {amount} = {fmt_money(value)}",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"Find {percent}% of {amount}.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(value),
        dedup_key=f"of_amount:{percent}:{amount}",
    )


def _generate_change(rng: random.Random):
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"{verb} {amount} by {percent}%.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(result),
        dedup_key=f"change:{percent}:{amount}:{increase}",
    )


def _generate_reverse(rng: random.Random):
    percent = sp.Rational(rng.choice(HIGHER_PERCENTS))
    original = rng.randrange(20, 401, 4)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = original * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    recovered = _to_fraction(result) / _to_fraction(multiplier)
    if recovered != Fraction(original, 1):
        raise ValueError("Reverse-percentage verification failed")

    verb = "increase" if increase else "decrease"
    steps = [
        f"Convert {percent}% to a multiplier: {fmt_money(multiplier)} (original × multiplier = new value)",
        f"Divide the new value by the multiplier: {fmt_money(result)} ÷ {fmt_money(multiplier)} = {fmt_money(original)}",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=f"After a {percent}% {verb}, an item costs £{fmt_money(result)}. Find the original price.",
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(original)}",
        dedup_key=f"reverse:{percent}:{original}:{increase}",
    )


def _generate_compound(rng: random.Random):
    original = rng.randrange(20, 401, 4)
    percent1 = sp.Rational(rng.choice(HIGHER_PERCENTS))
    percent2 = sp.Rational(rng.choice(HIGHER_PERCENTS))
    increase1 = rng.choice([True, False])
    increase2 = rng.choice([True, False])
    mult1 = _multiplier(percent1, increase1)
    mult2 = _multiplier(percent2, increase2)
    intermediate = original * mult1
    final = intermediate * mult2

    expected = _to_fraction(original) * _to_fraction(mult1) * _to_fraction(mult2)
    if expected != _to_fraction(final):
        raise ValueError("Compound-percentage verification failed")

    verb1 = "increases" if increase1 else "decreases"
    verb2 = "increases" if increase2 else "decreases"
    steps = [
        f"After the first change: {original} × {fmt_money(mult1)} = {fmt_money(intermediate)}",
        f"After the second change: {fmt_money(intermediate)} × {fmt_money(mult2)} = {fmt_money(final)}",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A price of £{original} {verb1} by {percent1}%, then {verb2} by {percent2}%. "
            "Find the final price."
        ),
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(final)}",
        dedup_key=f"compound:{original}:{percent1}:{increase1}:{percent2}:{increase2}",
    )


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["of_amount", "change"])
        return _generate_of_amount(rng) if shape == "of_amount" else _generate_change(rng)
    shape = rng.choice(["reverse", "compound"])
    return _generate_reverse(rng) if shape == "reverse" else _generate_compound(rng)


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Percentages",
    description="Percentages of amounts, percentage change, reverse percentages, and compound changes.",
    generate=generate,
)
