"""Shared per-question rounding-precision engine.

Many topics whose answer is a rounded length/area/volume/distance previously
all hardcoded the same instruction, "correct to 3 significant figures" -
per user request, each such question now randomly picks one of the three
real GCSE rounding instructions (1 decimal place / 2 decimal places / 3
significant figures) instead, with genuinely equal ("a third chance of
each") probability. This module is the single place that instruction text
and its matching Decimal-based rounding function live, so every topic using
it stays consistent and gets the scientific-notation-avoidance fix (see
`_round_to_sf`) for free - mirrors this app's `phrasing.py` precedent for a
small shared per-topic helper module.

Deliberately NOT used for: angle answers (always 1 decimal place by real
exam convention, never significant figures - swapping this in would be
mathematically wrong, not just a style choice), a standard-form mantissa
(always expressed to a small number of significant figures as part of
standard form's own notation, not a "final rounded answer" instruction),
and the `rounding_to_significant_figures` topic itself (which teaches
significant-figure rounding as a skill - changing its own wording would
undermine the topic).
"""

import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Callable


def _round_to_dp(value: float, dp: int) -> Decimal:
    """Round to dp decimal places, always as a plain fixed-point Decimal."""
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)


def _round_to_sf(value: float, sf: int) -> Decimal:
    """Round to sf significant figures, always displaying as a plain
    fixed-point decimal string. Decimal.quantize alone keeps a scientific
    exponent internally when the rounded value lands on a power of ten,
    which then prints as e.g. "3E+1" instead of "30" - the same bug class
    already documented and fixed for `estimation_rounding`/several
    `_round_to_3sf` helpers elsewhere in this codebase. Reformatting through
    `format(quantized, "f")` avoids it here too."""
    d = Decimal(str(value))
    if d == 0:
        return Decimal("0")
    exp = d.adjusted()
    quantized = d.quantize(Decimal(1).scaleb(exp - (sf - 1)), rounding=ROUND_HALF_UP)
    return Decimal(format(quantized, "f"))


@dataclass(frozen=True)
class RoundingSpec:
    phrase: str  # e.g. "2 decimal places" - for the prompt's "correct to {phrase}."
    short: str  # e.g. "2 d.p." - for a step's trailing "(...)" note
    round_fn: Callable[[float], Decimal]


def _spec_dp(dp: int) -> RoundingSpec:
    word = "place" if dp == 1 else "places"
    return RoundingSpec(
        phrase=f"{dp} decimal {word}",
        short=f"{dp} d.p.",
        round_fn=lambda v, dp=dp: _round_to_dp(v, dp),
    )


def _spec_sf(sf: int) -> RoundingSpec:
    return RoundingSpec(
        phrase=f"{sf} significant figures",
        short=f"{sf} s.f.",
        round_fn=lambda v, sf=sf: _round_to_sf(v, sf),
    )


_OPTIONS = (_spec_dp(1), _spec_dp(2), _spec_sf(3))


def pick_rounding(rng: random.Random) -> RoundingSpec:
    """Pick one of the three GCSE-standard rounding instructions at random,
    each equally likely: 1 decimal place, 2 decimal places, or 3 significant
    figures."""
    return rng.choice(_OPTIONS)
