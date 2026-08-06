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

**Numerator/denominator text is scanned for four special token kinds before
falling back to plain text**, since this content is raw PIL text with no
Paragraph-markup interpretation at all (see mathtext.py's docstring) - a
generator whose fraction content needs a subscript, a variable, an exponent,
or a radical still has to get it here, not in mathtext.py, which never sees
this text (it's already extracted into an opaque placeholder before
mathtext.py's own regexes run). All four are tried in one combined
`_TOKEN_RE` alternation (xn first, then a bare variable, then an exponent
suffix, then a radical) so each span is claimed by exactly one token kind,
never re-scanned:

1. **A literal "x_n" (optionally with a trailing "^digits")** is drawn as a
   real subscript (and superscript) - needed for `iteration.py`'s
   recurrence-formula fractions (e.g. numerator "a - x_n^2", denominator
   "x_n + b"). Matches this one specific token deliberately narrowly - only
   the literal substring "x_n" - so it doesn't touch any *other* topic's
   fraction content with an unrelated "^" in it. Drawn with the "x" in the
   same italic font mathtext.py uses for variables elsewhere (a font
   mismatch against the surrounding plain-Arial digits, invisible at this
   size) and the "n"/exponent smaller and offset.

2. **A bare "x" or "n"** (word-boundary-protected, mirroring mathtext.py's own
   `_VARIABLE_RE`) is drawn in the same italic font as "x_n"'s "x" - so a
   genuine variable inside a fraction (e.g. `algebraic_fractions_multiply_
   divide`'s "x^2 - d") is italicised consistently with how it renders
   everywhere else in the app. No other letter is italicised, matching
   mathtext.py's own "only x/n" convention.

3. **A bare "^exp" suffix** (e.g. the "^2" in "x^2", "t^2", "10^2", "(-2)^2")
   is drawn as a real raised, shrunk exponent - fixing a real gap where a
   bare "^" previously printed as a literal caret character inside a
   fraction, since this module never learned the "^" convention `mathtext.py`
   uses for ordinary prose text. Deliberately does **not** capture/re-draw
   its own base character (unlike an earlier version of this code, which
   only matched a single-character base and silently left a multi-character
   base like "10" or a parenthesised base like "(-2)" as a literal,
   unsuperscripted "^2" - found via a real rendered-PDF check, not a unit
   test written in advance) - the base is simply whatever plain (or
   variable-token) text already precedes it in the run, exactly matching
   how mathtext.py's own bare-exponent regex works in ordinary prose text.

4. **A radical "√digits"** (e.g. "√7", "√205.1") is drawn as a real hook +
   bar spanning the digits, mirroring `radical_images.py`'s geometry
   directly (not by pasting a separately-rendered image - keeping everything
   in one coordinate space avoids needing separate alignment/offset maths)
   - fixing a real gap where a bare "√" inside a `\frac{}{}` marker (e.g.
   `rationalise_denominator`'s "\frac{a}{√b}") previously rendered as a flat
   Arial glyph with no bar at all, a **deliberate prior decision**
   ("avoids recursive-rendering complexity") now revisited because the flat
   glyph reads ambiguously once a real bar is used everywhere else a radical
   appears.

`_measure_run`/`_run_extent`/`_draw_run` walk the numerator/denominator left
to right handling all four kinds, rather than measuring/drawing the whole
string as one plain `font.getbbox()`/`draw.text()` call the way a fraction
with no special tokens still does.
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

# A radical's own radicand is drawn less shrunk than plain fraction digits -
# radical_images.py's hook/bar geometry (mirrored here) needs real pixels to
# work with to stay a legible, smooth checkmark shape; at the full _DIGIT_SCALE
# reduction the hook degenerates into an illegible jagged scrawl (confirmed
# via a real rendered-PDF spike). A visibly-slightly-larger radicand than its
# surrounding fraction digits is the accepted trade-off.
_RAD_DIGIT_SCALE = 0.9

# Four token kinds, tried in this order within one combined alternation so
# each span is consumed exactly once (a later alternative never re-scans a
# span an earlier one already claimed): (1) "x_n"/"x_n^digits" - deliberately
# narrow, only this exact substring, tried first so its own trailing
# "^digits" is never re-claimed by the plain exponent-suffix alternative;
# (2) a bare "x"/"n" variable; (3) a bare "^exp" suffix (no base capture -
# see the module docstring for why); (4) a radical "√digits".
_XN_RE = re.compile(r"(?<![A-Za-z])x_n(?:\^(?P<sup>\d+))?(?![A-Za-z0-9])")
_VAR_RE = re.compile(r"(?<![A-Za-z])(?P<var>[xn])(?![A-Za-z0-9])")
_EXP_RE = re.compile(r"\^(?P<expval>-?\d+)")
_RADICAL_RE = re.compile(r"√(?P<radn>\d+(?:\.\d+)?)")

_TOKEN_RE = re.compile(
    f"(?P<xn>{_XN_RE.pattern})|(?:{_VAR_RE.pattern})|(?:{_EXP_RE.pattern})|(?:{_RADICAL_RE.pattern})"
)

# Subscript/superscript size, as a fraction of the base digit size, and their
# vertical offset (as a fraction of the base pixel size) - confirmed by a
# real rendered-PDF spike before shipping. Shared by the "x_n" subscript/
# superscript and the general "base^exp" exponent.
_SUB_SCALE = 0.62
_SUP_SCALE = 0.62
_SUB_DROP = 0.30
_SUP_RAISE = 0.38

# Radical hook/bar proportions, matching radical_images.py's own geometry -
# see that module's docstring for how these were chosen (proportional to the
# radicand's own digit height, verified by a real rendered-PDF spike).
_RAD_TICK_RATIO = 0.28
_RAD_TICK_DROP_RATIO = 0.22
_RAD_DIAG_RATIO = 0.42
_RAD_STROKE_RATIO = 0.12

# Absolute floors (raw supersampled pixels, i.e. _SCALE=4 per point) on the
# hook geometry - see _rad_geometry's docstring for why these are needed.
_RAD_MIN_TICK_W = round(2.5 * _SCALE)
_RAD_MIN_TICK_DROP = round(1.75 * _SCALE)
_RAD_MIN_DIAG_W = round(3.5 * _SCALE)
_RAD_MIN_STROKE = 2

# Extra vertical clearance (beyond the radical's own hook/bar geometry)
# between a fraction's main vinculum bar and a radical's own bar sitting
# directly below it, in whichever numerator/denominator run contains the
# radical - confirmed necessary by a real rendered spike (the two bars
# nearly touched without it).
_RAD_EXTRA_CLEARANCE = round(4 * _SCALE)


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


def _rad_geometry(rad_h: int) -> tuple[int, int, int, int]:
    """tick_w, tick_drop, diag_w, hook_w - proportional to this run's own
    radicand digit height, with a floor on each so the hook stays a
    legible, smooth checkmark shape even at the small sizes a fraction's
    numerator/denominator renders at (a radicand here is already shrunk by
    _DIGIT_SCALE - genuinely smaller than radical_images.py's own standalone
    use in normal prose text - confirmed via a real rendered-PDF spike that
    the un-floored proportions degenerate into a jagged, illegible mark at
    those sizes)."""
    tick_w = max(round(rad_h * _RAD_TICK_RATIO), _RAD_MIN_TICK_W)
    tick_drop = max(round(rad_h * _RAD_TICK_DROP_RATIO), _RAD_MIN_TICK_DROP)
    diag_w = max(round(rad_h * _RAD_DIAG_RATIO), _RAD_MIN_DIAG_W)
    return tick_w, tick_drop, diag_w, tick_w + diag_w


def _measure_run(font, x_font, sub_font, sup_font, rad_font, text: str) -> float:
    width = 0.0
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > pos:
            width += font.getlength(text[pos:m.start()])
        if m.group("xn"):
            width += x_font.getlength("x") + sub_font.getlength("n")
            if m.group("sup"):
                width += sup_font.getlength(m.group("sup"))
        elif m.group("var") is not None:
            width += x_font.getlength(m.group("var"))
        elif m.group("expval") is not None:
            width += sup_font.getlength(m.group("expval"))
        else:
            radn = m.group("radn")
            r_l, r_t, r_r, r_b = rad_font.getbbox(radn)
            rad_h = r_b - r_t
            _, _, _, hook_w = _rad_geometry(rad_h)
            pad_right = round(1.5 * _SCALE)
            overhang = round(1 * _SCALE)
            width += hook_w + (r_r - r_l) + pad_right + overhang
        pos = m.end()
    width += font.getlength(text[pos:])
    return width


def _run_extent(
    font, x_font, sub_font, sup_font, rad_font, text: str, sub_dy: int, sup_dy: int,
) -> tuple[float, int, int]:
    """Return (advance width, top, bottom) for `text`, in the same
    coordinate space as font.getbbox (used directly as pixel offsets by
    _render), accounting for any embedded x_n/variable/exponent/radical
    tokens."""

    def _plain(m: re.Match) -> str:
        if m.group("xn"):
            return "x"
        if m.group("var") is not None:
            return m.group("var")
        if m.group("expval") is not None:
            return ""
        return m.group("radn")

    plain_for_bbox = _TOKEN_RE.sub(_plain, text)
    _, top, _, bottom = font.getbbox(plain_for_bbox)
    for m in _TOKEN_RE.finditer(text):
        if m.group("xn"):
            _, sub_t, _, sub_b = sub_font.getbbox("n")
            bottom = max(bottom, sub_dy + sub_b)
            if m.group("sup"):
                _, sup_t, _, _ = sup_font.getbbox(m.group("sup"))
                top = min(top, sup_dy + sup_t)
        elif m.group("var") is not None:
            pass
        elif m.group("expval") is not None:
            _, sup_t, _, _ = sup_font.getbbox(m.group("expval"))
            top = min(top, sup_dy + sup_t)
        else:
            radn = m.group("radn")
            r_l, r_t, r_r, r_b = rad_font.getbbox(radn)
            rad_h = r_b - r_t
            _, tick_drop, _, _ = _rad_geometry(rad_h)
            pad_top = round(2 * _SCALE)
            # Extra headroom (beyond just fitting the hook/bar) so a
            # radical's own bar sits clearly separated from the fraction's
            # own vinculum bar directly above it, rather than nearly
            # touching it - confirmed via a real rendered spike.
            top = min(top, r_t - pad_top - _RAD_EXTRA_CLEARANCE)
            # The hook's lowest point overshoots tick_drop below the
            # digit's own ink-bottom - see _draw_run's matching comment.
            bottom = max(bottom, r_b + tick_drop)
    width = _measure_run(font, x_font, sub_font, sup_font, rad_font, text)
    return width, top, bottom


def _draw_run(
    draw, x0: float, y0: float, text: str, font, x_font, sub_font, sup_font, rad_font,
    sub_dy: int, sup_dy: int, fill,
) -> None:
    cursor = x0
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > pos:
            plain = text[pos:m.start()]
            draw.text((cursor, y0), plain, font=font, fill=fill)
            cursor += font.getlength(plain)
        if m.group("xn"):
            draw.text((cursor, y0), "x", font=x_font, fill=fill)
            cursor += x_font.getlength("x")
            draw.text((cursor, y0 + sub_dy), "n", font=sub_font, fill=fill)
            cursor += sub_font.getlength("n")
            if m.group("sup"):
                digits = m.group("sup")
                draw.text((cursor, y0 + sup_dy), digits, font=sup_font, fill=fill)
                cursor += sup_font.getlength(digits)
        elif m.group("var") is not None:
            var = m.group("var")
            draw.text((cursor, y0), var, font=x_font, fill=fill)
            cursor += x_font.getlength(var)
        elif m.group("expval") is not None:
            expval = m.group("expval")
            draw.text((cursor, y0 + sup_dy), expval, font=sup_font, fill=fill)
            cursor += sup_font.getlength(expval)
        else:
            radn = m.group("radn")
            r_l, r_t, r_r, r_b = rad_font.getbbox(radn)
            rad_h = r_b - r_t
            # Proportional to the radicand's own height, not a fixed
            # absolute value - a fixed stroke width looked disproportionately
            # thick/jagged at small radicands, confirmed via a real
            # rendered-PDF spike.
            stroke = max(_RAD_MIN_STROKE, round(rad_h * _RAD_STROKE_RATIO))
            tick_w, tick_drop, diag_w, hook_w = _rad_geometry(rad_h)
            pad_top = round(2 * _SCALE)
            pad_right = round(1.5 * _SCALE)
            bar_y = y0 + r_t - pad_top
            # The hook's lowest point sits below the digit's own ink-bottom
            # (pad_top + rad_h below the bar), not just `tick_drop` below the
            # bar itself - matching radical_images.py's "content_h + tick_drop"
            # geometry (content_h = rad_h + pad_top). Missing the "content_h"
            # term here previously made the hook collapse to a tiny sliver
            # instead of spanning the digit's full height, confirmed via a
            # real rendered-PDF spike compared side-by-side against
            # radical_images.py's own (correctly-proportioned) output.
            bottom_y = bar_y + pad_top + rad_h + tick_drop
            mid_y = bottom_y - tick_drop // 2
            bar_end_x = cursor + hook_w + (r_r - r_l) + pad_right
            draw.line(
                [(cursor, mid_y), (cursor + tick_w, bottom_y), (cursor + hook_w, bar_y)],
                fill=fill, width=stroke, joint="curve",
            )
            draw.line([(cursor + hook_w, bar_y), (bar_end_x, bar_y)], fill=fill, width=stroke)
            draw.text((cursor + hook_w + pad_right / 2 - r_l, y0), radn, font=rad_font, fill=fill)
            cursor = bar_end_x + round(1 * _SCALE)
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
    rad_font = ImageFont.truetype(font_path, round(font_size * _RAD_DIGIT_SCALE * _SCALE))
    sub_dy = round(digit_px * _SUB_DROP)
    sup_dy = -round(digit_px * _SUP_RAISE)

    num_w_raw, num_t, num_b = _run_extent(font, x_font, sub_font, sup_font, rad_font, num, sub_dy, sup_dy)
    den_w_raw, den_t, den_b = _run_extent(font, x_font, sub_font, sup_font, rad_font, den, sub_dy, sup_dy)
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
    _draw_run(draw, num_x, -num_t, num, font, x_font, sub_font, sup_font, rad_font, sub_dy, sup_dy, rgb)

    bar_y = num_h + gap_px + bar_thickness / 2
    draw.line([(0, bar_y), (bar_w, bar_y)], fill=rgb, width=bar_thickness)

    den_x = (bar_w - den_w) / 2
    den_y = num_h + gap_px + bar_thickness + gap_px
    _draw_run(draw, den_x, den_y - den_t, den, font, x_font, sub_font, sup_font, rad_font, sub_dy, sup_dy, rgb)

    path = os.path.join(_get_tmpdir(), f"frac_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return FractionImage(path=path, width_pt=bar_w / _SCALE, height_pt=total_h / _SCALE)
