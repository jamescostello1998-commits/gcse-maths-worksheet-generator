import math
import random
from fractions import Fraction

from app.core.models import Question, Tier
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


TOPIC_SHARE_TWO = TopicDefinition(
    id="ratio_share_two_part",
    display_name="Share a Two-Part Ratio",
    description="Share an amount between two parties in a given ratio.",
    generate=generate_share_two,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_FIND_SHARE = TopicDefinition(
    id="ratio_find_missing_share",
    display_name="Find a Missing Share",
    description="Given one share and the ratio, find the other share or the total.",
    generate=generate_find_share,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_SHARE_THREE = TopicDefinition(
    id="ratio_share_three_part",
    display_name="Share a Three-Part Ratio",
    description="Share an amount between three parties in a given ratio.",
    generate=generate_share_three,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_COMBINE = TopicDefinition(
    id="ratio_combine",
    display_name="Combine Ratios",
    description="Combine two linked ratios (a:b and b:c) into a single a:b:c ratio.",
    generate=generate_combine_ratios,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
