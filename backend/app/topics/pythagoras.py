import math
import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Pythagoras' Theorem"

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


def generate_hypotenuse_triple(tier: Tier, rng: random.Random) -> Question:
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
        topic_id="pythagoras_hypotenuse_triple",
        tier=Tier.FOUNDATION,
        prompt=f"A right-angled triangle has legs {leg1} cm and {leg2} cm. Find the length of the hypotenuse.",
        solution_steps=tuple(steps),
        final_answer=f"{hyp} cm",
        dedup_key=f"hyp_triple:{leg1}:{leg2}",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{leg1} cm", "leg2_label": f"{leg2} cm", "hyp_label": "?"},
        ),
    )


def generate_modelled_example_hypotenuse_triple(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c = rng.choice(PRIMITIVE_TRIPLES)
    k = rng.randint(1, 4)
    leg1, leg2, hyp = a * k, b * k, c * k
    sum_sq = leg1**2 + leg2**2
    if sum_sq != hyp**2:
        raise ValueError("modelled example hypotenuse_triple verification failed")
    # Independent check: converse of Pythagoras via the primitive triple relationship.
    if math.isqrt(sum_sq) ** 2 != sum_sq or math.isqrt(sum_sq) != hyp:
        raise ValueError("modelled example hypotenuse_triple converse check failed")

    teaching_steps = [
        "Pythagoras' theorem says that in any right-angled triangle, the square of the "
        "hypotenuse (the longest side, opposite the right angle) equals the sum of the "
        "squares of the other two sides.",
        f"Here the two shorter sides (the legs) are {leg1} cm and {leg2} cm, so we square "
        f"each of them and add the results together: {leg1}² + {leg2}² = {leg1**2} + {leg2**2} = {sum_sq}.",
        f"That total, {sum_sq}, is the hypotenuse squared - so to find the hypotenuse itself "
        f"we take the square root: c = √{sum_sq}.",
        f"Since {sum_sq} happens to be a perfect square here, the square root comes out as a "
        f"whole number: c = {hyp} cm.",
    ]
    worked_calculation = [
        f"c² = {leg1}² + {leg2}²",
        f"c² = {leg1**2} + {leg2**2} = {sum_sq}",
        f"c = √{sum_sq}",
        f"c = {hyp} cm",
    ]
    return ModelledExample(
        topic_id="pythagoras_hypotenuse_triple",
        tier=Tier.FOUNDATION,
        prompt=f"A right-angled triangle has legs {leg1} cm and {leg2} cm. Find the length of the hypotenuse.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{hyp} cm",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{leg1} cm", "leg2_label": f"{leg2} cm", "hyp_label": "?"},
        ),
    )


def generate_hypotenuse_decimal(tier: Tier, rng: random.Random) -> Question:
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
        topic_id="pythagoras_hypotenuse_decimal",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the length of the "
            "hypotenuse, correct to 1 decimal place."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{rounded} cm",
        dedup_key=f"hyp_decimal:{a}:{b}",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{a} cm", "leg2_label": f"{b} cm", "hyp_label": "?"},
        ),
    )


def generate_modelled_example_hypotenuse_decimal(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(100):
        a, b = rng.randint(5, 20), rng.randint(5, 20)
        s = a * a + b * b
        if math.isqrt(s) ** 2 != s:
            break
    else:
        raise ValueError("modelled example hypotenuse_decimal could not find a non-triple pair")

    value = math.sqrt(s)
    rounded = round(value, 1)
    # Independent check: squaring the rounded answer should land close to s - the
    # tolerance allows for the rounding error inherent in displaying to 1 d.p.
    # (up to ~0.05 in the root, so up to ~2 x value x 0.05 in the square).
    if abs(rounded * rounded - s) > 3.0:
        raise ValueError("modelled example hypotenuse_decimal verification failed")

    teaching_steps = [
        "Pythagoras' theorem tells us that the square of the hypotenuse equals the sum of "
        "the squares of the other two sides, in any right-angled triangle.",
        f"Square each of the two given legs and add them together: {a}² + {b}² = {a * a} + {b * b} = {s}.",
        f"To undo the squaring and get back to the hypotenuse itself, take the square root "
        f"of {s}. This time {s} isn't a perfect square, so the answer is a decimal.",
        f"√{s} ≈ {rounded}, rounded to 1 decimal place as the question asks - always check "
        "the question for how many decimal places or significant figures are wanted.",
    ]
    worked_calculation = [
        f"c² = {a}² + {b}²",
        f"c² = {a * a} + {b * b} = {s}",
        f"c = √{s}",
        f"c ≈ {rounded} cm (1 d.p.)",
    ]
    return ModelledExample(
        topic_id="pythagoras_hypotenuse_decimal",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the length of the "
            "hypotenuse, correct to 1 decimal place."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{rounded} cm",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{a} cm", "leg2_label": f"{b} cm", "hyp_label": "?"},
        ),
    )


def generate_shorter_leg(tier: Tier, rng: random.Random) -> Question:
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
        topic_id="pythagoras_shorter_leg",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A right-angled triangle has hypotenuse {hyp} cm and one leg {leg_known} cm. "
            "Find the length of the other leg."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{leg_missing} cm",
        dedup_key=f"shorter_leg:{leg_known}:{hyp}",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{leg_known} cm", "leg2_label": "?", "hyp_label": f"{hyp} cm"},
        ),
    )


def generate_modelled_example_shorter_leg(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c = rng.choice(PRIMITIVE_TRIPLES)
    k = rng.randint(1, 4)
    leg_known, hyp, leg_missing = a * k, c * k, b * k
    diff = hyp**2 - leg_known**2
    if diff != leg_missing**2:
        raise ValueError("modelled example shorter_leg verification failed")
    # Independent check: adding both legs' squares should reproduce the hypotenuse squared.
    if leg_known**2 + leg_missing**2 != hyp**2:
        raise ValueError("modelled example shorter_leg converse check failed")

    teaching_steps = [
        "Pythagoras' theorem still applies, but this time we're given the hypotenuse and "
        "one leg, and asked for the other leg - so the formula needs rearranging first.",
        f"Start from c² = a² + b². We know c = {hyp} cm and one leg a = {leg_known} cm, "
        "and we want the missing leg b.",
        f"Rearrange to make b² the subject: b² = c² - a² = {hyp}² - {leg_known}² = "
        f"{hyp**2} - {leg_known**2} = {diff}.",
        f"Take the square root of both sides to find b: b = √{diff} = {leg_missing} cm. "
        "Notice we subtract here, not add, because we're finding a leg rather than the hypotenuse.",
    ]
    worked_calculation = [
        f"b² = {hyp}² - {leg_known}²",
        f"b² = {hyp**2} - {leg_known**2} = {diff}",
        f"b = √{diff}",
        f"b = {leg_missing} cm",
    ]
    return ModelledExample(
        topic_id="pythagoras_shorter_leg",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A right-angled triangle has hypotenuse {hyp} cm and one leg {leg_known} cm. "
            "Find the length of the other leg."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{leg_missing} cm",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{leg_known} cm", "leg2_label": "?", "hyp_label": f"{hyp} cm"},
        ),
    )


def generate_surd_hypotenuse(tier: Tier, rng: random.Random) -> Question:
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
        topic_id="pythagoras_surd_hypotenuse",
        tier=Tier.HIGHER,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the exact length of the "
            "hypotenuse, giving your answer as a simplified surd."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{surd_str} cm",
        dedup_key=f"surd_hyp:{a}:{b}",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{a} cm", "leg2_label": f"{b} cm", "hyp_label": "?"},
        ),
    )


def generate_modelled_example_surd_hypotenuse(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(100):
        a, b = rng.randint(4, 15), rng.randint(4, 15)
        s = a * a + b * b
        m, r = _simplify_surd(s)
        if r != 1:
            break
    else:
        raise ValueError("modelled example surd_hypotenuse could not find a non-triple pair")

    if m * m * r != s:
        raise ValueError("modelled example surd_hypotenuse verification failed")

    surd_str = _fmt_surd(m, r)
    if m > 1:
        simplify_step = (
            f"{s} is not a perfect square, but it may still simplify. Look for the largest "
            f"square number that divides into {s} - here that's {m * m}, giving "
            f"√{s} = √({m * m} × {r}) = {surd_str}."
        )
    else:
        simplify_step = (
            f"{s} is not a perfect square. Check whether it simplifies by looking for a "
            f"square number that divides into it - here none does (other than 1), so "
            f"√{s} is already in its simplest form: {surd_str}."
        )
    teaching_steps = [
        "As always with Pythagoras' theorem, square the two legs and add them together to "
        "get the hypotenuse squared.",
        f"{a}² + {b}² = {a * a} + {b * b} = {s}. Since the question asks for an exact answer "
        f"rather than a rounded decimal, we leave this as a surd: c = √{s}.",
        simplify_step,
        f"So the exact hypotenuse is {surd_str} cm. Squaring this back - ({surd_str})² = "
        f"{m}² × {r} = {m * m} × {r} = {s} - confirms it matches c² exactly, with nothing "
        "rounded away.",
    ]
    worked_calculation = [
        f"c² = {a}² + {b}²",
        f"c² = {a * a} + {b * b} = {s}",
        f"c = √{s} = √({m * m} × {r})",
        f"c = {surd_str} cm",
    ]
    return ModelledExample(
        topic_id="pythagoras_surd_hypotenuse",
        tier=Tier.HIGHER,
        prompt=(
            f"A right-angled triangle has legs {a} cm and {b} cm. Find the exact length of the "
            "hypotenuse, giving your answer as a simplified surd."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{surd_str} cm",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{a} cm", "leg2_label": f"{b} cm", "hyp_label": "?"},
        ),
    )


def generate_ladder_context(tier: Tier, rng: random.Random) -> Question:
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
        topic_id="pythagoras_ladder_context",
        tier=Tier.HIGHER,
        prompt=(
            f"A ladder of length {ladder} m leans against a vertical wall with its base {base} m "
            "from the wall. Find the height the ladder reaches up the wall."
        ),
        solution_steps=tuple(steps),
        final_answer=answer_str,
        dedup_key=f"ladder:{use_triple}:{base}:{ladder}",
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{base} m", "leg2_label": "?", "hyp_label": f"{ladder} m"},
        ),
    )


def generate_modelled_example_ladder_context(tier: Tier, rng: random.Random) -> ModelledExample:
    use_triple = rng.random() < 0.5
    if use_triple:
        a, b, c = rng.choice(PRIMITIVE_TRIPLES)
        k = rng.randint(1, 3)
        ladder, base, height = c * k, a * k, b * k
        if base**2 + height**2 != ladder**2:
            raise ValueError("modelled example ladder_context (triple) verification failed")
        diff = ladder**2 - base**2
        teaching_steps = [
            "A ladder leaning against a wall forms a right-angled triangle: the ladder itself "
            "is the hypotenuse (the longest side, opposite the right angle where the wall "
            "meets the ground), the distance from the wall is one leg, and the height up the "
            "wall is the other leg.",
            f"We know the ladder (hypotenuse) = {ladder} m and the base distance = {base} m, "
            "and we want the height, so rearrange Pythagoras' theorem to make the missing "
            "leg the subject.",
            f"height² = ladder² - base² = {ladder}² - {base}² = {ladder**2} - {base**2} = {diff}.",
            f"height = √{diff} = {height} m. It's worth sanity-checking that the height is "
            "shorter than the ladder itself, which it is here - a good quick check that the "
            "answer is sensible.",
        ]
        worked_calculation = [
            f"height² = {ladder}² - {base}²",
            f"height² = {ladder**2} - {base**2} = {diff}",
            f"height = √{diff}",
            f"height = {height} m",
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
            raise ValueError("modelled example ladder_context (surd) could not find valid parameters")
        if m * m * r != s:
            raise ValueError("modelled example ladder_context (surd) verification failed")
        surd_str = _fmt_surd(m, r)
        teaching_steps = [
            "A ladder against a wall forms a right-angled triangle: the ladder is the "
            "hypotenuse, the base distance from the wall is one leg, and the height up the "
            "wall is the other leg we need to find.",
            f"Rearranged Pythagoras gives height² = ladder² - base² = {ladder}² - {base}² = "
            f"{ladder**2} - {base**2} = {s}.",
            f"{s} is not a perfect square, so rather than rounding we leave the answer as an "
            f"exact surd: height = √{s}, which simplifies to {surd_str} m.",
            "Leaving the answer as a surd like this keeps it exact - useful whenever the "
            "question asks for an exact value rather than a decimal approximation.",
        ]
        worked_calculation = [
            f"height² = {ladder}² - {base}²",
            f"height² = {ladder**2} - {base**2} = {s}",
            f"height = √{s}",
            f"height = {surd_str} m",
        ]
        answer_str = f"{surd_str} m"

    return ModelledExample(
        topic_id="pythagoras_ladder_context",
        tier=Tier.HIGHER,
        prompt=(
            f"A ladder of length {ladder} m leans against a vertical wall with its base {base} m "
            "from the wall. Find the height the ladder reaches up the wall."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer_str,
        diagram=DiagramSpec(
            kind="right_triangle",
            params={"leg1_label": f"{base} m", "leg2_label": "?", "hyp_label": f"{ladder} m"},
        ),
    )


TOPIC_HYPOTENUSE_TRIPLE = TopicDefinition(
    id="pythagoras_hypotenuse_triple",
    display_name="Hypotenuse (Triple)",
    description="Find the hypotenuse of a right-angled triangle, resulting in a whole number.",
    generate=generate_hypotenuse_triple,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_hypotenuse_triple,
)

TOPIC_HYPOTENUSE_DECIMAL = TopicDefinition(
    id="pythagoras_hypotenuse_decimal",
    display_name="Hypotenuse (Decimal)",
    description="Find the hypotenuse of a right-angled triangle, rounded to 1 decimal place.",
    generate=generate_hypotenuse_decimal,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_hypotenuse_decimal,
)

TOPIC_SHORTER_LEG = TopicDefinition(
    id="pythagoras_shorter_leg",
    display_name="Shorter Leg",
    description="Find a missing leg given the hypotenuse and the other leg.",
    generate=generate_shorter_leg,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_shorter_leg,
)

TOPIC_SURD_HYPOTENUSE = TopicDefinition(
    id="pythagoras_surd_hypotenuse",
    display_name="Exact Surd Hypotenuse",
    description="Find the hypotenuse as an exact, simplified surd.",
    generate=generate_surd_hypotenuse,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_surd_hypotenuse,
)

TOPIC_LADDER_CONTEXT = TopicDefinition(
    id="pythagoras_ladder_context",
    display_name="Ladder Context",
    description="Apply Pythagoras' theorem to a worded ladder-against-a-wall problem.",
    generate=generate_ladder_context,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_ladder_context,
)
