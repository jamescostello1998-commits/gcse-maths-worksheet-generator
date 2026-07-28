"""Centralised plain-text -> ReportLab Paragraph markup conversion for maths
text (question prompts, solution steps, final answers).

Topic generators emit plain text like "3x^2 + 5", "10^-3", "3/4" or "x^(1/4)"
using an ASCII convention (bare 'x'/'n' for algebraic variables, '^n' for
exponents, '^(num/den)' for a fractional exponent, "num/den" for a standalone
fraction) so they stay easy to write, verify, and unit-test. `to_markup` is
applied once, centrally, at PDF-render time to turn that into real
typesetting: x and n are italicised, '^n' becomes a superscript, a fractional
exponent is raised as one flat "(num/den)" unit, and a standalone fraction is
drawn as a true stacked vinculum (numerator over a horizontal line over
denominator, e.g. "3/4" -> a small inline image) rather than sitting inline
on the baseline. Any future topic that follows the same ASCII convention gets
correct typesetting for free.

Only x and n are italicised (not a, b, or other letters) - see CLAUDE.md for
why a blanket rule can't safely cover every single-letter variable (e.g. "a"
collides constantly with the English indefinite article).

**Standalone fractions are rendered as a small PNG and embedded inline via
`<img>`** (app/pdf/fraction_images.py) - a true vinculum can't be built from
Paragraph markup alone (there's no tag for "numerator, rule, denominator"),
and ReportLab's own image rasteriser (`renderPM`, which could otherwise turn
a vector `Drawing` into an embeddable image) isn't installed in this
environment (needs Cairo bindings) - so PIL draws the digits and rule
directly onto a transparent-background PNG instead, using the same font
files ReportLab/Windows already use, cached per unique (num, den, size,
bold, colour) so a repeated fraction like "1/2" isn't re-rendered on every
occurrence. `to_markup` therefore needs the caller's font size/colour/weight
(the surrounding Paragraph style) to size and colour the image to match -
see the `font_size`/`color`/`bold` parameters. `valign="bottom"` on the
`<img>` tag was confirmed (by rendering real text side by side at several
valign values and comparing pixel-for-pixel) to align the fraction's own
"baseline" - the bottom of the denominator digits - with the surrounding
text's baseline, with no extra offset math needed. The leading sign of a
negative fraction (e.g. "-3/4") stays a plain baseline character before the
`<img>` tag - only the num/den/rule are drawn as one unit. See
app/pdf/diagrams.py's `_draw_fraction` for the same true-vinculum idea
applied to diagram labels, which draws directly as vector shapes instead
(diagrams don't have Paragraph markup's inline-image constraint).

A fractional *exponent* (e.g. "x^(1/4)") is deliberately typeset differently
from a standalone fraction: just one flat `<super>(1/4)</super>` rather than
a raised-numerator/lowered-denominator vinculum inside a superscript (which
would need a second, much smaller image glued inside the exponent - judged
not worth the complexity for what's already a compact, readable unit as
plain raised text).

All three numeric patterns (fractional exponent, integer exponent, standalone
fraction) are matched by ONE combined regex in a single `re.sub` pass, rather
than three separate sequential passes - a fractional exponent's raised
"(1/4)" would otherwise be a bare digit-slash-digit substring indistinguishable
from a standalone fraction, and a later, separate fraction pass would re-match
and re-process it (producing a broken doubly-nested result). Matching
everything in one pass means each character is claimed by exactly one
alternative and never re-scanned.

**Glyph gotcha**: the unicode division slash U+2215 ("∕") is NOT in Helvetica
either (renders as a missing-glyph box, same class of issue as the "⁻¹"
gotcha documented in CLAUDE.md) - a fractional exponent's "/" must stay a
plain ASCII slash.

**Surd-over-integer gotcha**: an exact trig value like "√2/2" or "√3/2" (see
exact_trig_values.py) is a single already-clear unit, deliberately written as
a flat literal string, not run through the standalone-fraction path - but the
fraction regex would otherwise still match the trailing "2/2"/"3/2" substring
regardless of the preceding "√", turning just the digits into a fraction
image and leaving a stray literal "√" in front (genuinely confusing, since it
reads as if the radical applies only to the numerator). Excluded via a
`(?<!√)` negative lookbehind on the fraction alternative, so any fraction
glued directly after a "√" is left untouched as plain text.
"""

import re

from reportlab.lib.colors import Color

from app.pdf.fraction_images import get_fraction_image

# Matches, in priority order within one alternation so each span is consumed
# exactly once: (1) a fractional exponent "^(num/den)", (2) a plain integer
# exponent "^n", (3) a standalone "num/den" fraction.
_MATH_RE = re.compile(
    r"\^\((?P<epnum>-?\d+)/(?P<epden>-?\d+)\)"
    r"|\^(?P<exp>-?\d+)"
    r"|(?<!√)(?P<fsign>-?)(?P<fnum>\d+)/(?P<fden>\d+)"
)
# Matches a lone x or n not glued to another letter (so "box" or "and" are
# left alone) - single pass over the original text so italicising one
# variable can never change what the other one sees as its neighbour.
_VARIABLE_RE = re.compile(r"(?<![A-Za-z])[xn](?![A-Za-z])")


def _replace_math(m: re.Match, font_size: float, color: Color, bold: bool) -> str:
    if m.group("epnum") is not None:
        return f"<super>({m.group('epnum')}/{m.group('epden')})</super>"
    if m.group("exp") is not None:
        return f"<super>{m.group('exp')}</super>"
    sign, num, den = m.group("fsign"), m.group("fnum"), m.group("fden")
    img = get_fraction_image(num, den, font_size, bold, color)
    return f'{sign}<img src="{img.path}" width="{img.width_pt:.2f}" height="{img.height_pt:.2f}" valign="bottom"/>'


def to_markup(text: str, *, font_size: float, color: Color, bold: bool = False) -> str:
    # Italicise x/n BEFORE substituting fractions/exponents, not after: a
    # standalone fraction is now replaced with an <img src="..."/> tag whose
    # file path is a randomly-named temp file (tempfile.mkdtemp), and that
    # random suffix can itself contain a bare "x" or "n" flanked by
    # non-letters (e.g. ".../gcse_fractions_k_x7ili6/frac_0.png") - running
    # _VARIABLE_RE afterward would re-scan and italicise part of the file
    # path, corrupting it (found via an actual end-to-end worksheet render,
    # not a unit test - the synthetic spike text never happened to produce a
    # matching random suffix). Doing the math substitution last means its
    # inserted markup is never re-scanned by anything else.
    text = _VARIABLE_RE.sub(lambda m: f"<i>{m.group(0)}</i>", text)
    text = _MATH_RE.sub(lambda m: _replace_math(m, font_size, color, bold), text)
    return text
