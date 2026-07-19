import math
import random
from fractions import Fraction

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

TOPIC_ID = "ratio"


def _rand_part(rng: random.Random) -> int:
    return rng.randint(1, 9)


def _generate_share_two(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"Share {total} in the ratio {a}:{b}.",
        solution_steps=tuple(steps),
        final_answer=f"{share_a} : {share_b}",
        dedup_key=f"share_two:{a}:{b}:{k}",
    )


def _generate_find_share(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"find_share:{a}:{b}:{k}:{target}",
    )


def _generate_share_three(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=f"Share {total} in the ratio {a}:{b}:{c}.",
        solution_steps=tuple(steps),
        final_answer=f"{share_a} : {share_b} : {share_c}",
        dedup_key=f"share_three:{a}:{b}:{c}:{k}",
    )


def _generate_combine_ratios(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=f"Given that a:b = {p}:{q} and b:c = {r}:{s}, find a:b:c in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=f"{sa} : {sb} : {sc}",
        dedup_key=f"combine:{p}:{q}:{r}:{s}",
    )


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["share_two", "find_share"])
        return _generate_share_two(rng) if shape == "share_two" else _generate_find_share(rng)
    shape = rng.choice(["share_three", "combine_ratios"])
    return _generate_share_three(rng) if shape == "share_three" else _generate_combine_ratios(rng)


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Ratio",
    description="Share amounts in a given ratio, find missing shares, and combine ratios.",
    generate=generate,
)
