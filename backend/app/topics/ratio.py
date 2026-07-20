import math
import random
from fractions import Fraction

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
