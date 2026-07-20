import math
import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP_EXPAND = "Expanding Brackets"
GROUP_FACTORISE = "Factorising"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_quadratic(a, b, c) -> str:
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x^2")
        elif a == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{a}x^2")
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        if parts:
            parts.append(f"{'+' if b > 0 else '-'} {term}")
        else:
            parts.append(f"-{term}" if b < 0 else term)
    if c != 0 or not parts:
        if parts:
            parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
        else:
            parts.append(str(c))
    return " ".join(parts)


def _fmt_factor(p) -> str:
    if p == 0:
        return "x"
    return f"x + {p}" if p > 0 else f"x - {abs(p)}"


def _fmt_cubic(a, b, c, d) -> str:
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x^3")
        elif a == -1:
            parts.append("-x^3")
        else:
            parts.append(f"{a}x^3")
    if b != 0:
        term = "x^2" if abs(b) == 1 else f"{abs(b)}x^2"
        if parts:
            parts.append(f"{'+' if b > 0 else '-'} {term}")
        else:
            parts.append(f"-{term}" if b < 0 else term)
    if c != 0:
        term = "x" if abs(c) == 1 else f"{abs(c)}x"
        if parts:
            parts.append(f"{'+' if c > 0 else '-'} {term}")
        else:
            parts.append(f"-{term}" if c < 0 else term)
    if d != 0 or not parts:
        if parts:
            parts.append(f"{'+' if d > 0 else '-'} {abs(d)}")
        else:
            parts.append(str(d))
    return " ".join(parts)


def generate_expand_single(tier: Tier, rng: random.Random):
    a = _rand_nonzero(rng, -9, 9)
    b = _rand_nonzero(rng, -9, 9)
    c = rng.randint(-9, 9)
    expanded_coeff, expanded_const = a * b, a * c

    residual = sp.expand(a * (b * X + c) - (expanded_coeff * X + expanded_const))
    if residual != 0:
        raise ValueError("Expansion verification failed: single bracket")

    prompt = f"Expand: {a}({fmt_linear(b, c)})"
    steps = [
        f"Multiply {a} by {fmt_linear(b, 0)}: {fmt_linear(expanded_coeff, 0)}",
        f"Multiply {a} by {c}: {fmt_num(expanded_const)}",
        f"Combine: {fmt_linear(expanded_coeff, expanded_const)}",
    ]
    return Question(
        topic_id="expand_single_bracket",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_linear(expanded_coeff, expanded_const),
        dedup_key=f"expand_single:{a}:{b}:{c}",
    )


def generate_modelled_example_expand_single(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _rand_nonzero(rng, -9, 9)
    b = _rand_nonzero(rng, -9, 9)
    c = rng.randint(-9, 9)
    expanded_coeff, expanded_const = a * b, a * c

    residual = sp.expand(a * (b * X + c) - (expanded_coeff * X + expanded_const))
    if residual != 0:
        raise ValueError("modelled example expand_single verification failed (symbolic)")
    test_x = 2
    lhs_val = a * (b * test_x + c)
    rhs_val = expanded_coeff * test_x + expanded_const
    if lhs_val != rhs_val:
        raise ValueError("modelled example expand_single verification failed (numeric)")

    teaching_steps = [
        f"A number written directly next to a bracket, like {a}({fmt_linear(b, c)}), means "
        f"'multiply everything inside the bracket by {a}' - this is the distributive law, and it's "
        "the key idea behind expanding any bracket.",
        f"Multiply {a} by the x-term inside: {a} × {fmt_linear(b, 0)} = {fmt_linear(expanded_coeff, 0)}.",
        f"Multiply {a} by the constant term inside: {a} × {fmt_num(c)} = {fmt_num(expanded_const)}.",
        f"Combine both results into a single expression: {fmt_linear(expanded_coeff, expanded_const)}. "
        f"Check by substituting x = {test_x}: the original gives {a}×({b * test_x + c}) = {lhs_val}, "
        f"and the expanded form gives {expanded_coeff}×{test_x} + {expanded_const} = {rhs_val} - they "
        "match, confirming the expansion is correct.",
    ]
    worked_calculation = [
        f"{a}({fmt_linear(b, c)})",
        f"{a} × {fmt_linear(b, 0)} = {fmt_linear(expanded_coeff, 0)}",
        f"{a} × {fmt_num(c)} = {fmt_num(expanded_const)}",
        f"{fmt_linear(expanded_coeff, expanded_const)}",
    ]
    return ModelledExample(
        topic_id="expand_single_bracket",
        tier=Tier.FOUNDATION,
        prompt=f"Expand: {a}({fmt_linear(b, c)})",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_linear(expanded_coeff, expanded_const),
    )


def generate_factorise_common(tier: Tier, rng: random.Random):
    k = rng.randint(2, 9)
    a = _rand_nonzero(rng, -9, 9)
    b = _rand_nonzero(rng, -9, 9)
    while math.gcd(abs(a), abs(b)) != 1:
        a = _rand_nonzero(rng, -9, 9)
        b = _rand_nonzero(rng, -9, 9)

    full_coeff, full_const = k * a, k * b
    hcf = math.gcd(abs(full_coeff), abs(full_const))
    if hcf != k:
        raise ValueError("Factorise-common verification failed: HCF mismatch")

    prompt = f"Factorise: {fmt_linear(full_coeff, full_const)}"
    steps = [
        f"Find the highest common factor of {full_coeff} and {full_const}: {k}",
        f"Factorise: {k}({fmt_linear(a, b)})",
    ]
    return Question(
        topic_id="factorise_common_factor",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{k}({fmt_linear(a, b)})",
        dedup_key=f"factorise_common:{k}:{a}:{b}",
    )


def generate_modelled_example_factorise_common(tier: Tier, rng: random.Random) -> ModelledExample:
    k = rng.randint(2, 9)
    a = _rand_nonzero(rng, -9, 9)
    b = _rand_nonzero(rng, -9, 9)
    while math.gcd(abs(a), abs(b)) != 1:
        a = _rand_nonzero(rng, -9, 9)
        b = _rand_nonzero(rng, -9, 9)

    full_coeff, full_const = k * a, k * b
    hcf = math.gcd(abs(full_coeff), abs(full_const))
    if hcf != k:
        raise ValueError("modelled example factorise_common verification failed (HCF mismatch)")
    residual = sp.expand(k * (a * X + b) - (full_coeff * X + full_const))
    if residual != 0:
        raise ValueError("modelled example factorise_common verification failed (expansion check)")

    teaching_steps = [
        f"Factorising is the reverse of expanding: instead of multiplying a bracket out, we're pulling "
        f"a common number back out of {fmt_linear(full_coeff, full_const)}.",
        f"Look for the highest common factor (HCF) of {full_coeff} and {full_const} - the largest "
        f"number that divides into both exactly. Here that's {k}.",
        f"Divide each term by {k} to see what's left inside the bracket: {full_coeff} ÷ {k} = {a}, "
        f"and {full_const} ÷ {k} = {b}.",
        f"Write the answer as {k} multiplied by what's left: {k}({fmt_linear(a, b)}). Check by "
        f"expanding it back out: {k} × {fmt_linear(a, 0)} = {fmt_linear(full_coeff, 0)}, and "
        f"{k} × {fmt_num(b)} = {fmt_num(full_const)}, which reconstructs the original expression.",
    ]
    worked_calculation = [
        f"{fmt_linear(full_coeff, full_const)}",
        f"HCF({full_coeff}, {full_const}) = {k}",
        f"{k}({fmt_linear(a, b)})",
    ]
    return ModelledExample(
        topic_id="factorise_common_factor",
        tier=Tier.FOUNDATION,
        prompt=f"Factorise: {fmt_linear(full_coeff, full_const)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{k}({fmt_linear(a, b)})",
    )


def generate_expand_double(tier: Tier, rng: random.Random):
    a = _rand_nonzero(rng, -6, 6)
    b = _rand_nonzero(rng, -6, 6)
    c = _rand_nonzero(rng, -6, 6)
    d = _rand_nonzero(rng, -6, 6)

    expanded = sp.expand((a * X + b) * (c * X + d))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("Expansion verification failed: double bracket")

    prompt = f"Expand: ({fmt_linear(a, b)})({fmt_linear(c, d)})"
    steps = [
        f"First: {a}x × {c}x = {a * c}x^2",
        f"Outer: {a}x × {d} = {a * d}x",
        f"Inner: {b} × {c}x = {b * c}x",
        f"Last: {b} × {d} = {b * d}",
        f"Combine like terms: {_fmt_quadratic(qa, qb, qc)}",
    ]
    return Question(
        topic_id="expand_double_brackets",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=_fmt_quadratic(qa, qb, qc),
        dedup_key=f"expand_double:{a}:{b}:{c}:{d}",
    )


def generate_modelled_example_expand_double(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _rand_nonzero(rng, -6, 6)
    b = _rand_nonzero(rng, -6, 6)
    c = _rand_nonzero(rng, -6, 6)
    d = _rand_nonzero(rng, -6, 6)

    expanded = sp.expand((a * X + b) * (c * X + d))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("modelled example expand_double verification failed (symbolic)")
    for test_x in (2, -3):
        lhs = (a * test_x + b) * (c * test_x + d)
        rhs = qa * test_x**2 + qb * test_x + qc
        if lhs != rhs:
            raise ValueError("modelled example expand_double verification failed (numeric)")

    teaching_steps = [
        "When two brackets are multiplied together, every term in the first bracket must be multiplied "
        "by every term in the second bracket - a common way to remember this is FOIL: First, Outer, "
        "Inner, Last.",
        f"First: multiply the two x-terms together: {a}x × {c}x = {a * c}x^2.",
        f"Outer and Inner: multiply {a}x × {d} = {a * d}x, and {b} × {c}x = {b * c}x. Both of these are "
        f"x-terms, so add them together: {a * d}x + {b * c}x = {a * d + b * c}x.",
        f"Last: multiply the two constant terms: {b} × {d} = {b * d}.",
        f"Combine all four results into one expression: {_fmt_quadratic(qa, qb, qc)}. Check by "
        f"substituting x = 2 into both the original pair of brackets and this quadratic - both should "
        "give the same number.",
    ]
    worked_calculation = [
        f"({fmt_linear(a, b)})({fmt_linear(c, d)})",
        f"{a * c}x^2 + {a * d}x + {b * c}x + {b * d}",
        f"{_fmt_quadratic(qa, qb, qc)}",
    ]
    return ModelledExample(
        topic_id="expand_double_brackets",
        tier=Tier.HIGHER,
        prompt=f"Expand: ({fmt_linear(a, b)})({fmt_linear(c, d)})",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_quadratic(qa, qb, qc),
    )


def generate_expand_double_foundation(tier: Tier, rng: random.Random):
    # Same shape as generate_expand_double but with all-positive coefficients, so
    # a Foundation student only ever expands (x + p)(x + q) - no negative signs to
    # track - matching how double-bracket expansion is introduced on the real specs.
    a = rng.randint(1, 4)
    b = rng.randint(1, 9)
    c = rng.randint(1, 4)
    d = rng.randint(1, 9)

    expanded = sp.expand((a * X + b) * (c * X + d))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("Expansion verification failed: double bracket (foundation)")

    prompt = f"Expand: ({fmt_linear(a, b)})({fmt_linear(c, d)})"
    steps = [
        f"First: {a}x × {c}x = {a * c}x^2",
        f"Outer: {a}x × {d} = {a * d}x",
        f"Inner: {b} × {c}x = {b * c}x",
        f"Last: {b} × {d} = {b * d}",
        f"Combine like terms: {_fmt_quadratic(qa, qb, qc)}",
    ]
    return Question(
        topic_id="expand_double_brackets_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=_fmt_quadratic(qa, qb, qc),
        dedup_key=f"expand_double_f:{a}:{b}:{c}:{d}",
    )


def generate_modelled_example_expand_double_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(1, 4)
    b = rng.randint(1, 9)
    c = rng.randint(1, 4)
    d = rng.randint(1, 9)

    expanded = sp.expand((a * X + b) * (c * X + d))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("modelled example expand_double_foundation verification failed (symbolic)")
    for test_x in (2, 5):
        lhs = (a * test_x + b) * (c * test_x + d)
        rhs = qa * test_x**2 + qb * test_x + qc
        if lhs != rhs:
            raise ValueError("modelled example expand_double_foundation verification failed (numeric)")

    teaching_steps = [
        "When two brackets are multiplied together, every term in the first bracket must be multiplied "
        "by every term in the second bracket - a common way to remember this is FOIL: First, Outer, "
        "Inner, Last.",
        f"First: multiply the two x-terms together: {a}x × {c}x = {a * c}x^2.",
        f"Outer and Inner: multiply {a}x × {d} = {a * d}x, and {b} × {c}x = {b * c}x. Both of these are "
        f"x-terms, so add them together: {a * d}x + {b * c}x = {a * d + b * c}x.",
        f"Last: multiply the two constant terms: {b} × {d} = {b * d}.",
        f"Combine all four results into one expression: {_fmt_quadratic(qa, qb, qc)}. Check by "
        f"substituting x = 2 into both the original pair of brackets and this quadratic - both should "
        "give the same number.",
    ]
    worked_calculation = [
        f"({fmt_linear(a, b)})({fmt_linear(c, d)})",
        f"{a * c}x^2 + {a * d}x + {b * c}x + {b * d}",
        f"{_fmt_quadratic(qa, qb, qc)}",
    ]
    return ModelledExample(
        topic_id="expand_double_brackets_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Expand: ({fmt_linear(a, b)})({fmt_linear(c, d)})",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_quadratic(qa, qb, qc),
    )


def generate_expand_triple(tier: Tier, rng: random.Random):
    a, b = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)
    c, d = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)
    e, f = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)

    expanded = sp.expand((a * X + b) * (c * X + d) * (e * X + f))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (4 - len(coeffs)) + coeffs
    qa, qb, qc, qd = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) * (e * X + f) - (qa * X**3 + qb * X**2 + qc * X + qd))
    if residual != 0:
        raise ValueError("Expansion verification failed: triple bracket")

    # Independent verification: evaluate both the original product and the claimed
    # cubic at a couple of concrete x values and check they agree numerically - a
    # different method than the symbolic Poly coefficient extraction above.
    for test_x in (2, -3):
        lhs = (a * test_x + b) * (c * test_x + d) * (e * test_x + f)
        rhs = qa * test_x**3 + qb * test_x**2 + qc * test_x + qd
        if lhs != rhs:
            raise ValueError("Expansion verification failed: triple bracket numeric cross-check")

    mid_a, mid_b, mid_c = a * c, a * d + b * c, b * d
    prompt = f"Expand and simplify: ({fmt_linear(a, b)})({fmt_linear(c, d)})({fmt_linear(e, f)})"
    steps = [
        f"First expand two of the brackets: ({fmt_linear(a, b)})({fmt_linear(c, d)}) = {_fmt_quadratic(mid_a, mid_b, mid_c)}",
        f"Multiply the result by ({fmt_linear(e, f)}) and collect like terms",
        f"= {_fmt_cubic(qa, qb, qc, qd)}",
    ]
    return Question(
        topic_id="expand_triple_brackets",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=_fmt_cubic(qa, qb, qc, qd),
        dedup_key=f"expand_triple:{a}:{b}:{c}:{d}:{e}:{f}",
    )


def generate_modelled_example_expand_triple(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)
    c, d = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)
    e, f = _rand_nonzero(rng, -4, 4), _rand_nonzero(rng, -4, 4)

    expanded = sp.expand((a * X + b) * (c * X + d) * (e * X + f))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (4 - len(coeffs)) + coeffs
    qa, qb, qc, qd = (int(v) for v in coeffs)

    residual = sp.expand((a * X + b) * (c * X + d) * (e * X + f) - (qa * X**3 + qb * X**2 + qc * X + qd))
    if residual != 0:
        raise ValueError("modelled example expand_triple verification failed (symbolic)")
    for test_x in (2, -3):
        lhs = (a * test_x + b) * (c * test_x + d) * (e * test_x + f)
        rhs = qa * test_x**3 + qb * test_x**2 + qc * test_x + qd
        if lhs != rhs:
            raise ValueError("modelled example expand_triple verification failed (numeric)")

    mid_a, mid_b, mid_c = a * c, a * d + b * c, b * d
    teaching_steps = [
        "With three brackets multiplied together, it's too easy to make a mistake trying to do it all "
        "in one go - so the reliable method is to expand two of the brackets first, then multiply that "
        "result by the third.",
        f"Expand the first two brackets together, using the usual FOIL method: "
        f"({fmt_linear(a, b)})({fmt_linear(c, d)}) = {_fmt_quadratic(mid_a, mid_b, mid_c)}.",
        f"Now multiply that quadratic by the third bracket, ({fmt_linear(e, f)}) - multiply every term "
        "of the quadratic by every term of the bracket, then collect all the like terms together.",
        f"This gives the final cubic expression: {_fmt_cubic(qa, qb, qc, qd)}. Check by substituting "
        "x = 2 into the original three brackets and into this cubic - both should give the same value.",
    ]
    worked_calculation = [
        f"({fmt_linear(a, b)})({fmt_linear(c, d)})({fmt_linear(e, f)})",
        f"({fmt_linear(a, b)})({fmt_linear(c, d)}) = {_fmt_quadratic(mid_a, mid_b, mid_c)}",
        f"{_fmt_quadratic(mid_a, mid_b, mid_c)} × ({fmt_linear(e, f)})",
        f"{_fmt_cubic(qa, qb, qc, qd)}",
    ]
    return ModelledExample(
        topic_id="expand_triple_brackets",
        tier=Tier.HIGHER,
        prompt=f"Expand and simplify: ({fmt_linear(a, b)})({fmt_linear(c, d)})({fmt_linear(e, f)})",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_cubic(qa, qb, qc, qd),
    )


def _find_factor_pair(b: int, c: int) -> tuple[int, int]:
    """Find integers p, q with p + q == b and p * q == c, by searching the
    actual factor pairs of c (mirrors the standard manual method)."""
    if c == 0:
        return (0, b) if b != 0 else (0, 0)
    for d in range(1, abs(c) + 1):
        if c % d != 0:
            continue
        for p in (d, -d):
            q = c // p
            if p + q == b:
                return p, q
    raise ValueError(f"No integer factor pair found for b={b}, c={c}")


def generate_factorise_quadratic(tier: Tier, rng: random.Random):
    r1 = _rand_nonzero(rng, -9, 9)
    r2 = _rand_nonzero(rng, -9, 9)
    b = -(r1 + r2)
    c = r1 * r2

    p, q = _find_factor_pair(b, c)

    residual = sp.expand((X + p) * (X + q) - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("Factorise-quadratic verification failed")

    prompt = f"Factorise: {_fmt_quadratic(1, b, c)}"
    steps = [
        f"Find two numbers that multiply to {c} and add to {b}: {p} and {q}",
        f"Write as two brackets: ({_fmt_factor(p)})({_fmt_factor(q)})",
    ]
    return Question(
        topic_id="factorise_quadratics",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"({_fmt_factor(p)})({_fmt_factor(q)})",
        dedup_key=f"factorise_quadratic:{r1}:{r2}",
    )


def generate_modelled_example_factorise_quadratic(tier: Tier, rng: random.Random) -> ModelledExample:
    r1 = _rand_nonzero(rng, -9, 9)
    r2 = _rand_nonzero(rng, -9, 9)
    b = -(r1 + r2)
    c = r1 * r2

    p, q = _find_factor_pair(b, c)

    residual = sp.expand((X + p) * (X + q) - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("modelled example factorise_quadratic verification failed (symbolic)")
    for test_x in (3, -4):
        lhs = (test_x + p) * (test_x + q)
        rhs = test_x**2 + b * test_x + c
        if lhs != rhs:
            raise ValueError("modelled example factorise_quadratic verification failed (numeric)")

    teaching_steps = [
        f"To factorise {_fmt_quadratic(1, b, c)} into two brackets (x + p)(x + q), we need to find two "
        f"numbers p and q that multiply together to give the constant term ({c}) and add together to "
        f"give the coefficient of x ({b}).",
        f"List the pairs of numbers that multiply to give {c}, remembering that if {c} is negative one "
        "number must be positive and the other negative, and if it's positive they're either both "
        f"positive or both negative (matching the sign of {b}).",
        f"Check which pair adds to {b}: {p} and {q} multiply to give {p * q} and add to give {p + q}, "
        "so these are the numbers we need.",
        f"Write the answer as two brackets: ({_fmt_factor(p)})({_fmt_factor(q)}). Check by expanding "
        f"these brackets back out - they should reconstruct {_fmt_quadratic(1, b, c)} exactly.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(1, b, c)}",
        f"p × q = {c}, p + q = {b} -> p = {p}, q = {q}",
        f"({_fmt_factor(p)})({_fmt_factor(q)})",
    ]
    return ModelledExample(
        topic_id="factorise_quadratics",
        tier=Tier.HIGHER,
        prompt=f"Factorise: {_fmt_quadratic(1, b, c)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"({_fmt_factor(p)})({_fmt_factor(q)})",
    )


def generate_factorise_quadratic_foundation(tier: Tier, rng: random.Random):
    # Same shape as generate_factorise_quadratic but restricted to two positive
    # factors, so b and c in x^2 + bx + c are always positive - the simplest,
    # sign-free factorising pattern, matching Foundation-tier content on the specs.
    p = rng.randint(1, 9)
    q = rng.randint(1, 9)
    b = p + q
    c = p * q

    residual = sp.expand((X + p) * (X + q) - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("Factorise-quadratic verification failed (foundation)")

    prompt = f"Factorise: {_fmt_quadratic(1, b, c)}"
    steps = [
        f"Find two numbers that multiply to {c} and add to {b}: {p} and {q}",
        f"Write as two brackets: ({_fmt_factor(p)})({_fmt_factor(q)})",
    ]
    return Question(
        topic_id="factorise_quadratics_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"({_fmt_factor(p)})({_fmt_factor(q)})",
        dedup_key=f"factorise_quadratic_f:{p}:{q}",
    )


def generate_modelled_example_factorise_quadratic_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    p = rng.randint(1, 9)
    q = rng.randint(1, 9)
    b = p + q
    c = p * q

    residual = sp.expand((X + p) * (X + q) - (X**2 + b * X + c))
    if residual != 0:
        raise ValueError("modelled example factorise_quadratic_foundation verification failed (symbolic)")
    for test_x in (3, 6):
        lhs = (test_x + p) * (test_x + q)
        rhs = test_x**2 + b * test_x + c
        if lhs != rhs:
            raise ValueError("modelled example factorise_quadratic_foundation verification failed (numeric)")

    teaching_steps = [
        f"To factorise {_fmt_quadratic(1, b, c)} into two brackets (x + p)(x + q), we need to find two "
        f"numbers p and q that multiply together to give the constant term ({c}) and add together to "
        f"give the coefficient of x ({b}).",
        f"Since both {c} and {b} are positive here, both p and q must be positive numbers - list the "
        f"pairs of positive numbers that multiply to give {c}.",
        f"Check which pair adds to {b}: {p} and {q} multiply to give {p * q} and add to give {p + q}, "
        "so these are the numbers we need.",
        f"Write the answer as two brackets: ({_fmt_factor(p)})({_fmt_factor(q)}). Check by expanding "
        f"these brackets back out - they should reconstruct {_fmt_quadratic(1, b, c)} exactly.",
    ]
    worked_calculation = [
        f"{_fmt_quadratic(1, b, c)}",
        f"p × q = {c}, p + q = {b} -> p = {p}, q = {q}",
        f"({_fmt_factor(p)})({_fmt_factor(q)})",
    ]
    return ModelledExample(
        topic_id="factorise_quadratics_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Factorise: {_fmt_quadratic(1, b, c)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"({_fmt_factor(p)})({_fmt_factor(q)})",
    )


TOPIC_EXPAND_SINGLE = TopicDefinition(
    id="expand_single_bracket",
    display_name="Single Bracket",
    description="Expand a single bracket, e.g. a(bx + c).",
    generate=generate_expand_single,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_expand_single,
)

TOPIC_EXPAND_DOUBLE_FOUNDATION = TopicDefinition(
    id="expand_double_brackets_foundation",
    display_name="Double Brackets",
    description="Expand two brackets into a quadratic expression.",
    generate=generate_expand_double_foundation,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_expand_double_foundation,
)

TOPIC_EXPAND_DOUBLE = TopicDefinition(
    id="expand_double_brackets",
    display_name="Double Brackets",
    description="Expand two brackets into a quadratic expression, including negative coefficients.",
    generate=generate_expand_double,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_expand_double,
)

TOPIC_EXPAND_TRIPLE = TopicDefinition(
    id="expand_triple_brackets",
    display_name="Triple Brackets",
    description="Expand three linear brackets into a cubic expression.",
    generate=generate_expand_triple,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_expand_triple,
)

TOPIC_FACTORISE_COMMON = TopicDefinition(
    id="factorise_common_factor",
    display_name="Common Factor",
    description="Factorise an expression by taking out the highest common factor.",
    generate=generate_factorise_common,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_factorise_common,
)

TOPIC_FACTORISE_QUADRATIC_FOUNDATION = TopicDefinition(
    id="factorise_quadratics_foundation",
    display_name="Quadratics",
    description="Factorise a quadratic expression with two positive integer roots.",
    generate=generate_factorise_quadratic_foundation,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_factorise_quadratic_foundation,
)

TOPIC_FACTORISE_QUADRATIC = TopicDefinition(
    id="factorise_quadratics",
    display_name="Quadratics",
    description="Factorise a quadratic expression with integer roots, including negative roots.",
    generate=generate_factorise_quadratic,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_factorise_quadratic,
)
