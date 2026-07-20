import math
import random
from collections import Counter

import sympy as sp

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Factors, Multiples & Primes"


def _prime_factorise(n: int) -> list[int]:
    factors = []
    d = 2
    m = n
    while d * d <= m:
        while m % d == 0:
            factors.append(d)
            m //= d
        d += 1
    if m > 1:
        factors.append(m)
    return factors


def _is_prime_trial_division(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def generate_prime_numbers(tier: Tier, rng: random.Random) -> Question:
    lo, hi = 2, rng.choice([50, 100])
    numbers = rng.sample(range(lo, hi + 1), 6)

    primes_found = [n for n in numbers if _is_prime_trial_division(n)]

    # Independent check via sympy.isprime - a different primality-testing
    # implementation than the manual trial division above.
    sympy_primes = [n for n in numbers if sp.isprime(n)]
    if sympy_primes != primes_found:
        raise ValueError("prime_numbers verification failed")

    answer = ", ".join(str(n) for n in sorted(primes_found)) if primes_found else "None"
    steps = [
        f"Check each number for factors other than 1 and itself: {', '.join(str(n) for n in numbers)}",
        f"Prime numbers: {answer}",
    ]
    return Question(
        topic_id="prime_numbers",
        tier=Tier.FOUNDATION,
        prompt=f"From this list, write down all the prime numbers: {', '.join(str(n) for n in numbers)}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"primes:{sorted(numbers)}",
    )


def generate_multiples(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["list_multiples", "is_multiple"])

    if shape == "list_multiples":
        n = rng.randint(3, 12)
        count = 5
        multiples_list = [n * k for k in range(1, count + 1)]

        # Independent check: every value must be exactly divisible by n (a
        # different framing than the multiplication used to build the list).
        if any(m % n != 0 for m in multiples_list):
            raise ValueError("multiples verification failed")

        answer = ", ".join(str(m) for m in multiples_list)
        steps = [f"Multiply {n} by 1, 2, 3, 4, 5: {answer}"]
        return Question(
            topic_id="multiples",
            tier=Tier.FOUNDATION,
            prompt=f"Write down the first {count} multiples of {n}.",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"mult_list:{n}",
        )

    n = rng.randint(3, 15)
    k = rng.randint(2, 10)
    is_multiple_case = rng.choice([True, False])
    candidate = n * k if is_multiple_case else n * k + rng.randint(1, n - 1)

    # Independent check via divmod (a different code path than the modulo
    # test used to decide is_multiple_case above).
    quotient, remainder = divmod(candidate, n)
    is_multiple = remainder == 0
    if is_multiple != is_multiple_case:
        raise ValueError("multiples verification failed: is_multiple mismatch")

    answer = "Yes" if is_multiple else "No"
    steps = [
        f"{candidate} ÷ {n} = {quotient} remainder {remainder}",
        f"{answer}, {candidate} {'is' if is_multiple else 'is not'} a multiple of {n}.",
    ]
    return Question(
        topic_id="multiples",
        tier=Tier.FOUNDATION,
        prompt=f"Is {candidate} a multiple of {n}?",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"is_mult:{candidate}:{n}",
    )


def generate_factors(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["list_factors", "is_factor"])

    if shape == "list_factors":
        n = rng.randint(12, 60)
        factors_brute = [i for i in range(1, n + 1) if n % i == 0]

        # Independent check: collect factors via (i, n // i) pairs up to sqrt(n)
        # - a different traversal than the full 1..n scan above.
        pair_factors = set()
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                pair_factors.add(i)
                pair_factors.add(n // i)
        if pair_factors != set(factors_brute):
            raise ValueError("factors verification failed")

        answer = ", ".join(str(f) for f in factors_brute)
        steps = [f"Check every whole number from 1 to {n} to see if it divides exactly: {answer}"]
        return Question(
            topic_id="factors",
            tier=Tier.FOUNDATION,
            prompt=f"Write down all the factors of {n}.",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"factors_list:{n}",
        )

    n = rng.randint(12, 100)
    factors_of_n = [i for i in range(1, n + 1) if n % i == 0]
    is_factor_case = rng.choice([True, False])
    if is_factor_case:
        candidate = rng.choice(factors_of_n)
    else:
        non_factors = [i for i in range(2, n) if n % i != 0]
        candidate = rng.choice(non_factors)

    quotient, remainder = divmod(n, candidate)
    is_factor = remainder == 0
    if is_factor != is_factor_case:
        raise ValueError("factors verification failed: is_factor mismatch")

    answer = "Yes" if is_factor else "No"
    steps = [
        f"{n} ÷ {candidate} = {quotient} remainder {remainder}",
        f"{answer}, {candidate} {'is' if is_factor else 'is not'} a factor of {n}.",
    ]
    return Question(
        topic_id="factors",
        tier=Tier.FOUNDATION,
        prompt=f"Is {candidate} a factor of {n}?",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"is_factor:{n}:{candidate}",
    )


def generate_prime_factors_foundation(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        n = rng.randint(12, 200)
        factors = _prime_factorise(n)
        if len(factors) >= 3:
            break
    else:
        raise ValueError("prime_factors_foundation could not find a suitable number")

    # Independent check via sympy.factorint - a different factorisation
    # implementation than the manual trial-division loop above.
    sympy_counts = {int(p): int(e) for p, e in sp.factorint(n).items()}
    reconstructed = 1
    for p, e in sympy_counts.items():
        reconstructed *= p**e
    if reconstructed != n or dict(Counter(factors)) != sympy_counts:
        raise ValueError("prime_factors_foundation verification failed")

    product_str = " × ".join(str(f) for f in factors)
    steps = [
        f"Divide {n} repeatedly by the smallest prime that fits: {product_str}",
        f"{n} = {product_str}",
    ]
    return Question(
        topic_id="prime_factors_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Write {n} as a product of its prime factors.",
        solution_steps=tuple(steps),
        final_answer=product_str,
        dedup_key=f"primefactor_f:{n}",
    )


def generate_prime_factors_higher(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        n = rng.randint(100, 1000)
        factors = _prime_factorise(n)
        if len(factors) >= 3:
            break
    else:
        raise ValueError("prime_factors_higher could not find a suitable number")

    # Independent check via sympy.factorint - a different factorisation
    # implementation than the manual trial-division loop above.
    sympy_counts = {int(p): int(e) for p, e in sp.factorint(n).items()}
    reconstructed = 1
    for p, e in sympy_counts.items():
        reconstructed *= p**e
    if reconstructed != n or dict(Counter(factors)) != sympy_counts:
        raise ValueError("prime_factors_higher verification failed")

    index_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(sympy_counts.items()))
    steps = [
        f"Divide {n} repeatedly by the smallest prime that fits: {' × '.join(str(f) for f in factors)}",
        f"Write repeated factors using index notation: {n} = {index_str}",
    ]
    return Question(
        topic_id="prime_factors_higher",
        tier=Tier.HIGHER,
        prompt=f"Write {n} as a product of its prime factors, giving your answer in index form.",
        solution_steps=tuple(steps),
        final_answer=index_str,
        dedup_key=f"primefactor_h:{n}",
    )


def generate_lcm_by_listing(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(2, 15)
    b = rng.randint(2, 15)
    while b == a:
        b = rng.randint(2, 15)
    lcm_val = math.lcm(a, b)

    # Independent check: brute-force list multiples of each and find the
    # smallest common one - a different method than math.lcm.
    multiples_a = {a * k for k in range(1, 40)}
    multiples_b = {b * k for k in range(1, 40)}
    brute_lcm = min(multiples_a & multiples_b)
    if brute_lcm != lcm_val:
        raise ValueError("lcm_by_listing verification failed")

    steps = [
        f"Multiples of {a}: {', '.join(str(a * k) for k in range(1, 6))}, ...",
        f"Multiples of {b}: {', '.join(str(b * k) for k in range(1, 6))}, ...",
        f"Lowest common multiple = {lcm_val}",
    ]
    return Question(
        topic_id="lcm_by_listing",
        tier=Tier.FOUNDATION,
        prompt=f"Find the lowest common multiple (LCM) of {a} and {b}.",
        solution_steps=tuple(steps),
        final_answer=str(lcm_val),
        dedup_key=f"lcm_listing:{a}:{b}",
    )


def generate_hcf_by_listing(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(6, 60)
    b = rng.randint(6, 60)
    while b == a:
        b = rng.randint(6, 60)
    hcf_val = math.gcd(a, b)

    # Independent check: brute-force list all factors of both and take the
    # largest common one - a different method than math.gcd.
    factors_a = {i for i in range(1, a + 1) if a % i == 0}
    factors_b = {i for i in range(1, b + 1) if b % i == 0}
    brute_hcf = max(factors_a & factors_b)
    if brute_hcf != hcf_val:
        raise ValueError("hcf_by_listing verification failed")

    steps = [
        f"Factors of {a}: {', '.join(str(f) for f in sorted(factors_a))}",
        f"Factors of {b}: {', '.join(str(f) for f in sorted(factors_b))}",
        f"Highest common factor = {hcf_val}",
    ]
    return Question(
        topic_id="hcf_by_listing",
        tier=Tier.FOUNDATION,
        prompt=f"Find the highest common factor (HCF) of {a} and {b}.",
        solution_steps=tuple(steps),
        final_answer=str(hcf_val),
        dedup_key=f"hcf_listing:{a}:{b}",
    )


def generate_hcf_lcm_by_prime_factors(tier: Tier, rng: random.Random) -> Question:
    which = rng.choice(["hcf", "lcm"])
    for _ in range(50):
        a = rng.randint(20, 200)
        b = rng.randint(20, 200)
        if a != b and len(_prime_factorise(a)) >= 2 and len(_prime_factorise(b)) >= 2:
            break
    else:
        raise ValueError("hcf_lcm_by_prime_factors could not find suitable numbers")

    counts_a, counts_b = Counter(_prime_factorise(a)), Counter(_prime_factorise(b))
    all_primes = sorted(set(counts_a) | set(counts_b))

    result = 1
    for p in all_primes:
        exponent = min(counts_a.get(p, 0), counts_b.get(p, 0)) if which == "hcf" else max(
            counts_a.get(p, 0), counts_b.get(p, 0)
        )
        result *= p**exponent

    # Independent check via math.gcd/math.lcm - a different implementation
    # than the manual prime-exponent method used above.
    independent = math.gcd(a, b) if which == "hcf" else math.lcm(a, b)
    if independent != result:
        raise ValueError("hcf_lcm_by_prime_factors verification failed")

    def fmt_factorisation(counts: Counter) -> str:
        return " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(counts.items()))

    label = "HCF" if which == "hcf" else "LCM"
    op_word = "lowest power" if which == "hcf" else "highest power"
    steps = [
        f"{a} = {fmt_factorisation(counts_a)}",
        f"{b} = {fmt_factorisation(counts_b)}",
        f"{label}: take the {op_word} of each prime" + (" that appears in both numbers" if which == "hcf" else ""),
        f"{label} = {result}",
    ]
    return Question(
        topic_id="hcf_lcm_by_prime_factors",
        tier=Tier.HIGHER,
        prompt=f"Using prime factorisation, find the {label} of {a} and {b}.",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"hcf_lcm_pf:{a}:{b}:{which}",
    )


TOPIC_PRIME_NUMBERS = TopicDefinition(
    id="prime_numbers",
    display_name="Prime Numbers",
    description="Identify the prime numbers in a list.",
    generate=generate_prime_numbers,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_MULTIPLES = TopicDefinition(
    id="multiples",
    display_name="Multiples",
    description="List the multiples of a number, or check whether one number is a multiple of another.",
    generate=generate_multiples,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_FACTORS = TopicDefinition(
    id="factors",
    display_name="Factors",
    description="List the factors of a number, or check whether one number is a factor of another.",
    generate=generate_factors,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_PRIME_FACTORS_FOUNDATION = TopicDefinition(
    id="prime_factors_foundation",
    display_name="Prime Factor Decomposition",
    description="Write a number as a product of its prime factors.",
    generate=generate_prime_factors_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_PRIME_FACTORS_HIGHER = TopicDefinition(
    id="prime_factors_higher",
    display_name="Prime Factor Decomposition (Index Form)",
    description="Write a number as a product of its prime factors, using index notation.",
    generate=generate_prime_factors_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_LCM_BY_LISTING = TopicDefinition(
    id="lcm_by_listing",
    display_name="LCM by Listing",
    description="Find the lowest common multiple of two numbers by listing their multiples.",
    generate=generate_lcm_by_listing,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_HCF_BY_LISTING = TopicDefinition(
    id="hcf_by_listing",
    display_name="HCF by Listing",
    description="Find the highest common factor of two numbers by listing their factors.",
    generate=generate_hcf_by_listing,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_HCF_LCM_BY_PRIME_FACTORS = TopicDefinition(
    id="hcf_lcm_by_prime_factors",
    display_name="HCF & LCM using Prime Factors",
    description="Find the HCF or LCM of two larger numbers using their prime factorisations.",
    generate=generate_hcf_lcm_by_prime_factors,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
