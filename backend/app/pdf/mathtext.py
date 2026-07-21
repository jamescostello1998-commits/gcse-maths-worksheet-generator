"""Centralised plain-text -> ReportLab Paragraph markup conversion for maths
text (question prompts, solution steps, final answers).

Topic generators emit plain text like "3x^2 + 5", "10^-3" or "3/4" using an
ASCII convention (bare 'x'/'n' for algebraic variables, '^n' for exponents,
"num/den" for fractions) so they stay easy to write, verify, and unit-test.
`to_markup` is applied once, centrally, at PDF-render time to turn that into
real typesetting: x and n are italicised, '^n' becomes a superscript, and a
fraction gets its numerator raised/denominator lowered (e.g. "3/4" ->
3-raised / 4-lowered) rather than sitting inline on the baseline. Any future
topic that follows the same ASCII convention gets correct typesetting for
free.

Only x and n are italicised (not a, b, or other letters) - see CLAUDE.md for
why a blanket rule can't safely cover every single-letter variable (e.g. "a"
collides constantly with the English indefinite article).

Fractions here use ReportLab's native <super>/<sub> markup, not a true
stacked vinculum (numerator over a horizontal line over denominator) - a real
vinculum can't be built from Paragraph markup alone (ReportLab's inline <img>
tag only accepts a file-path string, and this environment has no working
image-rasterisation backend), so it would need PNGs rendered to temp files
via a hardcoded font path. See app/pdf/diagrams.py's `_draw_fraction` for the
real vinculum used in diagram labels, where the diagram is already being
drawn as vector shapes and no such workaround is needed.

**ReportLab quirk**: a comma immediately after a closing `</sub>` with no
space in between renders raised and glued to the preceding digit instead of
sitting on the baseline (verified in isolation - periods, colons, semicolons,
question marks and closing parens in the same position are all unaffected,
as is a comma after `</super>`; only sub+comma with zero gap breaks). Since
every fraction here ends in `</sub>`, and prose text often follows a fraction
straight with a comma (e.g. "...= 20/90, 2/9..."), `to_markup` inserts a
non-breaking space (u+00a0) before such a comma to dodge it.
"""

import re

_EXPONENT_RE = re.compile(r"\^(-?\d+)")
# Matches a lone x or n not glued to another letter (so "box" or "and" are
# left alone) - single pass over the original text so italicising one
# variable can never change what the other one sees as its neighbour.
_VARIABLE_RE = re.compile(r"(?<![A-Za-z])[xn](?![A-Za-z])")
_FRACTION_RE = re.compile(r"(-?)(\d+)/(\d+)")

_NBSP = " "


def _replace_fraction(m: re.Match, text: str) -> str:
    sign, num, den = m.groups()
    markup = f"{sign}<super>{num}</super>/<sub>{den}</sub>"
    if text[m.end() : m.end() + 1] == ",":
        markup += _NBSP  # dodges a ReportLab quirk - see module docstring
    return markup


def to_markup(text: str) -> str:
    text = _FRACTION_RE.sub(lambda m: _replace_fraction(m, text), text)
    text = _EXPONENT_RE.sub(lambda m: f"<super>{m.group(1)}</super>", text)
    text = _VARIABLE_RE.sub(lambda m: f"<i>{m.group(0)}</i>", text)
    return text
