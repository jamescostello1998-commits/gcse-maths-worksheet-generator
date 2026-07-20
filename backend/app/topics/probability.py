import itertools
import random
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
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
