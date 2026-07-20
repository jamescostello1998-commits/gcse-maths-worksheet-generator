import math
import random
from fractions import Fraction

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Powers, Roots & Indices"

_SQUARE_FREE_FACTORS = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15]


def generate_powers_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["evaluate", "law_multiply", "law_divide", "law_power"])

    if shape == "evaluate":
        base = rng.randint(2, 12)
        exponent = rng.choice([2, 3])
        result = base**exponent

        # Independent check via a manual repeated-multiplication loop - a
        # different code path than Python's ** operator.
        manual = 1
        for _ in range(exponent):
            manual *= base
        if manual != result:
            raise ValueError("powers_foundation verification failed")

        steps = [f"{base}^{exponent} = " + " × ".join([str(base)] * exponent) + f" = {result}"]
        return Question(
            topic_id="powers_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out {base}^{exponent}.",
            solution_steps=tuple(steps),
            final_answer=str(result),
            dedup_key=f"pow_eval:{base}:{exponent}",
        )

    base = rng.randint(2, 9)
    if shape == "law_multiply":
        m, n = rng.randint(2, 5), rng.randint(2, 5)
        result_exp = m + n
        # Independent check: evaluate both sides numerically and confirm
        # they match - a different method than adding the exponents.
        if base**m * base**n != base**result_exp:
            raise ValueError("powers_foundation verification failed")
        prompt = f"Simplify {base}^{m} × {base}^{n}, giving your answer as a single power of {base}."
        steps = [f"Add the powers: {m} + {n} = {result_exp}", f"{base}^{m} × {base}^{n} = {base}^{result_exp}"]
        dedup_key = f"pow_mult:{base}:{m}:{n}"
    elif shape == "law_divide":
        m = rng.randint(4, 8)
        n = rng.randint(1, m - 1)
        result_exp = m - n
        if base**m // base**n != base**result_exp:
            raise ValueError("powers_foundation verification failed")
        prompt = f"Simplify {base}^{m} ÷ {base}^{n}, giving your answer as a single power of {base}."
        steps = [f"Subtract the powers: {m} - {n} = {result_exp}", f"{base}^{m} ÷ {base}^{n} = {base}^{result_exp}"]
        dedup_key = f"pow_div:{base}:{m}:{n}"
    else:
        m, n = rng.randint(2, 4), rng.randint(2, 3)
        result_exp = m * n
        if (base**m) ** n != base**result_exp:
            raise ValueError("powers_foundation verification failed")
        prompt = f"Simplify ({base}^{m})^{n}, giving your answer as a single power of {base}."
        steps = [f"Multiply the powers: {m} × {n} = {result_exp}", f"({base}^{m})^{n} = {base}^{result_exp}"]
        dedup_key = f"pow_pow:{base}:{m}:{n}"

    return Question(
        topic_id="powers_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{base}^{result_exp}",
        dedup_key=dedup_key,
    )


def generate_powers_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["negative_index", "zero_index", "fractional_root", "fractional_full"])

    if shape == "negative_index":
        base = rng.randint(2, 6)
        exponent = rng.randint(2, 4)
        result = Fraction(1, base**exponent)

        # Independent check: raise the reciprocal 1/base to the positive
        # power - a different derivation than 1/(base**exponent).
        check = Fraction(1, base) ** exponent
        if check != result:
            raise ValueError("powers_higher verification failed")

        steps = [f"{base}^-{exponent} = 1/{base}^{exponent} = 1/{base**exponent}"]
        return Question(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {base}^-{exponent}. Give your answer as a fraction.",
            solution_steps=tuple(steps),
            final_answer=f"1/{base**exponent}",
            dedup_key=f"pow_neg:{base}:{exponent}",
        )

    if shape == "zero_index":
        base = rng.randint(2, 20)
        steps = ["Any nonzero number raised to the power 0 equals 1.", f"{base}^0 = 1"]
        return Question(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {base}^0.",
            solution_steps=tuple(steps),
            final_answer="1",
            dedup_key=f"pow_zero:{base}",
        )

    n = rng.choice([2, 3])
    root_val = rng.randint(2, 6)
    a = root_val**n

    if shape == "fractional_root":
        # Independent check via direct nth-root exponentiation (float), a
        # different method than the perfect-power construction above.
        check = round(a ** (1 / n))
        if check != root_val or check**n != a:
            raise ValueError("powers_higher verification failed")
        root_word = "square" if n == 2 else "cube"
        steps = [f"{a}^(1/{n}) means the {root_word} root of {a}.", f"{a}^(1/{n}) = {root_val}"]
        return Question(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {a}^(1/{n}).",
            solution_steps=tuple(steps),
            final_answer=str(root_val),
            dedup_key=f"pow_fracroot:{a}:{n}",
        )

    m = 2 if n == 3 else 3  # keep m != n so the fraction m/n isn't trivially 1
    result = root_val**m
    check = round(a ** (1 / n)) ** m
    if check != result:
        raise ValueError("powers_higher verification failed")
    steps = [
        f"{a}^({m}/{n}) = ({a}^(1/{n}))^{m}",
        f"{a}^(1/{n}) = {root_val}",
        f"{root_val}^{m} = {result}",
    ]
    return Question(
        topic_id="powers_higher",
        tier=Tier.HIGHER,
        prompt=f"Work out {a}^({m}/{n}).",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"pow_fracfull:{a}:{m}:{n}",
    )


def generate_roots_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["square_root", "cube_root", "estimate"])

    if shape == "square_root":
        root_val = rng.randint(2, 15)
        n = root_val**2
        # Independent check via math.isqrt - a different implementation than
        # the perfect-square construction above.
        check = math.isqrt(n)
        if check != root_val or check**2 != n:
            raise ValueError("roots_foundation verification failed")
        steps = [f"{root_val}^2 = {n}, so √{n} = {root_val}"]
        return Question(
            topic_id="roots_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out √{n}.",
            solution_steps=tuple(steps),
            final_answer=str(root_val),
            dedup_key=f"sqrt:{n}",
        )

    if shape == "cube_root":
        root_val = rng.randint(2, 10)
        n = root_val**3
        # Independent check via float cube-root estimation - a different
        # method than the perfect-cube construction above.
        check = round(n ** (1 / 3))
        if check != root_val or check**3 != n:
            raise ValueError("roots_foundation verification failed")
        steps = [f"{root_val}^3 = {n}, so the cube root of {n} = {root_val}"]
        return Question(
            topic_id="roots_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out the cube root of {n}.",
            solution_steps=tuple(steps),
            final_answer=str(root_val),
            dedup_key=f"cbrt:{n}",
        )

    lo = rng.randint(2, 14)
    hi = lo + 1
    n = rng.randint(lo**2 + 1, hi**2 - 1)

    # Independent check via math.isqrt (integer floor square root) - a
    # different method than the range construction above.
    if not (lo**2 < n < hi**2) or math.isqrt(n) != lo:
        raise ValueError("roots_foundation verification failed")

    steps = [
        f"{lo}^2 = {lo**2} and {hi}^2 = {hi**2}",
        f"Since {lo**2} < {n} < {hi**2}, √{n} is between {lo} and {hi}.",
    ]
    return Question(
        topic_id="roots_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Without using a calculator, show that √{n} lies between two consecutive whole numbers, and state them.",
        solution_steps=tuple(steps),
        final_answer=f"between {lo} and {hi}",
        dedup_key=f"estimate_root:{n}",
    )


def generate_roots_higher(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        k = rng.randint(2, 6)
        m = rng.choice(_SQUARE_FREE_FACTORS)
        n = k * k * m
        if n <= 300:
            break
    else:
        raise ValueError("roots_higher could not find suitable numbers")

    # Independent check: (1) reconstruct n from k and m directly, and (2)
    # confirm m is genuinely square-free via trial division - a different
    # check than how m was chosen from the curated list above.
    if k * k * m != n:
        raise ValueError("roots_higher verification failed: reconstruction mismatch")
    for p in range(2, int(m**0.5) + 1):
        if m % (p * p) == 0:
            raise ValueError("roots_higher verification failed: m is not square-free")

    steps = [
        f"Find the largest square factor of {n}: {k}^2 × {m} = {n}",
        f"√{n} = √({k}^2 × {m}) = {k}√{m}",
    ]
    return Question(
        topic_id="roots_higher",
        tier=Tier.HIGHER,
        prompt=f"Simplify √{n}, giving your answer in the form a√b.",
        solution_steps=tuple(steps),
        final_answer=f"{k}√{m}",
        dedup_key=f"surd:{n}",
    )


TOPIC_POWERS_FOUNDATION = TopicDefinition(
    id="powers_foundation",
    display_name="Powers & Indices",
    description="Evaluate powers and use the laws of indices with positive integer powers.",
    generate=generate_powers_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_POWERS_HIGHER = TopicDefinition(
    id="powers_higher",
    display_name="Negative & Fractional Indices",
    description="Evaluate powers with negative, zero, and fractional indices.",
    generate=generate_powers_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_ROOTS_FOUNDATION = TopicDefinition(
    id="roots_foundation",
    display_name="Square & Cube Roots",
    description="Evaluate square and cube roots of perfect squares and cubes, and estimate roots.",
    generate=generate_roots_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_ROOTS_HIGHER = TopicDefinition(
    id="roots_higher",
    display_name="Simplifying Surds",
    description="Simplify a square root into the form a√b.",
    generate=generate_roots_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
