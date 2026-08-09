"""Shared quantity-display helper: a raw base-unit amount (grams,
millilitres) reads more naturally in a larger unit (kg, litres) once it
reaches 1000 - e.g. `display_qty(1200, "g")` -> "1.2kg". Shared by
best_buys.py and proportion.py's direct_proportion recipe template, kept in
one place rather than duplicated per topic file, and reusable by any future
topic with the same convention.

Fixed-point formatting only (never a Decimal's own str()/normalize() output
directly) - see CLAUDE.md's documented estimation_rounding gotcha: a Decimal
that lands on a round value can otherwise print in scientific notation (e.g.
"3E+1" instead of "30") - confirmed the same failure mode applies here too
(a qty of exactly 10000 normalizes to "1E+1"), even though no current caller's
range actually reaches it.
"""

from decimal import Decimal

_LARGER_UNIT = {"g": "kg", "ml": "L"}


def needs_larger_unit(qty: int, unit: str) -> bool:
    return unit in _LARGER_UNIT and qty >= 1000


def display_qty(qty: int, unit: str) -> str:
    """Format a raw integer qty (in `unit`, "g" or "ml") for display,
    converting to the larger unit (kg/L) once qty reaches 1000. Units other
    than g/ml are returned unchanged."""
    if not needs_larger_unit(qty, unit):
        return f"{qty}{unit}"
    scaled = (Decimal(qty) / Decimal(1000)).normalize()
    return f"{format(scaled, 'f')}{_LARGER_UNIT[unit]}"
