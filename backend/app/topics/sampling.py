"""Sampling and populations (AQA 3.6 S1): inferring properties of a population
from a sample, and knowing the limitations of a sampling method. Two question
shapes via rng.choice, sharing one topic id:

- A stratified-sample calculation - fully randomised with a real numeric
  answer, verified independently (exact Fraction arithmetic cross-checked
  against a separate float/round computation - a genuinely different
  numeric path, not the same division repeated).
- A scenario-based question about sampling bias or a suitable sampling
  method - a curated bank of named scenarios (in the same spirit as
  algebraic_proof.py's TEMPLATES, since "is this a representative sample"
  has a definitive right answer that doesn't depend on drawing a random
  number), but each scenario still randomises its own cosmetic details
  (a location/number/group name) for surface variety, giving a
  dedup_key space much larger than the template count alone.
"""

import math
import random
from fractions import Fraction
from typing import Callable, NamedTuple

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "statistics"
GROUP = "Sampling and Populations"

_YEAR_GROUPS = ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11"]
_LOCATIONS = [
    "the school car park",
    "the canteen at lunchtime",
    "the front gate before 7am",
    "the school library",
    "the sports hall during a PE lesson",
    "the bus stop outside school",
]
_GROUP_WORDS = ["customers", "employees", "members", "clients", "subscribers"]
_TOWNS = ["Ashby", "Elmswood", "Riverdale", "Kingsmere", "Oakford"]


# --- Branch A: stratified sample calculation -------------------------------


def _stratified_case(rng: random.Random):
    n_strata = rng.choice([2, 3])
    names = rng.sample(_YEAR_GROUPS, k=n_strata)
    counts = [rng.randint(40, 260) for _ in names]
    total = sum(counts)
    sample_size = rng.randint(20, 100)
    target_idx = rng.randrange(n_strata)
    target_name, target_count = names[target_idx], counts[target_idx]

    # Primary computation: exact round-half-up via plain integer arithmetic
    # (the standard (2n + d) // (2d) identity for round-half-up of n/d),
    # never touching floats or Decimal at all.
    numerator = target_count * sample_size
    answer = (2 * numerator + total) // (2 * total)

    # Independent verification: recompute via exact Fraction arithmetic
    # instead (a different code path through Python's numeric stack, not
    # just the same integer division repeated), rounding half-up by taking
    # the floor of (exact fraction + 1/2) - still exact, no floats, so this
    # is immune to the float-precision tie-boundary failures a naive
    # float-based check hit on a wider trial run (not the original smaller
    # smoke test).
    exact = Fraction(numerator, total)
    fraction_answer = math.floor(exact + Fraction(1, 2))
    if fraction_answer != answer:
        raise ValueError("sampling: stratified calculation integer/fraction cross-check disagreed")
    if not (0 <= answer <= sample_size):
        raise ValueError("sampling: stratified calculation produced an out-of-range answer")

    return names, counts, total, sample_size, target_name, target_count, answer


def _stratified_question(rng: random.Random) -> tuple[str, tuple[str, ...], str, str]:
    names, counts, total, sample_size, target_name, target_count, answer = _stratified_case(rng)
    breakdown = ", ".join(f"{n}: {c}" for n, c in zip(names, counts))
    prompt = (
        f"A school has {total} students: {breakdown}. A stratified sample of {sample_size} students "
        f"is taken. How many students from {target_name} should be in the sample?"
    )
    steps = (
        f"{target_name} makes up {target_count} out of {total} students.",
        f"Sample size needed = ({target_count} ÷ {total}) × {sample_size}",
        f"= {answer} students (rounded to the nearest whole number)",
    )
    dedup_key = f"sampling_strat:{tuple(counts)}:{total}:{sample_size}:{target_name}"
    return prompt, steps, str(answer), dedup_key


# --- Branch B: sampling bias / suitable method scenarios -------------------


class _Scenario(NamedTuple):
    id: str
    build: Callable[[random.Random], tuple[str, tuple[str, ...], str]]


def _biased_convenience(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    location = rng.choice(_LOCATIONS)
    n = rng.randint(20, 60)
    group = rng.choice(_GROUP_WORDS)
    prompt = (
        f"A researcher wants to find out the opinions of all {group} at a large organisation. "
        f"She asks the first {n} {group} she meets at {location}. Explain why this sample "
        f"might not be representative of all the {group}."
    )
    steps = (
        f"Only {group} who happen to be at {location} at that particular time have any chance "
        "of being chosen - anyone who isn't there is automatically excluded.",
        "This is a convenience sample, not a random one, so it's likely to over-represent whichever "
        "kind of person tends to be in that place at that time, and under-represent everyone else.",
    )
    answer = "Biased - only people at that one location/time could be chosen, so the sample isn't representative."
    return prompt, steps, answer


def _biased_self_selecting(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    town = rng.choice(_TOWNS)
    topic = rng.choice(["a new leisure centre", "a proposed bus route", "a recycling scheme", "a new one-way system"])
    prompt = (
        f"The {town} council puts an online survey on its website asking residents for their opinion on "
        f"{topic}. Anyone can choose to fill it in. Explain why this sample might be biased."
    )
    steps = (
        "Only residents who see the survey and choose to respond are included - this is a "
        "self-selecting (voluntary response) sample.",
        "People with a strong opinion (especially those who are against the proposal) are far more "
        "likely to make the effort to respond than people who don't feel strongly either way.",
    )
    answer = "Biased - it's a self-selecting sample, so people with strong opinions are over-represented."
    return prompt, steps, answer


def _biased_excluded_subgroup(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    year = rng.choice(_YEAR_GROUPS)
    topic = rng.choice(["the school canteen menu", "the length of the school day", "the new uniform policy"])
    prompt = (
        f"A school wants to find out what all students think about {topic}, but only surveys "
        f"students in {year}. Explain why this sample might not be representative of the whole school."
    )
    steps = (
        f"Students in every other year group have no chance of being chosen at all.",
        f"{year} students might have different opinions from other year groups (e.g. due to age or how "
        "long they've been at the school), so their views alone can't safely represent everyone.",
    )
    answer = "Biased - only one year group was asked, so other year groups aren't represented at all."
    return prompt, steps, answer


def _method_simple_random(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    n = rng.randint(200, 900)
    k = rng.randint(20, 60)
    group = rng.choice(_GROUP_WORDS)
    prompt = (
        f"A company has {n} {group} on its books and wants to choose a sample of {k} to survey, giving "
        "every one of them an equal chance of being chosen. Name a suitable sampling method, and briefly "
        "describe how it would be carried out here."
    )
    steps = (
        "Every member of the population needs an equal chance of selection, with no particular group "
        "favoured over another.",
        f"Simple random sampling does this directly: number all {n} {group} from 1 to {n}, then use a "
        f"random number generator (or lottery method) to pick {k} distinct numbers.",
    )
    answer = f"Simple random sampling - number all {n} {group}, then randomly select {k} of them."
    return prompt, steps, answer


def _method_systematic(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    n = rng.randint(300, 1200)
    k = rng.choice([15, 20, 25, 30])
    prompt = (
        f"A quality-control inspector wants to check {k} items out of a production run of {n}, evenly "
        "spaced throughout the day's production. Name a suitable sampling method, and state the "
        "sampling interval she should use."
    )
    interval = n // k
    steps = (
        f"Sampling interval = population size ÷ sample size = {n} ÷ {k} = {interval} (rounded down)",
        f"Systematic sampling selects every {interval}th item from the production line, after choosing "
        "a random starting point within the first interval.",
    )
    answer = f"Systematic sampling - select every {interval}th item."
    return prompt, steps, answer


def _method_stratified_choice(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    if rng.random() < 0.5:
        group_a, group_b = "boys", "girls"
    else:
        group_a, group_b = rng.sample(_YEAR_GROUPS, k=2)
    prompt = (
        f"A school's students are split unevenly between {group_a} and {group_b}. The school wants a "
        "sample that reflects this split proportionally. Name a suitable sampling method."
    )
    steps = (
        "Since the two groups are different sizes, an equal number sampled from each would over- or "
        "under-represent one of them relative to the whole school.",
        "Stratified sampling fixes this: the population is split into the two groups (strata), and the "
        "number sampled from each is kept proportional to its size in the whole population.",
    )
    answer = "Stratified sampling - sample from each group in proportion to its size."
    return prompt, steps, answer


def _sample_too_small(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    n = rng.randint(2000, 8000)
    k = rng.randint(3, 8)
    prompt = (
        f"A survey of only {k} people is used to estimate the opinion of all {n} residents of a town. "
        "Explain why conclusions drawn from this sample are unreliable."
    )
    steps = (
        f"{k} people is a very small fraction of {n} residents.",
        "A sample this small can easily happen to contain an unusual mix of opinions purely by chance, "
        "so it may not reflect the true spread of opinion across the whole population.",
    )
    answer = "The sample is too small relative to the population to reliably represent it."
    return prompt, steps, answer


def _sampling_frame_out_of_date(rng: random.Random) -> tuple[str, tuple[str, ...], str]:
    town = rng.choice(_TOWNS)
    prompt = (
        f"A researcher selects a random sample of residents of {town} from an electoral register that "
        "is three years old. Explain one problem this could cause."
    )
    steps = (
        "The list used to select the sample is called the sampling frame - here, the electoral register.",
        "An out-of-date sampling frame no longer matches the true population: anyone who has moved into "
        "the town in the last three years has no chance of being selected, and anyone who has moved away "
        "or is no longer eligible may still be listed.",
    )
    answer = "The sampling frame is out of date, so new residents can't be selected and it no longer matches the true population."
    return prompt, steps, answer


_SCENARIOS: tuple[_Scenario, ...] = (
    _Scenario("biased_convenience", _biased_convenience),
    _Scenario("biased_self_selecting", _biased_self_selecting),
    _Scenario("biased_excluded_subgroup", _biased_excluded_subgroup),
    _Scenario("method_simple_random", _method_simple_random),
    _Scenario("method_systematic", _method_systematic),
    _Scenario("method_stratified_choice", _method_stratified_choice),
    _Scenario("sample_too_small", _sample_too_small),
    _Scenario("sampling_frame_out_of_date", _sampling_frame_out_of_date),
)


def _scenario_question(rng: random.Random) -> tuple[str, tuple[str, ...], str, str]:
    scenario = rng.choice(_SCENARIOS)
    prompt, steps, answer = scenario.build(rng)
    dedup_key = f"sampling_scenario:{scenario.id}:{prompt}"
    return prompt, steps, answer, dedup_key


def generate_sampling_methods(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["stratified", "scenario"])
    if shape == "stratified":
        prompt, steps, answer, dedup_key = _stratified_question(rng)
    else:
        prompt, steps, answer, dedup_key = _scenario_question(rng)

    return Question(
        topic_id="sampling_methods",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=steps,
        final_answer=answer,
        dedup_key=dedup_key,
    )


def generate_modelled_example_sampling_methods(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["stratified", "scenario"])
    if shape == "stratified":
        prompt, steps, answer, _ = _stratified_question(rng)
        teaching_steps = [
            "A stratified sample keeps each subgroup (stratum) represented in the same proportion as it "
            "appears in the whole population - so a bigger subgroup gets proportionally more people "
            "sampled from it, not the same number as a smaller subgroup.",
            *steps,
            f"So {answer} students from that group should be included, keeping the sample proportional "
            "to the whole population.",
        ]
        worked_calculation = list(steps)
    else:
        prompt, steps, answer, _ = _scenario_question(rng)
        teaching_steps = [
            "Questions about sampling are asking you to judge whether every member of the population had "
            "a fair, known chance of being included - if not, the sample can't safely represent the "
            "whole population.",
            *steps,
            f"So the key point here is: {answer}",
        ]
        worked_calculation = list(steps)

    return ModelledExample(
        topic_id="sampling_methods",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_SAMPLING_METHODS = TopicDefinition(
    id="sampling_methods",
    display_name="Sampling and Populations",
    description="Identify sources of sampling bias, choose a suitable sampling method, or calculate a stratified sample size.",
    generate=generate_sampling_methods,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_sampling_methods,
)
