"""Laws of indices applied to algebraic terms (coeff * x^exponent), rather
than to plain numbers (see powers_roots.py for the numeric version of the
same skill). Foundation keeps exponents positive integers only; Higher adds
negative, zero, and fractional exponents (the last mixing indices with roots,
assuming x > 0 so the root is unambiguous).
"""

import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Algebraic Indices"

_Xpos = sp.symbols("x", positive=True)


def _term(coeff: int, exp: int) -> str:
    """Render coeff * x^exp as e.g. '3x^2', 'x', '5', 'x^-2', '4x^-6'."""
    if exp == 0:
        return str(coeff)
    exp_str = "" if exp == 1 else f"^{exp}"
    if coeff == 1:
        return f"x{exp_str}"
    return f"{coeff}x{exp_str}"


def _term_frac(coeff: int, num: int, den: int) -> str:
    """Render coeff * x^(num/den) as e.g. 'x^(1/2)', '6x^2' style fraction exponent."""
    exp_str = f"^({num}/{den})"
    return f"x{exp_str}" if coeff == 1 else f"{coeff}x{exp_str}"


# ---------------------------------------------------------------------------
# algebraic_indices_foundation
# ---------------------------------------------------------------------------


def generate_algebraic_indices_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["multiply", "divide", "power"])

    if shape == "multiply":
        c1, c2 = rng.randint(1, 6), rng.randint(1, 6)
        p, q = rng.randint(2, 6), rng.randint(2, 6)
        coeff, exp = c1 * c2, p + q

        # Independent verification: build both sides symbolically and confirm
        # they're identical, a different route than the manual add-the-
        # exponents/multiply-the-coefficients arithmetic in the steps.
        lhs = (c1 * X**p) * (c2 * X**q)
        rhs = coeff * X**exp
        if sp.expand(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_foundation (multiply) verification failed")

        steps = [
            "Multiplying powers of the same base: add the exponents, and multiply the coefficients.",
            f"{_term(c1, p)} × {_term(c2, q)} = ({c1}×{c2}) x^({p}+{q})",
            f"= {_term(coeff, exp)}",
        ]
        return Question(
            topic_id="algebraic_indices_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Simplify {_term(c1, p)} × {_term(c2, q)}",
            solution_steps=tuple(steps),
            final_answer=_term(coeff, exp),
            dedup_key=f"alg_ind_f_mult:{c1}:{p}:{c2}:{q}",
        )

    if shape == "divide":
        c2 = rng.randint(1, 4)
        r = rng.randint(1, 6)
        c1 = c2 * r  # guarantees exact coefficient division
        q = rng.randint(2, 4)
        p = rng.randint(q + 1, q + 4)  # p > q so the result stays a positive power
        exp = p - q

        lhs = sp.simplify((c1 * X**p) / (c2 * X**q))
        rhs = r * X**exp
        if sp.expand(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_foundation (divide) verification failed")

        steps = [
            "Dividing powers of the same base: subtract the exponents, and divide the coefficients.",
            f"{_term(c1, p)} ÷ {_term(c2, q)} = ({c1}÷{c2}) x^({p}-{q})",
            f"= {_term(r, exp)}",
        ]
        return Question(
            topic_id="algebraic_indices_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Simplify {_term(c1, p)} ÷ {_term(c2, q)}",
            solution_steps=tuple(steps),
            final_answer=_term(r, exp),
            dedup_key=f"alg_ind_f_div:{c1}:{p}:{c2}:{q}",
        )

    # power
    c = rng.randint(1, 6)
    p, q = rng.randint(2, 5), rng.randint(2, 4)
    coeff, exp = c**q, p * q

    lhs = (c * X**p) ** q
    rhs = coeff * X**exp
    if sp.expand(lhs - rhs) != 0:
        raise ValueError("algebraic_indices_foundation (power) verification failed")

    steps = [
        "Raising a power to another power: multiply the exponents, and raise the coefficient to that power too.",
        f"({_term(c, p)})^{q} = {c}^{q} x^({p}×{q})",
        f"= {_term(coeff, exp)}",
    ]
    return Question(
        topic_id="algebraic_indices_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Simplify ({_term(c, p)})^{q}",
        solution_steps=tuple(steps),
        final_answer=_term(coeff, exp),
        dedup_key=f"alg_ind_f_pow:{c}:{p}:{q}",
    )


def generate_modelled_example_algebraic_indices_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["multiply", "divide", "power"])

    if shape == "multiply":
        c1, c2 = rng.randint(1, 6), rng.randint(1, 6)
        p, q = rng.randint(2, 6), rng.randint(2, 6)
        coeff, exp = c1 * c2, p + q

        lhs = (c1 * X**p) * (c2 * X**q)
        rhs = coeff * X**exp
        if sp.expand(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_foundation (multiply) verification failed")

        teaching_steps = [
            f"{_term(c1, p)} means {c1} lots of x multiplied by itself {p} times, and {_term(c2, q)} means "
            f"{c2} lots of x multiplied by itself {q} times - multiplying them together just piles all of "
            "those x's into one product.",
            f"Deal with the numbers and the x's separately: multiply the coefficients ({c1}×{c2} = {coeff}), "
            f"and for the powers of x, use the law that says powers of the SAME base multiply by adding "
            f"their exponents ({p}+{q} = {exp}).",
            f"Putting both parts back together gives {_term(coeff, exp)}.",
        ]
        worked_calculation = [
            f"{_term(c1, p)} × {_term(c2, q)}",
            f"= ({c1}×{c2}) x^({p}+{q})",
            f"= {_term(coeff, exp)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Simplify {_term(c1, p)} × {_term(c2, q)}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(coeff, exp),
        )

    if shape == "divide":
        c2 = rng.randint(1, 4)
        r = rng.randint(1, 6)
        c1 = c2 * r
        q = rng.randint(2, 4)
        p = rng.randint(q + 1, q + 4)
        exp = p - q

        lhs = sp.simplify((c1 * X**p) / (c2 * X**q))
        rhs = r * X**exp
        if sp.expand(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_foundation (divide) verification failed")

        teaching_steps = [
            f"Dividing {_term(c1, p)} by {_term(c2, q)} is really cancelling: every one of the {q} x's on "
            "the bottom cancels an x on the top, leaving the leftover x's plus whatever the numbers divide to.",
            f"Divide the coefficients ({c1}÷{c2} = {r}), and for the powers of x, use the law that says "
            f"dividing powers of the SAME base means subtracting the exponents ({p}-{q} = {exp}).",
            f"That gives {_term(r, exp)} - notice the exponent got smaller because more x's were on the "
            "bottom being cancelled away.",
        ]
        worked_calculation = [
            f"{_term(c1, p)} ÷ {_term(c2, q)}",
            f"= ({c1}÷{c2}) x^({p}-{q})",
            f"= {_term(r, exp)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_foundation",
            tier=Tier.FOUNDATION,
            prompt=f"Simplify {_term(c1, p)} ÷ {_term(c2, q)}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(r, exp),
        )

    c = rng.randint(1, 6)
    p, q = rng.randint(2, 5), rng.randint(2, 4)
    coeff, exp = c**q, p * q

    lhs = (c * X**p) ** q
    rhs = coeff * X**exp
    if sp.expand(lhs - rhs) != 0:
        raise ValueError("modelled example algebraic_indices_foundation (power) verification failed")

    teaching_steps = [
        f"({_term(c, p)})^{q} means the whole bracket {_term(c, p)} is multiplied by itself {q} times - so "
        f"BOTH the coefficient {c} and the power of x inside get raised to the power {q}, not just one of them.",
        f"Raise the coefficient: {c}^{q} = {coeff}. Raise the power of x using the law that says a power "
        f"raised to another power multiplies the exponents: {p}×{q} = {exp}.",
        f"Combine the two results to get {_term(coeff, exp)}.",
    ]
    worked_calculation = [
        f"({_term(c, p)})^{q}",
        f"= {c}^{q} x^({p}×{q})",
        f"= {_term(coeff, exp)}",
    ]
    return ModelledExample(
        topic_id="algebraic_indices_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Simplify ({_term(c, p)})^{q}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_term(coeff, exp),
    )


# ---------------------------------------------------------------------------
# algebraic_indices_higher
# ---------------------------------------------------------------------------


def _rand_exp_pair(rng: random.Random) -> tuple[int, int]:
    """Pick two exponents in [-4, 6], not both zero (an all-zero pair would
    leave no x at all in the question, which defeats the point of an
    algebraic-indices topic)."""
    while True:
        p, q = rng.randint(-4, 6), rng.randint(-4, 6)
        if p != 0 or q != 0:
            return p, q


def _rand_nonzero_exp(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _frac_multiply_params(rng: random.Random) -> tuple[int, int, int, int, int]:
    """Pick (n, k, m1, m2, ...) for x^(m1/n) x x^(m2/n) -> x^k, choosing m1 = 1
    and m2 = n*k - 1 so both fractions are automatically in lowest terms
    (gcd(1, n) = 1 and gcd(nk-1, n) = gcd(-1, n) = 1) without any reduction
    step, verified separately in scratch testing before writing this."""
    n = rng.choice([2, 3, 4])
    k = rng.randint(1, 3)
    m1 = 1
    m2 = n * k - 1
    if rng.random() < 0.5:
        m1, m2 = m2, m1
    return n, k, m1, m2


def generate_algebraic_indices_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["multiply", "divide", "power", "fractional"])

    if shape == "multiply":
        c1, c2 = rng.randint(1, 6), rng.randint(1, 6)
        p, q = _rand_exp_pair(rng)
        coeff, exp = c1 * c2, p + q

        lhs = (c1 * X**p) * (c2 * X**q)
        rhs = coeff * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_higher (multiply) verification failed")

        steps = [
            "Multiplying powers of the same base: add the exponents (this still works when an exponent "
            "is negative or zero), and multiply the coefficients.",
            f"{_term(c1, p)} × {_term(c2, q)} = ({c1}×{c2}) x^({p}+({q}))",
            f"= {_term(coeff, exp)}",
        ]
        return Question(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term(c1, p)} × {_term(c2, q)}",
            solution_steps=tuple(steps),
            final_answer=_term(coeff, exp),
            dedup_key=f"alg_ind_h_mult:{c1}:{p}:{c2}:{q}",
        )

    if shape == "divide":
        c2 = rng.randint(1, 4)
        r = rng.randint(1, 6)
        c1 = c2 * r
        p, q = _rand_exp_pair(rng)
        exp = p - q

        lhs = sp.simplify((c1 * X**p) / (c2 * X**q))
        rhs = r * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_higher (divide) verification failed")

        steps = [
            "Dividing powers of the same base: subtract the exponents (this still works when an exponent "
            "is negative or zero), and divide the coefficients.",
            f"{_term(c1, p)} ÷ {_term(c2, q)} = ({c1}÷{c2}) x^({p}-({q}))",
            f"= {_term(r, exp)}",
        ]
        return Question(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term(c1, p)} ÷ {_term(c2, q)}",
            solution_steps=tuple(steps),
            final_answer=_term(r, exp),
            dedup_key=f"alg_ind_h_div:{c1}:{p}:{c2}:{q}",
        )

    if shape == "power":
        c = rng.randint(1, 4)
        p = _rand_nonzero_exp(rng, -3, 5)
        q = rng.randint(2, 4)  # keep the outer exponent positive so coeff**q stays an integer
        coeff, exp = c**q, p * q

        lhs = (c * X**p) ** q
        rhs = coeff * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_higher (power) verification failed")

        steps = [
            "Raising a power to another power: multiply the exponents (this still works when the inner "
            "exponent is negative or zero), and raise the coefficient to that power too.",
            f"({_term(c, p)})^{q} = {c}^{q} x^({p}×{q})",
            f"= {_term(coeff, exp)}",
        ]
        return Question(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify ({_term(c, p)})^{q}",
            solution_steps=tuple(steps),
            final_answer=_term(coeff, exp),
            dedup_key=f"alg_ind_h_pow:{c}:{p}:{q}",
        )

    # fractional
    sub = rng.choice(["multiply_frac", "root_power"])

    if sub == "multiply_frac":
        n, k, m1, m2 = _frac_multiply_params(rng)
        c1, c2 = rng.randint(1, 4), rng.randint(1, 4)
        coeff = c1 * c2

        # Independent verification: exponents are added as exact sympy Rationals,
        # a separate computation from the m1+m2 = n*k arithmetic used to build the
        # question in the first place.
        lhs = c1 * X ** sp.Rational(m1, n) * c2 * X ** sp.Rational(m2, n)
        rhs = coeff * X**k
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("algebraic_indices_higher (multiply_frac) verification failed")

        steps = [
            "Multiplying powers of the same base: add the exponents, even when they're fractions.",
            f"{_term_frac(c1, m1, n)} × {_term_frac(c2, m2, n)} = ({c1}×{c2}) x^({m1}/{n}+{m2}/{n})",
            f"= {_term(coeff, k)}",
        ]
        return Question(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term_frac(c1, m1, n)} × {_term_frac(c2, m2, n)}",
            solution_steps=tuple(steps),
            final_answer=_term(coeff, k),
            dedup_key=f"alg_ind_h_multfrac:{c1}:{m1}:{c2}:{m2}:{n}",
        )

    # root_power: (c^2 x^2m)^(1/2) -> c x^m, assuming x > 0
    c = rng.randint(2, 6)
    m = rng.randint(1, 4)
    base_coeff, base_exp = c**2, 2 * m

    # Independent verification uses a positive-x symbol, since sqrt(x^2m) is
    # only unambiguously x^m when x is known to be nonnegative - a genuinely
    # different check than the "halve the exponent" arithmetic in the steps.
    lhs = (base_coeff * _Xpos**base_exp) ** sp.Rational(1, 2)
    rhs = c * _Xpos**m
    if sp.simplify(lhs - rhs) != 0:
        raise ValueError("algebraic_indices_higher (root_power) verification failed")

    steps = [
        "Raising to the power 1/2 means taking a square root: take the square root of the coefficient and "
        "halve the exponent of x separately (assuming x > 0, so the root is unambiguous).",
        f"sqrt({base_coeff}) = {c}, and {base_exp}/2 = {m}.",
        f"({base_coeff}x^{base_exp})^(1/2) = {_term(c, m)}",
    ]
    return Question(
        topic_id="algebraic_indices_higher",
        tier=Tier.HIGHER,
        prompt=f"Simplify ({base_coeff}x^{base_exp})^(1/2), given that x > 0.",
        solution_steps=tuple(steps),
        final_answer=_term(c, m),
        dedup_key=f"alg_ind_h_rootpow:{c}:{m}",
    )


def generate_modelled_example_algebraic_indices_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["multiply", "divide", "power", "fractional"])

    if shape == "multiply":
        c1, c2 = rng.randint(1, 6), rng.randint(1, 6)
        p, q = _rand_exp_pair(rng)
        coeff, exp = c1 * c2, p + q

        lhs = (c1 * X**p) * (c2 * X**q)
        rhs = coeff * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_higher (multiply) verification failed")

        teaching_steps = [
            "The law for multiplying powers of the same base - add the exponents - doesn't stop working "
            "just because an exponent is negative or zero. A negative exponent still just means 'reciprocal', "
            "so the same addition rule applies exactly as it does for positive exponents.",
            f"Multiply the coefficients: {c1}×{c2} = {coeff}. Add the exponents of x, being careful with "
            f"the signs: {p} + ({q}) = {exp}.",
            f"Combine both parts to get {_term(coeff, exp)}"
            + (
                " - a negative overall exponent just means the x-part ends up on the bottom of a fraction."
                if exp < 0
                else "."
            ),
        ]
        worked_calculation = [
            f"{_term(c1, p)} × {_term(c2, q)}",
            f"= ({c1}×{c2}) x^({p}+({q}))",
            f"= {_term(coeff, exp)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term(c1, p)} × {_term(c2, q)}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(coeff, exp),
        )

    if shape == "divide":
        c2 = rng.randint(1, 4)
        r = rng.randint(1, 6)
        c1 = c2 * r
        p, q = _rand_exp_pair(rng)
        exp = p - q

        lhs = sp.simplify((c1 * X**p) / (c2 * X**q))
        rhs = r * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_higher (divide) verification failed")

        teaching_steps = [
            "The law for dividing powers of the same base - subtract the exponents - also still works with "
            "negative or zero exponents; just subtract them as signed numbers.",
            f"Divide the coefficients: {c1}÷{c2} = {r}. Subtract the exponents of x, taking care with the "
            f"signs: {p} - ({q}) = {exp}.",
            f"That gives {_term(r, exp)}"
            + (
                " - the exponent came out negative here, which just means x ends up on the bottom."
                if exp < 0
                else "."
            ),
        ]
        worked_calculation = [
            f"{_term(c1, p)} ÷ {_term(c2, q)}",
            f"= ({c1}÷{c2}) x^({p}-({q}))",
            f"= {_term(r, exp)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term(c1, p)} ÷ {_term(c2, q)}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(r, exp),
        )

    if shape == "power":
        c = rng.randint(1, 4)
        p = _rand_nonzero_exp(rng, -3, 5)
        q = rng.randint(2, 4)
        coeff, exp = c**q, p * q

        lhs = (c * X**p) ** q
        rhs = coeff * X**exp
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_higher (power) verification failed")

        teaching_steps = [
            "Raising a bracket to a power still means multiplying the exponents inside, whether the inner "
            "exponent is positive, negative, or zero - the law itself doesn't change.",
            f"Raise the coefficient to the power {q}: {c}^{q} = {coeff}. Multiply the exponents of x: "
            f"{p}×{q} = {exp}.",
            f"Combine both to get {_term(coeff, exp)}.",
        ]
        worked_calculation = [
            f"({_term(c, p)})^{q}",
            f"= {c}^{q} x^({p}×{q})",
            f"= {_term(coeff, exp)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify ({_term(c, p)})^{q}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(coeff, exp),
        )

    sub = rng.choice(["multiply_frac", "root_power"])

    if sub == "multiply_frac":
        n, k, m1, m2 = _frac_multiply_params(rng)
        c1, c2 = rng.randint(1, 4), rng.randint(1, 4)
        coeff = c1 * c2

        lhs = c1 * X ** sp.Rational(m1, n) * c2 * X ** sp.Rational(m2, n)
        rhs = coeff * X**k
        if sp.simplify(lhs - rhs) != 0:
            raise ValueError("modelled example algebraic_indices_higher (multiply_frac) verification failed")

        teaching_steps = [
            f"A fractional exponent like {m1}/{n} isn't anything mysterious - it's still just 'a power', "
            "and the same law for multiplying powers of the same base (add the exponents) applies exactly "
            "as it does for whole-number exponents.",
            f"Multiply the coefficients: {c1}×{c2} = {coeff}. Add the two fractional exponents: "
            f"{m1}/{n} + {m2}/{n} = {m1 + m2}/{n} = {k}.",
            f"Because the fractions share the same denominator {n}, the exponents combine to a whole "
            f"number {k}, giving {_term(coeff, k)} with no fraction left in the final exponent.",
        ]
        worked_calculation = [
            f"{_term_frac(c1, m1, n)} × {_term_frac(c2, m2, n)}",
            f"= ({c1}×{c2}) x^({m1}/{n}+{m2}/{n})",
            f"= {_term(coeff, k)}",
        ]
        return ModelledExample(
            topic_id="algebraic_indices_higher",
            tier=Tier.HIGHER,
            prompt=f"Simplify {_term_frac(c1, m1, n)} × {_term_frac(c2, m2, n)}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_term(coeff, k),
        )

    c = rng.randint(2, 6)
    m = rng.randint(1, 4)
    base_coeff, base_exp = c**2, 2 * m

    lhs = (base_coeff * _Xpos**base_exp) ** sp.Rational(1, 2)
    rhs = c * _Xpos**m
    if sp.simplify(lhs - rhs) != 0:
        raise ValueError("modelled example algebraic_indices_higher (root_power) verification failed")

    teaching_steps = [
        "A power of 1/2 on the outside of a bracket means 'take the square root of the whole bracket'. "
        "Since the bracket is a product, the root can be applied to the coefficient and the power of x "
        "separately.",
        f"The square root of the coefficient {base_coeff} is {c} (since {c}×{c} = {base_coeff}), and the "
        f"square root of x^{base_exp} is x^{m} (halve the exponent: {base_exp}/2 = {m}).",
        "This halving trick for the root of a power only gives a single unambiguous answer when x is "
        "known to be positive, which is why the question states x > 0.",
        f"Putting both parts together gives {_term(c, m)}.",
    ]
    worked_calculation = [
        f"({base_coeff}x^{base_exp})^(1/2)",
        f"= sqrt({base_coeff}) × x^({base_exp}/2)",
        f"= {_term(c, m)}",
    ]
    return ModelledExample(
        topic_id="algebraic_indices_higher",
        tier=Tier.HIGHER,
        prompt=f"Simplify ({base_coeff}x^{base_exp})^(1/2), given that x > 0.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_term(c, m),
    )


TOPIC_ALGEBRAIC_INDICES_FOUNDATION = TopicDefinition(
    id="algebraic_indices_foundation",
    display_name="Laws of Indices with Algebra",
    description="Multiply, divide, and raise to a power algebraic terms with positive integer exponents.",
    generate=generate_algebraic_indices_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_algebraic_indices_foundation,
)

TOPIC_ALGEBRAIC_INDICES_HIGHER = TopicDefinition(
    id="algebraic_indices_higher",
    display_name="Laws of Indices with Algebra (Negative and Fractional)",
    description="Apply the laws of indices to algebraic terms with negative, zero, and fractional exponents.",
    generate=generate_algebraic_indices_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_indices_higher,
)
