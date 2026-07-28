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
"""

import atexit
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color

_FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
_FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

# Pixels rendered per PDF point (the PNG is supersampled at this scale, then
# displayed at 1/_SCALE its pixel size) - keeps the fraction crisp at normal
# print resolution (~288dpi) without the file size of a much higher scale.
_SCALE = 4

# Numerator/denominator digits are drawn smaller than the surrounding text -
# same scale diagrams.py's own vinculum helper (_draw_fraction) uses.
_DIGIT_SCALE = 0.72


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


def _render(num: str, den: str, font_size: float, bold: bool, color: Color) -> FractionImage:
    global _next_id
    font_path = _FONT_BOLD if bold else _FONT_REGULAR
    digit_px = round(font_size * _DIGIT_SCALE * _SCALE)
    font = ImageFont.truetype(font_path, digit_px)

    num_l, num_t, num_r, num_b = font.getbbox(num)
    den_l, den_t, den_r, den_b = font.getbbox(den)
    num_w, num_h = num_r - num_l, num_b - num_t
    den_w, den_h = den_r - den_l, den_b - den_t

    pad_px = round(2 * _SCALE)
    gap_px = round(1.5 * _SCALE)
    bar_thickness = max(1, round(0.9 * _SCALE))
    bar_w = max(num_w, den_w) + 2 * pad_px
    total_h = num_h + gap_px + bar_thickness + gap_px + den_h

    img = Image.new("RGBA", (bar_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgb = (round(color.red * 255), round(color.green * 255), round(color.blue * 255), 255)

    num_x = (bar_w - num_w) / 2 - num_l
    draw.text((num_x, -num_t), num, font=font, fill=rgb)

    bar_y = num_h + gap_px + bar_thickness / 2
    draw.line([(0, bar_y), (bar_w, bar_y)], fill=rgb, width=bar_thickness)

    den_x = (bar_w - den_w) / 2 - den_l
    den_y = num_h + gap_px + bar_thickness + gap_px
    draw.text((den_x, den_y - den_t), den, font=font, fill=rgb)

    path = os.path.join(_get_tmpdir(), f"frac_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return FractionImage(path=path, width_pt=bar_w / _SCALE, height_pt=total_h / _SCALE)
