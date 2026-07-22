import dataclasses
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.number_format import fmt_money, to_fraction

SECTION = "ratio_proportion"
GROUP = "Percentages"

FOUNDATION_PERCENTS = ["10", "20", "25", "50"]
HIGHER_PERCENTS = ["12", "15", "17.5", "24", "30", "35", "42.5", "60"]

SIMPLE_INTEREST_RATES = ["2", "3", "4", "5", "6"]
FIND_CHANGE_PERCENTS = ["5", "10", "15", "20", "25", "40", "50"]
CALCULATOR_PERCENTS = ["17.5", "3.6", "8.25", "6.4", "9.75", "22.5", "4.8", "13.5"]


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


def generate_modelled_example_of_amount(tier: Tier, rng: random.Random) -> ModelledExample:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    amount = rng.randrange(20, 501, 20)
    value = percent / 100 * amount

    frac_check = (to_fraction(percent) / 100) * amount
    if frac_check != to_fraction(value):
        raise ValueError("modelled example of_amount verification failed")

    product = int(amount * percent)
    teaching_steps = [
        f"To find {percent}% of {amount}, it helps to first turn the percentage into a fraction: "
        f"{percent}% means {percent} out of every 100, so {percent}% = {percent}/100.",
        f"In maths, 'of' means multiply, so {percent}% of {amount} = {percent}/100 × {amount}.",
        f"Multiply {amount} by {percent} first: {amount} × {percent} = {product}. "
        f"Then divide by 100: {product} ÷ 100 = {fmt_money(value)}.",
        f"So {percent}% of {amount} is {fmt_money(value)}.",
    ]
    worked_calculation = [
        f"{percent}% of {amount}",
        f"= {percent}/100 × {amount}",
        f"= {product} ÷ 100",
        f"= {fmt_money(value)}",
    ]
    return ModelledExample(
        topic_id="percentage_of_amount",
        tier=Tier.FOUNDATION,
        prompt=f"Find {percent}% of {amount}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(value),
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


def generate_modelled_example_change(tier: Tier, rng: random.Random) -> ModelledExample:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    amount = rng.randrange(20, 501, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = amount * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    frac_check = to_fraction(sp.Integer(amount)) * to_fraction(multiplier)
    if frac_check != to_fraction(result):
        raise ValueError("modelled example percentage_change verification failed")

    verb = "Increase" if increase else "Decrease"
    base_pct = 100 + percent if increase else 100 - percent
    teaching_steps = [
        f"To {verb.lower()} {amount} by {percent}%, the quickest method is to build a single "
        "multiplier that does the whole job in one step, rather than working out the percentage "
        "separately and then adding or subtracting it.",
        f"The original amount is always 100% of itself. If we {verb.lower()} it by {percent}%, the "
        f"new amount is {fmt_money(base_pct)}% of the original "
        f"({'100% + ' if increase else '100% - '}{percent}%).",
        f"Turn {fmt_money(base_pct)}% into a decimal multiplier by dividing by 100: "
        f"{fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}.",
        f"Multiply the original amount by this multiplier: {amount} × {fmt_money(multiplier)} = "
        f"{fmt_money(result)}.",
        f"So {'increasing' if increase else 'decreasing'} {amount} by {percent}% gives "
        f"{fmt_money(result)}.",
    ]
    worked_calculation = [
        f"{verb} {amount} by {percent}%",
        f"Multiplier = {fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}",
        f"{amount} × {fmt_money(multiplier)}",
        f"= {fmt_money(result)}",
    ]
    return ModelledExample(
        topic_id="percentage_change",
        tier=Tier.FOUNDATION,
        prompt=f"{verb} {amount} by {percent}%.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(result),
    )


def generate_reverse(tier: Tier, rng: random.Random) -> Question:
    # Keep the ORIGINAL decimal string for display - str(sp.Rational("17.5"))
    # renders as the ugly fraction "35/2", not "17.5" (see percentage_increase_
    # decrease_calculator above for the same fix pattern).
    percent_str = rng.choice(HIGHER_PERCENTS)
    percent = sp.Rational(percent_str)
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
        f"Convert {percent_str}% to a multiplier: {fmt_money(multiplier)} (original × multiplier = new value)",
        f"Divide the new value by the multiplier: {fmt_money(result)} ÷ {fmt_money(multiplier)} = {fmt_money(original)}",
    ]
    return Question(
        topic_id="reverse_percentage",
        tier=Tier.HIGHER,
        prompt=f"After a {percent_str}% {verb}, an item costs £{fmt_money(result)}. Find the original price.",
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(original)}",
        dedup_key=f"reverse:{percent_str}:{original}:{increase}",
    )


def generate_modelled_example_reverse(tier: Tier, rng: random.Random) -> ModelledExample:
    percent_str = rng.choice(HIGHER_PERCENTS)
    percent = sp.Rational(percent_str)
    original = rng.randrange(20, 401, 4)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = original * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    recovered = to_fraction(result) / to_fraction(multiplier)
    if recovered != to_fraction(sp.Integer(original)):
        raise ValueError("modelled example reverse_percentage verification failed")

    verb = "increase" if increase else "decrease"
    base_pct = 100 + percent if increase else 100 - percent
    teaching_steps = [
        f"We're told the price AFTER a {percent_str}% {verb}, and asked to find the price BEFORE it. A "
        f"common mistake is to take {percent_str}% of £{fmt_money(result)} and add or subtract it — but "
        "that's wrong, because the original percentage change was applied to the ORIGINAL price, which "
        "we don't know yet, not to the new one.",
        f"Instead, express the new price as a percentage of the original: a {percent_str}% {verb} means "
        f"the new price is {fmt_money(base_pct)}% of the original, which as a multiplier is "
        f"{fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}.",
        "Since new price = original price × multiplier, to work backwards we reverse the "
        f"multiplication by dividing instead: original = £{fmt_money(result)} ÷ {fmt_money(multiplier)}.",
        f"£{fmt_money(result)} ÷ {fmt_money(multiplier)} = £{fmt_money(original)}, so the original price "
        f"must have been £{fmt_money(original)}.",
    ]
    worked_calculation = [
        f"New price = £{fmt_money(result)} (after a {percent_str}% {verb})",
        f"Multiplier = {fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}",
        f"Original = {fmt_money(result)} ÷ {fmt_money(multiplier)}",
        f"= £{fmt_money(original)}",
    ]
    return ModelledExample(
        topic_id="reverse_percentage",
        tier=Tier.HIGHER,
        prompt=(
            f"After a {percent_str}% {verb}, an item costs £{fmt_money(result)}. Find the original price."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"£{fmt_money(original)}",
    )


def generate_reverse_foundation(tier: Tier, rng: random.Random) -> Question:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    original = rng.randrange(20, 401, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = original * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    recovered = to_fraction(result) / to_fraction(multiplier)
    if recovered != to_fraction(sp.Integer(original)):
        raise ValueError("Reverse-percentage (foundation) verification failed")

    verb = "increase" if increase else "decrease"
    steps = [
        f"Convert {percent}% to a multiplier: {fmt_money(multiplier)} (original × multiplier = new value)",
        f"Divide the new value by the multiplier: {fmt_money(result)} ÷ {fmt_money(multiplier)} = {fmt_money(original)}",
    ]
    return Question(
        topic_id="reverse_percentage_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"After a {percent}% {verb}, an item costs £{fmt_money(result)}. Find the original price.",
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(original)}",
        dedup_key=f"reverse_f:{percent}:{original}:{increase}",
    )


def generate_modelled_example_reverse_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    percent = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    original = rng.randrange(20, 401, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    result = original * multiplier

    # Independent verification via Python's Fraction (separate implementation path).
    recovered = to_fraction(result) / to_fraction(multiplier)
    if recovered != to_fraction(sp.Integer(original)):
        raise ValueError("modelled example reverse_percentage_foundation verification failed")

    verb = "increase" if increase else "decrease"
    base_pct = 100 + percent if increase else 100 - percent
    teaching_steps = [
        f"This is a reverse percentage problem: we're given the value AFTER the {percent}% {verb}, "
        "and asked to find the value BEFORE it. It's tempting to just take "
        f"{percent}% of £{fmt_money(result)} and add or subtract it, but that gives the wrong answer "
        "because the percentage was applied to the ORIGINAL price, not the new one.",
        f"Instead, think of the new price as a percentage of the original: an {verb} of {percent}% "
        f"means the new price is {fmt_money(base_pct)}% of the original, i.e. a multiplier of "
        f"{fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}.",
        f"Since new price = original × multiplier, to undo the multiplication we divide the new price "
        f"by the multiplier instead: £{fmt_money(result)} ÷ {fmt_money(multiplier)}.",
        f"£{fmt_money(result)} ÷ {fmt_money(multiplier)} = £{fmt_money(original)}, so that must have "
        "been the original price.",
    ]
    worked_calculation = [
        f"New price = £{fmt_money(result)} (after a {percent}% {verb})",
        f"Multiplier = {fmt_money(base_pct)} ÷ 100 = {fmt_money(multiplier)}",
        f"Original = {fmt_money(result)} ÷ {fmt_money(multiplier)}",
        f"= £{fmt_money(original)}",
    ]
    return ModelledExample(
        topic_id="reverse_percentage_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"After a {percent}% {verb}, an item costs £{fmt_money(result)}. Find the original price."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"£{fmt_money(original)}",
    )


def generate_compound(tier: Tier, rng: random.Random) -> Question:
    original = rng.randrange(20, 401, 4)
    # Keep the ORIGINAL decimal strings for display - str(sp.Rational("17.5"))
    # renders as the ugly fraction "35/2", not "17.5".
    percent1_str = rng.choice(HIGHER_PERCENTS)
    percent2_str = rng.choice(HIGHER_PERCENTS)
    percent1 = sp.Rational(percent1_str)
    percent2 = sp.Rational(percent2_str)
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
            f"A price of £{original} {verb1} by {percent1_str}%, then {verb2} by {percent2_str}%. "
            "Find the final price."
        ),
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(final)}",
        dedup_key=f"compound:{original}:{percent1_str}:{increase1}:{percent2_str}:{increase2}",
    )


def generate_modelled_example_compound(tier: Tier, rng: random.Random) -> ModelledExample:
    original = rng.randrange(20, 401, 4)
    percent1_str = rng.choice(HIGHER_PERCENTS)
    percent2_str = rng.choice(HIGHER_PERCENTS)
    percent1 = sp.Rational(percent1_str)
    percent2 = sp.Rational(percent2_str)
    increase1 = rng.choice([True, False])
    increase2 = rng.choice([True, False])
    mult1 = _multiplier(percent1, increase1)
    mult2 = _multiplier(percent2, increase2)
    intermediate = original * mult1
    final = intermediate * mult2

    expected = to_fraction(sp.Integer(original)) * to_fraction(mult1) * to_fraction(mult2)
    if expected != to_fraction(final):
        raise ValueError("modelled example compound_percentage verification failed")

    verb1 = "increases" if increase1 else "decreases"
    verb2 = "increases" if increase2 else "decreases"
    teaching_steps = [
        "With two successive percentage changes, a very common mistake is to add the two percentages "
        "together and apply them in one go. That doesn't work here, because the second change is "
        "applied to the NEW amount after the first change, not to the original amount.",
        f"So the two changes must be applied one at a time, in order. First, convert each percentage "
        f"change to a multiplier: a {percent1_str}% {verb1[:-1]} is ×{fmt_money(mult1)}, and a {percent2_str}% "
        f"{verb2[:-1]} is ×{fmt_money(mult2)}.",
        f"Apply the first multiplier to the original price: £{original} × {fmt_money(mult1)} = "
        f"£{fmt_money(intermediate)}. This is the price after only the first change.",
        f"Now apply the second multiplier to THAT new price, not the original: "
        f"£{fmt_money(intermediate)} × {fmt_money(mult2)} = £{fmt_money(final)}.",
        f"So after both changes, the final price is £{fmt_money(final)}.",
    ]
    worked_calculation = [
        f"£{original} {verb1} by {percent1_str}%, then {verb2} by {percent2_str}%",
        f"After change 1: {original} × {fmt_money(mult1)} = {fmt_money(intermediate)}",
        f"After change 2: {fmt_money(intermediate)} × {fmt_money(mult2)} = {fmt_money(final)}",
        f"= £{fmt_money(final)}",
    ]
    return ModelledExample(
        topic_id="compound_percentage",
        tier=Tier.HIGHER,
        prompt=(
            f"A price of £{original} {verb1} by {percent1_str}%, then {verb2} by {percent2_str}%. "
            "Find the final price."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"£{fmt_money(final)}",
    )


def generate_compound_foundation(tier: Tier, rng: random.Random) -> Question:
    original = rng.randrange(20, 401, 20)
    percent1 = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    percent2 = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    increase1 = rng.choice([True, False])
    increase2 = rng.choice([True, False])
    mult1 = _multiplier(percent1, increase1)
    mult2 = _multiplier(percent2, increase2)
    intermediate = original * mult1
    final = intermediate * mult2

    expected = to_fraction(sp.Integer(original)) * to_fraction(mult1) * to_fraction(mult2)
    if expected != to_fraction(final):
        raise ValueError("Compound-percentage (foundation) verification failed")

    verb1 = "increases" if increase1 else "decreases"
    verb2 = "increases" if increase2 else "decreases"
    steps = [
        f"After the first change: {original} × {fmt_money(mult1)} = {fmt_money(intermediate)}",
        f"After the second change: {fmt_money(intermediate)} × {fmt_money(mult2)} = {fmt_money(final)}",
    ]
    return Question(
        topic_id="compound_percentage_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A price of £{original} {verb1} by {percent1}%, then {verb2} by {percent2}%. "
            "Find the final price."
        ),
        solution_steps=tuple(steps),
        final_answer=f"£{fmt_money(final)}",
        dedup_key=f"compound_f:{original}:{percent1}:{increase1}:{percent2}:{increase2}",
    )


def generate_modelled_example_compound_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    original = rng.randrange(20, 401, 20)
    percent1 = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    percent2 = sp.Rational(rng.choice(FOUNDATION_PERCENTS))
    increase1 = rng.choice([True, False])
    increase2 = rng.choice([True, False])
    mult1 = _multiplier(percent1, increase1)
    mult2 = _multiplier(percent2, increase2)
    intermediate = original * mult1
    final = intermediate * mult2

    expected = to_fraction(sp.Integer(original)) * to_fraction(mult1) * to_fraction(mult2)
    if expected != to_fraction(final):
        raise ValueError("modelled example compound_percentage_foundation verification failed")

    verb1 = "increases" if increase1 else "decreases"
    verb2 = "increases" if increase2 else "decreases"
    teaching_steps = [
        "With two successive percentage changes, a very common mistake is to add the two percentages "
        "together and apply them in one go. That doesn't work here, because the second change is "
        "applied to the NEW amount after the first change, not to the original amount.",
        f"So the two changes must be applied one at a time, in order. First, convert each percentage "
        f"change to a multiplier: a {percent1}% {verb1[:-1]} is ×{fmt_money(mult1)}, and a {percent2}% "
        f"{verb2[:-1]} is ×{fmt_money(mult2)}.",
        f"Apply the first multiplier to the original price: £{original} × {fmt_money(mult1)} = "
        f"£{fmt_money(intermediate)}. This is the price after only the first change.",
        f"Now apply the second multiplier to THAT new price, not the original: "
        f"£{fmt_money(intermediate)} × {fmt_money(mult2)} = £{fmt_money(final)}.",
        f"So after both changes, the final price is £{fmt_money(final)}.",
    ]
    worked_calculation = [
        f"£{original} {verb1} by {percent1}%, then {verb2} by {percent2}%",
        f"After change 1: {original} × {fmt_money(mult1)} = {fmt_money(intermediate)}",
        f"After change 2: {fmt_money(intermediate)} × {fmt_money(mult2)} = {fmt_money(final)}",
        f"= £{fmt_money(final)}",
    ]
    return ModelledExample(
        topic_id="compound_percentage_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A price of £{original} {verb1} by {percent1}%, then {verb2} by {percent2}%. "
            "Find the final price."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"£{fmt_money(final)}",
    )


TOPIC_OF_AMOUNT = TopicDefinition(
    id="percentage_of_amount",
    display_name="Percentage of an Amount",
    description="Find a percentage of a given amount.",
    generate=generate_of_amount,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_of_amount,
)

TOPIC_CHANGE = TopicDefinition(
    id="percentage_change",
    display_name="Percentage Change",
    description="Increase or decrease an amount by a percentage.",
    generate=generate_change,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_change,
)

TOPIC_REVERSE = TopicDefinition(
    id="reverse_percentage",
    display_name="Reverse Percentage",
    description="Find the original amount given a value after a percentage change.",
    generate=generate_reverse,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_reverse,
)

TOPIC_REVERSE_FOUNDATION = TopicDefinition(
    id="reverse_percentage_foundation",
    display_name="Reverse Percentage (Foundation)",
    description="Find the original amount given a value after a simple percentage change.",
    generate=generate_reverse_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_reverse_foundation,
)

TOPIC_COMPOUND = TopicDefinition(
    id="compound_percentage",
    display_name="Compound Percentage Change",
    description="Apply two successive percentage changes to an amount.",
    generate=generate_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_compound,
)

TOPIC_COMPOUND_FOUNDATION = TopicDefinition(
    id="compound_percentage_foundation",
    display_name="Compound Percentage Change (Foundation)",
    description="Apply two successive percentage changes to an amount.",
    generate=generate_compound_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_compound_foundation,
)


# ===========================================================================
# Simple Interest
# ===========================================================================


def generate_simple_interest(tier: Tier, rng: random.Random) -> Question:
    principal = rng.randrange(200, 5001, 100)
    rate = sp.Rational(rng.choice(SIMPLE_INTEREST_RATES))
    years = rng.randint(1, 5)
    annual_interest = principal * rate / 100
    interest = annual_interest * years

    # Independent verification: build up the interest year-by-year via
    # repeated addition (a physically different method - simple interest is
    # the same fixed amount added every year) and confirm it matches the
    # closed-form multiplication used above.
    running_total = sp.Integer(0)
    for _ in range(years):
        running_total += annual_interest
    if to_fraction(running_total) != to_fraction(interest):
        raise ValueError("simple_interest verification failed")

    total_amount = principal + interest
    ask_total = rng.choice([True, False])

    steps = [
        "Simple interest formula: I = P × r × t ÷ 100",
        f"I = {principal} × {rate} × {years} ÷ 100 = £{fmt_money(interest)}",
    ]
    if ask_total:
        steps.append(f"Total in the account = P + I = £{principal} + £{fmt_money(interest)} = £{fmt_money(total_amount)}")
        answer = f"£{fmt_money(total_amount)}"
        question_line = f"Find the total amount in the account after {years} years."
    else:
        answer = f"£{fmt_money(interest)}"
        question_line = "Find the interest earned."

    return Question(
        topic_id="simple_interest",
        tier=Tier.FOUNDATION,
        prompt=(
            f"£{principal} is invested at a simple interest rate of {rate}% per year for "
            f"{years} years. {question_line}"
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"si:{principal}:{rate}:{years}:{ask_total}",
    )


def generate_modelled_example_simple_interest(tier: Tier, rng: random.Random) -> ModelledExample:
    principal = rng.randrange(200, 5001, 100)
    rate = sp.Rational(rng.choice(SIMPLE_INTEREST_RATES))
    years = rng.randint(1, 5)
    annual_interest = principal * rate / 100
    interest = annual_interest * years

    running_total = sp.Integer(0)
    for _ in range(years):
        running_total += annual_interest
    if to_fraction(running_total) != to_fraction(interest):
        raise ValueError("modelled example simple_interest verification failed")

    total_amount = principal + interest
    ask_total = rng.choice([True, False])

    if ask_total:
        answer = f"£{fmt_money(total_amount)}"
        question_line = f"Find the total amount in the account after {years} years."
    else:
        answer = f"£{fmt_money(interest)}"
        question_line = "Find the interest earned."

    teaching_steps = [
        "Simple interest means the SAME amount of interest is earned every single year - unlike "
        "compound interest, the interest itself never earns extra interest, so it never grows "
        "faster year on year.",
        f"Each year's interest is {rate}% of the ORIGINAL principal, £{principal}: "
        f"{rate}/100 × £{principal} = £{fmt_money(annual_interest)}.",
        f"Since this same amount is earned every year, over {years} years the total interest is "
        f"£{fmt_money(annual_interest)} × {years} = £{fmt_money(interest)}. (As a check, adding "
        f"£{fmt_money(annual_interest)} to a running total {years} times gives exactly the same "
        f"figure, since simple interest just adds the same amount again and again.)",
    ]
    if ask_total:
        teaching_steps.append(
            f"The total amount in the account is the original principal plus all the interest "
            f"earned: £{principal} + £{fmt_money(interest)} = £{fmt_money(total_amount)}."
        )
    else:
        teaching_steps.append(f"So the interest earned over {years} years is £{fmt_money(interest)}.")

    worked_calculation = [
        f"Interest per year = {rate}% of £{principal} = £{fmt_money(annual_interest)}",
        f"Over {years} years: £{fmt_money(annual_interest)} × {years} = £{fmt_money(interest)}",
    ]
    if ask_total:
        worked_calculation.append(f"Total = £{principal} + £{fmt_money(interest)} = £{fmt_money(total_amount)}")

    return ModelledExample(
        topic_id="simple_interest",
        tier=Tier.FOUNDATION,
        prompt=(
            f"£{principal} is invested at a simple interest rate of {rate}% per year for "
            f"{years} years. {question_line}"
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Finding a Percentage Change (reverse of Percentage Change)
# ===========================================================================


def generate_find_percentage_change(tier: Tier, rng: random.Random) -> Question:
    percent = sp.Rational(rng.choice(FIND_CHANGE_PERCENTS))
    original = rng.randrange(20, 401, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    new_value = original * multiplier
    diff = (new_value - original) if increase else (original - new_value)
    verb = "increase" if increase else "decrease"

    # Compute the percentage change the way a student would: difference divided
    # by the ORIGINAL value, then converted to a percentage.
    computed_percent = diff / original * 100

    # Independent verification: take the computed percentage, rebuild it into a
    # multiplier, apply it to the original value, and confirm this reproduces
    # the given new value exactly - the reverse direction to the subtract/
    # divide/multiply method used to compute the percentage above.
    check_multiplier = _multiplier(computed_percent, increase)
    reconstructed = original * check_multiplier
    if to_fraction(reconstructed) != to_fraction(new_value):
        raise ValueError("find_percentage_change verification failed")

    steps = [
        f"Find the difference between the two values: £{fmt_money(new_value)} and £{original} "
        f"differ by £{fmt_money(diff)}",
        f"Divide by the ORIGINAL value and convert to a percentage: £{fmt_money(diff)} ÷ £{original} "
        f"× 100 = {fmt_money(computed_percent)}%",
    ]
    return Question(
        topic_id="find_percentage_change",
        tier=Tier.FOUNDATION,
        prompt=f"The price of an item changes from £{original} to £{fmt_money(new_value)}. Find the percentage {verb}.",
        solution_steps=tuple(steps),
        final_answer=f"{fmt_money(computed_percent)}% {verb}",
        dedup_key=f"fpc:{percent}:{original}:{increase}",
    )


def generate_modelled_example_find_percentage_change(tier: Tier, rng: random.Random) -> ModelledExample:
    percent = sp.Rational(rng.choice(FIND_CHANGE_PERCENTS))
    original = rng.randrange(20, 401, 20)
    increase = rng.choice([True, False])
    multiplier = _multiplier(percent, increase)
    new_value = original * multiplier
    diff = (new_value - original) if increase else (original - new_value)
    verb = "increase" if increase else "decrease"

    computed_percent = diff / original * 100
    check_multiplier = _multiplier(computed_percent, increase)
    reconstructed = original * check_multiplier
    if to_fraction(reconstructed) != to_fraction(new_value):
        raise ValueError("modelled example find_percentage_change verification failed")

    teaching_steps = [
        f"This is the REVERSE of a normal percentage-change question: instead of being told a "
        "percentage and asked to apply it, we're given the price BEFORE (£"
        f"{original}) and AFTER (£{fmt_money(new_value)}), and have to work out what percentage "
        "change happened between them.",
        f"First find how much the value actually changed by: £{fmt_money(new_value)} and "
        f"£{original} differ by £{fmt_money(diff)}. This is a {verb} since the price went "
        f"{'up' if increase else 'down'}.",
        f"To turn that change into a percentage, divide it by the ORIGINAL value (never the new "
        f"one) and multiply by 100: £{fmt_money(diff)} ÷ £{original} × 100 = "
        f"{fmt_money(computed_percent)}%.",
        f"As a check, applying a {fmt_money(computed_percent)}% {verb} back to the original price "
        f"£{original} should reproduce the new price exactly: it gives £{fmt_money(reconstructed)}, "
        f"which matches £{fmt_money(new_value)}.",
    ]
    worked_calculation = [
        f"Difference = £{fmt_money(new_value)} vs £{original} = £{fmt_money(diff)}",
        f"£{fmt_money(diff)} ÷ £{original} × 100 = {fmt_money(computed_percent)}%",
        f"= {fmt_money(computed_percent)}% {verb}",
    ]

    return ModelledExample(
        topic_id="find_percentage_change",
        tier=Tier.FOUNDATION,
        prompt=f"The price of an item changes from £{original} to £{fmt_money(new_value)}. Find the percentage {verb}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{fmt_money(computed_percent)}% {verb}",
    )


# ===========================================================================
# Percentage Increase/Decrease (Calculator) - Higher sibling of percentage_change
# ===========================================================================


def _fmt_pence_amount(pounds: int, pence: int) -> str:
    return f"{pounds}.{pence:02d}"


def generate_percentage_increase_decrease_calculator(tier: Tier, rng: random.Random) -> Question:
    # Keep the ORIGINAL decimal string for display/Decimal use throughout -
    # str(sp.Rational("17.5")) renders as the ugly fraction "35/2", not "17.5",
    # so the Rational conversion is only ever used for the exact-arithmetic path.
    percent_str = rng.choice(CALCULATOR_PERCENTS)
    percent = sp.Rational(percent_str)
    pounds = rng.randint(10, 800)
    pence = rng.choice([0, 5, 15, 20, 25, 35, 40, 45, 55, 60, 65, 75, 80, 85, 95])
    amount_str = _fmt_pence_amount(pounds, pence)
    increase = rng.choice([True, False])

    # Primary route: sympy Rational exact arithmetic, rounded via Decimal.
    amount = sp.Rational(pounds) + sp.Rational(pence, 100)
    multiplier = _multiplier(percent, increase)
    exact = amount * multiplier
    exact_fraction = to_fraction(exact)
    dec_primary = Decimal(exact_fraction.numerator) / Decimal(exact_fraction.denominator)
    rounded_primary = dec_primary.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Independent verification: redo the entire calculation in pure Decimal
    # arithmetic (no sympy/Fraction involved at all), then round separately -
    # a genuinely different computation path to the sympy/Fraction one above.
    percent_dec = Decimal(percent_str)
    amount_dec = Decimal(pounds) + Decimal(pence) / Decimal(100)
    multiplier_dec = (
        Decimal(1) + percent_dec / Decimal(100) if increase else Decimal(1) - percent_dec / Decimal(100)
    )
    dec_secondary = amount_dec * multiplier_dec
    rounded_secondary = dec_secondary.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if rounded_primary != rounded_secondary:
        raise ValueError("percentage_increase_decrease_calculator: independent computations disagree")

    verb = "Increase" if increase else "Decrease"
    steps = [
        f"Convert {percent_str}% to a multiplier: {multiplier_dec}",
        f"Multiply: £{amount_str} × {multiplier_dec} = £{rounded_primary} (calculator, 2 d.p.)",
    ]
    return Question(
        topic_id="percentage_increase_decrease_calculator",
        tier=Tier.HIGHER,
        prompt=(
            f"Using a calculator, {verb.lower()} £{amount_str} by {percent_str}%. "
            "Give your answer to 2 decimal places."
        ),
        solution_steps=tuple(steps),
        final_answer=f"£{rounded_primary}",
        dedup_key=f"pidc:{percent_str}:{pounds}:{pence}:{increase}",
    )


def generate_modelled_example_percentage_increase_decrease_calculator(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    # See generate_percentage_increase_decrease_calculator: the original decimal
    # string must be kept for display/Decimal use, since str(sp.Rational(...))
    # renders fractional percents like "35/2" rather than "17.5".
    percent_str = rng.choice(CALCULATOR_PERCENTS)
    percent = sp.Rational(percent_str)
    pounds = rng.randint(10, 800)
    pence = rng.choice([0, 5, 15, 20, 25, 35, 40, 45, 55, 60, 65, 75, 80, 85, 95])
    amount_str = _fmt_pence_amount(pounds, pence)
    increase = rng.choice([True, False])

    amount = sp.Rational(pounds) + sp.Rational(pence, 100)
    multiplier = _multiplier(percent, increase)
    exact = amount * multiplier
    exact_fraction = to_fraction(exact)
    dec_primary = Decimal(exact_fraction.numerator) / Decimal(exact_fraction.denominator)
    rounded_primary = dec_primary.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    percent_dec = Decimal(percent_str)
    amount_dec = Decimal(pounds) + Decimal(pence) / Decimal(100)
    multiplier_dec = (
        Decimal(1) + percent_dec / Decimal(100) if increase else Decimal(1) - percent_dec / Decimal(100)
    )
    dec_secondary = amount_dec * multiplier_dec
    rounded_secondary = dec_secondary.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if rounded_primary != rounded_secondary:
        raise ValueError(
            "modelled example percentage_increase_decrease_calculator: independent computations disagree"
        )

    verb = "Increase" if increase else "Decrease"
    teaching_steps = [
        f"This percentage ({percent_str}%) and this amount (£{amount_str}) are deliberately messy - "
        "they won't combine to a clean answer by hand, so a calculator is expected here.",
        f"As always, turn the percentage change into a single multiplier first: a {percent_str}% "
        f"{'increase' if increase else 'decrease'} is ×{multiplier_dec} "
        f"({'100% + ' if increase else '100% - '}{percent_str}%, then ÷100).",
        f"Multiply the amount by this multiplier on your calculator: £{amount_str} × "
        f"{multiplier_dec} = £{dec_primary} - keep all the calculator's decimal places "
        "for now, don't round early.",
        f"Only round at the very end, to 2 decimal places (the nearest penny): £{rounded_primary}.",
        "As a check, redoing the whole calculation with the percentage and amount entered as plain "
        f"decimals (rather than as exact fractions) and rounding separately gives the same "
        f"£{rounded_secondary}, confirming the answer.",
    ]
    worked_calculation = [
        f"{verb} £{amount_str} by {percent_str}%",
        f"Multiplier = {multiplier_dec}",
        f"£{amount_str} × {multiplier_dec} = £{dec_primary}",
        f"= £{rounded_primary} (2 d.p.)",
    ]

    return ModelledExample(
        topic_id="percentage_increase_decrease_calculator",
        tier=Tier.HIGHER,
        prompt=(
            f"Using a calculator, {verb.lower()} £{amount_str} by {percent_str}%. "
            "Give your answer to 2 decimal places."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"£{rounded_primary}",
    )


# ===========================================================================
# Mixed Percentages Practice - dispatcher over the 4 existing percentage skills
# ===========================================================================

_MIXED_PERCENTAGE_GENERATORS = [
    (generate_of_amount, Tier.FOUNDATION),
    (generate_change, Tier.FOUNDATION),
    (generate_reverse, Tier.HIGHER),
    (generate_compound, Tier.HIGHER),
]

_MIXED_PERCENTAGE_MODELLED_GENERATORS = [
    (generate_modelled_example_of_amount, Tier.FOUNDATION),
    (generate_modelled_example_change, Tier.FOUNDATION),
    (generate_modelled_example_reverse, Tier.HIGHER),
    (generate_modelled_example_compound, Tier.HIGHER),
]


def generate_mixed_percentages(tier: Tier, rng: random.Random) -> Question:
    generate, gen_tier = rng.choice(_MIXED_PERCENTAGE_GENERATORS)
    q = generate(gen_tier, rng)
    return dataclasses.replace(
        q, topic_id="mixed_percentages", tier=Tier.HIGHER, dedup_key=f"mixed_pct:{q.dedup_key}"
    )


def generate_modelled_example_mixed_percentages(tier: Tier, rng: random.Random) -> ModelledExample:
    generate, gen_tier = rng.choice(_MIXED_PERCENTAGE_MODELLED_GENERATORS)
    example = generate(gen_tier, rng)
    return dataclasses.replace(example, topic_id="mixed_percentages", tier=Tier.HIGHER)


TOPIC_SIMPLE_INTEREST = TopicDefinition(
    id="simple_interest",
    display_name="Simple Interest",
    description="Calculate simple interest earned on a principal over several years, or the total amount.",
    generate=generate_simple_interest,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_simple_interest,
)

TOPIC_FIND_PERCENTAGE_CHANGE = TopicDefinition(
    id="find_percentage_change",
    display_name="Finding a Percentage Change",
    description="Find the percentage increase or decrease between an original and a new value.",
    generate=generate_find_percentage_change,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_find_percentage_change,
)

TOPIC_PERCENTAGE_INCREASE_DECREASE_CALCULATOR = TopicDefinition(
    id="percentage_increase_decrease_calculator",
    display_name="Percentage Increase/Decrease (Calculator)",
    description="Increase or decrease a money amount by a messier percentage using a calculator.",
    generate=generate_percentage_increase_decrease_calculator,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_percentage_increase_decrease_calculator,
)

TOPIC_MIXED_PERCENTAGES = TopicDefinition(
    id="mixed_percentages",
    display_name="Mixed Percentages Practice",
    description="A mix of percentage-of-an-amount, percentage change, reverse percentage, and compound percentage questions.",
    generate=generate_mixed_percentages,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_mixed_percentages,
)
