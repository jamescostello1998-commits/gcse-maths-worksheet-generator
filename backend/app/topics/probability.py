import itertools
import random
from fractions import Fraction

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

TOPIC_ID = "probability"

COLOURS = ["red", "blue", "green", "yellow", "purple"]


def _generate_single_event(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is {target_colour}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"single:{colours}:{counts}:{target_colour}",
    )


def _generate_complement(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {bag_desc} counters. A counter is picked at random. "
            f"Find the probability that it is NOT {target_colour}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{p_complement.numerator}/{p_complement.denominator}",
        dedup_key=f"complement:{colours}:{counts}:{target_colour}",
    )


def _generate_combined_dice(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"combined_dice:{event}:{key_param}",
    )


def _generate_conditional_without_replacement(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random "
            "without replacement. Find the probability that both counters are the same colour."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"conditional:{colours}:{counts}",
    )


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["single_event", "complement"])
        return _generate_single_event(rng) if shape == "single_event" else _generate_complement(rng)
    shape = rng.choice(["combined_dice", "conditional"])
    return _generate_combined_dice(rng) if shape == "combined_dice" else _generate_conditional_without_replacement(rng)


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Probability",
    description="Single and combined events, the complement rule, and probability without replacement.",
    generate=generate,
)
