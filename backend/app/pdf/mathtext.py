"""Centralised plain-text -> ReportLab Paragraph markup conversion for maths
text (question prompts, solution steps, final answers).

Topic generators emit plain text like "3x^2 + 5", "10^-3", "3/4" or "x^(1/4)"
using an ASCII convention (bare 'x'/'n' for algebraic variables, '^n' for
exponents, '^(num/den)' for a fractional exponent, "num/den" for a standalone
fraction) so they stay easy to write, verify, and unit-test. `to_markup` is
applied once, centrally, at PDF-render time to turn that into real
typesetting: x and n are italicised, '^n' becomes a superscript, a fractional
exponent is raised as one flat "(num/den)" unit, and a standalone fraction
gets its numerator raised/denominator lowered (e.g. "3/4" -> 3-raised /
4-lowered) rather than sitting inline on the baseline. Any future topic that
follows the same ASCII convention gets correct typesetting for free.

Only x and n are italicised (not a, b, or other letters) - see CLAUDE.md for
why a blanket rule can't safely cover every single-letter variable (e.g. "a"
collides constantly with the English indefinite article).

Standalone fractions here use ReportLab's native <super>/<sub> markup, not a
true stacked vinculum (numerator over a horizontal line over denominator) - a
real vinculum can't be built from Paragraph markup alone (ReportLab's inline
<img> tag only accepts a file-path string, and this environment has no
working image-rasterisation backend), so it would need PNGs rendered to temp
files via a hardcoded font path. See app/pdf/diagrams.py's `_draw_fraction`
for the real vinculum used in diagram labels, where the diagram is already
being drawn as vector shapes and no such workaround is needed.

A fractional *exponent* (e.g. "x^(1/4)") is deliberately typeset differently
from a standalone fraction: just one flat `<super>(1/4)</super>` rather than
a nested raised-numerator/lowered-denominator fraction inside a superscript.
Nesting `<super>` inside `<super>` was tried and rendered with the numerator
and denominator overlapping each other (verified by rendering both side by
side) - a single flat superscript reads cleanly instead.

All three numeric patterns (fractional exponent, integer exponent, standalone
fraction) are matched by ONE combined regex in a single `re.sub` pass, rather
than three separate sequential passes - a fractional exponent's raised
"(1/4)" would otherwise be a bare digit-slash-digit substring indistinguishable
from a standalone fraction, and a later, separate fraction pass would re-match
and re-process it (producing a broken doubly-nested result). Matching
everything in one pass means each character is claimed by exactly one
alternative and never re-scanned.

**ReportLab quirk**: a comma immediately after a closing `</sub>` with no
space in between renders raised and glued to the preceding digit instead of
sitting on the baseline (verified in isolation - periods, colons, semicolons,
question marks and closing parens in the same position are all unaffected,
as is a comma after `</super>`; only sub+comma with zero gap breaks). Since
every standalone fraction here ends in `</sub>`, and prose text often follows
a fraction straight with a comma (e.g. "...= 20/90, 2/9..."), `to_markup`
inserts a non-breaking space (u+00a0) before such a comma to dodge it.

**Glyph gotcha**: the unicode division slash U+2215 ("∕") is NOT in Helvetica
either (renders as a missing-glyph box, same class of issue as the "⁻¹"
gotcha documented in CLAUDE.md) - a fractional exponent's "/" must stay a
plain ASCII slash.
"""

import re

# Matches, in priority order within one alternation so each span is consumed
# exactly once: (1) a fractional exponent "^(num/den)", (2) a plain integer
# exponent "^n", (3) a standalone "num/den" fraction.
_MATH_RE = re.compile(
    r"\^\((?P<epnum>-?\d+)/(?P<epden>-?\d+)\)"
    r"|\^(?P<exp>-?\d+)"
    r"|(?P<fsign>-?)(?P<fnum>\d+)/(?P<fden>\d+)"
)
# Matches a lone x or n not glued to another letter (so "box" or "and" are
# left alone) - single pass over the original text so italicising one
# variable can never change what the other one sees as its neighbour.
_VARIABLE_RE = re.compile(r"(?<![A-Za-z])[xn](?![A-Za-z])")

_NBSP = " "


def _replace_math(m: re.Match, text: str) -> str:
    if m.group("epnum") is not None:
        return f"<super>({m.group('epnum')}/{m.group('epden')})</super>"
    if m.group("exp") is not None:
        return f"<super>{m.group('exp')}</super>"
    sign, num, den = m.group("fsign"), m.group("fnum"), m.group("fden")
    markup = f"{sign}<super>{num}</super>/<sub>{den}</sub>"
    if text[m.end() : m.end() + 1] == ",":
        markup += _NBSP  # dodges a ReportLab quirk - see module docstring
    return markup


def to_markup(text: str) -> str:
    text = _MATH_RE.sub(lambda m: _replace_math(m, text), text)
    text = _VARIABLE_RE.sub(lambda m: f"<i>{m.group(0)}</i>", text)
    return text
