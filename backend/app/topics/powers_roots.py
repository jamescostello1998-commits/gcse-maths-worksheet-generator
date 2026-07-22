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


def _largest_square_factor(n: int) -> tuple[int, int]:
    """Return (k, m) with k*k*m == n and m square-free, k maximal."""
    k = math.isqrt(n)
    while k > 1:
        if n % (k * k) == 0:
            return k, n // (k * k)
        k -= 1
    return 1, n


def _fmt_p_plus_q_root(p_val: int, q_val: int, c: int) -> str:
    """Render p_val + q_val*sqrt(c) as 'P + Q√c' (or 'P - Q√c'), omitting a
    coefficient of 1 on the surd term."""
    if q_val == 0:
        return str(p_val)
    sign = "+" if q_val > 0 else "-"
    coeff = abs(q_val)
    term = f"√{c}" if coeff == 1 else f"{coeff}√{c}"
    return f"{p_val} {sign} {term}"


def generate_negative_indices(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["evaluate", "law_multiply", "law_divide"])

    if shape == "evaluate":
        base = rng.randint(2, 10)
        n = rng.randint(1, 3)
        result = base**n

        # Independent check via sympy's own exponentiation of a Rational
        # base with a negative integer exponent - a different code path
        # than the manual Fraction(1, base**n) construction.
        check = sp.Rational(base) ** (-n)
        if check != sp.Rational(1, result):
            raise ValueError("negative_indices verification failed")

        steps = [
            f"A negative index means take the reciprocal: {base}^-{n} = 1/{base}^{n}",
            f"{base}^{n} = {result}",
            f"{base}^-{n} = 1/{result}",
        ]
        return Question(
            topic_id="negative_indices",
            tier=Tier.FOUNDATION,
            prompt=f"Work out {base}^-{n}. Give your answer as a fraction.",
            solution_steps=tuple(steps),
            final_answer=f"1/{result}",
            dedup_key=f"negidx_eval:{base}:{n}",
        )

    base = rng.randint(2, 9)
    if shape == "law_multiply":
        m, n = rng.randint(1, 4), rng.randint(1, 4)
        result_exp = -(m + n)

        # Independent check: evaluate both sides as exact fractions via a
        # direct multiplication of reciprocals - a different path than the
        # "add the (negative) powers" law used in the displayed steps.
        lhs = Fraction(1, base**m) * Fraction(1, base**n)
        rhs = Fraction(1, base ** (m + n))
        if lhs != rhs:
            raise ValueError("negative_indices verification failed")

        prompt = f"Simplify {base}^-{m} × {base}^-{n}, giving your answer as a single power of {base}."
        steps = [
            f"Add the powers: -{m} + (-{n}) = {result_exp}",
            f"{base}^-{m} × {base}^-{n} = {base}^{result_exp}",
        ]
        dedup_key = f"negidx_mult:{base}:{m}:{n}"
    else:
        m = rng.randint(1, 4)
        n = rng.randint(1, 4)
        while n == m:
            n = rng.randint(1, 4)
        result_exp = n - m

        # Independent check: evaluate both sides as exact fractions via
        # direct division - a different path than the "subtract the
        # (negative) powers" law used in the displayed steps.
        lhs = Fraction(1, base**m) / Fraction(1, base**n)
        rhs = Fraction(base**n, base**m)
        if lhs != rhs:
            raise ValueError("negative_indices verification failed")
        if (result_exp >= 0 and lhs != Fraction(base**result_exp, 1)) or (
            result_exp < 0 and lhs != Fraction(1, base ** (-result_exp))
        ):
            raise ValueError("negative_indices verification failed")

        prompt = f"Simplify {base}^-{m} ÷ {base}^-{n}, giving your answer as a single power of {base}."
        steps = [
            f"Subtract the powers: -{m} - (-{n}) = {result_exp}",
            f"{base}^-{m} ÷ {base}^-{n} = {base}^{result_exp}",
        ]
        dedup_key = f"negidx_div:{base}:{m}:{n}"

    return Question(
        topic_id="negative_indices",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{base}^{result_exp}",
        dedup_key=dedup_key,
    )


def generate_modelled_example_negative_indices(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["evaluate", "law_multiply", "law_divide"])

    if shape == "evaluate":
        base = rng.randint(2, 10)
        n = rng.randint(1, 3)
        result = base**n

        check = sp.Rational(base) ** (-n)
        if check != sp.Rational(1, result):
            raise ValueError("modelled example negative_indices verification failed")

        teaching_steps = [
            "A negative index doesn't make the answer negative - it's an instruction to take the "
            f"reciprocal (flip the number to 1 over it). {base}^-{n} means 1 ÷ {base}^{n}, not "
            f"-({base}^{n}).",
            f"Rewrite {base}^-{n} as 1/{base}^{n}, keeping the exponent positive but moving the whole "
            "expression underneath a 1.",
            f"Now evaluate the positive power on the bottom as usual: {base}^{n} = {result}.",
            f"So {base}^-{n} = 1/{result}.",
        ]
        worked_calculation = [f"{base}^-{n}", f"= 1/{base}^{n}", f"= 1/{result}"]
        return ModelledExample(
            topic_id="negative_indices",
            tier=Tier.FOUNDATION,
            prompt=f"Work out {base}^-{n}. Give your answer as a fraction.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"1/{result}",
        )

    base = rng.randint(2, 9)
    if shape == "law_multiply":
        m, n = rng.randint(1, 4), rng.randint(1, 4)
        result_exp = -(m + n)
        lhs = Fraction(1, base**m) * Fraction(1, base**n)
        rhs = Fraction(1, base ** (m + n))
        if lhs != rhs:
            raise ValueError("modelled example negative_indices verification failed")

        prompt = f"Simplify {base}^-{m} × {base}^-{n}, giving your answer as a single power of {base}."
        teaching_steps = [
            f"{base}^-{m} and {base}^-{n} are both negative powers of the SAME base, so the usual "
            "multiplying-powers law still applies: add the exponents together, keeping their signs.",
            f"Adding the exponents: -{m} + (-{n}) = {result_exp}. Both exponents were already negative, "
            "so the total gets more negative, not less.",
            f"This gives {base}^-{m} × {base}^-{n} = {base}^{result_exp} - still a single power of "
            f"{base}, just with a more negative index.",
        ]
        worked_calculation = [f"{base}^-{m} × {base}^-{n}", f"= {base}^(-{m}-{n})", f"= {base}^{result_exp}"]
        answer = f"{base}^{result_exp}"
    else:
        m = rng.randint(1, 4)
        n = rng.randint(1, 4)
        while n == m:
            n = rng.randint(1, 4)
        result_exp = n - m
        lhs = Fraction(1, base**m) / Fraction(1, base**n)
        rhs = Fraction(base**n, base**m)
        if lhs != rhs:
            raise ValueError("modelled example negative_indices verification failed")

        prompt = f"Simplify {base}^-{m} ÷ {base}^-{n}, giving your answer as a single power of {base}."
        teaching_steps = [
            f"{base}^-{m} ÷ {base}^-{n} is still a division of powers of the SAME base, so the usual "
            "dividing-powers law applies: subtract the exponents, keeping their signs.",
            f"Subtract the exponents: -{m} - (-{n}) = -{m} + {n} = {result_exp}. Subtracting a negative "
            "flips it into an addition, which is a common place to slip up.",
            f"This gives {base}^-{m} ÷ {base}^-{n} = {base}^{result_exp} - a single power of {base}.",
        ]
        worked_calculation = [f"{base}^-{m} ÷ {base}^-{n}", f"= {base}^(-{m}-(-{n}))", f"= {base}^{result_exp}"]
        answer = f"{base}^{result_exp}"

    return ModelledExample(
        topic_id="negative_indices",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_simplifying_indices_challenging(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["mult_then_power", "frac_then_neg", "power_then_divide"])

    if shape == "mult_then_power":
        base = rng.randint(2, 6)
        for _ in range(50):
            m = rng.choice([x for x in range(-3, 4) if x != 0])
            n = rng.choice([x for x in range(-3, 4) if x != 0])
            p = rng.choice([2, 3])
            combined = (m + n) * p
            if combined != 0 and abs(combined) <= 6:
                break
        else:
            raise ValueError("simplifying_indices_challenging could not construct mult_then_power case")

        result = Fraction(base**combined, 1) if combined >= 0 else Fraction(1, base ** (-combined))

        # Independent check: evaluate the whole original expression directly
        # via sympy - a different path than manually combining exponents.
        original = (sp.Rational(base) ** m * sp.Rational(base) ** n) ** p
        if original != sp.Rational(result.numerator, result.denominator):
            raise ValueError("simplifying_indices_challenging verification failed")

        prompt = f"Simplify ({base}^{m} × {base}^{n})^{p}, giving your answer as a fraction where necessary."
        answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
        steps = [
            f"Add the powers inside the bracket first: {m} + {n} = {m + n}",
            f"({base}^{m} × {base}^{n})^{p} = ({base}^{m + n})^{p}",
            f"Multiply the powers: {m + n} × {p} = {combined}",
            f"({base}^{m + n})^{p} = {base}^{combined} = {answer}",
        ]
        return Question(
            topic_id="simplifying_indices_challenging",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"simp_multpow:{base}:{m}:{n}:{p}",
        )

    if shape == "frac_then_neg":
        b = rng.choice([2, 3])
        r = rng.randint(2, 5)
        base = r**b
        a = rng.randint(1, 3)
        while a == b:
            a = rng.randint(1, 3)
        c = rng.randint(1, 3)
        combined = a - b * c

        result = Fraction(r**combined, 1) if combined >= 0 else Fraction(1, r ** (-combined))

        # Independent check: evaluate the original expression directly via
        # sympy's own handling of a Rational base with a rational exponent -
        # a different path than the r^(a - b*c) exponent bookkeeping.
        original = sp.Rational(base) ** sp.Rational(a, b) * sp.Rational(base) ** (-c)
        if original != sp.Rational(result.numerator, result.denominator):
            raise ValueError("simplifying_indices_challenging verification failed")

        prompt = f"Simplify {base}^({a}/{b}) × {base}^-{c}, giving your answer as a fraction where necessary."
        answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
        root_word = "square" if b == 2 else "cube"
        steps = [
            f"{base}^(1/{b}) is the {root_word} root of {base}, which is {r}, so {base}^({a}/{b}) = {r}^{a}",
            f"{base}^-{c} = 1/{base}^{c} = 1/{r}^{b * c}",
            f"{base}^({a}/{b}) × {base}^-{c} = {r}^{a} × 1/{r}^{b * c} = {r}^({a}-{b * c}) = {r}^{combined}",
            f"{r}^{combined} = {answer}",
        ]
        return Question(
            topic_id="simplifying_indices_challenging",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"simp_fracneg:{r}:{b}:{a}:{c}",
        )

    base = rng.randint(2, 6)
    for _ in range(50):
        m = rng.choice([x for x in range(-3, 4) if x != 0])
        n = rng.choice([2, 3])
        p = rng.choice([x for x in range(-4, 5) if x != 0])
        combined = m * n - p
        if combined != 0 and abs(combined) <= 6:
            break
    else:
        raise ValueError("simplifying_indices_challenging could not construct power_then_divide case")

    result = Fraction(base**combined, 1) if combined >= 0 else Fraction(1, base ** (-combined))

    # Independent check: evaluate the whole original expression directly via
    # sympy - a different path than the m*n - p exponent bookkeeping.
    original = (sp.Rational(base) ** m) ** n / sp.Rational(base) ** p
    if original != sp.Rational(result.numerator, result.denominator):
        raise ValueError("simplifying_indices_challenging verification failed")

    prompt = f"Simplify ({base}^{m})^{n} ÷ {base}^{p}, giving your answer as a fraction where necessary."
    answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
    steps = [
        f"Multiply the powers in the bracket: {m} × {n} = {m * n}",
        f"({base}^{m})^{n} = {base}^{m * n}",
        f"Subtract the powers to divide: {m * n} - ({p}) = {combined}",
        f"{base}^{m * n} ÷ {base}^{p} = {base}^{combined} = {answer}",
    ]
    return Question(
        topic_id="simplifying_indices_challenging",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"simp_powdiv:{base}:{m}:{n}:{p}",
    )


def generate_modelled_example_simplifying_indices_challenging(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["mult_then_power", "frac_then_neg", "power_then_divide"])

    if shape == "mult_then_power":
        base = rng.randint(2, 6)
        for _ in range(50):
            m = rng.choice([x for x in range(-3, 4) if x != 0])
            n = rng.choice([x for x in range(-3, 4) if x != 0])
            p = rng.choice([2, 3])
            combined = (m + n) * p
            if combined != 0 and abs(combined) <= 6:
                break
        else:
            raise ValueError("modelled example simplifying_indices_challenging could not construct case")

        result = Fraction(base**combined, 1) if combined >= 0 else Fraction(1, base ** (-combined))
        original = (sp.Rational(base) ** m * sp.Rational(base) ** n) ** p
        if original != sp.Rational(result.numerator, result.denominator):
            raise ValueError("modelled example simplifying_indices_challenging verification failed")

        answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
        teaching_steps = [
            "This question stacks two separate index laws in one go, so work from the innermost part "
            "outward rather than trying to do everything at once.",
            f"Inside the bracket, {base}^{m} and {base}^{n} are powers of the SAME base being multiplied, "
            f"so add their exponents: {m} + {n} = {m + n}, giving {base}^{m + n}.",
            f"Now the outer power applies: raising {base}^{m + n} to the power {p} means multiplying the "
            f"exponents, {m + n} × {p} = {combined}, giving {base}^{combined}.",
            f"Finally evaluate {base}^{combined}: since the exponent is negative, take the reciprocal of "
            f"{base}^{-combined}, giving {answer}." if combined < 0 else
            f"Finally evaluate {base}^{combined} = {answer}.",
        ]
        worked_calculation = [
            f"({base}^{m} × {base}^{n})^{p}",
            f"= ({base}^{m + n})^{p}",
            f"= {base}^{combined}",
            f"= {answer}",
        ]
        return ModelledExample(
            topic_id="simplifying_indices_challenging",
            tier=Tier.HIGHER,
            prompt=f"Simplify ({base}^{m} × {base}^{n})^{p}, giving your answer as a fraction where necessary.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    if shape == "frac_then_neg":
        b = rng.choice([2, 3])
        r = rng.randint(2, 5)
        base = r**b
        a = rng.randint(1, 3)
        while a == b:
            a = rng.randint(1, 3)
        c = rng.randint(1, 3)
        combined = a - b * c

        result = Fraction(r**combined, 1) if combined >= 0 else Fraction(1, r ** (-combined))
        original = sp.Rational(base) ** sp.Rational(a, b) * sp.Rational(base) ** (-c)
        if original != sp.Rational(result.numerator, result.denominator):
            raise ValueError("modelled example simplifying_indices_challenging verification failed")

        answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
        root_word = "square" if b == 2 else "cube"
        teaching_steps = [
            f"This question combines a fractional index with a negative one, so deal with each piece "
            "separately before combining them.",
            f"{base}^(1/{b}) means the {root_word} root of {base}, which is {r} (since {r}^{b} = {base}), "
            f"so {base}^({a}/{b}) = {r}^{a}.",
            f"{base}^-{c} means the reciprocal of {base}^{c}. Since {base} = {r}^{b}, that's "
            f"1/{r}^({b}×{c}) = 1/{r}^{b * c}.",
            f"Multiplying {r}^{a} by 1/{r}^{b * c} combines to a single power of {r}: "
            f"{r}^({a}-{b * c}) = {r}^{combined} = {answer}.",
        ]
        worked_calculation = [
            f"{base}^({a}/{b}) × {base}^-{c}",
            f"= {r}^{a} × {r}^-{b * c}",
            f"= {r}^{combined}",
            f"= {answer}",
        ]
        return ModelledExample(
            topic_id="simplifying_indices_challenging",
            tier=Tier.HIGHER,
            prompt=f"Simplify {base}^({a}/{b}) × {base}^-{c}, giving your answer as a fraction where necessary.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    base = rng.randint(2, 6)
    for _ in range(50):
        m = rng.choice([x for x in range(-3, 4) if x != 0])
        n = rng.choice([2, 3])
        p = rng.choice([x for x in range(-4, 5) if x != 0])
        combined = m * n - p
        if combined != 0 and abs(combined) <= 6:
            break
    else:
        raise ValueError("modelled example simplifying_indices_challenging could not construct case")

    result = Fraction(base**combined, 1) if combined >= 0 else Fraction(1, base ** (-combined))
    original = (sp.Rational(base) ** m) ** n / sp.Rational(base) ** p
    if original != sp.Rational(result.numerator, result.denominator):
        raise ValueError("modelled example simplifying_indices_challenging verification failed")

    answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
    teaching_steps = [
        "This question combines a 'power of a power' law with a division law, so simplify the bracket "
        "first before dealing with the division.",
        f"({base}^{m})^{n} means raising {base}^{m} to the power {n}, which multiplies the exponents: "
        f"{m} × {n} = {m * n}, giving {base}^{m * n}.",
        f"Dividing by {base}^{p} then subtracts that exponent: {m * n} - ({p}) = {combined}, giving "
        f"{base}^{combined}.",
        f"Evaluating {base}^{combined} gives {answer}.",
    ]
    worked_calculation = [
        f"({base}^{m})^{n} ÷ {base}^{p}",
        f"= {base}^{m * n} ÷ {base}^{p}",
        f"= {base}^{combined}",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="simplifying_indices_challenging",
        tier=Tier.HIGHER,
        prompt=f"Simplify ({base}^{m})^{n} ÷ {base}^{p}, giving your answer as a fraction where necessary.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def _format_fraction(frac: Fraction) -> str:
    return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"


def _show_solved_x(raw_num: int, raw_den: int, frac: Fraction) -> str:
    """Render 'x = <reduced fraction>', showing the raw-fraction-to-reduced-
    fraction step only when the raw form actually differs from the reduced
    one (otherwise 'x = 3/2 = 3/2' reads as an odd, pointless duplicate)."""
    raw_str = str(raw_num) if raw_den == 1 else f"{raw_num}/{raw_den}"
    answer = _format_fraction(frac)
    if raw_str == answer:
        return f"x = {answer}"
    return f"x = {raw_str} = {answer}"


def generate_indices_common_base_equations(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["power_equals_number", "linear_both_sides", "reciprocal"])

    if shape == "power_equals_number":
        p = rng.choice([2, 3, 5])
        i = rng.randint(2, 4)
        j = rng.randint(3, 6)
        a = p**i
        b_val = p**j
        x = Fraction(j, i)

        # Independent check: substitute the solved x back into the ORIGINAL
        # (un-rewritten) equation a^x = b_val, evaluated via sympy - a
        # different path than the common-base rewriting used to derive x.
        lhs = sp.N(sp.Rational(a) ** sp.Rational(x.numerator, x.denominator), 30)
        rhs = sp.N(sp.Rational(b_val), 30)
        if abs(lhs - rhs) > sp.Float("1e-20"):
            raise ValueError("indices_common_base_equations verification failed")

        answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
        steps = [
            f"Write both sides as powers of {p}: {a} = {p}^{i} and {b_val} = {p}^{j}",
            f"{a}^x = {b_val} becomes ({p}^{i})^x = {p}^{j}, i.e. {p}^({i}x) = {p}^{j}",
            f"Since the bases match, the powers must be equal: {i}x = {j}",
            _show_solved_x(j, i, x),
        ]
        return Question(
            topic_id="indices_common_base_equations",
            tier=Tier.HIGHER,
            prompt=f"Solve {a}^x = {b_val}.",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"idxeq_power:{p}:{i}:{j}",
        )

    if shape == "linear_both_sides":
        for _ in range(50):
            p = rng.choice([2, 3, 5])
            i1 = rng.randint(1, 4)
            i2 = rng.randint(1, 4)
            m = rng.randint(1, 4)
            n = rng.randint(2, 3)
            denom = i1 - i2 * n
            if denom != 0 and i1 != i2:
                x = Fraction(-i1 * m, denom)
                break
        else:
            raise ValueError("indices_common_base_equations could not construct linear_both_sides case")

        a = p**i1
        c = p**i2

        # Independent check: substitute x back into the ORIGINAL equation
        # a^(x+m) = c^(n*x), evaluated via sympy - a different path than the
        # linear-equation rewriting used to derive x.
        lhs = sp.N(sp.Rational(a) ** (sp.Rational(x.numerator, x.denominator) + m), 30)
        rhs = sp.N(sp.Rational(c) ** (n * sp.Rational(x.numerator, x.denominator)), 30)
        if abs(lhs - rhs) > sp.Float("1e-20"):
            raise ValueError("indices_common_base_equations verification failed")

        answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
        rhs_coeff = "x" if n == 1 else f"{n}x"
        lhs_bracket = f"x+{m}" if i1 == 1 else f"{i1}(x+{m})"
        lhs_expanded = f"x+{i1 * m}" if i1 == 1 else f"{i1}x+{i1 * m}"
        lhs_x_term = "x" if i1 == 1 else f"{i1}x"
        rhs_unexpanded = f"{n}x" if i2 == 1 else f"{i2}×{n}x"
        steps = [
            f"Write both sides as powers of {p}: {a} = {p}^{i1} and {c} = {p}^{i2}",
            f"{a}^(x+{m}) = {c}^({rhs_coeff}) becomes {p}^({lhs_bracket}) = {p}^({rhs_unexpanded}), "
            f"i.e. {p}^({lhs_expanded}) = {p}^({i2 * n}x)",
            f"Since the bases match, the powers must be equal: {lhs_x_term} + {i1 * m} = {i2 * n}x",
            f"Rearranging: {denom}x = -{i1 * m}, so {_show_solved_x(-i1 * m, denom, x)}",
        ]
        return Question(
            topic_id="indices_common_base_equations",
            tier=Tier.HIGHER,
            prompt=f"Solve {a}^(x+{m}) = {c}^({rhs_coeff}).",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"idxeq_linear:{p}:{i1}:{i2}:{m}:{n}",
        )

    p = rng.choice([2, 3, 5])
    c = rng.randint(1, 3)
    k = rng.randint(1, 4)
    x = Fraction(-k, c)

    # Independent check: substitute x back into the ORIGINAL equation
    # p^(c*x) = 1/p^k, evaluated via sympy - a different path than the
    # rewriting-as-a-negative-power method used to derive x.
    lhs = sp.N(sp.Rational(p) ** (c * sp.Rational(x.numerator, x.denominator)), 30)
    rhs = sp.N(sp.Rational(1, p**k), 30)
    if abs(lhs - rhs) > sp.Float("1e-20"):
        raise ValueError("indices_common_base_equations verification failed")

    answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    coeff_str = "x" if c == 1 else f"{c}x"
    exp_str = coeff_str if c == 1 else f"({coeff_str})"
    steps = [
        f"Write the right-hand side as a power of {p}: 1/{p}^{k} = {p}^-{k}",
        f"{p}^{exp_str} = {p}^-{k}",
        f"Since the bases match, the powers must be equal: {coeff_str} = -{k}",
        _show_solved_x(-k, c, x),
    ]
    return Question(
        topic_id="indices_common_base_equations",
        tier=Tier.HIGHER,
        prompt=f"Solve {p}^{exp_str} = 1/{p**k}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"idxeq_recip:{p}:{c}:{k}",
    )


def generate_modelled_example_indices_common_base_equations(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["power_equals_number", "linear_both_sides", "reciprocal"])

    if shape == "power_equals_number":
        p = rng.choice([2, 3, 5])
        i = rng.randint(2, 4)
        j = rng.randint(3, 6)
        a = p**i
        b_val = p**j
        x = Fraction(j, i)

        lhs = sp.N(sp.Rational(a) ** sp.Rational(x.numerator, x.denominator), 30)
        rhs = sp.N(sp.Rational(b_val), 30)
        if abs(lhs - rhs) > sp.Float("1e-20"):
            raise ValueError("modelled example indices_common_base_equations verification failed")

        answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
        teaching_steps = [
            f"Neither side of {a}^x = {b_val} is written as a power of the same number yet, but an "
            "equation like this can only be solved neatly once both sides share a common base.",
            f"Both {a} and {b_val} happen to be powers of {p}: {a} = {p}^{i}, and {b_val} = {p}^{j}.",
            f"Rewriting the left-hand side using the common base: {a}^x = ({p}^{i})^x = {p}^({i}x). Now "
            f"the equation reads {p}^({i}x) = {p}^{j}.",
            "Once both sides are powers of the SAME base, the only way they can be equal is if the "
            f"exponents themselves are equal: {i}x = {j}, so {_show_solved_x(j, i, x)}.",
        ]
        worked_calculation = [
            f"{a}^x = {b_val}",
            f"({p}^{i})^x = {p}^{j}",
            f"{i}x = {j}",
            f"x = {answer}",
        ]
        return ModelledExample(
            topic_id="indices_common_base_equations",
            tier=Tier.HIGHER,
            prompt=f"Solve {a}^x = {b_val}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    if shape == "linear_both_sides":
        for _ in range(50):
            p = rng.choice([2, 3, 5])
            i1 = rng.randint(1, 4)
            i2 = rng.randint(1, 4)
            m = rng.randint(1, 4)
            n = rng.randint(2, 3)
            denom = i1 - i2 * n
            if denom != 0 and i1 != i2:
                x = Fraction(-i1 * m, denom)
                break
        else:
            raise ValueError("modelled example indices_common_base_equations could not construct case")

        a = p**i1
        c = p**i2
        lhs = sp.N(sp.Rational(a) ** (sp.Rational(x.numerator, x.denominator) + m), 30)
        rhs = sp.N(sp.Rational(c) ** (n * sp.Rational(x.numerator, x.denominator)), 30)
        if abs(lhs - rhs) > sp.Float("1e-20"):
            raise ValueError("modelled example indices_common_base_equations verification failed")

        answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
        rhs_coeff = "x" if n == 1 else f"{n}x"
        lhs_bracket = f"x+{m}" if i1 == 1 else f"{i1}(x+{m})"
        lhs_expanded = f"x+{i1 * m}" if i1 == 1 else f"{i1}x+{i1 * m}"
        lhs_x_term = "x" if i1 == 1 else f"{i1}x"
        rhs_unexpanded = f"{n}x" if i2 == 1 else f"{i2}×{n}x"
        teaching_steps = [
            f"Here both sides already have an expression in the exponent, but the same common-base idea "
            f"still applies: {a} = {p}^{i1} and {c} = {p}^{i2} are both powers of {p}.",
            f"Rewrite each side as a power of {p}: {a}^(x+{m}) = {p}^({lhs_bracket}) = {p}^({lhs_expanded}), "
            f"and {c}^({rhs_coeff}) = {p}^({rhs_unexpanded}) = {p}^({i2 * n}x).",
            f"With matching bases, the exponents must be equal: {lhs_x_term} + {i1 * m} = {i2 * n}x.",
            f"Collecting the x terms onto one side: {denom}x = -{i1 * m}, so x = {answer}.",
        ]
        worked_calculation = [
            f"{a}^(x+{m}) = {c}^({rhs_coeff})",
            f"{p}^({lhs_expanded}) = {p}^({i2 * n}x)",
            f"{lhs_x_term} + {i1 * m} = {i2 * n}x",
            f"x = {answer}",
        ]
        return ModelledExample(
            topic_id="indices_common_base_equations",
            tier=Tier.HIGHER,
            prompt=f"Solve {a}^(x+{m}) = {c}^({rhs_coeff}).",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    p = rng.choice([2, 3, 5])
    c = rng.randint(1, 3)
    k = rng.randint(1, 4)
    x = Fraction(-k, c)

    lhs = sp.N(sp.Rational(p) ** (c * sp.Rational(x.numerator, x.denominator)), 30)
    rhs = sp.N(sp.Rational(1, p**k), 30)
    if abs(lhs - rhs) > sp.Float("1e-20"):
        raise ValueError("modelled example indices_common_base_equations verification failed")

    answer = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    coeff_str = "x" if c == 1 else f"{c}x"
    exp_str = coeff_str if c == 1 else f"({coeff_str})"
    teaching_steps = [
        f"The right-hand side, 1/{p}^{k}, looks different from a power of {p} at first glance, but a "
        "reciprocal of a power is just that power written with a negative exponent.",
        f"Rewrite 1/{p}^{k} as {p}^-{k}. Now the equation {p}^{exp_str} = 1/{p**k} reads "
        f"{p}^{exp_str} = {p}^-{k}, with matching bases on both sides.",
        f"Since the bases match, the exponents themselves must be equal: {coeff_str} = -{k}.",
        (f"Dividing both sides by {c} gives {_show_solved_x(-k, c, x)}." if c != 1 else f"So {_show_solved_x(-k, c, x)}."),
    ]
    worked_calculation = [
        f"{p}^{exp_str} = 1/{p**k}",
        f"{p}^{exp_str} = {p}^-{k}",
        f"{coeff_str} = -{k}",
        f"x = {answer}",
    ]
    return ModelledExample(
        topic_id="indices_common_base_equations",
        tier=Tier.HIGHER,
        prompt=f"Solve {p}^{exp_str} = 1/{p**k}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_surds_multiply_divide(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["multiply_clean", "multiply_surd", "divide_clean", "divide_surd"])

    if shape == "multiply_clean":
        d = rng.choice(_SQUARE_FREE_FACTORS)
        s = rng.randint(2, 6)
        a, b = d * s * s, d
        result = d * s

        # Independent check: evaluate the product numerically via sympy - a
        # different path than the a = d*s^2 construction above.
        original = sp.N(sp.sqrt(a) * sp.sqrt(b), 30)
        claimed = sp.N(sp.Integer(result), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("surds_multiply_divide verification failed")

        steps = [
            f"√{a} × √{b} = √({a} × {b}) = √{a * b}",
            f"√{a * b} = {result}",
        ]
        return Question(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Work out √{a} × √{b}, giving your answer as an integer.",
            solution_steps=tuple(steps),
            final_answer=str(result),
            dedup_key=f"surdmul_clean:{a}:{b}",
        )

    if shape == "multiply_surd":
        for _ in range(200):
            a = rng.randint(2, 15)
            b = rng.randint(2, 15)
            if a == b or math.isqrt(a) ** 2 == a or math.isqrt(b) ** 2 == b:
                continue
            n = a * b
            k, m = _largest_square_factor(n)
            if k > 1 and m > 1:
                break
        else:
            raise ValueError("surds_multiply_divide could not construct multiply_surd case")

        # Independent check: confirm m is genuinely square-free via trial
        # division, and confirm the product numerically via sympy - both
        # different paths than the _largest_square_factor search above.
        for prime in range(2, int(m**0.5) + 1):
            if m % (prime * prime) == 0:
                raise ValueError("surds_multiply_divide verification failed: m is not square-free")
        original = sp.N(sp.sqrt(a) * sp.sqrt(b), 30)
        claimed = sp.N(k * sp.sqrt(m), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("surds_multiply_divide verification failed")

        steps = [
            f"√{a} × √{b} = √({a} × {b}) = √{n}",
            f"Find the largest square factor of {n}: {k}^2 × {m} = {n}",
            f"√{n} = √({k}^2 × {m}) = {k}√{m}",
        ]
        return Question(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Simplify √{a} × √{b}, giving your answer in the form a√b.",
            solution_steps=tuple(steps),
            final_answer=f"{k}√{m}",
            dedup_key=f"surdmul_surd:{a}:{b}",
        )

    if shape == "divide_clean":
        b = rng.randint(2, 10)
        s = rng.randint(2, 6)
        a = b * s * s
        result = s

        original = sp.N(sp.sqrt(a) / sp.sqrt(b), 30)
        claimed = sp.N(sp.Integer(result), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("surds_multiply_divide verification failed")

        steps = [
            f"√{a} ÷ √{b} = √({a}/{b}) = √{a // b}",
            f"√{a // b} = {result}",
        ]
        return Question(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Work out √{a} ÷ √{b}, giving your answer as an integer.",
            solution_steps=tuple(steps),
            final_answer=str(result),
            dedup_key=f"surddiv_clean:{a}:{b}",
        )

    b = rng.randint(2, 10)
    k = rng.randint(2, 6)
    m = rng.choice(_SQUARE_FREE_FACTORS)
    a = b * k * k * m
    quotient = a // b

    # Independent check: confirm m is genuinely square-free, confirm the
    # a/b reconstruction, and confirm the quotient numerically via sympy -
    # all different paths than the a = b*k^2*m construction above.
    for prime in range(2, int(m**0.5) + 1):
        if m % (prime * prime) == 0:
            raise ValueError("surds_multiply_divide verification failed: m is not square-free")
    if a % b != 0 or quotient != k * k * m:
        raise ValueError("surds_multiply_divide verification failed: division mismatch")
    original = sp.N(sp.sqrt(a) / sp.sqrt(b), 30)
    claimed = sp.N(k * sp.sqrt(m), 30)
    if abs(original - claimed) > sp.Float("1e-20"):
        raise ValueError("surds_multiply_divide verification failed")

    steps = [
        f"√{a} ÷ √{b} = √({a}/{b}) = √{quotient}",
        f"Find the largest square factor of {quotient}: {k}^2 × {m} = {quotient}",
        f"√{quotient} = √({k}^2 × {m}) = {k}√{m}",
    ]
    return Question(
        topic_id="surds_multiply_divide",
        tier=Tier.HIGHER,
        prompt=f"Simplify √{a} ÷ √{b}, giving your answer in the form a√b.",
        solution_steps=tuple(steps),
        final_answer=f"{k}√{m}",
        dedup_key=f"surddiv_surd:{a}:{b}",
    )


def generate_modelled_example_surds_multiply_divide(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["multiply_clean", "multiply_surd", "divide_clean", "divide_surd"])

    if shape == "multiply_clean":
        d = rng.choice(_SQUARE_FREE_FACTORS)
        s = rng.randint(2, 6)
        a, b = d * s * s, d
        result = d * s

        original = sp.N(sp.sqrt(a) * sp.sqrt(b), 30)
        claimed = sp.N(sp.Integer(result), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("modelled example surds_multiply_divide verification failed")

        teaching_steps = [
            f"When multiplying two surds, √{a} × √{b}, they can be combined under a single root: "
            f"√a × √b = √(a × b).",
            f"So √{a} × √{b} = √({a} × {b}) = √{a * b}.",
            f"{a * b} happens to be a perfect square, so this root simplifies all the way down to a "
            f"whole number: √{a * b} = {result}.",
        ]
        worked_calculation = [f"√{a} × √{b}", f"= √{a * b}", f"= {result}"]
        return ModelledExample(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Work out √{a} × √{b}, giving your answer as an integer.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(result),
        )

    if shape == "multiply_surd":
        for _ in range(200):
            a = rng.randint(2, 15)
            b = rng.randint(2, 15)
            if a == b or math.isqrt(a) ** 2 == a or math.isqrt(b) ** 2 == b:
                continue
            n = a * b
            k, m = _largest_square_factor(n)
            if k > 1 and m > 1:
                break
        else:
            raise ValueError("modelled example surds_multiply_divide could not construct multiply_surd case")

        for prime in range(2, int(m**0.5) + 1):
            if m % (prime * prime) == 0:
                raise ValueError("modelled example surds_multiply_divide verification failed: m is not square-free")
        original = sp.N(sp.sqrt(a) * sp.sqrt(b), 30)
        claimed = sp.N(k * sp.sqrt(m), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("modelled example surds_multiply_divide verification failed")

        teaching_steps = [
            f"Multiplying two surds combines them under one root: √{a} × √{b} = √({a} × {b}) = √{n}.",
            f"{n} isn't a perfect square, but it may still hide a square factor that can be pulled out. "
            f"The largest square factor of {n} is {k}^2 = {k * k}, since {n} = {k}^2 × {m}.",
            f"Splitting the root apart using √(a×b) = √a × √b: √{n} = √({k * k} × {m}) = √{k * k} × √{m}.",
            f"√{k * k} simplifies exactly to {k}, while √{m} can't be simplified further since {m} has no "
            f"square factors left. So √{a} × √{b} = {k}√{m}.",
        ]
        worked_calculation = [f"√{a} × √{b}", f"= √{n}", f"= √({k}^2 × {m})", f"= {k}√{m}"]
        return ModelledExample(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Simplify √{a} × √{b}, giving your answer in the form a√b.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"{k}√{m}",
        )

    if shape == "divide_clean":
        b = rng.randint(2, 10)
        s = rng.randint(2, 6)
        a = b * s * s
        result = s

        original = sp.N(sp.sqrt(a) / sp.sqrt(b), 30)
        claimed = sp.N(sp.Integer(result), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("modelled example surds_multiply_divide verification failed")

        teaching_steps = [
            f"When dividing two surds, √{a} ÷ √{b}, they can be combined under a single root: "
            "√a ÷ √b = √(a/b).",
            f"So √{a} ÷ √{b} = √({a}/{b}) = √{a // b}.",
            f"{a // b} happens to be a perfect square, so this root simplifies all the way down to a "
            f"whole number: √{a // b} = {result}.",
        ]
        worked_calculation = [f"√{a} ÷ √{b}", f"= √{a // b}", f"= {result}"]
        return ModelledExample(
            topic_id="surds_multiply_divide",
            tier=Tier.HIGHER,
            prompt=f"Work out √{a} ÷ √{b}, giving your answer as an integer.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(result),
        )

    b = rng.randint(2, 10)
    k = rng.randint(2, 6)
    m = rng.choice(_SQUARE_FREE_FACTORS)
    a = b * k * k * m
    quotient = a // b

    for prime in range(2, int(m**0.5) + 1):
        if m % (prime * prime) == 0:
            raise ValueError("modelled example surds_multiply_divide verification failed: m is not square-free")
    if a % b != 0 or quotient != k * k * m:
        raise ValueError("modelled example surds_multiply_divide verification failed: division mismatch")
    original = sp.N(sp.sqrt(a) / sp.sqrt(b), 30)
    claimed = sp.N(k * sp.sqrt(m), 30)
    if abs(original - claimed) > sp.Float("1e-20"):
        raise ValueError("modelled example surds_multiply_divide verification failed")

    teaching_steps = [
        f"Dividing two surds combines them under one root: √{a} ÷ √{b} = √({a}/{b}) = √{quotient}.",
        f"{quotient} isn't a perfect square, but it may still hide a square factor that can be pulled "
        f"out. The largest square factor of {quotient} is {k}^2 = {k * k}, since {quotient} = {k}^2 × {m}.",
        f"Splitting the root apart: √{quotient} = √({k * k} × {m}) = √{k * k} × √{m}.",
        f"√{k * k} simplifies exactly to {k}, while √{m} can't be simplified further since {m} has no "
        f"square factors left. So √{a} ÷ √{b} = {k}√{m}.",
    ]
    worked_calculation = [f"√{a} ÷ √{b}", f"= √{quotient}", f"= √({k}^2 × {m})", f"= {k}√{m}"]
    return ModelledExample(
        topic_id="surds_multiply_divide",
        tier=Tier.HIGHER,
        prompt=f"Simplify √{a} ÷ √{b}, giving your answer in the form a√b.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{k}√{m}",
    )


def generate_algebraic_surds(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["foil", "squared"])

    if shape == "foil":
        for _ in range(50):
            p = rng.randint(2, 9)
            q = rng.randint(2, 9)
            c = rng.choice(_SQUARE_FREE_FACTORS)
            s1 = rng.choice([1, -1])
            s2 = rng.choice([1, -1])
            p_val = p * q + s1 * s2 * c
            q_val = s1 * q + s2 * p
            if q_val != 0:
                break
        else:
            raise ValueError("algebraic_surds could not construct a foil case")

        # Independent check: expand the original bracket expression via
        # sympy and evaluate both it and the claimed p + q√c form to high
        # precision - a different path than the FOIL-by-hand arithmetic
        # used to derive p_val/q_val above.
        b1 = p + s1 * sp.sqrt(c)
        b2 = q + s2 * sp.sqrt(c)
        original = sp.N(b1 * b2, 30)
        claimed = sp.N(p_val + q_val * sp.sqrt(c), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("algebraic_surds verification failed")

        bracket1 = f"{p} {'+' if s1 > 0 else '-'} √{c}"
        bracket2 = f"{q} {'+' if s2 > 0 else '-'} √{c}"
        cross1 = f"{'+' if s2 > 0 else '-'}{p}√{c}"
        cross2 = f"{'+' if s1 > 0 else '-'}{q}√{c}"
        square_term = f"{'+' if s1 * s2 > 0 else '-'}{c}"
        answer = _fmt_p_plus_q_root(p_val, q_val, c)
        steps = [
            f"Expand the brackets (FOIL): ({bracket1})({bracket2}) = {p * q} {cross1} {cross2} {square_term}",
            f"√{c} × √{c} = {c}, so the last term is a whole number: {square_term}",
            f"Combine the whole-number terms: {p * q} {square_term} = {p_val}",
            f"Combine the √{c} terms: {cross1} {cross2} = {'+' if q_val > 0 else '-'}{abs(q_val)}√{c}",
            f"({bracket1})({bracket2}) = {answer}",
        ]
        return Question(
            topic_id="algebraic_surds",
            tier=Tier.HIGHER,
            prompt=f"Expand and simplify ({bracket1})({bracket2}), giving your answer in the form p + q√{c}.",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"algsurd_foil:{p}:{q}:{c}:{s1}:{s2}",
        )

    p = rng.randint(2, 9)
    c = rng.choice(_SQUARE_FREE_FACTORS)
    s = rng.choice([1, -1])
    p_val = p * p + c
    q_val = 2 * s * p

    # Independent check: expand the original squared bracket via sympy and
    # evaluate both it and the claimed p + q√c form to high precision - a
    # different path than the (a+b)^2 expansion-by-hand used above.
    bracket = p + s * sp.sqrt(c)
    original = sp.N(bracket**2, 30)
    claimed = sp.N(p_val + q_val * sp.sqrt(c), 30)
    if abs(original - claimed) > sp.Float("1e-20"):
        raise ValueError("algebraic_surds verification failed")

    bracket_str = f"{p} {'+' if s > 0 else '-'} √{c}"
    answer = _fmt_p_plus_q_root(p_val, q_val, c)
    cross_term = f"{'+' if s > 0 else '-'}{2 * p}√{c}"
    steps = [
        f"({bracket_str})^2 = ({bracket_str})({bracket_str})",
        f"Expand: {p * p} {cross_term} {cross_term} + {c}",
        f"Combine the whole-number terms: {p * p} + {c} = {p_val}",
        f"Combine the √{c} terms: {cross_term} {cross_term} = {'+' if q_val > 0 else '-'}{abs(q_val)}√{c}",
        f"({bracket_str})^2 = {answer}",
    ]
    return Question(
        topic_id="algebraic_surds",
        tier=Tier.HIGHER,
        prompt=f"Expand and simplify ({bracket_str})^2, giving your answer in the form p + q√{c}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"algsurd_sq:{p}:{c}:{s}",
    )


def generate_modelled_example_algebraic_surds(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["foil", "squared"])

    if shape == "foil":
        for _ in range(50):
            p = rng.randint(2, 9)
            q = rng.randint(2, 9)
            c = rng.choice(_SQUARE_FREE_FACTORS)
            s1 = rng.choice([1, -1])
            s2 = rng.choice([1, -1])
            p_val = p * q + s1 * s2 * c
            q_val = s1 * q + s2 * p
            if q_val != 0:
                break
        else:
            raise ValueError("modelled example algebraic_surds could not construct a foil case")

        b1 = p + s1 * sp.sqrt(c)
        b2 = q + s2 * sp.sqrt(c)
        original = sp.N(b1 * b2, 30)
        claimed = sp.N(p_val + q_val * sp.sqrt(c), 30)
        if abs(original - claimed) > sp.Float("1e-20"):
            raise ValueError("modelled example algebraic_surds verification failed")

        bracket1 = f"{p} {'+' if s1 > 0 else '-'} √{c}"
        bracket2 = f"{q} {'+' if s2 > 0 else '-'} √{c}"
        answer = _fmt_p_plus_q_root(p_val, q_val, c)
        teaching_steps = [
            f"Even with surds inside, two brackets multiply together the same way as any other pair of "
            f"brackets - expand every term against every other term (FOIL: First, Outer, Inner, Last).",
            f"({bracket1})({bracket2}) gives four terms: {p}×{q}, {p}×({'+' if s2 > 0 else '-'}√{c}), "
            f"({'+' if s1 > 0 else '-'}√{c})×{q}, and ({'+' if s1 > 0 else '-'}√{c})×({'+' if s2 > 0 else '-'}√{c}).",
            f"The key simplification is the Last term: √{c} × √{c} = {c} exactly, since multiplying a "
            "square root by itself always undoes the root - this turns a surd-times-surd term into a "
            "whole number.",
            f"Collecting the whole-number terms ({p}×{q} and the √{c}×√{c} term) gives {p_val}, and "
            f"collecting the two remaining surd terms (which share the same √{c}) gives the coefficient "
            f"{q_val}. So the answer is {answer}.",
        ]
        worked_calculation = [
            f"({bracket1})({bracket2})",
            f"= {p * q} + (surd terms) + {'+' if s1 * s2 > 0 else '-'}{c}",
            f"= {answer}",
        ]
        return ModelledExample(
            topic_id="algebraic_surds",
            tier=Tier.HIGHER,
            prompt=f"Expand and simplify ({bracket1})({bracket2}), giving your answer in the form p + q√{c}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
        )

    p = rng.randint(2, 9)
    c = rng.choice(_SQUARE_FREE_FACTORS)
    s = rng.choice([1, -1])
    p_val = p * p + c
    q_val = 2 * s * p

    bracket = p + s * sp.sqrt(c)
    original = sp.N(bracket**2, 30)
    claimed = sp.N(p_val + q_val * sp.sqrt(c), 30)
    if abs(original - claimed) > sp.Float("1e-20"):
        raise ValueError("modelled example algebraic_surds verification failed")

    bracket_str = f"{p} {'+' if s > 0 else '-'} √{c}"
    answer = _fmt_p_plus_q_root(p_val, q_val, c)
    teaching_steps = [
        f"Squaring a bracket means multiplying it by itself: ({bracket_str})^2 = ({bracket_str})({bracket_str}). "
        "It is a very common mistake to just square each term separately (getting p^2 + c) and forget "
        "the middle 'cross' terms entirely - don't do that here.",
        f"Expanding fully gives four terms: {p}×{p}, {p}×({'+' if s > 0 else '-'}√{c}) TWICE (once from "
        f"each direction), and ({'+' if s > 0 else '-'}√{c})×({'+' if s > 0 else '-'}√{c}).",
        f"The last term simplifies to a whole number since √{c} × √{c} = {c} exactly, and the two "
        f"identical cross terms double up rather than cancel.",
        f"Collecting the whole-number parts ({p}^2 = {p * p}, plus {c} from the surd-squared term) gives "
        f"{p_val}, and doubling the single cross term ({'+' if s > 0 else '-'}{p}√{c} counted twice) "
        f"gives the coefficient {q_val}. So ({bracket_str})^2 = {answer}.",
    ]
    worked_calculation = [
        f"({bracket_str})^2",
        f"= {p * p} {'+' if s > 0 else '-'}{2 * p}√{c} {'+' if s > 0 else '-'}{2 * p}√{c} + {c}",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="algebraic_surds",
        tier=Tier.HIGHER,
        prompt=f"Expand and simplify ({bracket_str})^2, giving your answer in the form p + q√{c}.",
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

TOPIC_NEGATIVE_INDICES = TopicDefinition(
    id="negative_indices",
    display_name="Negative Indices",
    description="Evaluate and simplify negative integer indices of a numeric base.",
    generate=generate_negative_indices,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_negative_indices,
)

TOPIC_SIMPLIFYING_INDICES_CHALLENGING = TopicDefinition(
    id="simplifying_indices_challenging",
    display_name="Simplifying Indices (Challenging)",
    description="Combine two or more index laws in a single numeric simplification.",
    generate=generate_simplifying_indices_challenging,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_simplifying_indices_challenging,
)

TOPIC_INDICES_COMMON_BASE_EQUATIONS = TopicDefinition(
    id="indices_common_base_equations",
    display_name="Solving Index Equations",
    description="Solve equations by rewriting both sides with a common base.",
    generate=generate_indices_common_base_equations,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_indices_common_base_equations,
)

TOPIC_SURDS_MULTIPLY_DIVIDE = TopicDefinition(
    id="surds_multiply_divide",
    display_name="Multiplying and Dividing Surds",
    description="Multiply or divide two surds, simplifying the result.",
    generate=generate_surds_multiply_divide,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_surds_multiply_divide,
)

TOPIC_ALGEBRAIC_SURDS = TopicDefinition(
    id="algebraic_surds",
    display_name="Surds in Algebraic Expressions",
    description="Expand and simplify bracket expressions involving surds into the form p + q√r.",
    generate=generate_algebraic_surds,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_surds,
)
