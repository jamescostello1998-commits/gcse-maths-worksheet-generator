import itertools
import random
from decimal import Decimal
from fractions import Fraction
from typing import Optional

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "probability"
GROUP = "Probability"

COLOURS = ["red", "blue", "green", "yellow", "purple"]


def generate_single_event(tier: Tier, rng: random.Random) -> Question:
    n_colours = rng.randint(2, 4)
    colours = rng.sample(COLOURS, n_colours)
    counts = [rng.randint(2, 8) for _ in colours]
    total = sum(counts)
    target_idx = rng.randrange(n_colours)
    target_colour = colours[target_idx]
    favourable = counts[target_idx]
    formula_prob = Fraction(favourable, total)

    items = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    brute_count = sum(1 for it in items if it == target_colour)
    brute_prob = Fraction(brute_count, len(items))
    if brute_prob != formula_prob:
        raise ValueError("single_event verification failed")

    bag_desc = ", ".join(f"{cnt} {c}" for c, cnt in zip(colours, counts))
    steps = [
        f"Total counters = {total}",
        f"Number of {target_colour} counters = {favourable}",
        f"P({target_colour}) = {favourable}/{total} = {formula_prob.numerator}/{formula_prob.denominator}",
    ]
    return Question(
        topic_id="probability_single_event",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is {target_colour}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"single:{colours}:{counts}:{target_colour}",
        diagram=DiagramSpec(
            kind="bag_of_counters", params={"counts": dict(zip(colours, counts)), "highlight": target_colour}
        ),
    )


def generate_modelled_example_single_event(tier: Tier, rng: random.Random) -> ModelledExample:
    n_colours = rng.randint(2, 4)
    colours = rng.sample(COLOURS, n_colours)
    counts = [rng.randint(2, 8) for _ in colours]
    total = sum(counts)
    target_idx = rng.randrange(n_colours)
    target_colour = colours[target_idx]
    favourable = counts[target_idx]
    formula_prob = Fraction(favourable, total)

    items = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    brute_count = sum(1 for it in items if it == target_colour)
    brute_prob = Fraction(brute_count, len(items))
    if brute_prob != formula_prob:
        raise ValueError("modelled example single_event verification failed")

    bag_desc = ", ".join(f"{cnt} {c}" for c, cnt in zip(colours, counts))
    simplify_note = (
        f", which simplifies to {formula_prob.numerator}/{formula_prob.denominator}"
        if favourable != formula_prob.numerator or total != formula_prob.denominator
        else ""
    )
    teaching_steps = [
        "Probability compares how many ways an event CAN happen to how many outcomes are possible "
        "in total, as long as every outcome is equally likely.",
        f"Count the total number of counters in the bag: {' + '.join(str(c) for c in counts)} = {total}. "
        "This is the total number of equally likely outcomes.",
        f"Count how many of those are {target_colour}: {favourable}. This is the number of favourable outcomes.",
        f"P({target_colour}) = favourable outcomes ÷ total outcomes = {favourable}/{total}{simplify_note}.",
    ]
    worked_calculation = [
        f"Total outcomes = {' + '.join(str(c) for c in counts)} = {total}",
        f"P({target_colour}) = {favourable}/{total}",
    ]
    if simplify_note:
        worked_calculation.append(f"= {formula_prob.numerator}/{formula_prob.denominator}")

    return ModelledExample(
        topic_id="probability_single_event",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is {target_colour}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        diagram=DiagramSpec(
            kind="bag_of_counters", params={"counts": dict(zip(colours, counts)), "highlight": target_colour}
        ),
    )


def generate_complement(tier: Tier, rng: random.Random) -> Question:
    n_colours = rng.randint(2, 4)
    colours = rng.sample(COLOURS, n_colours)
    counts = [rng.randint(2, 8) for _ in colours]
    total = sum(counts)
    target_idx = rng.randrange(n_colours)
    target_colour = colours[target_idx]
    favourable = counts[target_idx]
    p_event = Fraction(favourable, total)
    p_complement = 1 - p_event

    items = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    brute_not = sum(1 for it in items if it != target_colour)
    brute_prob = Fraction(brute_not, len(items))
    if brute_prob != p_complement:
        raise ValueError("complement verification failed")

    bag_desc = ", ".join(f"{cnt} {c}" for c, cnt in zip(colours, counts))
    steps = [
        f"P({target_colour}) = {favourable}/{total} = {p_event.numerator}/{p_event.denominator}",
        f"P(not {target_colour}) = 1 - {p_event.numerator}/{p_event.denominator} = "
        f"{p_complement.numerator}/{p_complement.denominator}",
    ]
    return Question(
        topic_id="probability_complement",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is NOT {target_colour}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{p_complement.numerator}/{p_complement.denominator}",
        dedup_key=f"complement:{colours}:{counts}:{target_colour}",
        diagram=DiagramSpec(
            kind="bag_of_counters", params={"counts": dict(zip(colours, counts)), "highlight": target_colour}
        ),
    )


def generate_modelled_example_complement(tier: Tier, rng: random.Random) -> ModelledExample:
    n_colours = rng.randint(2, 4)
    colours = rng.sample(COLOURS, n_colours)
    counts = [rng.randint(2, 8) for _ in colours]
    total = sum(counts)
    target_idx = rng.randrange(n_colours)
    target_colour = colours[target_idx]
    favourable = counts[target_idx]
    p_event = Fraction(favourable, total)
    p_complement = 1 - p_event

    items = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    brute_not = sum(1 for it in items if it != target_colour)
    brute_prob = Fraction(brute_not, len(items))
    if brute_prob != p_complement:
        raise ValueError("modelled example complement verification failed")

    bag_desc = ", ".join(f"{cnt} {c}" for c, cnt in zip(colours, counts))
    teaching_steps = [
        "The complement of an event is 'the event doesn't happen' - together an event and its complement "
        "cover every possibility, so their probabilities must add up to exactly 1.",
        f"First find P({target_colour}) the normal way: there are {favourable} {target_colour} counters out "
        f"of {total} in total, so P({target_colour}) = {favourable}/{total}.",
        f"Since P({target_colour}) + P(not {target_colour}) = 1, we can find P(not {target_colour}) by "
        "subtracting from 1, instead of counting all the other counters directly.",
        f"P(not {target_colour}) = 1 - {p_event.numerator}/{p_event.denominator} = "
        f"{p_complement.numerator}/{p_complement.denominator}.",
    ]
    worked_calculation = [
        f"P({target_colour}) = {favourable}/{total} = {p_event.numerator}/{p_event.denominator}",
        f"P(not {target_colour}) = 1 - {p_event.numerator}/{p_event.denominator}",
        f"= {p_complement.numerator}/{p_complement.denominator}",
    ]
    return ModelledExample(
        topic_id="probability_complement",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is NOT {target_colour}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{p_complement.numerator}/{p_complement.denominator}",
        diagram=DiagramSpec(
            kind="bag_of_counters", params={"counts": dict(zip(colours, counts)), "highlight": target_colour}
        ),
    )


def generate_combined_dice(tier: Tier, rng: random.Random) -> Question:
    event = rng.choice(["both_specific", "sum_equals", "at_least_one"])
    sample = list(itertools.product(range(1, 7), range(1, 7)))

    if event == "both_specific":
        target = rng.randint(1, 6)
        matches = [o for o in sample if o[0] == target and o[1] == target]
        formula_prob = Fraction(1, 6) * Fraction(1, 6)
        prompt = f"Two fair six-sided dice are rolled. Find the probability that both dice show {target}."
        steps = [
            f"P(first die is {target}) = 1/6, P(second die is {target}) = 1/6",
            f"Independent events multiply: P(both {target}) = 1/6 × 1/6 = "
            f"{formula_prob.numerator}/{formula_prob.denominator}",
        ]
        key_param = target
    elif event == "sum_equals":
        target_sum = rng.randint(2, 12)
        matches = [o for o in sample if o[0] + o[1] == target_sum]
        ways = 6 - abs(target_sum - 7)
        formula_prob = Fraction(ways, 36)
        prompt = (
            "Two fair six-sided dice are rolled. Find the probability that the two "
            f"scores add up to {target_sum}."
        )
        steps = [
            f"Number of ways to score a total of {target_sum} out of 36 equally likely outcomes = {ways}",
            f"P(total = {target_sum}) = {ways}/36 = {formula_prob.numerator}/{formula_prob.denominator}",
        ]
        key_param = target_sum
    else:
        target = rng.randint(1, 6)
        matches = [o for o in sample if target in o]
        formula_prob = 1 - Fraction(5, 6) * Fraction(5, 6)
        prompt = f"Two fair six-sided dice are rolled. Find the probability that at least one die shows {target}."
        steps = [
            f"P(neither die shows {target}) = 5/6 × 5/6 = 25/36",
            f"P(at least one {target}) = 1 - 25/36 = {formula_prob.numerator}/{formula_prob.denominator}",
        ]
        key_param = target

    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError(f"combined_dice verification failed for event={event}")

    return Question(
        topic_id="probability_combined_dice",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"combined_dice:{event}:{key_param}",
        diagram=DiagramSpec(kind="dice", params={"values": [rng.randint(1, 6), rng.randint(1, 6)]}),
    )


def generate_modelled_example_combined_dice(tier: Tier, rng: random.Random) -> ModelledExample:
    event = rng.choice(["both_specific", "sum_equals", "at_least_one"])
    sample = list(itertools.product(range(1, 7), range(1, 7)))

    if event == "both_specific":
        target = rng.randint(1, 6)
        matches = [o for o in sample if o[0] == target and o[1] == target]
        formula_prob = Fraction(1, 6) * Fraction(1, 6)
        prompt = f"Two fair six-sided dice are rolled. Find the probability that both dice show {target}."
        teaching_steps = [
            "When two dice are rolled, what happens on one die doesn't affect the other - the events are "
            "independent, so we can multiply their individual probabilities together.",
            f"P(first die shows {target}) = 1/6, since each of the 6 faces is equally likely.",
            f"P(second die shows {target}) = 1/6 too, for the same reason.",
            "For independent events, P(both happen) = P(first) × P(second) = 1/6 × 1/6 = "
            f"{formula_prob.numerator}/{formula_prob.denominator}.",
        ]
        worked_calculation = [
            f"P(both dice show {target}) = 1/6 × 1/6",
            f"= {formula_prob.numerator}/{formula_prob.denominator}",
        ]
    elif event == "sum_equals":
        target_sum = rng.randint(2, 12)
        matches = [o for o in sample if o[0] + o[1] == target_sum]
        ways = 6 - abs(target_sum - 7)
        formula_prob = Fraction(ways, 36)
        prompt = (
            "Two fair six-sided dice are rolled. Find the probability that the two "
            f"scores add up to {target_sum}."
        )
        teaching_steps = [
            "There are 6 × 6 = 36 equally likely ways the two dice can land, since each of the 6 outcomes on "
            "the first die can pair with each of the 6 outcomes on the second.",
            f"List (or count) the pairs that add up to {target_sum} - there are {ways} such pairs out of "
            "the 36.",
            "Probability is favourable outcomes divided by total outcomes, using the full list of 36 pairs "
            "as the sample space rather than treating each die separately.",
            f"P(total = {target_sum}) = {ways}/36 = {formula_prob.numerator}/{formula_prob.denominator}.",
        ]
        worked_calculation = [
            f"Ways to score {target_sum} out of 36 = {ways}",
            f"P(total = {target_sum}) = {ways}/36 = {formula_prob.numerator}/{formula_prob.denominator}",
        ]
    else:
        target = rng.randint(1, 6)
        matches = [o for o in sample if target in o]
        formula_prob = 1 - Fraction(5, 6) * Fraction(5, 6)
        prompt = f"Two fair six-sided dice are rolled. Find the probability that at least one die shows {target}."
        teaching_steps = [
            "'At least one' can be awkward to count directly (it covers first-only, second-only, and both), "
            "so it's usually easier to use the complement: at least one is the opposite of neither.",
            f"P(neither die shows {target}) = 5/6 × 5/6 = 25/36, since each die independently avoids "
            f"{target} with probability 5/6.",
            "Since 'at least one' and 'neither' are complements, their probabilities add to 1.",
            f"P(at least one {target}) = 1 - 25/36 = {formula_prob.numerator}/{formula_prob.denominator}.",
        ]
        worked_calculation = [
            f"P(neither die shows {target}) = 5/6 × 5/6 = 25/36",
            f"P(at least one {target}) = 1 - 25/36 = {formula_prob.numerator}/{formula_prob.denominator}",
        ]

    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError(f"modelled example combined_dice verification failed for event={event}")

    return ModelledExample(
        topic_id="probability_combined_dice",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        diagram=DiagramSpec(kind="dice", params={"values": [rng.randint(1, 6), rng.randint(1, 6)]}),
    )


def generate_conditional_without_replacement(tier: Tier, rng: random.Random) -> Question:
    colours = rng.sample(COLOURS, 2)
    counts = [rng.randint(3, 7) for _ in colours]
    total = sum(counts)

    total_ordered_pairs = total * (total - 1)
    same_colour_pairs = sum(cnt * (cnt - 1) for cnt in counts)
    formula_prob = Fraction(same_colour_pairs, total_ordered_pairs)

    labels = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    same_count = sum(1 for i, j in itertools.permutations(range(total), 2) if labels[i] == labels[j])
    brute_prob = Fraction(same_count, total_ordered_pairs)
    if brute_prob != formula_prob:
        raise ValueError("conditional_without_replacement verification failed")

    c1, c2 = colours
    n1, n2 = counts
    term1 = Fraction(n1, total) * Fraction(n1 - 1, total - 1)
    term2 = Fraction(n2, total) * Fraction(n2 - 1, total - 1)
    steps = [
        f"P(both {c1}) = {n1}/{total} × {n1 - 1}/{total - 1} = {term1.numerator}/{term1.denominator}",
        f"P(both {c2}) = {n2}/{total} × {n2 - 1}/{total - 1} = {term2.numerator}/{term2.denominator}",
        f"P(both same colour) = {term1.numerator}/{term1.denominator} + {term2.numerator}/{term2.denominator} "
        f"= {formula_prob.numerator}/{formula_prob.denominator}",
    ]
    return Question(
        topic_id="probability_conditional",
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random "
            "without replacement. Find the probability that both counters are the same colour."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"conditional:{colours}:{counts}",
        diagram=DiagramSpec(kind="bag_of_counters", params={"counts": {c1: n1, c2: n2}}),
    )


def generate_modelled_example_conditional_without_replacement(tier: Tier, rng: random.Random) -> ModelledExample:
    colours = rng.sample(COLOURS, 2)
    counts = [rng.randint(3, 7) for _ in colours]
    total = sum(counts)

    total_ordered_pairs = total * (total - 1)
    same_colour_pairs = sum(cnt * (cnt - 1) for cnt in counts)
    formula_prob = Fraction(same_colour_pairs, total_ordered_pairs)

    labels = [c for c, cnt in zip(colours, counts) for _ in range(cnt)]
    same_count = sum(1 for i, j in itertools.permutations(range(total), 2) if labels[i] == labels[j])
    brute_prob = Fraction(same_count, total_ordered_pairs)
    if brute_prob != formula_prob:
        raise ValueError("modelled example conditional_without_replacement verification failed")

    c1, c2 = colours
    n1, n2 = counts
    term1 = Fraction(n1, total) * Fraction(n1 - 1, total - 1)
    term2 = Fraction(n2, total) * Fraction(n2 - 1, total - 1)
    teaching_steps = [
        "Once the first counter is picked and NOT replaced, the bag has one fewer counter in it - so the "
        "probability for the second pick depends on what happened on the first pick. This is why it's called "
        "'without replacement' or 'conditional' probability.",
        f"'Both the same colour' can happen two different ways: both {c1}, or both {c2} - so we work out "
        "each way separately and add them together at the end.",
        f"For both {c1}: P(1st is {c1}) = {n1}/{total}. Now only {n1 - 1} {c1} counters remain out of "
        f"{total - 1} total, so P(2nd is {c1} | 1st was {c1}) = {n1 - 1}/{total - 1}. Multiply these: "
        f"{term1.numerator}/{term1.denominator}.",
        f"Do the same for both {c2}: {n2}/{total} × {n2 - 1}/{total - 1} = "
        f"{term2.numerator}/{term2.denominator}. Add the two ways together, since either satisfies "
        f"'both the same colour': {term1.numerator}/{term1.denominator} + {term2.numerator}/{term2.denominator} "
        f"= {formula_prob.numerator}/{formula_prob.denominator}.",
    ]
    worked_calculation = [
        f"P(both {c1}) = {n1}/{total} × {n1 - 1}/{total - 1} = {term1.numerator}/{term1.denominator}",
        f"P(both {c2}) = {n2}/{total} × {n2 - 1}/{total - 1} = {term2.numerator}/{term2.denominator}",
        f"P(same colour) = {term1.numerator}/{term1.denominator} + {term2.numerator}/{term2.denominator}",
        f"= {formula_prob.numerator}/{formula_prob.denominator}",
    ]
    return ModelledExample(
        topic_id="probability_conditional",
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random "
            "without replacement. Find the probability that both counters are the same colour."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        diagram=DiagramSpec(kind="bag_of_counters", params={"counts": {c1: n1, c2: n2}}),
    )


def _spinner_labels(rng: random.Random, sides: int) -> list[str]:
    """A random label set for an n-sided spinner: either numeric (1..sides)
    or the initial letters of `sides` distinct colours (all of COLOURS' first
    letters - R, B, G, Y, P - are distinct, so this never collides)."""
    style = rng.choice(["numeric", "colour"])
    if style == "numeric":
        return [str(i) for i in range(1, sides + 1)]
    return [c[0].upper() for c in rng.sample(COLOURS, sides)]


def _build_listing_outcomes(rng: random.Random):
    """Shared setup for the two-event listing scenario, used by both the
    normal generator and its modelled-example twin. Returns (context sentence,
    vals_a, vals_b, scenario name)."""
    scenario = rng.choice(
        ["coin_die", "two_coins", "coin_spinner3", "coin_spinner4", "two_spinner3", "spinner3_spinner4"]
    )
    if scenario == "coin_die":
        vals_a, vals_b = ["H", "T"], [str(i) for i in range(1, 7)]
        context = "A coin is flipped and a die is rolled."
    elif scenario == "two_coins":
        vals_a, vals_b = ["H", "T"], ["H", "T"]
        context = "Two coins are flipped."
    elif scenario == "coin_spinner3":
        vals_a = ["H", "T"]
        vals_b = _spinner_labels(rng, 3)
        context = f"A coin is flipped and a 3-sided spinner (labelled {', '.join(vals_b)}) is spun."
    elif scenario == "coin_spinner4":
        vals_a = ["H", "T"]
        vals_b = _spinner_labels(rng, 4)
        context = f"A coin is flipped and a 4-sided spinner (labelled {', '.join(vals_b)}) is spun."
    elif scenario == "two_spinner3":
        vals_a = _spinner_labels(rng, 3)
        vals_b = _spinner_labels(rng, 3)
        context = (
            f"Two 3-sided spinners are spun: one labelled {', '.join(vals_a)} "
            f"and the other labelled {', '.join(vals_b)}."
        )
    else:  # spinner3_spinner4
        vals_a = _spinner_labels(rng, 3)
        vals_b = _spinner_labels(rng, 4)
        context = (
            f"A 3-sided spinner (labelled {', '.join(vals_a)}) and a 4-sided spinner "
            f"(labelled {', '.join(vals_b)}) are both spun."
        )

    total = len(vals_a) * len(vals_b)
    if not (4 <= total <= 12):
        raise ValueError("listing_outcomes total outcomes out of expected range")

    # Only single-spinner scenarios get an illustration - the two-spinner scenarios
    # would need two diagrams shown at once, which draw_spinner doesn't support.
    diagram = DiagramSpec(kind="spinner", params={"sectors": vals_b}) if scenario in (
        "coin_spinner3", "coin_spinner4",
    ) else None

    return context, vals_a, vals_b, scenario, diagram


def generate_listing_outcomes(tier: Tier, rng: random.Random) -> Question:
    context, vals_a, vals_b, scenario, diagram = _build_listing_outcomes(rng)
    total = len(vals_a) * len(vals_b)

    listing = [f"{a}{b}" for a in vals_a for b in vals_b]

    brute = list(itertools.product(vals_a, vals_b))
    brute_listing = [f"{a}{b}" for a, b in brute]
    if len(brute_listing) != len(listing) or set(brute_listing) != set(listing):
        raise ValueError("listing_outcomes verification failed")

    steps = [
        f"There are {len(vals_a)} possible outcomes for the first event and {len(vals_b)} for the "
        f"second, so there are {len(vals_a)} × {len(vals_b)} = {total} possible combined outcomes.",
        "For each outcome of the first event, list every outcome of the second event: " + ", ".join(listing),
    ]
    return Question(
        topic_id="probability_listing_outcomes",
        tier=Tier.FOUNDATION,
        prompt=f"{context} List all the possible outcomes.",
        solution_steps=tuple(steps),
        final_answer=", ".join(listing),
        dedup_key=f"listing:{scenario}:{vals_a}:{vals_b}",
        diagram=diagram,
    )


def generate_modelled_example_listing_outcomes(tier: Tier, rng: random.Random) -> ModelledExample:
    context, vals_a, vals_b, scenario, diagram = _build_listing_outcomes(rng)
    total = len(vals_a) * len(vals_b)

    listing = [f"{a}{b}" for a in vals_a for b in vals_b]

    brute = list(itertools.product(vals_a, vals_b))
    brute_listing = [f"{a}{b}" for a, b in brute]
    if len(brute_listing) != len(listing) or set(brute_listing) != set(listing):
        raise ValueError("modelled example listing_outcomes verification failed")

    teaching_steps = [
        "When two events happen together, every outcome of the first event can be paired with every "
        "outcome of the second - so the total number of combined outcomes is found by multiplying the "
        "number of outcomes for each event, not adding them.",
        f"Here the first event has {len(vals_a)} possible outcomes and the second has {len(vals_b)}, "
        f"so there are {len(vals_a)} × {len(vals_b)} = {total} combined outcomes altogether.",
        "The safest way to list every outcome without missing (or repeating) one is to work through the "
        "first event's outcomes one at a time, and for each one write down every outcome of the second "
        "event before moving on to the next.",
        f"Following that method systematically gives: {', '.join(listing)}.",
    ]
    worked_calculation = [
        f"{len(vals_a)} × {len(vals_b)} = {total} outcomes",
        ", ".join(listing),
    ]

    return ModelledExample(
        topic_id="probability_listing_outcomes",
        tier=Tier.FOUNDATION,
        prompt=f"{context} List all the possible outcomes.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(listing),
        diagram=diagram,
    )


def _independent_event(rng: random.Random, exclude_kind: Optional[str] = None):
    """A single random event for the AND rule: a description, a short name
    for the target outcome, its probability as an exact Fraction, a kind tag
    (used to avoid picking the same physical object twice), and diagram info
    for that event (None for a coin - not one of the illustrated diagram
    kinds; an int target face for a die; a (sides, target) pair for a spinner)."""
    kinds = [k for k in ("coin", "die", "spinner") if k != exclude_kind]
    kind = rng.choice(kinds)
    if kind == "coin":
        return "a coin is flipped", "heads", Fraction(1, 2), kind, None
    if kind == "die":
        target = rng.randint(1, 6)
        return "a fair die is rolled", f"rolling a {target}", Fraction(1, 6), kind, target
    sides = rng.choice([3, 4, 5, 6, 8, 10])
    target = rng.randint(1, sides)
    return f"a {sides}-sided spinner is spun", f"landing on {target}", Fraction(1, sides), kind, (sides, target)


def _build_or_rule(rng: random.Random):
    denom = rng.choice([5, 8, 10, 12])
    colour_a, colour_b = rng.sample(COLOURS, 2)
    num_a = rng.randint(1, denom - 2)
    num_b = rng.randint(1, denom - num_a - 1) if denom - num_a - 1 >= 1 else 1
    p_a = Fraction(num_a, denom)
    p_b = Fraction(num_b, denom)
    formula_prob = p_a + p_b

    dec_sum = (Decimal(num_a) / Decimal(denom)) + (Decimal(num_b) / Decimal(denom))
    dec_formula = Decimal(formula_prob.numerator) / Decimal(formula_prob.denominator)
    if abs(dec_sum - dec_formula) > Decimal("1e-15"):
        raise ValueError("and_or_rule (or) verification failed")

    prompt = (
        f"A bag contains coloured counters. P({colour_a}) = {num_a}/{denom}. "
        f"P({colour_b}) = {num_b}/{denom}. A counter cannot be both colours. "
        f"Find P({colour_a} or {colour_b})."
    )
    steps = [
        f"A counter cannot be both {colour_a} and {colour_b}, so these events are mutually exclusive.",
        "For mutually exclusive events, P(A or B) = P(A) + P(B).",
        f"P({colour_a} or {colour_b}) = {num_a}/{denom} + {num_b}/{denom} = "
        f"{formula_prob.numerator}/{formula_prob.denominator}",
    ]
    dedup_key = f"or:{colour_a}:{colour_b}:{num_a}:{num_b}:{denom}"
    counts = {colour_a: num_a, colour_b: num_b}
    other = denom - num_a - num_b
    if other > 0:
        counts["other"] = other
    diagram = DiagramSpec(kind="bag_of_counters", params={"counts": counts})
    return prompt, steps, formula_prob, dedup_key, colour_a, colour_b, num_a, num_b, denom, diagram


def _build_and_rule(rng: random.Random):
    desc_a, name_a, p_a, kind_a, info_a = _independent_event(rng)
    desc_b, name_b, p_b, kind_b, info_b = _independent_event(rng, exclude_kind=kind_a)
    formula_prob = p_a * p_b

    dec_product = (Decimal(p_a.numerator) / Decimal(p_a.denominator)) * (
        Decimal(p_b.numerator) / Decimal(p_b.denominator)
    )
    dec_formula = Decimal(formula_prob.numerator) / Decimal(formula_prob.denominator)
    if abs(dec_product - dec_formula) > Decimal("1e-15"):
        raise ValueError("and_or_rule (and) verification failed")

    cap_desc_a = desc_a[0].upper() + desc_a[1:]
    prompt = (
        f"{cap_desc_a} (P({name_a}) = {p_a.numerator}/{p_a.denominator}) and {desc_b} "
        f"(P({name_b}) = {p_b.numerator}/{p_b.denominator}). These two events are independent. "
        f"Find P({name_a} and {name_b})."
    )
    steps = [
        f"P({name_a}) = {p_a.numerator}/{p_a.denominator}",
        f"P({name_b}) = {p_b.numerator}/{p_b.denominator}",
        f"These are independent events, so P({name_a} and {name_b}) = P({name_a}) × P({name_b}) = "
        f"{p_a.numerator}/{p_a.denominator} × {p_b.numerator}/{p_b.denominator} = "
        f"{formula_prob.numerator}/{formula_prob.denominator}",
    ]
    dedup_key = f"and:{kind_a}:{kind_b}:{name_a}:{name_b}:{p_a}:{p_b}"

    # Illustrate whichever non-coin object is present (a die takes priority if
    # both a die and a spinner appear, since a coin can only pair with at most
    # one of them).
    if kind_a == "die" or kind_b == "die":
        target = info_a if kind_a == "die" else info_b
        diagram = DiagramSpec(kind="dice", params={"values": [target], "highlight": [0]})
    elif kind_a == "spinner" or kind_b == "spinner":
        sides, target = info_a if kind_a == "spinner" else info_b
        diagram = DiagramSpec(
            kind="spinner", params={"sectors": [str(i) for i in range(1, sides + 1)], "highlight": [target - 1]}
        )
    else:
        diagram = None

    return prompt, steps, formula_prob, dedup_key, name_a, name_b, p_a, p_b, diagram


def generate_and_or_rule(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < 0.5:
        result = _build_or_rule(rng)
    else:
        result = _build_and_rule(rng)
    prompt, steps, formula_prob, dedup_key, diagram = result[0], result[1], result[2], result[3], result[-1]

    return Question(
        topic_id="probability_and_or_rule",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_modelled_example_and_or_rule(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < 0.5:
        prompt, _steps, formula_prob, _key, colour_a, colour_b, num_a, num_b, denom, diagram = _build_or_rule(rng)
        teaching_steps = [
            "Two events are 'mutually exclusive' if they can never both happen at the same time - here a "
            "single counter obviously can't be both colours at once.",
            "For mutually exclusive events, the OR rule says you can simply ADD the individual "
            "probabilities together to get the probability that either one happens.",
            f"P({colour_a}) = {num_a}/{denom} and P({colour_b}) = {num_b}/{denom}, so P({colour_a} or "
            f"{colour_b}) = {num_a}/{denom} + {num_b}/{denom}.",
            f"Adding the numerators (since the denominators already match) gives "
            f"{formula_prob.numerator}/{formula_prob.denominator}.",
        ]
        worked_calculation = [
            f"P({colour_a} or {colour_b}) = {num_a}/{denom} + {num_b}/{denom}",
            f"= {formula_prob.numerator}/{formula_prob.denominator}",
        ]
    else:
        prompt, _steps, formula_prob, _key, name_a, name_b, p_a, p_b, diagram = _build_and_rule(rng)
        teaching_steps = [
            "Two events are 'independent' if the outcome of one has no effect at all on the outcome of "
            "the other - here the two events happen on completely separate objects.",
            "For independent events, the AND rule says you MULTIPLY the individual probabilities together "
            "to get the probability that both happen.",
            f"P({name_a}) = {p_a.numerator}/{p_a.denominator} and P({name_b}) = "
            f"{p_b.numerator}/{p_b.denominator}, so P({name_a} and {name_b}) = "
            f"{p_a.numerator}/{p_a.denominator} × {p_b.numerator}/{p_b.denominator}.",
            f"Multiplying numerators together and denominators together gives "
            f"{formula_prob.numerator}/{formula_prob.denominator}.",
        ]
        worked_calculation = [
            f"P({name_a} and {name_b}) = {p_a.numerator}/{p_a.denominator} × {p_b.numerator}/{p_b.denominator}",
            f"= {formula_prob.numerator}/{formula_prob.denominator}",
        ]

    return ModelledExample(
        topic_id="probability_and_or_rule",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        diagram=diagram,
    )


_EXPECTATION_DENOMINATORS = [4, 5, 6, 8, 10, 12, 20, 25]
_EXPECTATION_MULTIPLIERS = [4, 5, 6, 8, 10, 15, 20]


def _build_expectation(rng: random.Random):
    denominator = rng.choice(_EXPECTATION_DENOMINATORS)
    numerator = rng.randint(1, denominator - 1)
    trials = denominator * rng.choice(_EXPECTATION_MULTIPLIERS)
    frac = f"{numerator}/{denominator}"

    context = rng.choice(["die", "spinner", "coin", "batch", "bus"])
    diagram = None
    if context == "die":
        target = rng.randint(1, 6)
        prompt = (
            f"A biased die has P(rolling a {target}) = {frac}. The die is rolled {trials} times. "
            f"How many times would you expect to get a {target}?"
        )
        event_desc = f"get a {target}"
        ctx_key = f"die:{target}"
        # A biased die is still a physical 6-sided die - illustrating a standard
        # die with the target face highlighted is faithful without inventing
        # anything. The spinner branch below has no side-count to draw from, so
        # it's deliberately left without a diagram.
        diagram = DiagramSpec(kind="dice", params={"values": [target], "highlight": [0]})
    elif context == "spinner":
        colour = rng.choice(COLOURS)
        prompt = (
            f"A spinner has P(landing on {colour}) = {frac}. The spinner is spun {trials} times. "
            f"How many times would you expect it to land on {colour}?"
        )
        event_desc = f"land on {colour}"
        ctx_key = f"spinner:{colour}"
    elif context == "coin":
        prompt = (
            f"A biased coin has P(heads) = {frac}. The coin is flipped {trials} times. "
            "How many times would you expect to get heads?"
        )
        event_desc = "get heads"
        ctx_key = "coin"
    elif context == "batch":
        prompt = (
            f"In a batch of items, the probability that an item is defective is {frac}. "
            f"{trials} items are checked. How many would you expect to be defective?"
        )
        event_desc = "be defective"
        ctx_key = "batch"
    else:
        prompt = (
            f"The probability that a particular bus is late is {frac}. The bus runs {trials} times. "
            "On how many occasions would you expect it to be late?"
        )
        event_desc = "be late"
        ctx_key = "bus"

    expected_frac = Fraction(numerator, denominator) * trials
    if expected_frac.denominator != 1:
        raise ValueError("expectation did not resolve to a whole number")
    expected_primary = expected_frac.numerator

    expected_check = (trials // denominator) * numerator
    if expected_check != expected_primary:
        raise ValueError("expectation verification failed")

    steps = [
        f"Expected number of times = probability × number of trials = {frac} × {trials}",
        f"= {expected_primary}",
    ]
    dedup_key = f"expectation:{ctx_key}:{numerator}:{denominator}:{trials}"
    return prompt, steps, expected_primary, dedup_key, event_desc, numerator, denominator, trials, frac, diagram


def generate_expectation(tier: Tier, rng: random.Random) -> Question:
    prompt, steps, expected, dedup_key, *_, diagram = _build_expectation(rng)
    return Question(
        topic_id="probability_expectation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(expected),
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_modelled_example_expectation(tier: Tier, rng: random.Random) -> ModelledExample:
    prompt, _steps, expected, _key, event_desc, numerator, denominator, trials, frac, diagram = _build_expectation(
        rng
    )

    teaching_steps = [
        "To find an 'expected' frequency, we assume the probability holds exactly and scale it up to the "
        "number of trials - it's a prediction of what should happen on average, not a guarantee of the "
        "exact result every time.",
        f"The probability of the event is {frac}, meaning we expect it roughly {numerator} times out of "
        f"every {denominator} trials.",
        f"There are {trials} trials in total, and {trials} ÷ {denominator} = {trials // denominator} "
        f"complete groups of {denominator}, so we expect {numerator} occurrences in each of those groups.",
        f"Expected number of times to {event_desc} = {frac} × {trials} = {expected}.",
    ]
    worked_calculation = [
        f"{frac} × {trials}",
        f"= {expected}",
    ]

    return ModelledExample(
        topic_id="probability_expectation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(expected),
        diagram=diagram,
    )


TOPIC_SINGLE_EVENT = TopicDefinition(
    id="probability_single_event",
    display_name="Single Event",
    description="Find the probability of a single equally-likely outcome.",
    generate=generate_single_event,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_single_event,
)

TOPIC_COMPLEMENT = TopicDefinition(
    id="probability_complement",
    display_name="Complement",
    description="Use the complement rule: P(not A) = 1 - P(A).",
    generate=generate_complement,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_complement,
)

TOPIC_COMBINED_DICE = TopicDefinition(
    id="probability_combined_dice",
    display_name="Combined Dice",
    description="Find the probability of combined outcomes when rolling two dice.",
    generate=generate_combined_dice,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_combined_dice,
)

TOPIC_CONDITIONAL = TopicDefinition(
    id="probability_conditional",
    display_name="Conditional (Without Replacement)",
    description="Find the probability of picking two items of the same type without replacement.",
    generate=generate_conditional_without_replacement,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_conditional_without_replacement,
)

TOPIC_LISTING_OUTCOMES = TopicDefinition(
    id="probability_listing_outcomes",
    display_name="Listing Outcomes",
    description="Systematically list all the possible outcomes of two combined events.",
    generate=generate_listing_outcomes,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_listing_outcomes,
)

TOPIC_AND_OR_RULE = TopicDefinition(
    id="probability_and_or_rule",
    display_name="AND / OR Rule",
    description="Use the OR rule for mutually exclusive events and the AND rule for independent events.",
    generate=generate_and_or_rule,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_and_or_rule,
)

TOPIC_EXPECTATION = TopicDefinition(
    id="probability_expectation",
    display_name="Expected Frequency",
    description="Find the expected number of occurrences of an event given its probability and the number of trials.",
    generate=generate_expectation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_expectation,
)
