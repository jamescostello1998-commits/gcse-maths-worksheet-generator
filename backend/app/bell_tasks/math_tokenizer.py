"""Splits a plain-ASCII question prompt (the same convention `app/pdf/mathtext.py`
already parses - bare `x`/`n` variables, `^n` exponents, `num/den` fractions,
`\\vec{a}`/`\\vec{b}` vector markers, plus digits/operators/currency/percent/degree
symbols) into an ordered list of tokens for building a Bell Tasks .pptx paragraph:

- `TextSpan` - plain text, rendered as a normal run in either "Calibri" (prose
  words) or "Cambria Math" (bare digits/operators/variables) - a literal
  per-token font switch, matching this feature's original design.
- `FractionSpan` / `ExponentSpan` / `FractionalExponentSpan` - structured
  math that gets rendered as a REAL native PowerPoint equation object (OMML,
  via `app/bell_tasks/omml.py`), not styled text - e.g. "3/4" becomes an
  actual stacked fraction, "x^2" an actual superscript, both fully editable
  in PowerPoint's own equation editor, confirmed by a direct spike (build a
  minimal `mc:AlternateContent`/`a14:m` XML fragment, open the saved file in
  real PowerPoint via COM automation, and look at the rendered result) before
  writing any of this module's logic.

Scope decision for exponents specifically: an exponent only gets promoted to
a true native superscript when its base is unambiguous - a bare digit run
(`10^-3`) or a single letter not itself preceded by another letter (`x^2`,
`n^2`, `f^-1`, `u^2`/`v^2` in a SUVAT context). Real generator output also
contains exponents whose "base" is a whole bracketed expression
(`(x - 3)^2`), a multi-letter identifier (`cos^-1`, `sin^-1`), or a run-
together coefficient-and-variable (`at^2`, meaning `a * t^2`, not `(at)^2`) -
correctly identifying the true base in those cases would need balanced-
parenthesis scanning or word-level disambiguation, a materially bigger and
more error-prone undertaking than this feature asked for. Those cases
deliberately fall back to the pre-existing plain "^n" inline-text rendering
(still Cambria Math-styled, just not a true superscript) rather than risk
mis-rendering an exponent on the wrong span of text.
"""

import re
from dataclasses import dataclass

FONT_WORDS = "Calibri"
FONT_MATH = "Cambria Math"


@dataclass(frozen=True)
class TextSpan:
    text: str
    font: str


@dataclass(frozen=True)
class FractionSpan:
    sign: str
    numerator: str
    denominator: str


@dataclass(frozen=True)
class ExponentSpan:
    base: str
    exponent: str


@dataclass(frozen=True)
class FractionalExponentSpan:
    base: str
    numerator: str
    denominator: str


Token = TextSpan | FractionSpan | ExponentSpan | FractionalExponentSpan

# A base is "unambiguous" only when it's a bare digit run or a single letter
# not itself preceded by another letter (see module docstring). The
# lookbehind on the letter alternative is what excludes the tail of a longer
# word/identifier (e.g. the "s" in "cos^-1", the "t" in "at^2").
_BASE = r"(?:(?<![A-Za-z])[A-Za-z]|\d+)"

_MATH_SPAN_RE = re.compile(
    r"\\vec\{(?P<vec>[ab])\}"
    r"|(?P<feb>" + _BASE + r")\^\((?P<fenum>-?\d+)/(?P<feden>-?\d+)\)"
    r"|(?P<eb>" + _BASE + r")\^(?P<exp>-?\d+)"
    r"|\^\(-?\d+/-?\d+\)"
    r"|\^-?\d+"
    r"|(?<!\u221a)(?P<fsign>-?)(?P<fnum>\d+)/(?P<fden>\d+)"
    r"|(?<![A-Za-z])[xn](?![A-Za-z])"
    r"|\u00a3?-?\d+(?:\.\d+)?%?\u00b0?"
    r"|-(?![A-Za-z])"
    r"|[+=\u00d7\u00f7\u2264\u2265\u03c0\u221a]"
)


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    for m in _MATH_SPAN_RE.finditer(text):
        if m.start() > pos:
            tokens.append(TextSpan(text[pos : m.start()], FONT_WORDS))

        if m.group("vec") is not None:
            tokens.append(TextSpan(m.group("vec"), FONT_MATH))
        elif m.group("feb") is not None:
            tokens.append(FractionalExponentSpan(m.group("feb"), m.group("fenum"), m.group("feden")))
        elif m.group("eb") is not None:
            tokens.append(ExponentSpan(m.group("eb"), m.group("exp")))
        elif m.group("fnum") is not None:
            tokens.append(FractionSpan(m.group("fsign") or "", m.group("fnum"), m.group("fden")))
        else:
            tokens.append(TextSpan(m.group(0), FONT_MATH))

        pos = m.end()
    if pos < len(text):
        tokens.append(TextSpan(text[pos:], FONT_WORDS))
    return tokens
