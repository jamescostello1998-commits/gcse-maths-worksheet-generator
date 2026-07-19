import math
import random

import sympy as sp

from app.core.models import Question, Tier
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


TOPIC_EXPAND_SINGLE = TopicDefinition(
    id="expand_single_bracket",
    display_name="Single Bracket",
    description="Expand a single bracket, e.g. a(bx + c).",
    generate=generate_expand_single,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_EXPAND_DOUBLE_FOUNDATION = TopicDefinition(
    id="expand_double_brackets_foundation",
    display_name="Double Brackets",
    description="Expand two brackets into a quadratic expression.",
    generate=generate_expand_double_foundation,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_EXPAND_DOUBLE = TopicDefinition(
    id="expand_double_brackets",
    display_name="Double Brackets",
    description="Expand two brackets into a quadratic expression, including negative coefficients.",
    generate=generate_expand_double,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.HIGHER,
)

TOPIC_EXPAND_TRIPLE = TopicDefinition(
    id="expand_triple_brackets",
    display_name="Triple Brackets",
    description="Expand three linear brackets into a cubic expression.",
    generate=generate_expand_triple,
    section=SECTION,
    group=GROUP_EXPAND,
    fixed_tier=Tier.HIGHER,
)

TOPIC_FACTORISE_COMMON = TopicDefinition(
    id="factorise_common_factor",
    display_name="Common Factor",
    description="Factorise an expression by taking out the highest common factor.",
    generate=generate_factorise_common,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_FACTORISE_QUADRATIC_FOUNDATION = TopicDefinition(
    id="factorise_quadratics_foundation",
    display_name="Quadratics",
    description="Factorise a quadratic expression with two positive integer roots.",
    generate=generate_factorise_quadratic_foundation,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_FACTORISE_QUADRATIC = TopicDefinition(
    id="factorise_quadratics",
    display_name="Quadratics",
    description="Factorise a quadratic expression with integer roots, including negative roots.",
    generate=generate_factorise_quadratic,
    section=SECTION,
    group=GROUP_FACTORISE,
    fixed_tier=Tier.HIGHER,
)
