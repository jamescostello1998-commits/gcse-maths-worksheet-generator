"""Renders a standalone "num/den" fraction as a small transparent PNG - a
real numerator/horizontal-bar/denominator vinculum - for embedding inline in
ReportLab Paragraph markup via `<img>`. Paragraph markup has no way to draw
this shape directly: ReportLab's own image rasteriser (`renderPM`, needed to
turn a vector `Drawing` into an `<img>`-embeddable file) isn't installed in
this environment (it needs Cairo bindings) - so PIL renders the glyphs
directly instead, using the same TrueType font files Windows/ReportLab
already use.

Results are cached in memory (keyed by every visual parameter) and written
once per unique fraction to a per-process temp directory, since the same
fraction (e.g. "1/2") recurs constantly across a worksheet's 20+ questions -
regenerating the PNG on every occurrence would be wasteful.

**A literal "x_n" (optionally with a trailing "^digits") inside the
numerator/denominator text is drawn as a real subscript (and superscript)**,
not literal underscore/caret characters - needed for `iteration.py`'s
recurrence-formula fractions (e.g. numerator "a - x_n^2", denominator
"x_n + b"), whose algebraic content forces them through the `\frac{}{}`
marker in the first place (see mathtext.py's docstring), which draws its
num/den as raw PIL text with no markup interpretation at all. `_XN_RE`
matches this one specific token deliberately narrowly - only the literal
substring "x_n" (never a bare "^digits" on its own) - so it can never touch
any *other* topic's existing `\frac{}{}` content (several other files use
this marker for fractions with a genuine "^" in them, e.g. a rearranged
formula in `changing_subject.py`, which must render completely unchanged).
`_measure_run`/`_draw_run` walk the numerator/denominator left to right,
drawing the "x" in the same italic font mathtext.py uses for variables
elsewhere (so it matches the rest of the app, even though the surrounding
digits/operators stay in plain Arial - a font mismatch invisible at this
size, and no other topic's fraction content contains a bare "x_n" for this
to affect) and the "n"/exponent smaller and offset, rather than measuring/
drawing the whole string as one plain `font.getbbox()`/`draw.text()` call
the way every other fraction still does.
"""

import atexit
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color

_FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
_FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
_FONT_ITALIC = r"C:\Windows\Fonts\timesi.ttf"
_FONT_BOLD_ITALIC = r"C:\Windows\Fonts\timesbi.ttf"

# Pixels rendered per PDF point (the PNG is supersampled at this scale, then
# displayed at 1/_SCALE its pixel size) - keeps the fraction crisp at normal
# print resolution (~288dpi) without the file size of a much higher scale.
_SCALE = 4

# Numerator/denominator digits are drawn smaller than the surrounding text -
# same scale diagrams.py's own vinculum helper (_draw_fraction) uses.
_DIGIT_SCALE = 0.72

# A literal "x_n" (optionally "x_n^<digits>") inside a numerator/denominator
# string - see the module docstring's final paragraph. Deliberately matches
# ONLY this one exact substring, never a bare "^digits" alone, so no other
# topic's existing fraction content is affected.
_XN_RE = re.compile(r"(?<![A-Za-z])x_n(?:\^(?P<sup>\d+))?(?![A-Za-z0-9])")

# Subscript/superscript size, as a fraction of the base digit size, and their
# vertical offset (as a fraction of the base pixel size) - confirmed by a
# real rendered-PDF spike before shipping.
_SUB_SCALE = 0.62
_SUP_SCALE = 0.62
_SUB_DROP = 0.30
_SUP_RAISE = 0.38


@dataclass(frozen=True)
class FractionImage:
    path: str
    width_pt: float
    height_pt: float


_cache: dict[tuple, FractionImage] = {}
_tmpdir: Optional[str] = None
_next_id = 0


def _get_tmpdir() -> str:
    global _tmpdir
    if _tmpdir is None:
        _tmpdir = tempfile.mkdtemp(prefix="gcse_fractions_")
        atexit.register(shutil.rmtree, _tmpdir, ignore_errors=True)
    return _tmpdir


def get_fraction_image(num: str, den: str, font_size: float, bold: bool, color: Color) -> FractionImage:
    key = (num, den, round(font_size, 2), bold, round(color.red, 4), round(color.green, 4), round(color.blue, 4))
    cached = _cache.get(key)
    if cached is not None:
        return cached
    image = _render(num, den, font_size, bold, color)
    _cache[key] = image
    return image


def _measure_run(font, x_font, sub_font, sup_font, text: str) -> float:
    width = 0.0
    pos = 0
    for m in _XN_RE.finditer(text):
        if m.start() > pos:
            width += font.getlength(text[pos:m.start()])
        width += x_font.getlength("x") + sub_font.getlength("n")
        if m.group("sup"):
            width += sup_font.getlength(m.group("sup"))
        pos = m.end()
    width += font.getlength(text[pos:])
    return width


def _run_extent(font, x_font, sub_font, sup_font, text: str, sub_dy: int, sup_dy: int) -> tuple[float, int, int]:
    """Return (advance width, top, bottom) for `text`, in the same
    coordinate space as font.getbbox (used directly as pixel offsets by
    _render), accounting for any embedded x_n/x_n^d run tokens."""
    plain_for_bbox = _XN_RE.sub("x", text)
    _, top, _, bottom = font.getbbox(plain_for_bbox)
    for m in _XN_RE.finditer(text):
        _, sub_t, _, sub_b = sub_font.getbbox("n")
        bottom = max(bottom, sub_dy + sub_b)
        if m.group("sup"):
            _, sup_t, _, _ = sup_font.getbbox(m.group("sup"))
            top = min(top, sup_dy + sup_t)
    width = _measure_run(font, x_font, sub_font, sup_font, text)
    return width, top, bottom


def _draw_run(draw, x0: float, y0: float, text: str, font, x_font, sub_font, sup_font, sub_dy: int, sup_dy: int, fill) -> None:
    cursor = x0
    pos = 0
    for m in _XN_RE.finditer(text):
        if m.start() > pos:
            plain = text[pos:m.start()]
            draw.text((cursor, y0), plain, font=font, fill=fill)
            cursor += font.getlength(plain)
        draw.text((cursor, y0), "x", font=x_font, fill=fill)
        cursor += x_font.getlength("x")
        draw.text((cursor, y0 + sub_dy), "n", font=sub_font, fill=fill)
        cursor += sub_font.getlength("n")
        if m.group("sup"):
            digits = m.group("sup")
            draw.text((cursor, y0 + sup_dy), digits, font=sup_font, fill=fill)
            cursor += sup_font.getlength(digits)
        pos = m.end()
    tail = text[pos:]
    if tail:
        draw.text((cursor, y0), tail, font=font, fill=fill)


def _render(num: str, den: str, font_size: float, bold: bool, color: Color) -> FractionImage:
    global _next_id
    font_path = _FONT_BOLD if bold else _FONT_REGULAR
    italic_path = _FONT_BOLD_ITALIC if bold else _FONT_ITALIC
    digit_px = round(font_size * _DIGIT_SCALE * _SCALE)
    font = ImageFont.truetype(font_path, digit_px)
    x_font = ImageFont.truetype(italic_path, digit_px)
    sub_font = ImageFont.truetype(italic_path, max(1, round(digit_px * _SUB_SCALE)))
    sup_font = ImageFont.truetype(font_path, max(1, round(digit_px * _SUP_SCALE)))
    sub_dy = round(digit_px * _SUB_DROP)
    sup_dy = -round(digit_px * _SUP_RAISE)

    num_w_raw, num_t, num_b = _run_extent(font, x_font, sub_font, sup_font, num, sub_dy, sup_dy)
    den_w_raw, den_t, den_b = _run_extent(font, x_font, sub_font, sup_font, den, sub_dy, sup_dy)
    num_w, num_h = round(num_w_raw), num_b - num_t
    den_w, den_h = round(den_w_raw), den_b - den_t

    pad_px = round(2 * _SCALE)
    gap_px = round(1.5 * _SCALE)
    bar_thickness = max(1, round(0.9 * _SCALE))
    bar_w = max(num_w, den_w) + 2 * pad_px
    total_h = num_h + gap_px + bar_thickness + gap_px + den_h

    img = Image.new("RGBA", (bar_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgb = (round(color.red * 255), round(color.green * 255), round(color.blue * 255), 255)

    num_x = (bar_w - num_w) / 2
    _draw_run(draw, num_x, -num_t, num, font, x_font, sub_font, sup_font, sub_dy, sup_dy, rgb)

    bar_y = num_h + gap_px + bar_thickness / 2
    draw.line([(0, bar_y), (bar_w, bar_y)], fill=rgb, width=bar_thickness)

    den_x = (bar_w - den_w) / 2
    den_y = num_h + gap_px + bar_thickness + gap_px
    _draw_run(draw, den_x, den_y - den_t, den, font, x_font, sub_font, sup_font, sub_dy, sup_dy, rgb)

    path = os.path.join(_get_tmpdir(), f"frac_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return FractionImage(path=path, width_pt=bar_w / _SCALE, height_pt=total_h / _SCALE)
