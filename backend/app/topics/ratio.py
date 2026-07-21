import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "ratio_proportion"
GROUP = "Ratio"


def _rand_part(rng: random.Random) -> int:
    return rng.randint(1, 9)


def generate_share_two(tier: Tier, rng: random.Random) -> Question:
    a, b = _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 20)
    total = k * (a + b)
    share_a, share_b = a * k, b * k

    if share_a + share_b != total or share_a * b != share_b * a:
        raise ValueError("share_two verification failed")

    steps = [
        f"Total parts = {a} + {b} = {a + b}",
        f"Value of one part = {total} ÷ {a + b} = {k}",
        f"Share 1 = {a} × {k} = {share_a}",
        f"Share 2 = {b} × {k} = {share_b}",
    ]
    return Question(
        topic_id="ratio_share_two_part",
        tier=Tier.FOUNDATION,
        prompt=f"Share {total} in the ratio {a}:{b}.",
        solution_steps=tuple(steps),
        final_answer=f"{share_a} : {share_b}",
        dedup_key=f"share_two:{a}:{b}:{k}",
    )


def generate_modelled_example_share_two(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 20)
    total = k * (a + b)
    share_a, share_b = a * k, b * k

    # Independent verification via Fraction (separate path from the multiply-out above).
    if Fraction(share_a, total) != Fraction(a, a + b):
        raise ValueError("modelled example share_two verification failed")
    if share_a + share_b != total:
        raise ValueError("modelled example share_two verification failed (total)")

    teaching_steps = [
        f"Sharing {total} in the ratio {a}:{b} means splitting it into {a} + {b} = {a + b} equal "
        f"'parts' in total, then giving one side {a} of those parts and the other side {b} of them.",
        f"To find out what ONE part is worth, divide the total by the total number of parts: "
        f"{total} ÷ {a + b} = {k}.",
        f"Now scale each side of the ratio up by that value: the first share is {a} parts, so "
        f"{a} × {k} = {share_a}. The second share is {b} parts, so {b} × {k} = {share_b}.",
        f"As a check, the two shares should add back up to the original total: "
        f"{share_a} + {share_b} = {share_a + share_b}, which matches {total}.",
    ]
    worked_calculation = [
        f"Share {total} in the ratio {a}:{b}",
        f"Total parts = {a} + {b} = {a + b}",
        f"1 part = {total} ÷ {a + b} = {k}",
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}",
    ]
    return ModelledExample(
        topic_id="ratio_share_two_part",
        tier=Tier.FOUNDATION,
        prompt=f"Share {total} in the ratio {a}:{b}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{share_a} : {share_b}",
    )


def generate_find_share(tier: Tier, rng: random.Random) -> Question:
    a, b = _rand_part(rng), _rand_part(rng)
    while b == a:
        b = _rand_part(rng)
    k = rng.randint(2, 20)
    share_a, share_b = a * k, b * k
    target = rng.choice(["other_share", "total"])

    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("find_share verification failed")

    base_steps = [
        f"Value of one part = {share_a} ÷ {a} = {k}",
        f"Second amount = {b} × {k} = {share_b}",
    ]
    if target == "other_share":
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The first amount is {share_a}. "
            "Find the second amount."
        )
        answer = str(share_b)
        steps = base_steps
    else:
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The first amount is {share_a}. "
            "Find the total of both amounts."
        )
        answer = str(share_a + share_b)
        steps = base_steps + [f"Total = {share_a} + {share_b} = {share_a + share_b}"]

    return Question(
        topic_id="ratio_find_missing_share",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"find_share:{a}:{b}:{k}:{target}",
    )


def generate_modelled_example_find_share(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = _rand_part(rng), _rand_part(rng)
    while b == a:
        b = _rand_part(rng)
    k = rng.randint(2, 20)
    share_a, share_b = a * k, b * k
    target = rng.choice(["other_share", "total"])

    # Independent verification via Fraction (separate path from the multiply-out above).
    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("modelled example find_share verification failed")

    if target == "other_share":
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The first amount is {share_a}. "
            "Find the second amount."
        )
        answer = str(share_b)
        teaching_steps = [
            f"The ratio {a}:{b} tells us how the two amounts compare, but not their actual values — to "
            f"find those, we need to know what a single 'part' of the ratio is worth.",
            f"We're told the first amount, {share_a}, corresponds to {a} parts of the ratio. Dividing "
            f"tells us the value of one part: {share_a} ÷ {a} = {k}.",
            f"The second amount corresponds to {b} parts, so multiply the value of one part by {b}: "
            f"{b} × {k} = {share_b}.",
            f"So the second amount is {share_b}.",
        ]
        worked_calculation = [
            f"Ratio {a}:{b}, first amount = {share_a}",
            f"1 part = {share_a} ÷ {a} = {k}",
            f"Second amount = {b} × {k} = {share_b}",
        ]
    else:
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The first amount is {share_a}. "
            "Find the total of both amounts."
        )
        answer = str(share_a + share_b)
        teaching_steps = [
            f"The ratio {a}:{b} tells us how the two amounts compare, but not their actual values — to "
            "find those, we need to know what a single 'part' of the ratio is worth.",
            f"We're told the first amount, {share_a}, corresponds to {a} parts of the ratio. Dividing "
            f"tells us the value of one part: {share_a} ÷ {a} = {k}.",
            f"The second amount corresponds to {b} parts, so multiply the value of one part by {b}: "
            f"{b} × {k} = {share_b}.",
            f"The total of both amounts is the first amount plus the second amount: "
            f"{share_a} + {share_b} = {share_a + share_b}.",
        ]
        worked_calculation = [
            f"Ratio {a}:{b}, first amount = {share_a}",
            f"1 part = {share_a} ÷ {a} = {k}",
            f"Second amount = {b} × {k} = {share_b}",
            f"Total = {share_a} + {share_b} = {share_a + share_b}",
        ]

    return ModelledExample(
        topic_id="ratio_find_missing_share",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_share_three(tier: Tier, rng: random.Random) -> Question:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 15)
    total = k * (a + b + c)
    share_a, share_b, share_c = a * k, b * k, c * k

    if share_a + share_b + share_c != total:
        raise ValueError("share_three verification failed")

    steps = [
        f"Total parts = {a} + {b} + {c} = {a + b + c}",
        f"Value of one part = {total} ÷ {a + b + c} = {k}",
        f"Share 1 = {a} × {k} = {share_a}",
        f"Share 2 = {b} × {k} = {share_b}",
        f"Share 3 = {c} × {k} = {share_c}",
    ]
    return Question(
        topic_id="ratio_share_three_part",
        tier=Tier.HIGHER,
        prompt=f"Share {total} in the ratio {a}:{b}:{c}.",
        solution_steps=tuple(steps),
        final_answer=f"{share_a} : {share_b} : {share_c}",
        dedup_key=f"share_three:{a}:{b}:{c}:{k}",
    )


def generate_modelled_example_share_three(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 15)
    total = k * (a + b + c)
    share_a, share_b, share_c = a * k, b * k, c * k

    # Independent verification via Fraction (separate path from the multiply-out above).
    if Fraction(share_a, total) != Fraction(a, a + b + c):
        raise ValueError("modelled example share_three verification failed")
    if share_a + share_b + share_c != total:
        raise ValueError("modelled example share_three verification failed (total)")

    teaching_steps = [
        f"With a three-way ratio like {a}:{b}:{c}, the method is exactly the same as sharing between "
        f"two — just with one extra share. There are {a} + {b} + {c} = {a + b + c} equal parts in "
        "total.",
        f"To find the value of one part, divide the total by the total number of parts: "
        f"{total} ÷ {a + b + c} = {k}.",
        f"Then multiply each person's number of parts by that value: {a} × {k} = {share_a}, "
        f"{b} × {k} = {share_b}, and {c} × {k} = {share_c}.",
        f"As a check, all three shares should add back up to the original total: "
        f"{share_a} + {share_b} + {share_c} = {share_a + share_b + share_c}, which matches {total}.",
    ]
    worked_calculation = [
        f"Share {total} in the ratio {a}:{b}:{c}",
        f"Total parts = {a} + {b} + {c} = {a + b + c}",
        f"1 part = {total} ÷ {a + b + c} = {k}",
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}, {c} × {k} = {share_c}",
    ]
    return ModelledExample(
        topic_id="ratio_share_three_part",
        tier=Tier.HIGHER,
        prompt=f"Share {total} in the ratio {a}:{b}:{c}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{share_a} : {share_b} : {share_c}",
    )


def generate_share_three_foundation(tier: Tier, rng: random.Random) -> Question:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 10)
    total = k * (a + b + c)
    share_a, share_b, share_c = a * k, b * k, c * k

    if share_a + share_b + share_c != total:
        raise ValueError("share_three_foundation verification failed")

    steps = [
        f"Total parts = {a} + {b} + {c} = {a + b + c}",
        f"Value of one part = {total} ÷ {a + b + c} = {k}",
        f"Share 1 = {a} × {k} = {share_a}",
        f"Share 2 = {b} × {k} = {share_b}",
        f"Share 3 = {c} × {k} = {share_c}",
    ]
    return Question(
        topic_id="ratio_share_three_part_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Share {total} in the ratio {a}:{b}:{c}.",
        solution_steps=tuple(steps),
        final_answer=f"{share_a} : {share_b} : {share_c}",
        dedup_key=f"share_three_f:{a}:{b}:{c}:{k}",
    )


def generate_modelled_example_share_three_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 10)
    total = k * (a + b + c)
    share_a, share_b, share_c = a * k, b * k, c * k

    # Independent verification via Fraction (separate path from the multiply-out above).
    if Fraction(share_a, total) != Fraction(a, a + b + c):
        raise ValueError("modelled example share_three_foundation verification failed")
    if share_a + share_b + share_c != total:
        raise ValueError("modelled example share_three_foundation verification failed (total)")

    teaching_steps = [
        f"With a three-way ratio like {a}:{b}:{c}, the method is exactly the same as sharing between "
        f"two — just with one extra share. There are {a} + {b} + {c} = {a + b + c} equal parts in "
        "total.",
        f"To find the value of one part, divide the total by the total number of parts: "
        f"{total} ÷ {a + b + c} = {k}.",
        f"Then multiply each person's number of parts by that value: {a} × {k} = {share_a}, "
        f"{b} × {k} = {share_b}, and {c} × {k} = {share_c}.",
        f"As a check, all three shares should add back up to the original total: "
        f"{share_a} + {share_b} + {share_c} = {share_a + share_b + share_c}, which matches {total}.",
    ]
    worked_calculation = [
        f"Share {total} in the ratio {a}:{b}:{c}",
        f"Total parts = {a} + {b} + {c} = {a + b + c}",
        f"1 part = {total} ÷ {a + b + c} = {k}",
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}, {c} × {k} = {share_c}",
    ]
    return ModelledExample(
        topic_id="ratio_share_three_part_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Share {total} in the ratio {a}:{b}:{c}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{share_a} : {share_b} : {share_c}",
    )


def generate_combine_ratios(tier: Tier, rng: random.Random) -> Question:
    p, q = _rand_part(rng), _rand_part(rng)
    r, s = _rand_part(rng), _rand_part(rng)

    lcm_val = q * r // math.gcd(q, r)
    scale1 = lcm_val // q
    scale2 = lcm_val // r
    combined_a, combined_b, combined_c = p * scale1, lcm_val, s * scale2

    if Fraction(combined_a, combined_b) != Fraction(p, q):
        raise ValueError("combine_ratios verification failed (a:b)")
    if Fraction(combined_b, combined_c) != Fraction(r, s):
        raise ValueError("combine_ratios verification failed (b:c)")

    g = math.gcd(math.gcd(combined_a, combined_b), combined_c)
    sa, sb, sc = combined_a // g, combined_b // g, combined_c // g

    steps = [
        f"Scale a:b = {p}:{q} by {scale1} so b = {lcm_val}: a:b = {combined_a}:{combined_b}",
        f"Scale b:c = {r}:{s} by {scale2} so b = {lcm_val}: b:c = {combined_b}:{combined_c}",
        f"Combine: a:b:c = {combined_a}:{combined_b}:{combined_c}",
        f"Simplify by dividing by {g}: a:b:c = {sa}:{sb}:{sc}",
    ]
    return Question(
        topic_id="ratio_combine",
        tier=Tier.HIGHER,
        prompt=f"Given that a:b = {p}:{q} and b:c = {r}:{s}, find a:b:c in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=f"{sa} : {sb} : {sc}",
        dedup_key=f"combine:{p}:{q}:{r}:{s}",
    )


def generate_modelled_example_combine_ratios(tier: Tier, rng: random.Random) -> ModelledExample:
    p, q = _rand_part(rng), _rand_part(rng)
    r, s = _rand_part(rng), _rand_part(rng)

    lcm_val = q * r // math.gcd(q, r)
    scale1 = lcm_val // q
    scale2 = lcm_val // r
    combined_a, combined_b, combined_c = p * scale1, lcm_val, s * scale2

    # Independent verification via Fraction (separate path from the scale-and-combine above).
    if Fraction(combined_a, combined_b) != Fraction(p, q):
        raise ValueError("modelled example combine_ratios verification failed (a:b)")
    if Fraction(combined_b, combined_c) != Fraction(r, s):
        raise ValueError("modelled example combine_ratios verification failed (b:c)")

    g = math.gcd(math.gcd(combined_a, combined_b), combined_c)
    sa, sb, sc = combined_a // g, combined_b // g, combined_c // g

    teaching_steps = [
        f"We're given a:b = {p}:{q} and b:c = {r}:{s}, but 'b' means something different sized in each "
        f"ratio ({q} parts in the first, {r} parts in the second), so we can't just line them up yet — "
        "'b' has to represent the SAME number of parts in both before we can combine them.",
        f"The trick is to rescale both ratios so that the value of b matches in each. The easiest common "
        f"value to use is the LCM of the two 'b' values, {q} and {r}: LCM({q}, {r}) = {lcm_val}.",
        f"Scale a:b = {p}:{q} up by {scale1} (since {q} × {scale1} = {lcm_val}), giving "
        f"a:b = {combined_a}:{combined_b}. Scale b:c = {r}:{s} up by {scale2} (since "
        f"{r} × {scale2} = {lcm_val}), giving b:c = {combined_b}:{combined_c}.",
        f"Now that b = {combined_b} in both, they can be combined directly into one three-part ratio: "
        f"a:b:c = {combined_a}:{combined_b}:{combined_c}.",
        (
            f"Finally, divide all three parts by their highest common factor, {g}, to simplify: "
            f"a:b:c = {sa}:{sb}:{sc}."
            if g > 1
            else f"The three parts {combined_a}, {combined_b}, {combined_c} already share no common "
            f"factor, so a:b:c = {combined_a}:{combined_b}:{combined_c} is already in its simplest form."
        ),
    ]
    worked_calculation = [
        f"a:b = {p}:{q}, b:c = {r}:{s}",
        f"LCM({q}, {r}) = {lcm_val}",
        f"a:b = {combined_a}:{combined_b}, b:c = {combined_b}:{combined_c}",
        f"a:b:c = {combined_a}:{combined_b}:{combined_c}",
    ]
    if g > 1:
        worked_calculation.append(f"= {sa}:{sb}:{sc}")

    return ModelledExample(
        topic_id="ratio_combine",
        tier=Tier.HIGHER,
        prompt=f"Given that a:b = {p}:{q} and b:c = {r}:{s}, find a:b:c in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{sa} : {sb} : {sc}",
    )


TOPIC_SHARE_TWO = TopicDefinition(
    id="ratio_share_two_part",
    display_name="Share a Two-Part Ratio",
    description="Share an amount between two parties in a given ratio.",
    generate=generate_share_two,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_share_two,
)

TOPIC_FIND_SHARE = TopicDefinition(
    id="ratio_find_missing_share",
    display_name="Find a Missing Share",
    description="Given one share and the ratio, find the other share or the total.",
    generate=generate_find_share,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_find_share,
)

TOPIC_SHARE_THREE = TopicDefinition(
    id="ratio_share_three_part",
    display_name="Share a Three-Part Ratio",
    description="Share an amount between three parties in a given ratio.",
    generate=generate_share_three,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_share_three,
)

TOPIC_SHARE_THREE_FOUNDATION = TopicDefinition(
    id="ratio_share_three_part_foundation",
    display_name="Share a Three-Part Ratio (Foundation)",
    description="Share an amount between three parties in a given ratio.",
    generate=generate_share_three_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_share_three_foundation,
)

TOPIC_COMBINE = TopicDefinition(
    id="ratio_combine",
    display_name="Combine Ratios",
    description="Combine two linked ratios (a:b and b:c) into a single a:b:c ratio.",
    generate=generate_combine_ratios,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_combine_ratios,
)


def _fmt_ratio_n(frac: Fraction) -> tuple[str, bool]:
    """Formats a ratio's 'n' value: exact integer if it divides cleanly,
    otherwise rounded to 2 d.p. Returns (display string, was_rounded)."""
    if frac.denominator == 1:
        return str(frac.numerator), False
    dec = (Decimal(frac.numerator) / Decimal(frac.denominator)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return str(dec), True


def _fmt_frac(frac: Fraction) -> str:
    return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"


def generate_ratio_1_to_n(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(1, 12)
    b = rng.randint(1, 12)
    while b == a:
        b = rng.randint(1, 12)
    form = rng.choice(["1:n", "n:1"])

    n_frac = Fraction(b, a) if form == "1:n" else Fraction(a, b)

    # Independent verification: manually reduce via math.gcd (a separate route from
    # Fraction's own internal reduction used above), then compare.
    g = math.gcd(a, b)
    check_frac = Fraction(b // g, a // g) if form == "1:n" else Fraction(a // g, b // g)
    if check_frac != n_frac:
        raise ValueError("ratio_1_to_n verification failed")

    n_display, was_rounded = _fmt_ratio_n(n_frac)
    approx = "≈" if was_rounded else "="
    suffix = " (to 2 d.p.)" if was_rounded else ""

    if form == "1:n":
        prompt = f"Write the ratio {a}:{b} in the form 1:n."
        steps = [
            f"Divide both parts of the ratio by {a} (the first part) so the first part becomes 1.",
            f"{a} ÷ {a} = 1, {b} ÷ {a} {approx} {n_display}",
        ]
        answer = f"1 : {n_display}{suffix}"
    else:
        prompt = f"Write the ratio {a}:{b} in the form n:1."
        steps = [
            f"Divide both parts of the ratio by {b} (the second part) so the second part becomes 1.",
            f"{a} ÷ {b} {approx} {n_display}, {b} ÷ {b} = 1",
        ]
        answer = f"{n_display} : 1{suffix}"

    return Question(
        topic_id="ratio_1_to_n",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"ratio_1_to_n:{a}:{b}:{form}",
    )


def generate_modelled_example_ratio_1_to_n(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(1, 12)
    b = rng.randint(1, 12)
    while b == a:
        b = rng.randint(1, 12)
    form = rng.choice(["1:n", "n:1"])

    n_frac = Fraction(b, a) if form == "1:n" else Fraction(a, b)

    # Independent verification: manually reduce via math.gcd (a separate route from
    # Fraction's own internal reduction used above), then compare.
    g = math.gcd(a, b)
    check_frac = Fraction(b // g, a // g) if form == "1:n" else Fraction(a // g, b // g)
    if check_frac != n_frac:
        raise ValueError("modelled example ratio_1_to_n verification failed")

    n_display, was_rounded = _fmt_ratio_n(n_frac)
    approx = "≈" if was_rounded else "="
    suffix = " (to 2 d.p.)" if was_rounded else ""
    rounding_note = ", which doesn't come out exact, so we round it to 2 decimal places." if was_rounded else "."

    if form == "1:n":
        prompt = f"Write the ratio {a}:{b} in the form 1:n."
        answer = f"1 : {n_display}{suffix}"
        teaching_steps = [
            "Writing a ratio in the form 1:n means scaling it down so the FIRST part becomes exactly "
            "1 - everything else has to scale by the same amount to keep the ratio equivalent.",
            f"Since the first part is currently {a}, dividing both parts by {a} will turn it into 1. "
            f"{a} ÷ {a} = 1, so that's the left-hand side sorted.",
            f"Do the same division to the second part: {b} ÷ {a} {approx} {n_display}{rounding_note}",
            f"So the ratio {a}:{b} is equivalent to 1 : {n_display} - both describe the same relative "
            "sizes, just scaled differently.",
        ]
        worked_calculation = [
            f"Write {a}:{b} as 1:n",
            f"n = {b} ÷ {a} {approx} {n_display}",
        ]
    else:
        prompt = f"Write the ratio {a}:{b} in the form n:1."
        answer = f"{n_display} : 1{suffix}"
        teaching_steps = [
            "Writing a ratio in the form n:1 means scaling it down so the SECOND part becomes exactly "
            "1 - everything else has to scale by the same amount to keep the ratio equivalent.",
            f"Since the second part is currently {b}, dividing both parts by {b} will turn it into 1. "
            f"{b} ÷ {b} = 1, so that's the right-hand side sorted.",
            f"Do the same division to the first part: {a} ÷ {b} {approx} {n_display}{rounding_note}",
            f"So the ratio {a}:{b} is equivalent to {n_display} : 1 - both describe the same relative "
            "sizes, just scaled differently.",
        ]
        worked_calculation = [
            f"Write {a}:{b} as n:1",
            f"n = {a} ÷ {b} {approx} {n_display}",
        ]

    return ModelledExample(
        topic_id="ratio_1_to_n",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_ratio_difference(tier: Tier, rng: random.Random) -> Question:
    a, b = _rand_part(rng), _rand_part(rng)
    while b == a:
        b = _rand_part(rng)
    k = rng.randint(2, 20)
    share_a, share_b = a * k, b * k
    part_diff = abs(a - b)
    diff = part_diff * k
    ask_total = rng.choice([True, False])

    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("ratio_difference verification failed (ratio)")
    if abs(share_a - share_b) != diff:
        raise ValueError("ratio_difference verification failed (difference)")

    steps = [
        f"Difference in parts = {max(a, b)} - {min(a, b)} = {part_diff} parts",
        f"Value of one part = {diff} ÷ {part_diff} = {k}",
        f"First amount = {a} × {k} = {share_a}",
        f"Second amount = {b} × {k} = {share_b}",
    ]
    if ask_total:
        total = share_a + share_b
        steps.append(f"Total = {share_a} + {share_b} = {total}")
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The difference between them is {diff}. "
            "Find both amounts and their total."
        )
        answer = f"{share_a} : {share_b} (total {total})"
    else:
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The difference between them is {diff}. "
            "Find both amounts."
        )
        answer = f"{share_a} : {share_b}"

    return Question(
        topic_id="ratio_difference",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"ratio_difference:{a}:{b}:{k}:{ask_total}",
    )


def generate_modelled_example_ratio_difference(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = _rand_part(rng), _rand_part(rng)
    while b == a:
        b = _rand_part(rng)
    k = rng.randint(2, 20)
    share_a, share_b = a * k, b * k
    part_diff = abs(a - b)
    diff = part_diff * k
    ask_total = rng.choice([True, False])

    # Independent verification via Fraction (separate path from the multiply-out above).
    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("modelled example ratio_difference verification failed (ratio)")
    if abs(share_a - share_b) != diff:
        raise ValueError("modelled example ratio_difference verification failed (difference)")

    total = share_a + share_b

    teaching_steps = [
        f"This is a ratio-sharing question with a twist: instead of being told the TOTAL, we're told "
        f"the DIFFERENCE between the two amounts, {diff}. The method still starts the same way - work "
        "out what one 'part' of the ratio is worth.",
        f"In the ratio {a}:{b}, the two amounts are {max(a, b)} parts and {min(a, b)} parts, so the "
        f"gap between them is {max(a, b)} - {min(a, b)} = {part_diff} parts - not {a} + {b} parts, "
        "since we're subtracting, not sharing a total.",
        f"That {part_diff}-part gap is worth {diff} in real terms, so one part is worth "
        f"{diff} ÷ {part_diff} = {k}.",
        f"Now scale each side of the ratio by that value: {a} × {k} = {share_a} and "
        f"{b} × {k} = {share_b}."
        + (f" Adding them gives the total: {share_a} + {share_b} = {total}." if ask_total else ""),
        f"As a check, the difference between the two amounts should still be {diff}: "
        f"{max(share_a, share_b)} - {min(share_a, share_b)} = {abs(share_a - share_b)}.",
    ]
    worked_calculation = [
        f"Ratio {a}:{b}, difference = {diff}",
        f"1 part = {diff} ÷ {part_diff} = {k}",
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}",
    ]
    if ask_total:
        worked_calculation.append(f"Total = {share_a} + {share_b} = {total}")
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The difference between them is {diff}. "
            "Find both amounts and their total."
        )
        answer = f"{share_a} : {share_b} (total {total})"
    else:
        prompt = (
            f"Two amounts are in the ratio {a}:{b}. The difference between them is {diff}. "
            "Find both amounts."
        )
        answer = f"{share_a} : {share_b}"

    return ModelledExample(
        topic_id="ratio_difference",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_ratio_difference_higher(tier: Tier, rng: random.Random) -> Question:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    while len({a, b, c}) < 3:
        a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 15)
    share_a, share_b, share_c = a * k, b * k, c * k
    part_diff = max(a, b, c) - min(a, b, c)
    diff = part_diff * k
    ask_total = rng.choice([True, False])

    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("ratio_difference_higher verification failed (a:b)")
    if Fraction(share_b, share_c) != Fraction(b, c):
        raise ValueError("ratio_difference_higher verification failed (b:c)")
    # Independent recompute of the difference directly from the generated shares
    # themselves, rather than from the original a/b/c parts.
    if max(share_a, share_b, share_c) - min(share_a, share_b, share_c) != diff:
        raise ValueError("ratio_difference_higher verification failed (difference)")

    total = share_a + share_b + share_c
    steps = [
        f"Difference in parts = {max(a, b, c)} - {min(a, b, c)} = {part_diff} parts",
        f"Value of one part = {diff} ÷ {part_diff} = {k}",
        f"Amount 1 = {a} × {k} = {share_a}",
        f"Amount 2 = {b} × {k} = {share_b}",
        f"Amount 3 = {c} × {k} = {share_c}",
    ]
    if ask_total:
        steps.append(f"Total = {share_a} + {share_b} + {share_c} = {total}")
        prompt = (
            f"Amounts are in the ratio {a}:{b}:{c}. The difference between the largest and smallest "
            f"amount is {diff}. Find all three amounts and their total."
        )
        answer = f"{share_a} : {share_b} : {share_c} (total {total})"
    else:
        prompt = (
            f"Amounts are in the ratio {a}:{b}:{c}. The difference between the largest and smallest "
            f"amount is {diff}. Find all three amounts."
        )
        answer = f"{share_a} : {share_b} : {share_c}"

    return Question(
        topic_id="ratio_difference_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"ratio_difference_higher:{a}:{b}:{c}:{k}:{ask_total}",
    )


def generate_modelled_example_ratio_difference_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    while len({a, b, c}) < 3:
        a, b, c = _rand_part(rng), _rand_part(rng), _rand_part(rng)
    k = rng.randint(2, 15)
    share_a, share_b, share_c = a * k, b * k, c * k
    part_diff = max(a, b, c) - min(a, b, c)
    diff = part_diff * k
    ask_total = rng.choice([True, False])

    if Fraction(share_a, share_b) != Fraction(a, b):
        raise ValueError("modelled example ratio_difference_higher verification failed (a:b)")
    if Fraction(share_b, share_c) != Fraction(b, c):
        raise ValueError("modelled example ratio_difference_higher verification failed (b:c)")
    if max(share_a, share_b, share_c) - min(share_a, share_b, share_c) != diff:
        raise ValueError("modelled example ratio_difference_higher verification failed (difference)")

    total = share_a + share_b + share_c

    teaching_steps = [
        "With a three-part ratio, 'the difference' means the gap between the LARGEST share and the "
        "SMALLEST share - the middle one doesn't come into that calculation at all, though it still "
        "needs its own share worked out afterwards.",
        f"In the ratio {a}:{b}:{c}, the largest part is {max(a, b, c)} and the smallest is "
        f"{min(a, b, c)}, so the gap between them is {max(a, b, c)} - {min(a, b, c)} = {part_diff} "
        "parts.",
        f"That {part_diff}-part gap is worth {diff} in real terms, so one part is worth "
        f"{diff} ÷ {part_diff} = {k}.",
        f"Now every share can be found by multiplying its number of parts by that value: "
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}, {c} × {k} = {share_c}."
        + (
            f" Adding all three gives the total: {share_a} + {share_b} + {share_c} = {total}."
            if ask_total
            else ""
        ),
        f"As a check, the largest and smallest of those three shares should still differ by {diff}: "
        f"{max(share_a, share_b, share_c)} - {min(share_a, share_b, share_c)} = "
        f"{max(share_a, share_b, share_c) - min(share_a, share_b, share_c)}.",
    ]
    worked_calculation = [
        f"Ratio {a}:{b}:{c}, largest - smallest = {diff}",
        f"1 part = {diff} ÷ {part_diff} = {k}",
        f"{a} × {k} = {share_a}, {b} × {k} = {share_b}, {c} × {k} = {share_c}",
    ]
    if ask_total:
        worked_calculation.append(f"Total = {share_a} + {share_b} + {share_c} = {total}")
        prompt = (
            f"Amounts are in the ratio {a}:{b}:{c}. The difference between the largest and smallest "
            f"amount is {diff}. Find all three amounts and their total."
        )
        answer = f"{share_a} : {share_b} : {share_c} (total {total})"
    else:
        prompt = (
            f"Amounts are in the ratio {a}:{b}:{c}. The difference between the largest and smallest "
            f"amount is {diff}. Find all three amounts."
        )
        answer = f"{share_a} : {share_b} : {share_c}"

    return ModelledExample(
        topic_id="ratio_difference_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


_X_SYM = sp.symbols("x")


def _fmt_lin_expr(coeff: int, const: int) -> str:
    term = "x" if coeff == 1 else ("-x" if coeff == -1 else f"{coeff}x")
    if const > 0:
        return f"{term} + {const}"
    if const < 0:
        return f"{term} - {-const}"
    return term


def _fmt_coeff_x(coeff: int) -> str:
    if coeff == 1:
        return "x"
    if coeff == -1:
        return "-x"
    return f"{coeff}x"


def _build_ratio_equation(rng: random.Random):
    """Picks a target x value and small integer coefficients p, q, m, n first (so
    the answer is controlled), then derives r so that (x+p):(qx+r) = m:n holds
    exactly at x = x_target. Bounded retry loop (rejects non-integer r, a
    degenerate/no-solution equation, or a non-positive share on either side)."""
    for _ in range(500):
        x_target = rng.randint(-8, 12)
        if x_target == 0:
            continue
        p = rng.randint(-9, 9)
        q = rng.randint(1, 5)
        m = rng.randint(1, 9)
        n = rng.randint(1, 9)
        if m == n or math.gcd(m, n) != 1:
            continue
        coeff = n - m * q
        if coeff == 0:
            continue
        numerator = n * (x_target + p) - m * q * x_target
        if numerator % m != 0:
            continue
        r = numerator // m
        left_val = x_target + p
        right_val = q * x_target + r
        if left_val <= 0 or right_val <= 0:
            continue
        if n * left_val != m * right_val:
            continue
        return x_target, p, q, r, m, n, coeff
    raise ValueError("ratio_to_equation: could not construct a valid question")


def generate_ratio_to_equation(tier: Tier, rng: random.Random) -> Question:
    x_target, p, q, r, m, n, coeff = _build_ratio_equation(rng)

    # Independent verification via sympy, solving the equation from scratch - a
    # genuinely different method than the algebraic construction above.
    lhs = n * (_X_SYM + p)
    rhs = m * (q * _X_SYM + r)
    solved = sp.solve(sp.Eq(lhs, rhs), _X_SYM)
    if len(solved) != 1 or solved[0] != x_target:
        raise ValueError("ratio_to_equation verification failed")

    left_expr = _fmt_lin_expr(1, p)
    right_expr = _fmt_lin_expr(q, r)
    const_term = m * r - n * p

    steps = [
        f"Cross-multiply: {n}({left_expr}) = {m}({right_expr})",
        f"Expand: {_fmt_lin_expr(n, n * p)} = {_fmt_lin_expr(m * q, m * r)}",
        f"Collect x terms: {_fmt_coeff_x(coeff)} = {const_term}",
        f"x = {const_term} ÷ {coeff} = {x_target}",
    ]

    return Question(
        topic_id="ratio_to_equation",
        tier=Tier.HIGHER,
        prompt=f"({left_expr}) : ({right_expr}) = {m}:{n}. Find the value of x.",
        solution_steps=tuple(steps),
        final_answer=f"x = {x_target}",
        dedup_key=f"ratio_to_equation:{x_target}:{p}:{q}:{r}:{m}:{n}",
    )


def generate_modelled_example_ratio_to_equation(tier: Tier, rng: random.Random) -> ModelledExample:
    x_target, p, q, r, m, n, coeff = _build_ratio_equation(rng)

    # Independent verification via sympy, solving the equation from scratch.
    lhs = n * (_X_SYM + p)
    rhs = m * (q * _X_SYM + r)
    solved = sp.solve(sp.Eq(lhs, rhs), _X_SYM)
    if len(solved) != 1 or solved[0] != x_target:
        raise ValueError("modelled example ratio_to_equation verification failed")

    left_expr = _fmt_lin_expr(1, p)
    right_expr = _fmt_lin_expr(q, r)
    const_term = m * r - n * p
    prompt = f"({left_expr}) : ({right_expr}) = {m}:{n}. Find the value of x."

    teaching_steps = [
        f"A ratio written as (expression) : (expression) = {m}:{n} is really just saying the two "
        f"expressions have the same relationship to each other as {m} and {n} do - so we can turn it "
        f"into an ordinary equation by cross-multiplying, exactly like with any two equal fractions.",
        f"Cross-multiplying ({left_expr}) : ({right_expr}) = {m}:{n} means multiplying the LEFT "
        f"expression by {n} and the RIGHT expression by {m}, then setting them equal: "
        f"{n}({left_expr}) = {m}({right_expr}).",
        f"Multiply out both brackets: {n} × ({left_expr}) becomes {_fmt_lin_expr(n, n * p)}, and "
        f"{m} × ({right_expr}) becomes {_fmt_lin_expr(m * q, m * r)}.",
        f"Now it's a normal linear equation - gather all the x terms on one side and all the numbers "
        f"on the other. That leaves {_fmt_coeff_x(coeff)} = {const_term}, so dividing gives "
        f"x = {const_term} ÷ {coeff} = {x_target}.",
        f"It's worth checking this by substituting x = {x_target} back in: the two expressions become "
        f"{x_target + p} and {q * x_target + r}, and {x_target + p}:{q * x_target + r} should simplify "
        f"down to {m}:{n}.",
    ]
    worked_calculation = [
        f"({left_expr}) : ({right_expr}) = {m}:{n}",
        f"{n}({left_expr}) = {m}({right_expr})",
        f"{_fmt_lin_expr(n, n * p)} = {_fmt_lin_expr(m * q, m * r)}",
        f"{_fmt_coeff_x(coeff)} = {const_term}",
        f"x = {const_term} ÷ {coeff} = {x_target}",
    ]

    return ModelledExample(
        topic_id="ratio_to_equation",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {x_target}",
    )


def generate_ratio_shape_similar_foundation(tier: Tier, rng: random.Random) -> Question:
    denom = rng.choice([1, 2, 3, 4])
    numer = rng.randint(1, 5)
    while numer == denom:
        numer = rng.randint(1, 5)
    k = Fraction(numer, denom)
    len_a = denom * rng.randint(1, 6)
    len_a2 = denom * rng.randint(1, 6)

    len_b_frac = len_a * k
    answer_frac = len_a2 * k
    if len_b_frac.denominator != 1 or answer_frac.denominator != 1:
        raise ValueError("ratio_shape_similar_foundation: non-integer construction")
    len_b = len_b_frac.numerator
    answer = answer_frac.numerator

    # Independent verification via Fraction cross-multiplication.
    if Fraction(len_b, len_a) != Fraction(answer, len_a2):
        raise ValueError("ratio_shape_similar_foundation verification failed")

    steps = [
        f"Scale factor = {len_b} ÷ {len_a} = {_fmt_frac(k)}",
        f"Corresponding length = {len_a2} × {_fmt_frac(k)} = {answer}",
    ]
    prompt = (
        f"Shape A and Shape B are similar. A side on shape A is {len_a} cm. The corresponding side "
        f"on shape B is {len_b} cm. Another side on shape A is {len_a2} cm. Find the length of the "
        "corresponding side on shape B."
    )
    return Question(
        topic_id="ratio_shape_similar_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{answer} cm",
        dedup_key=f"ratio_shape_similar_f:{len_a}:{len_a2}:{numer}:{denom}",
    )


def generate_modelled_example_ratio_shape_similar_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    denom = rng.choice([1, 2, 3, 4])
    numer = rng.randint(1, 5)
    while numer == denom:
        numer = rng.randint(1, 5)
    k = Fraction(numer, denom)
    len_a = denom * rng.randint(1, 6)
    len_a2 = denom * rng.randint(1, 6)

    len_b_frac = len_a * k
    answer_frac = len_a2 * k
    if len_b_frac.denominator != 1 or answer_frac.denominator != 1:
        raise ValueError("modelled example ratio_shape_similar_foundation: non-integer construction")
    len_b = len_b_frac.numerator
    answer = answer_frac.numerator

    # Independent verification via Fraction cross-multiplication.
    if Fraction(len_b, len_a) != Fraction(answer, len_a2):
        raise ValueError("modelled example ratio_shape_similar_foundation verification failed")

    prompt = (
        f"Shape A and Shape B are similar. A side on shape A is {len_a} cm. The corresponding side "
        f"on shape B is {len_b} cm. Another side on shape A is {len_a2} cm. Find the length of the "
        "corresponding side on shape B."
    )
    teaching_steps = [
        "When two shapes are similar, every length on one shape is the SAME multiple of the "
        "corresponding length on the other shape - that multiple is called the scale factor.",
        f"We can find the scale factor from the pair of corresponding sides we already know: "
        f"{len_a} cm on shape A matches {len_b} cm on shape B, so the scale factor is "
        f"{len_b} ÷ {len_a} = {_fmt_frac(k)}.",
        f"Because the shapes are similar, EVERY other pair of corresponding sides must use that same "
        f"scale factor - so the {len_a2} cm side on shape A becomes "
        f"{len_a2} × {_fmt_frac(k)} = {answer} cm on shape B.",
        "As a check, both pairs of corresponding sides should give the same ratio: "
        f"{len_b}:{len_a} and {answer}:{len_a2} simplify to the same fraction.",
    ]
    worked_calculation = [
        f"Scale factor = {len_b} ÷ {len_a} = {_fmt_frac(k)}",
        f"{len_a2} × {_fmt_frac(k)} = {answer}",
    ]

    return ModelledExample(
        topic_id="ratio_shape_similar_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{answer} cm",
    )


def _build_similar_shape_higher(rng: random.Random):
    sub_type = rng.choice(["area", "volume"])
    exponent = 2 if sub_type == "area" else 3
    len_a = rng.randint(2, 6)
    len_b = rng.randint(2, 6)
    while len_b == len_a:
        len_b = rng.randint(2, 6)
    k = Fraction(len_b, len_a)
    d = k.denominator
    measure_a = (d**exponent) * rng.randint(1, 10)
    measure_b_frac = measure_a * (k**exponent)
    if measure_b_frac.denominator != 1:
        raise ValueError("ratio_shape_similar_higher: non-integer construction")
    measure_b = measure_b_frac.numerator
    direction = rng.choice(["a_to_b", "b_to_a"])
    return sub_type, exponent, len_a, len_b, k, measure_a, measure_b, direction


def generate_ratio_shape_similar_higher(tier: Tier, rng: random.Random) -> Question:
    sub_type, exponent, len_a, len_b, k, measure_a, measure_b, direction = _build_similar_shape_higher(rng)
    unit_label = "cm²" if sub_type == "area" else "cm^3"
    noun = sub_type

    # Independent verification: re-derive the scale factor fresh from the raw
    # corresponding lengths via math.gcd-based reduction (a separate route from
    # Fraction's own internal reduction used to build k above), then confirm the
    # measure ratio matches k raised to the correct power.
    g = math.gcd(len_b, len_a)
    k_check = Fraction(len_b // g, len_a // g)
    if Fraction(measure_b, measure_a) != k_check**exponent:
        raise ValueError("ratio_shape_similar_higher verification failed")

    k_str = _fmt_frac(k)
    k_pow_str = _fmt_frac(k**exponent)

    if direction == "a_to_b":
        prompt = (
            f"Shape A and Shape B are similar. A length on shape A is {len_a} cm and the "
            f"corresponding length on shape B is {len_b} cm. The {noun} of shape A is "
            f"{measure_a} {unit_label}. Find the {noun} of shape B."
        )
        answer = f"{measure_b} {unit_label}"
        last_step = f"{noun.capitalize()} of B = {measure_a} × {k_pow_str} = {measure_b} {unit_label}"
    else:
        prompt = (
            f"Shape A and Shape B are similar. A length on shape A is {len_a} cm and the "
            f"corresponding length on shape B is {len_b} cm. The {noun} of shape B is "
            f"{measure_b} {unit_label}. Find the {noun} of shape A."
        )
        answer = f"{measure_a} {unit_label}"
        last_step = f"{noun.capitalize()} of A = {measure_b} ÷ {k_pow_str} = {measure_a} {unit_label}"

    steps = [
        f"Linear scale factor = {len_b} ÷ {len_a} = {k_str}",
        f"{noun.capitalize()} scale factor = ({k_str})^{exponent} = {k_pow_str}",
        last_step,
    ]

    return Question(
        topic_id="ratio_shape_similar_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"ratio_shape_similar_h:{sub_type}:{len_a}:{len_b}:{measure_a}:{direction}",
    )


def generate_modelled_example_ratio_shape_similar_higher(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    sub_type, exponent, len_a, len_b, k, measure_a, measure_b, direction = _build_similar_shape_higher(rng)
    unit_label = "cm²" if sub_type == "area" else "cm^3"
    noun = sub_type

    # Independent verification: re-derive the scale factor fresh from the raw
    # corresponding lengths via math.gcd-based reduction, then confirm the measure
    # ratio matches k raised to the correct power.
    g = math.gcd(len_b, len_a)
    k_check = Fraction(len_b // g, len_a // g)
    if Fraction(measure_b, measure_a) != k_check**exponent:
        raise ValueError("modelled example ratio_shape_similar_higher verification failed")

    k_str = _fmt_frac(k)
    k_pow_str = _fmt_frac(k**exponent)
    power_word = "squared" if sub_type == "area" else "cubed"
    dimension_word = "two" if exponent == 2 else "three"

    if direction == "a_to_b":
        prompt = (
            f"Shape A and Shape B are similar. A length on shape A is {len_a} cm and the "
            f"corresponding length on shape B is {len_b} cm. The {noun} of shape A is "
            f"{measure_a} {unit_label}. Find the {noun} of shape B."
        )
        answer = f"{measure_b} {unit_label}"
        worked_calculation = [
            f"Scale factor k = {len_b} ÷ {len_a} = {k_str}",
            f"{noun.capitalize()} scale factor = k^{exponent} = {k_pow_str}",
            f"{measure_a} × {k_pow_str} = {measure_b}",
        ]
        apply_step = (
            f"Multiply the known {noun}, {measure_a} {unit_label}, by that {noun} scale factor: "
            f"{measure_a} × {k_pow_str} = {measure_b} {unit_label}."
        )
    else:
        prompt = (
            f"Shape A and Shape B are similar. A length on shape A is {len_a} cm and the "
            f"corresponding length on shape B is {len_b} cm. The {noun} of shape B is "
            f"{measure_b} {unit_label}. Find the {noun} of shape A."
        )
        answer = f"{measure_a} {unit_label}"
        worked_calculation = [
            f"Scale factor k = {len_b} ÷ {len_a} = {k_str}",
            f"{noun.capitalize()} scale factor = k^{exponent} = {k_pow_str}",
            f"{measure_b} ÷ {k_pow_str} = {measure_a}",
        ]
        apply_step = (
            f"Since we're going backwards this time (from B to A), divide instead of multiplying: "
            f"{measure_b} ÷ {k_pow_str} = {measure_a} {unit_label}."
        )

    teaching_steps = [
        f"A really common mistake here is applying the LINEAR scale factor straight to the {noun} - "
        f"that only works for lengths. Whenever a scale factor is applied to {noun}, it has to be "
        f"{power_word} first, because {noun} scales with {dimension_word} dimensions at once.",
        f"Start the same way as any similar-shapes question: find the linear scale factor from a pair "
        f"of corresponding lengths, {len_a} cm and {len_b} cm: k = {len_b} ÷ {len_a} = {k_str}.",
        f"Because {noun} scales by k {power_word}, the {noun} scale factor is "
        f"({k_str})^{exponent} = {k_pow_str}, not just {k_str}.",
        apply_step,
        f"So the {noun} of shape {'B' if direction == 'a_to_b' else 'A'} is {answer}.",
    ]

    return ModelledExample(
        topic_id="ratio_shape_similar_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_RATIO_1_TO_N = TopicDefinition(
    id="ratio_1_to_n",
    display_name="Ratio in the Form 1:n",
    description="Write a ratio in the form 1:n or n:1.",
    generate=generate_ratio_1_to_n,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_ratio_1_to_n,
)

TOPIC_RATIO_DIFFERENCE = TopicDefinition(
    id="ratio_difference",
    display_name="Ratio Given the Difference",
    description="Given the difference between two shares and their ratio, find both amounts.",
    generate=generate_ratio_difference,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_ratio_difference,
)

TOPIC_RATIO_DIFFERENCE_HIGHER = TopicDefinition(
    id="ratio_difference_higher",
    display_name="Ratio Given the Difference (Three Parts)",
    description=(
        "Given the difference between the largest and smallest share of a three-part ratio, "
        "find all three amounts."
    ),
    generate=generate_ratio_difference_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_ratio_difference_higher,
)

TOPIC_RATIO_TO_EQUATION = TopicDefinition(
    id="ratio_to_equation",
    display_name="Ratio Problems with Algebra",
    description="Solve an algebraic ratio equation of the form (x + p) : (qx + r) = m:n.",
    generate=generate_ratio_to_equation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_ratio_to_equation,
)

TOPIC_RATIO_SHAPE_SIMILAR_FOUNDATION = TopicDefinition(
    id="ratio_shape_similar_foundation",
    display_name="Similar Shapes: Lengths",
    description="Use the scale factor between similar shapes to find a missing length.",
    generate=generate_ratio_shape_similar_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_ratio_shape_similar_foundation,
)

TOPIC_RATIO_SHAPE_SIMILAR_HIGHER = TopicDefinition(
    id="ratio_shape_similar_higher",
    display_name="Similar Shapes: Area and Volume",
    description=(
        "Use the area or volume scale factor (k^2 or k^3) between similar shapes to find a "
        "missing area or volume."
    ),
    generate=generate_ratio_shape_similar_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_ratio_shape_similar_higher,
)
