"""Shared helpers for formatting and stepwise-solving linear expressions.

Used by both the linear_equations topic and the angles topic (which reduces
to solving a linear equation once an angle fact produces one).
"""

import sympy as sp

X = sp.symbols("x")


def fmt_num(n) -> str:
    n = sp.Rational(n)
    if n.is_Integer:
        return str(int(n))
    return f"{n.p}/{n.q}"


def fmt_linear(coeff, const) -> str:
    """Render coeff*x + const as e.g. '3x + 5', '-x - 4', '7', '2x'."""
    coeff = sp.Rational(coeff)
    const = sp.Rational(const)
    parts: list[str] = []
    if coeff != 0:
        if coeff == 1:
            parts.append("x")
        elif coeff == -1:
            parts.append("-x")
        else:
            parts.append(f"{fmt_num(coeff)}x")
    if const != 0:
        sign = "+" if const > 0 else "-"
        term = fmt_num(sp.Abs(const))
        if parts:
            parts.append(f"{sign} {term}")
        else:
            parts.append(f"-{term}" if const < 0 else term)
    if not parts:
        return "0"
    return " ".join(parts)


def solve_linear_with_steps(
    lhs_coeff, lhs_const, rhs_coeff, rhs_const
) -> tuple[list[str], sp.Rational]:
    """Solve lhs_coeff*x + lhs_const = rhs_coeff*x + rhs_const, recording each
    manual algebra step as a human-readable string. Returns (steps, solution).
    """
    lhs_coeff = sp.Rational(lhs_coeff)
    lhs_const = sp.Rational(lhs_const)
    rhs_coeff = sp.Rational(rhs_coeff)
    rhs_const = sp.Rational(rhs_const)

    steps = [f"{fmt_linear(lhs_coeff, lhs_const)} = {fmt_linear(rhs_coeff, rhs_const)}"]

    if rhs_coeff != 0:
        new_lhs_coeff = lhs_coeff - rhs_coeff
        if rhs_coeff > 0:
            steps.append(f"Subtract {fmt_num(rhs_coeff)}x from both sides:")
        else:
            steps.append(f"Add {fmt_num(sp.Abs(rhs_coeff))}x to both sides:")
        steps.append(f"{fmt_linear(new_lhs_coeff, lhs_const)} = {fmt_num(rhs_const)}")
        lhs_coeff, rhs_coeff = new_lhs_coeff, sp.Integer(0)

    if lhs_coeff == 0:
        raise ValueError("Equation has no unique solution (coefficient of x is 0)")

    if lhs_const != 0:
        new_rhs_const = rhs_const - lhs_const
        if lhs_const > 0:
            steps.append(f"Subtract {fmt_num(lhs_const)} from both sides:")
        else:
            steps.append(f"Add {fmt_num(sp.Abs(lhs_const))} to both sides:")
        steps.append(f"{fmt_linear(lhs_coeff, 0)} = {fmt_num(new_rhs_const)}")
        lhs_const, rhs_const = sp.Integer(0), new_rhs_const

    if lhs_coeff != 1:
        solution = sp.Rational(rhs_const / lhs_coeff)
        steps.append(f"Divide both sides by {fmt_num(lhs_coeff)}:")
        steps.append(f"x = {fmt_num(solution)}")
    else:
        solution = rhs_const
        steps.append(f"x = {fmt_num(solution)}")

    return steps, solution
