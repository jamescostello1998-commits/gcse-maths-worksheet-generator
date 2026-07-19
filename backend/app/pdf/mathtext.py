"""Centralised plain-text -> ReportLab Paragraph markup conversion for maths
text (question prompts, solution steps, final answers).

Topic generators emit plain text like "3x^2 + 5" or "10^-3" using an ASCII
convention (bare 'x' for the variable, '^n' for exponents) so they stay easy
to write, verify, and unit-test. `to_markup` is applied once, centrally, at
PDF-render time to turn that into real typesetting: the variable x is
italicised and '^n' becomes a superscript. Any future topic that follows the
same ASCII convention gets correct typesetting for free.
"""

import re

_EXPONENT_RE = re.compile(r"\^(-?\d+)")
_VARIABLE_RE = re.compile(r"(?<![A-Za-z])x(?![A-Za-z])")


def to_markup(text: str) -> str:
    text = _EXPONENT_RE.sub(lambda m: f"<super>{m.group(1)}</super>", text)
    text = _VARIABLE_RE.sub("<i>x</i>", text)
    return text
