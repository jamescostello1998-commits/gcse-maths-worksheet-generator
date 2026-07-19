import math
import random

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

TOPIC_ID = "pythagoras"

PRIMITIVE_TRIPLES = [
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
    (20, 21, 29),
    (9, 40, 41),
    (12, 35, 37),
    (11, 60, 61),
]


def _simplify_surd(n: int) -> tuple[int, int]:
    """Return (m, r) such that m * sqrt(r) == sqrt(n), with r square-free."""
    m, remainder, d = 1, n, 2
    while d * d <= remainder:
        while remainder % (d * d) == 0:
            remainder //= d * d
            m *= d
        d += 1
    return m, remainder


def _fmt_surd(m: int, r: int) -> str:
    if r == 1:
        return str(m)
    if m == 1:
        return f"√{r}"
    return f"{m}√{r}"


def _generate_hypotenuse_triple(rng: random.Random) -> Question:
    a, b, c = rng.choice(PRIMITIVE_TRIPLES)
    k = rng.randint(1, 4)
    leg1, leg2, hyp = a * k, b * k, c * k
    if leg1**2 + leg2**2 != hyp**2:
        raise ValueError("hypotenuse_triple verification failed")

    sum_sq = leg1**2 + leg2**2
    steps = [
        f"c² = a² + b² = {leg1}² + {leg2}² = {leg1**2} + {leg2**2} = {sum_sq}",
        f"c = √{sum_sq} = {hyp}",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"A right-angled triangle has legs {leg1} cm and {leg2} cm. Find the length of the hypotenuse.",
        solution_steps=tuple(steps),
        final_answer=f"{hyp} cm",
        dedup_key=f"hyp_triple:{leg1}:{leg2}",
    )


def _generate_hypotenuse_decimal(rng: random.Random) -> Question:
    for _ in range(100):
        a, b = rng.randint(5, 20), rng.randint(5, 20)
        s = a * a + b * b
        if math.isqrt(s) ** 2 != s:
            break
    else:
        raise ValueError("hypotenuse_decimal could not find a non-triple pair")

    value = math.sqrt(s)
    rounded = round(value, 1)
    steps = [
        f"c² = a² + b² = {a}² + {b}² = {a * a} + {b * b} = {s}",
        f"c = √{s} ≈ {rounded} cm (1 d.p.)",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the length of the "
            "hypotenuse, correct to 1 decimal place."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{rounded} cm",
        dedup_key=f"hyp_decimal:{a}:{b}",
    )


def _generate_shorter_leg(rng: random.Random) -> Question:
    a, b, c = rng.choice(PRIMITIVE_TRIPLES)
    k = rng.randint(1, 4)
    leg_known, hyp, leg_missing = a * k, c * k, b * k
    if leg_known**2 + leg_missing**2 != hyp**2:
        raise ValueError("shorter_leg verification failed")

    diff = hyp**2 - leg_known**2
    steps = [
        f"b² = c² - a² = {hyp}² - {leg_known}² = {hyp**2} - {leg_known**2} = {diff}",
        f"b = √{diff} = {leg_missing}",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A right-angled triangle has hypotenuse {hyp} cm and one leg {leg_known} cm. "
            "Find the length of the other leg."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{leg_missing} cm",
        dedup_key=f"shorter_leg:{leg_known}:{hyp}",
    )


def _generate_surd_hypotenuse(rng: random.Random) -> Question:
    for _ in range(100):
        a, b = rng.randint(4, 15), rng.randint(4, 15)
        s = a * a + b * b
        m, r = _simplify_surd(s)
        if r != 1:
            break
    else:
        raise ValueError("surd_hypotenuse could not find a non-triple pair")

    if m * m * r != s:
        raise ValueError("surd_hypotenuse verification failed")

    surd_str = _fmt_surd(m, r)
    steps = [
        f"c² = a² + b² = {a}² + {b}² = {a * a} + {b * b} = {s}",
        f"c = √{s} = {surd_str} cm (exact form)",
    ]
    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the exact length of the "
            "hypotenuse, giving your answer as a simplified surd."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{surd_str} cm",
        dedup_key=f"surd_hyp:{a}:{b}",
    )


def _generate_ladder_context(rng: random.Random) -> Question:
    use_triple = rng.random() < 0.5
    if use_triple:
        a, b, c = rng.choice(PRIMITIVE_TRIPLES)
        k = rng.randint(1, 3)
        ladder, base, height = c * k, a * k, b * k
        if base**2 + height**2 != ladder**2:
            raise ValueError("ladder_context (triple) verification failed")
        steps = [
            f"height² = ladder² - base² = {ladder}² - {base}² = "
            f"{ladder**2} - {base**2} = {ladder**2 - base**2}",
            f"height = √{ladder**2 - base**2} = {height} m",
        ]
        answer_str = f"{height} m"
    else:
        for _ in range(100):
            base = rng.randint(3, 10)
            ladder = base + rng.randint(3, 10)
            s = ladder**2 - base**2
            m, r = _simplify_surd(s)
            if r != 1:
                break
        else:
            raise ValueError("ladder_context (surd) could not find valid parameters")
        if m * m * r != s:
            raise ValueError("ladder_context (surd) verification failed")
        surd_str = _fmt_surd(m, r)
        steps = [
            f"height² = ladder² - base² = {ladder}² - {base}² = "
            f"{ladder**2} - {base**2} = {s}",
            f"height = √{s} = {surd_str} m (exact form)",
        ]
        answer_str = f"{surd_str} m"

    return Question(
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A ladder of length {ladder} m leans against a vertical wall with its base {base} m "
            "from the wall. Find the height the ladder reaches up the wall."
        ),
        solution_steps=tuple(steps),
        final_answer=answer_str,
        dedup_key=f"ladder:{use_triple}:{base}:{ladder}",
    )


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["hypotenuse_triple", "hypotenuse_decimal"])
        return _generate_hypotenuse_triple(rng) if shape == "hypotenuse_triple" else _generate_hypotenuse_decimal(rng)
    shape = rng.choice(["shorter_leg", "surd_hypotenuse", "ladder_context"])
    if shape == "shorter_leg":
        return _generate_shorter_leg(rng)
    if shape == "surd_hypotenuse":
        return _generate_surd_hypotenuse(rng)
    return _generate_ladder_context(rng)


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Pythagoras' Theorem",
    description="Find missing sides in right-angled triangles, including exact surd answers.",
    generate=generate,
)
