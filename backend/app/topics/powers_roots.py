import math
import random
from fractions import Fraction

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
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


def generate_modelled_example_powers_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["evaluate", "law_multiply", "law_divide", "law_power"])

    if shape == "evaluate":
        base = rng.randint(2, 12)
        exponent = rng.choice([2, 3])
        result = base**exponent

        manual = 1
        for _ in range(exponent):
            manual *= base
        if manual != result:
            raise ValueError("modelled example powers_foundation verification failed")

        power_word = "squared" if exponent == 2 else "cubed"
        repeated = " × ".join([str(base)] * exponent)
        teaching_steps = [
            f"{base}^{exponent} means {base} multiplied by itself {exponent} times (read as "
            f"'{base} {power_word}') - it does NOT mean {base} multiplied by {exponent}, which is a "
            "very common mistake.",
            f"Write it out in full as repeated multiplication: {repeated}.",
            f"Multiply through, left to right: {repeated} = {result}.",
            f"So {base}^{exponent} = {result}.",
        ]
        worked_calculation = [f"{base}^{exponent}", f"= {repeated}", f"= {result}"]
        return ModelledExample(
            topic_id="powers_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out {base}^{exponent}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(result),
        )

    base = rng.randint(2, 9)
    if shape == "law_multiply":
        m, n = rng.randint(2, 5), rng.randint(2, 5)
        result_exp = m + n
        if base**m * base**n != base**result_exp:
            raise ValueError("modelled example powers_foundation verification failed")
        prompt = f"Simplify {base}^{m} × {base}^{n}, giving your answer as a single power of {base}."
        teaching_steps = [
            f"{base}^{m} means {m} copies of {base} multiplied together, and {base}^{n} means {n} more "
            f"copies. Multiplying {base}^{m} × {base}^{n} just joins all of those copies into one long "
            "multiplication of the same base.",
            f"In total that's {m} + {n} = {result_exp} copies of {base} multiplied together, which is "
            f"exactly what {base}^{result_exp} means.",
            "This gives the general law: when multiplying powers of the SAME base, add the exponents "
            f"together. {base}^{m} × {base}^{n} = {base}^{result_exp}.",
        ]
        worked_calculation = [f"{base}^{m} × {base}^{n}", f"= {base}^({m}+{n})", f"= {base}^{result_exp}"]
        answer = f"{base}^{result_exp}"
    elif shape == "law_divide":
        m = rng.randint(4, 8)
        n = rng.randint(1, m - 1)
        result_exp = m - n
        if base**m // base**n != base**result_exp:
            raise ValueError("modelled example powers_foundation verification failed")
        prompt = f"Simplify {base}^{m} ÷ {base}^{n}, giving your answer as a single power of {base}."
        teaching_steps = [
            f"{base}^{m} ÷ {base}^{n} means {m} copies of {base} multiplied together on top, divided by "
            f"{n} copies of {base} on the bottom. Since dividing cancels matching factors, {n} of the "
            "copies on top cancel exactly with the copies on the bottom.",
            f"That leaves {m} - {n} = {result_exp} copies of {base} still multiplied together on top, "
            "with nothing left to cancel with underneath.",
            "This gives the general law: when dividing powers of the SAME base, subtract the exponents. "
            f"{base}^{m} ÷ {base}^{n} = {base}^{result_exp}.",
        ]
        worked_calculation = [f"{base}^{m} ÷ {base}^{n}", f"= {base}^({m}-{n})", f"= {base}^{result_exp}"]
        answer = f"{base}^{result_exp}"
    else:
        m, n = rng.randint(2, 4), rng.randint(2, 3)
        result_exp = m * n
        if (base**m) ** n != base**result_exp:
            raise ValueError("modelled example powers_foundation verification failed")
        prompt = f"Simplify ({base}^{m})^{n}, giving your answer as a single power of {base}."
        teaching_steps = [
            f"({base}^{m})^{n} means {base}^{m} multiplied by itself {n} times over - that's {n} "
            f"separate groups, each containing {m} copies of {base}.",
            f"Altogether that's {m} × {n} = {result_exp} copies of {base} multiplied together across "
            "all the groups combined.",
            "This gives the general law: when raising a power to another power, multiply the exponents "
            f"together. ({base}^{m})^{n} = {base}^{result_exp}.",
        ]
        worked_calculation = [f"({base}^{m})^{n}", f"= {base}^({m}×{n})", f"= {base}^{result_exp}"]
        answer = f"{base}^{result_exp}"

    return ModelledExample(
        topic_id="powers_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_powers_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["negative_index", "zero_index", "fractional_root", "fractional_full"])

    if shape == "negative_index":
        base = rng.randint(2, 6)
        exponent = rng.randint(2, 4)
        result = Fraction(1, base**exponent)

        check = Fraction(1, base) ** exponent
        if check != result:
            raise ValueError("modelled example powers_higher verification failed")

        teaching_steps = [
            "A negative index doesn't make the answer come out negative - instead, it's an instruction "
            f"to take the reciprocal (flip the number to 1 over it). {base}^-{exponent} means "
            f"1 ÷ {base}^{exponent}, not -({base}^{exponent}).",
            f"So rewrite {base}^-{exponent} as 1/{base}^{exponent}, keeping the exponent positive but "
            "moving the whole expression underneath a 1.",
            f"Now evaluate the positive power on the bottom as usual: {base}^{exponent} = {base**exponent}.",
            f"This gives {base}^-{exponent} = 1/{base**exponent}.",
        ]
        worked_calculation = [f"{base}^-{exponent}", f"= 1/{base}^{exponent}", f"= 1/{base**exponent}"]
        return ModelledExample(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {base}^-{exponent}. Give your answer as a fraction.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"1/{base**exponent}",
        )

    if shape == "zero_index":
        base = rng.randint(2, 20)
        teaching_steps = [
            "It might seem surprising, but ANY nonzero number raised to the power 0 equals 1 - this "
            "isn't an arbitrary rule, it falls directly out of the law for dividing powers.",
            f"Using the division law, {base}^m ÷ {base}^m = {base}^(m-m) = {base}^0 for any exponent m. "
            f"But {base}^m ÷ {base}^m is also just a number divided by itself, which always equals 1.",
            f"Since both expressions describe the same calculation, {base}^0 must equal 1 - and this "
            "argument works for any nonzero base, not just this one.",
            f"So {base}^0 = 1.",
        ]
        worked_calculation = [f"{base}^0", "= 1"]
        return ModelledExample(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {base}^0.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer="1",
        )

    n = rng.choice([2, 3])
    root_val = rng.randint(2, 6)
    a = root_val**n

    if shape == "fractional_root":
        check = round(a ** (1 / n))
        if check != root_val or check**n != a:
            raise ValueError("modelled example powers_higher verification failed")
        root_word = "square" if n == 2 else "cube"
        teaching_steps = [
            f"A power written as a unit fraction, 1/{n}, is another way of writing a root: a^(1/{n}) "
            f"means the {n}th root of a. So {a}^(1/{n}) is asking for the {root_word} root of {a}.",
            f"The {root_word} root of {a} is the number which, when raised to the power {n}, gives back {a}.",
            f"{root_val}^{n} = {a}, so that number is {root_val}.",
            f"Therefore {a}^(1/{n}) = {root_val}.",
        ]
        worked_calculation = [f"{a}^(1/{n})", f"= {root_word} root of {a}", f"= {root_val}"]
        return ModelledExample(
            topic_id="powers_higher",
            tier=Tier.HIGHER,
            prompt=f"Work out {a}^(1/{n}).",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(root_val),
        )

    m = 2 if n == 3 else 3  # keep m != n so the fraction m/n isn't trivially 1
    result = root_val**m
    check = round(a ** (1 / n)) ** m
    if check != result:
        raise ValueError("modelled example powers_higher verification failed")
    root_word = "square" if n == 2 else "cube"
    teaching_steps = [
        f"A power written as a fraction m/n, like {m}/{n} here, combines two separate steps in one go: "
        f"the denominator ({n}) means take a root, and the numerator ({m}) means raise to a power.",
        "It doesn't matter which of the two steps is done first, but taking the root first is usually "
        "easier because it keeps the numbers smaller before the power is applied.",
        f"{a}^({m}/{n}) = ({a}^(1/{n}))^{m}. The {root_word} root of {a} is {root_val}, since "
        f"{root_val}^{n} = {a}.",
        f"Now raise that root to the power {m}: {root_val}^{m} = {result}.",
    ]
    worked_calculation = [
        f"{a}^({m}/{n})",
        f"= ({a}^(1/{n}))^{m}",
        f"= {root_val}^{m}",
        f"= {result}",
    ]
    return ModelledExample(
        topic_id="powers_higher",
        tier=Tier.HIGHER,
        prompt=f"Work out {a}^({m}/{n}).",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(result),
    )


def generate_modelled_example_roots_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["square_root", "cube_root", "estimate"])

    if shape == "square_root":
        root_val = rng.randint(2, 15)
        n = root_val**2
        check = math.isqrt(n)
        if check != root_val or check**2 != n:
            raise ValueError("modelled example roots_foundation verification failed")
        teaching_steps = [
            f"√{n} is asking 'what number, multiplied by itself, gives {n}?' - square rooting is the "
            "inverse operation to squaring.",
            f"Think about which whole number squares to give a number the size of {n}, and try "
            f"{root_val} as a candidate.",
            f"Check: {root_val}^2 = {root_val} × {root_val} = {n}, which confirms the guess is exactly right.",
            f"So √{n} = {root_val}.",
        ]
        worked_calculation = [f"√{n}", f"{root_val}^2 = {n}", f"√{n} = {root_val}"]
        return ModelledExample(
            topic_id="roots_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out √{n}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(root_val),
        )

    if shape == "cube_root":
        root_val = rng.randint(2, 10)
        n = root_val**3
        check = round(n ** (1 / 3))
        if check != root_val or check**3 != n:
            raise ValueError("modelled example roots_foundation verification failed")
        teaching_steps = [
            f"The cube root of {n} is asking 'what number, multiplied by itself three times, gives "
            f"{n}?' - it's the inverse operation to cubing.",
            f"Try {root_val} as a candidate: cubing a number means multiplying it by itself twice more, "
            f"i.e. {root_val} × {root_val} × {root_val}.",
            f"Check: {root_val}^3 = {n}, which confirms the guess is exactly right.",
            f"So the cube root of {n} is {root_val}.",
        ]
        worked_calculation = [f"cube root of {n}", f"{root_val}^3 = {n}", f"cube root of {n} = {root_val}"]
        return ModelledExample(
            topic_id="roots_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Work out the cube root of {n}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(root_val),
        )

    lo = rng.randint(2, 14)
    hi = lo + 1
    n = rng.randint(lo**2 + 1, hi**2 - 1)

    if not (lo**2 < n < hi**2) or math.isqrt(n) != lo:
        raise ValueError("modelled example roots_foundation verification failed")

    teaching_steps = [
        f"{n} isn't a perfect square, so √{n} isn't a whole number - but it must still lie between two "
        "consecutive whole numbers, and those can be pinned down without a calculator.",
        f"List the perfect squares either side of {n}: try {lo}^2 = {lo**2} and {hi}^2 = {hi**2}.",
        f"Since {lo**2} < {n} < {hi**2}, and square rooting doesn't change the order of positive numbers, "
        f"it follows that √{lo**2} < √{n} < √{hi**2}, i.e. {lo} < √{n} < {hi}.",
        f"So √{n} lies between the consecutive whole numbers {lo} and {hi}.",
    ]
    worked_calculation = [
        f"{lo}^2 = {lo**2}, {hi}^2 = {hi**2}",
        f"{lo**2} < {n} < {hi**2}",
        f"{lo} < √{n} < {hi}",
    ]
    return ModelledExample(
        topic_id="roots_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Without using a calculator, show that √{n} lies between two consecutive whole numbers, and state them.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"between {lo} and {hi}",
    )


def generate_modelled_example_roots_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(50):
        k = rng.randint(2, 6)
        m = rng.choice(_SQUARE_FREE_FACTORS)
        n = k * k * m
        if n <= 300:
            break
    else:
        raise ValueError("modelled example roots_higher could not find suitable numbers")

    if k * k * m != n:
        raise ValueError("modelled example roots_higher verification failed: reconstruction mismatch")
    for p in range(2, int(m**0.5) + 1):
        if m % (p * p) == 0:
            raise ValueError("modelled example roots_higher verification failed: m is not square-free")

    teaching_steps = [
        f"√{n} isn't a whole number, but it can still be simplified if {n} has a square number hiding "
        "inside it as a factor - that square factor can be 'pulled out' from underneath the root sign.",
        f"Look for the largest square number that divides exactly into {n}: here {n} = {k}^2 × {m}, and "
        f"{k}^2 = {k * k} is the largest such square factor of {n}.",
        f"Using the rule √(a × b) = √a × √b, split the root apart: √{n} = √({k * k} × {m}) = √{k * k} × √{m}.",
        f"√{k * k} simplifies exactly to {k} (it's a perfect square), but √{m} can't be simplified any "
        f"further since {m} itself has no square factors left inside it. So √{n} = {k}√{m}.",
    ]
    worked_calculation = [
        f"√{n}",
        f"= √({k}^2 × {m})",
        f"= {k}√{m}",
    ]
    return ModelledExample(
        topic_id="roots_higher",
        tier=Tier.HIGHER,
        prompt=f"Simplify √{n}, giving your answer in the form a√b.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{k}√{m}",
    )


def _fmt_simple_rationalised(a2: int, b: int, b2: int) -> str:
    """Render a2*sqrt(b)/b2, omitting the denominator entirely when b2 == 1."""
    term = f"{a2}√{b}" if a2 != 1 else f"√{b}"
    return term if b2 == 1 else f"{term}/{b2}"


def _build_rationalise_simple(rng: random.Random) -> Question:
    a = rng.randint(2, 20)
    b = rng.choice(_SQUARE_FREE_FACTORS)

    # Independent check that b is genuinely square-free - a different check
    # than the curated _SQUARE_FREE_FACTORS list it was drawn from.
    for p in range(2, int(b**0.5) + 1):
        if b % (p * p) == 0:
            raise ValueError("rationalise_denominator verification failed: b is not square-free")

    g = math.gcd(a, b)
    a2, b2 = a // g, b // g

    # Independent verification: evaluate both the original expression and
    # the claimed rationalised result to high precision and confirm they
    # match closely - a different check than the gcd-simplification
    # arithmetic above (no sp.nsimplify, per project convention).
    original = sp.Rational(a) / sp.sqrt(b)
    claimed = sp.Rational(a2, b2) * sp.sqrt(b)
    if abs(sp.N(original, 30) - sp.N(claimed, 30)) > sp.Float("1e-20"):
        raise ValueError("rationalise_denominator simple verification failed")

    answer = _fmt_simple_rationalised(a2, b, b2)
    steps = [f"Multiply the top and bottom by √{b}: {a}/√{b} = {a}√{b}/{b}"]
    if g > 1:
        steps.append(f"Simplify {a}/{b} by dividing by {g}: {answer}")
    else:
        steps.append(f"= {answer}")

    return Question(
        topic_id="rationalise_denominator",
        tier=Tier.HIGHER,
        prompt=f"Rationalise the denominator of {a}/√{b}, giving your answer in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"rationalise_simple:{a}:{b}",
    )


def _build_rationalise_conjugate(rng: random.Random) -> Question:
    for _ in range(300):
        b = rng.randint(2, 9)
        c = rng.choice(_SQUARE_FREE_FACTORS)
        D = b * b - c
        if D > 0:
            break
    else:
        raise ValueError("rationalise_denominator: could not construct conjugate-shape numbers")

    a = rng.randint(2, 12)
    sign = rng.choice([1, -1])  # original denominator is (b + sign*root_c)
    conj_sign = -sign

    denom_str = f"{b} + √{c}" if sign > 0 else f"{b} - √{c}"
    conj_str = f"{b} - √{c}" if sign > 0 else f"{b} + √{c}"

    raw_numerator_str = f"{a * b} {'+' if conj_sign > 0 else '-'} {a}√{c}"

    g = math.gcd(a, D)
    a2, D2 = a // g, D // g
    nc, kc = a2 * b, a2
    numerator_str = f"{nc} {'+' if conj_sign > 0 else '-'} {kc}√{c}"
    answer = numerator_str if D2 == 1 else f"({numerator_str})/{D2}"

    # Independent verification: evaluate both the original expression and
    # the claimed rationalised result to high precision and confirm they
    # match closely - a different check than the conjugate-multiplication
    # algebra above (no sp.nsimplify, per project convention).
    original = sp.Rational(a) / (b + sign * sp.sqrt(c))
    claimed = (nc + conj_sign * kc * sp.sqrt(c)) / D2
    if abs(sp.N(original, 30) - sp.N(claimed, 30)) > sp.Float("1e-20"):
        raise ValueError("rationalise_denominator conjugate verification failed")

    prompt = f"Rationalise the denominator of {a}/({denom_str}), giving your answer in its simplest form."
    steps = [
        f"Multiply the numerator and denominator by the conjugate of the denominator, ({conj_str}):",
        f"{a}/({denom_str}) = {a}({conj_str}) / [({denom_str})({conj_str})]",
        f"The denominator is a difference of two squares: {b}^2 - {c} = {D}",
        f"The numerator is {a}({conj_str}) = {raw_numerator_str}",
    ]
    if g > 1:
        steps.append(f"Simplify by dividing numerator and denominator by {g}: {answer}")
    else:
        steps.append(f"= {answer}")

    return Question(
        topic_id="rationalise_denominator",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"rationalise_conj:{a}:{b}:{c}:{sign}",
    )


def generate_rationalise_denominator(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["simple", "conjugate"])
    if shape == "simple":
        return _build_rationalise_simple(rng)
    return _build_rationalise_conjugate(rng)


def generate_modelled_example_rationalise_denominator(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["simple", "conjugate"])

    if shape == "simple":
        a = rng.randint(2, 20)
        b = rng.choice(_SQUARE_FREE_FACTORS)

        for p in range(2, int(b**0.5) + 1):
            if b % (p * p) == 0:
                raise ValueError("modelled example rationalise_denominator verification failed: b is not square-free")

        g = math.gcd(a, b)
        a2, b2 = a // g, b // g

        original = sp.Rational(a) / sp.sqrt(b)
        claimed = sp.Rational(a2, b2) * sp.sqrt(b)
        if abs(sp.N(original, 30) - sp.N(claimed, 30)) > sp.Float("1e-20"):
            raise ValueError("modelled example rationalise_denominator simple verification failed")

        answer = _fmt_simple_rationalised(a2, b, b2)
        teaching_steps = [
            f"A fraction like {a}/√{b} has an irrational (never-terminating, non-repeating) number sitting "
            "in the denominator - by convention, GCSE answers avoid leaving a root on the bottom, so it "
            "needs to be moved to the top instead.",
            f"The trick is to multiply the fraction by √{b}/√{b}, which equals 1, so the value of the "
            f"fraction doesn't change - but on the bottom, √{b} × √{b} = {b}, a whole number.",
            f"Applying this: {a}/√{b} = ({a} × √{b})/(√{b} × √{b}) = {a}√{b}/{b}.",
            (
                f"The fraction {a}/{b} still shares a common factor of {g}, so dividing both by it gives "
                f"the fully simplified answer {answer}."
                if g > 1
                else f"{a} and {b} share no common factor, so {a}√{b}/{b} is already fully simplified."
            ),
            f"So {a}/√{b} rationalises to {answer}.",
        ]
        worked_calculation = [
            f"{a}/√{b}",
            f"= {a}√{b}/{b}",
            f"= {answer}",
        ]
        return ModelledExample(
            topic_id="rationalise_denominator",
            tier=Tier.HIGHER,
            prompt=f"Rationalise the denominator of {a}/√{b}, giving your answer in its simplest form.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    for _ in range(300):
        b = rng.randint(2, 9)
        c = rng.choice(_SQUARE_FREE_FACTORS)
        D = b * b - c
        if D > 0:
            break
    else:
        raise ValueError("modelled example rationalise_denominator: could not construct conjugate-shape numbers")

    a = rng.randint(2, 12)
    sign = rng.choice([1, -1])
    conj_sign = -sign

    denom_str = f"{b} + √{c}" if sign > 0 else f"{b} - √{c}"
    conj_str = f"{b} - √{c}" if sign > 0 else f"{b} + √{c}"
    raw_numerator_str = f"{a * b} {'+' if conj_sign > 0 else '-'} {a}√{c}"

    g = math.gcd(a, D)
    a2, D2 = a // g, D // g
    nc, kc = a2 * b, a2
    numerator_str = f"{nc} {'+' if conj_sign > 0 else '-'} {kc}√{c}"
    answer = numerator_str if D2 == 1 else f"({numerator_str})/{D2}"

    original = sp.Rational(a) / (b + sign * sp.sqrt(c))
    claimed = (nc + conj_sign * kc * sp.sqrt(c)) / D2
    if abs(sp.N(original, 30) - sp.N(claimed, 30)) > sp.Float("1e-20"):
        raise ValueError("modelled example rationalise_denominator conjugate verification failed")

    teaching_steps = [
        f"A denominator like ({denom_str}) can't be rationalised just by multiplying by √{c}/√{c}, since "
        f"that would leave a mixed term - instead, the trick is to multiply by the 'conjugate', "
        f"({conj_str}), which has the opposite sign in front of the root.",
        f"Multiplying a bracket by its conjugate always gives a difference of two squares, which clears "
        f"the root completely: ({denom_str})({conj_str}) = {b}^2 - {c} = {D}, a whole number.",
        f"Multiply the numerator by the same conjugate to keep the fraction's value unchanged: "
        f"{a}({conj_str}) = {raw_numerator_str}.",
        f"Putting the new numerator over the new denominator gives ({raw_numerator_str})/{D}.",
        (
            f"{a} and {D} share a common factor of {g}, so dividing numerator and denominator by it gives "
            f"the fully simplified answer {answer}."
            if g > 1
            else f"{a} and {D} share no common factor, so ({raw_numerator_str})/{D} is already fully "
            "simplified."
        ),
    ]
    worked_calculation = [
        f"{a}/({denom_str})",
        f"= {a}({conj_str}) / ({b}^2 - {c})",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="rationalise_denominator",
        tier=Tier.HIGHER,
        prompt=f"Rationalise the denominator of {a}/({denom_str}), giving your answer in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_POWERS_FOUNDATION = TopicDefinition(
    id="powers_foundation",
    display_name="Powers & Indices",
    description="Evaluate powers and use the laws of indices with positive integer powers.",
    generate=generate_powers_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_powers_foundation,
)

TOPIC_POWERS_HIGHER = TopicDefinition(
    id="powers_higher",
    display_name="Negative & Fractional Indices",
    description="Evaluate powers with negative, zero, and fractional indices.",
    generate=generate_powers_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_powers_higher,
)

TOPIC_ROOTS_FOUNDATION = TopicDefinition(
    id="roots_foundation",
    display_name="Square & Cube Roots",
    description="Evaluate square and cube roots of perfect squares and cubes, and estimate roots.",
    generate=generate_roots_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_roots_foundation,
)

TOPIC_ROOTS_HIGHER = TopicDefinition(
    id="roots_higher",
    display_name="Simplifying Surds",
    description="Simplify a square root into the form a√b.",
    generate=generate_roots_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_roots_higher,
)

TOPIC_RATIONALISE_DENOMINATOR = TopicDefinition(
    id="rationalise_denominator",
    display_name="Rationalising the Denominator",
    description="Rationalise a denominator containing a surd, including conjugate denominators.",
    generate=generate_rationalise_denominator,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_rationalise_denominator,
)
