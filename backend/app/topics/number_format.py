"""Shared helpers for converting exact sympy Rationals to clean display strings.

Used by any topic whose answers are exact rational values that should render
as either a clean integer, a terminating decimal, or (failing that) a
reduced fraction - never a rounded float that could hide a wrong answer.
"""

from fractions import Fraction

import sympy as sp


def to_fraction(value: sp.Rational) -> Fraction:
    r = sp.Rational(value)
    return Fraction(int(r.p), int(r.q))


def fmt_money(value) -> str:
    r = sp.Rational(value)
    if r.is_Integer:
        return str(int(r))
    denom = int(sp.fraction(r)[1])
    while denom % 2 == 0:
        denom //= 2
    while denom % 5 == 0:
        denom //= 5
    if denom == 1:
        return f"{float(r):.2f}"
    return f"{r.p}/{r.q}"
