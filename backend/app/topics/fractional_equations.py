"""Solving equations that involve fractions - three topics:

- fractional_equations_F  : single fractional term (Corbett V111 style) - clears
  one denominator to a linear equation (x/a = b, x/a +- c = d, (x+p)/a = b, mx/a = c).
- fractional_equations_H   : two fractional terms combined over a common
  denominator (x/a + x/b = c, (x+p)/a +- (x+q)/b = c) - still reduces to linear.
- fractional_equations_advanced_H : fractions with the unknown in the
  denominator (Corbett V111a / V112 Q3) - clears to a QUADRATIC.

Every fraction is emitted with the \\frac{}{} marker so mathtext.py renders a
true vinculum (a bare "x/2" would not - its fraction regex only fires on bare
digits). The linear topics reuse algebra_utils.solve_linear_with_steps; the
advanced topic reuses the quadratic-root display conventions from
quadratic_equations.py. Every generator verifies its answer independently with
sympy (a different path than the manual step-building), per this project's rule.
"""

import math
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP_LINEAR = "Solving Linear Equations"
GROUP_ALG_FRAC = "Algebraic Fractions"

INSTRUCTION = "Solve the following equation."
INSTRUCTION_ADV = "Solve the following equation, giving your answers to 2 decimal places where necessary."


def _frac(num, den) -> str:
    return f"\\frac{{{num}}}{{{den}}}"


def _xplus(p: int) -> str:
    """Render 'x + p' / 'x - |p|' / 'x' for a denominator like (x + p)."""
    if p == 0:
        return "x"
    return f"x + {p}" if p > 0 else f"x - {abs(p)}"


def _signed(p: int) -> str:
    return f"+ {p}" if p >= 0 else f"- {abs(p)}"


# ---------------------------------------------------------------------------
# Foundation: a single fractional term -> linear
# ---------------------------------------------------------------------------


def _build_fractional_F(rng: random.Random):
    shape = rng.choice(["single", "add_sub", "bracket", "coeff"])
    if shape == "single":  # x/a = b
        a = rng.randint(2, 12)
        b = rng.randint(2, 15)
        x_sol = a * b
        disp = f"{_frac('x', a)} = {b}"
        steps = [f"Multiply both sides by {a}: x = {b} × {a}", f"x = {x_sol}"]
        lhs, rhs = X / a, b
    elif shape == "add_sub":  # x/a +- c = d
        a = rng.randint(2, 10)
        c = rng.randint(1, 12)
        k = rng.randint(2, 12)  # value of x/a
        op = rng.choice(["+", "-"])
        d = k + c if op == "+" else k - c
        x_sol = a * k
        move = "Subtract" if op == "+" else "Add"
        prep = "from" if op == "+" else "to"
        disp = f"{_frac('x', a)} {op} {c} = {d}"
        steps = [
            f"{move} {c} {prep} both sides: {_frac('x', a)} = {k}",
            f"Multiply both sides by {a}: x = {x_sol}",
        ]
        lhs = X / a + c if op == "+" else X / a - c
        rhs = d
    elif shape == "bracket":  # (x + p)/a = b
        a = rng.randint(2, 9)
        b = rng.randint(2, 12)
        p = rng.choice([n for n in range(-9, 10) if n != 0])
        x_sol = a * b - p
        disp = f"{_frac(f'x {_signed(p)}', a)} = {b}"
        steps = [
            f"Multiply both sides by {a}: x {_signed(p)} = {a * b}",
            f"x = {x_sol}",
        ]
        lhs, rhs = (X + p) / a, b
    else:  # coeff: (m x)/a = c
        m = rng.randint(2, 6)
        a = rng.randint(2, 12)
        c = rng.randint(2, 12)
        num = c * a
        if num % m != 0:
            return None
        x_sol = num // m
        disp = f"{_frac(f'{m}x', a)} = {c}"
        steps = [
            f"Multiply both sides by {a}: {m}x = {c * a}",
            f"Divide both sides by {m}: x = {x_sol}",
        ]
        lhs, rhs = (m * X) / a, c
    return disp, steps, sp.Integer(x_sol), lhs, rhs, shape


def _verify_single_root(lhs, rhs, expected) -> bool:
    sols = sp.solve(sp.Eq(lhs, rhs), X)
    return len(sols) == 1 and sp.Rational(sols[0]) == sp.Rational(expected)


def generate_fractional_equations_F(tier: Tier, rng: random.Random) -> Question:
    for _ in range(60):
        built = _build_fractional_F(rng)
        if built is None:
            continue
        disp, steps, x_sol, lhs, rhs, shape = built
        if _verify_single_root(lhs, rhs, x_sol):
            break
    else:
        raise ValueError("fractional_equations_F could not build a verified equation")
    return Question(
        topic_id="fractional_equations_F",
        tier=Tier.FOUNDATION,
        prompt=f"{INSTRUCTION}\n{disp}",
        solution_steps=tuple(steps),
        final_answer=f"x = {fmt_num(x_sol)}",
        dedup_key=f"frac_eq_f:{shape}:{disp}",
    )


def generate_modelled_example_fractional_equations_F(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(60):
        built = _build_fractional_F(rng)
        if built is None:
            continue
        disp, steps, x_sol, lhs, rhs, shape = built
        if _verify_single_root(lhs, rhs, x_sol):
            break
    else:
        raise ValueError("fractional_equations_F modelled example could not build a verified equation")
    teaching_steps = [
        "When an equation has a variable divided by a number, the first move is to get rid of that "
        "fraction - multiply BOTH sides of the equation by the number underneath, which cancels the "
        "denominator and leaves a straightforward equation to finish.",
        "Do the same operation to every term on both sides so the equation stays balanced, then solve "
        "what is left in the usual way (undo any addition/subtraction, then any multiplication).",
        "Each step below shows one balancing move, ending with x on its own: " + "  ".join(steps),
    ]
    worked_calculation = [disp] + list(steps)
    return ModelledExample(
        topic_id="fractional_equations_F",
        tier=Tier.FOUNDATION,
        prompt=f"{INSTRUCTION}\n{disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {fmt_num(x_sol)}",
    )


# ---------------------------------------------------------------------------
# Higher: two fractional terms -> linear (via common denominator)
# ---------------------------------------------------------------------------


def _build_fractional_H(rng: random.Random):
    shape = rng.choice(["two_terms", "two_brackets"])
    if shape == "two_terms":  # x/a + x/b = c
        a, b = rng.sample(range(2, 9), 2)
        c = rng.randint(2, 12)
        lcm = a * b // math.gcd(a, b)
        coeff_num = lcm // a + lcm // b
        lhs, rhs = X / a + X / b, c
        disp = f"{_frac('x', a)} + {_frac('x', b)} = {c}"
        steps = [
            f"Multiply every term by the LCM of {a} and {b}, which is {lcm}:",
            f"{lcm // a}x + {lcm // b}x = {c * lcm}",
            f"{coeff_num}x = {c * lcm}",
            f"x = {fmt_num(sp.Rational(c * lcm, coeff_num))}",
        ]
        x_sol = sp.Rational(c * lcm, coeff_num)
    else:  # (x + p)/a +- (x + q)/b = c
        a, b = rng.sample(range(2, 8), 2)
        p = rng.choice([n for n in range(-8, 9) if n != 0])
        q = rng.choice([n for n in range(-8, 9) if n != 0])
        c = rng.randint(-6, 8)
        op = rng.choice(["+", "-"])
        lcm = a * b // math.gcd(a, b)
        lhs = (X + p) / a + (X + q) / b if op == "+" else (X + p) / a - (X + q) / b
        rhs = c
        sols = sp.solve(sp.Eq(lhs, rhs), X)
        if len(sols) != 1:
            return None
        x_sol = sp.Rational(sols[0])
        # After clearing, it is linear: coeff*x + const = c*lcm.
        m1, m2 = lcm // a, lcm // b
        lin_coeff = m1 + m2 if op == "+" else m1 - m2
        lin_const = m1 * p + m2 * q if op == "+" else m1 * p - m2 * q
        tail_steps, tail_sol = solve_linear_with_steps(lin_coeff, lin_const, 0, c * lcm)
        if tail_sol != x_sol:
            return None
        disp = f"{_frac(f'x {_signed(p)}', a)} {op} {_frac(f'x {_signed(q)}', b)} = {c}"
        steps = [f"Multiply every term by the LCM of {a} and {b}, which is {lcm}:"] + tail_steps
    return disp, steps, x_sol, lhs, rhs, shape


def generate_fractional_equations_H(tier: Tier, rng: random.Random) -> Question:
    for _ in range(80):
        built = _build_fractional_H(rng)
        if built is None:
            continue
        disp, steps, x_sol, lhs, rhs, shape = built
        if _verify_single_root(lhs, rhs, x_sol):
            break
    else:
        raise ValueError("fractional_equations_H could not build a verified equation")
    return Question(
        topic_id="fractional_equations_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION}\n{disp}",
        solution_steps=tuple(steps),
        final_answer=f"x = {fmt_num(x_sol)}",
        dedup_key=f"frac_eq_h:{shape}:{disp}",
    )


def generate_modelled_example_fractional_equations_H(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(80):
        built = _build_fractional_H(rng)
        if built is None:
            continue
        disp, steps, x_sol, lhs, rhs, shape = built
        if _verify_single_root(lhs, rhs, x_sol):
            break
    else:
        raise ValueError("fractional_equations_H modelled example could not build a verified equation")
    teaching_steps = [
        "With a fraction on more than one term, the key idea is to clear ALL the denominators in one "
        "go: find the lowest common multiple (LCM) of the denominators and multiply every single term "
        "by it. Each denominator then divides into the LCM exactly, leaving no fractions behind.",
        "Multiplying every term (on both sides) by the same number keeps the equation balanced. What "
        "remains is an ordinary linear equation - collect the x-terms together, then solve.",
        "Following that through: " + "  ".join(steps),
    ]
    worked_calculation = [disp] + list(steps)
    return ModelledExample(
        topic_id="fractional_equations_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION}\n{disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {fmt_num(x_sol)}",
    )


# ---------------------------------------------------------------------------
# Advanced Higher: unknown in the denominator -> quadratic
# ---------------------------------------------------------------------------


def _fmt_root(r) -> str:
    """Exact value for a rational root, otherwise a 2-decimal-place decimal."""
    if r.is_rational:
        return fmt_num(sp.Rational(r))
    return format(Decimal(float(r)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def _fmt_quadratic(a, b, c) -> str:
    parts = []
    parts.append("x^2" if a == 1 else ("-x^2" if a == -1 else f"{a}x^2"))
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    if c != 0:
        parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
    return " ".join(parts) + " = 0"


def _build_advanced(rng: random.Random):
    shape = rng.choice(["sum", "proportion"])
    if shape == "sum":  # a/(x+p) +- b/(x+q) = c
        a = rng.randint(1, 6)
        b = rng.randint(1, 6)
        p = rng.randint(-6, 6)
        q = rng.choice([n for n in range(-6, 7) if n != p])
        c = rng.choice([n for n in range(1, 5)])
        op = rng.choice(["+", "-"])
        term2 = sp.Rational(b) / (X + q)
        lhs = sp.Rational(a) / (X + p) + (term2 if op == "+" else -term2)
        rhs = c
        disp = f"{_frac(a, _xplus(p))} {op} {_frac(b, _xplus(q))} = {c}"
        bad = {-p, -q}
    else:  # a/(x+p) = (x+q)/d  -> cross multiply -> quadratic
        a = rng.randint(2, 9)
        p = rng.randint(-6, 6)
        q = rng.randint(-6, 6)
        d = rng.randint(2, 6)
        lhs = sp.Rational(a) / (X + p)
        rhs = (X + q) / d
        disp = f"{_frac(a, _xplus(p))} = {_frac(_xplus(q), d)}"
        bad = {-p}
    return shape, lhs, rhs, disp, bad


def _solve_advanced(lhs, rhs, bad):
    """Clear denominators to a quadratic; return (A, B, C, valid_roots) or None
    if it doesn't reduce to a genuine quadratic with real, non-extraneous
    roots. A/B/C are normalised to a positive leading coefficient for display."""
    quad = sp.expand(sp.numer(sp.together(lhs - rhs)))
    poly = sp.Poly(quad, X)
    if poly.degree() != 2:
        return None
    A, B, C = (int(v) for v in poly.all_coeffs())
    if A < 0:  # display ax^2+bx+c=0 with a positive leading term (roots unchanged)
        A, B, C = -A, -B, -C
    if B * B - 4 * A * C < 0:  # no real roots
        return None
    bad_vals = {sp.Integer(v) for v in bad}
    # Substitution check against the ORIGINAL fractional equation - a genuinely
    # different path than the poly above, and it rejects any extraneous root
    # that would make an original denominator zero.
    diff = sp.sympify(lhs) - sp.sympify(rhs)
    verified = []
    for r in sp.solve(sp.Eq(lhs, rhs), X):
        if not r.is_real or r in bad_vals:
            continue
        if sp.simplify(diff.subs(X, r)) == 0:
            verified.append(r)
    if not verified:
        return None
    return A, B, C, verified


def generate_fractional_equations_advanced(tier: Tier, rng: random.Random) -> Question:
    for _ in range(120):
        shape, lhs, rhs, disp, bad = _build_advanced(rng)
        solved = _solve_advanced(lhs, rhs, bad)
        if solved is None:
            continue
        A, B, C, roots = solved
        break
    else:
        raise ValueError("fractional_equations_advanced could not build a verified equation")
    root_strs = sorted({_fmt_root(r) for r in roots})
    answer = " or ".join(f"x = {s}" for s in root_strs)
    steps = [
        "Multiply both sides by the denominator(s) to clear the fractions.",
        f"This rearranges to {_fmt_quadratic(A, B, C)}.",
        f"Solving the quadratic: {answer}.",
    ]
    return Question(
        topic_id="fractional_equations_advanced_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION_ADV}\n{disp}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"frac_eq_adv:{shape}:{disp}",
    )


def generate_modelled_example_fractional_equations_advanced(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(120):
        shape, lhs, rhs, disp, bad = _build_advanced(rng)
        solved = _solve_advanced(lhs, rhs, bad)
        if solved is None:
            continue
        A, B, C, roots = solved
        break
    else:
        raise ValueError("fractional_equations_advanced modelled example could not build a verified equation")
    root_strs = sorted({_fmt_root(r) for r in roots})
    answer = " or ".join(f"x = {s}" for s in root_strs)
    teaching_steps = [
        "When the unknown appears in a denominator, you still start by clearing the fractions - "
        "multiply every term by each denominator (or by their product). Because the denominators "
        "contain x, multiplying them out produces an x-squared term, so the equation becomes a "
        "quadratic rather than a linear one.",
        f"Expanding and collecting everything on one side gives the quadratic {_fmt_quadratic(A, B, C)}.",
        "Solve that quadratic in the usual way (factorising, or the quadratic formula). Give any "
        "non-exact roots to 2 decimal places, and reject a value that would make an original "
        "denominator zero.",
        f"The solutions are {answer}.",
    ]
    worked_calculation = [disp, _fmt_quadratic(A, B, C), answer]
    return ModelledExample(
        topic_id="fractional_equations_advanced_H",
        tier=Tier.HIGHER,
        prompt=f"{INSTRUCTION_ADV}\n{disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_FRACTIONAL_EQUATIONS_F = TopicDefinition(
    id="fractional_equations_F",
    display_name="Equations Involving Fractions",
    description="Solve a linear equation containing a fractional term by clearing the denominator.",
    generate=generate_fractional_equations_F,
    section=SECTION,
    group=GROUP_LINEAR,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_fractional_equations_F,
)

TOPIC_FRACTIONAL_EQUATIONS_H = TopicDefinition(
    id="fractional_equations_H",
    display_name="Equations Involving Fractions (Higher)",
    description="Solve an equation with two fractional terms by multiplying through by the common denominator.",
    generate=generate_fractional_equations_H,
    section=SECTION,
    group=GROUP_LINEAR,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_fractional_equations_H,
)

TOPIC_FRACTIONAL_EQUATIONS_ADVANCED = TopicDefinition(
    id="fractional_equations_advanced_H",
    display_name="Fractional Equations (Unknown in the Denominator)",
    description="Solve an equation with the unknown in a denominator, clearing fractions to a quadratic.",
    generate=generate_fractional_equations_advanced,
    section=SECTION,
    group=GROUP_ALG_FRAC,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_fractional_equations_advanced,
)
