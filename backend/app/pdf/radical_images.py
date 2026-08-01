"""Renders a true full-length radical sign (a hook plus a horizontal bar
spanning the whole radicand, e.g. "\u221a72" with the bar over "72") as a
small transparent PNG, for embedding inline in ReportLab Paragraph markup via
`<img>`. Mirrors `app/pdf/fraction_images.py`'s approach and for the same
reason: Paragraph markup has no tag for "hook + bar over content", and
ReportLab's own image rasteriser (`renderPM`) isn't installed in this
environment - so PIL draws the hook/bar/digits directly onto a transparent
PNG instead, using the same TrueType font file `fraction_images.py` already
uses.

Only bare-digit radicands are supported (see `mathtext.py`'s `√(?P<radn>\\d+)`
regex) - a confirmed audit of every topic generator found no case of a
radical wrapping non-digit content (e.g. an unevaluated expression like
"√(k^2 × m)") that would need this treatment; those stay plain literal text,
unchanged from before this module existed.

Results are cached in memory (keyed by every visual parameter) and written
once per unique radical to a per-process temp directory - same caching
precedent as `fraction_images.py`, for the same reason (a radical like
"√5" recurs constantly across a worksheet's 20+ questions).
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

# Pixels rendered per PDF point - see fraction_images.py's identical constant.
_SCALE = 4

# Radicand digits are drawn smaller than the surrounding text, matching
# fraction_images.py's own numerator/denominator digit scale.
_DIGIT_SCALE = 0.72


@dataclass(frozen=True)
class RadicalImage:
    path: str
    width_pt: float
    height_pt: float


_cache: dict[tuple, RadicalImage] = {}
_tmpdir: Optional[str] = None
_next_id = 0


def _get_tmpdir() -> str:
    global _tmpdir
    if _tmpdir is None:
        _tmpdir = tempfile.mkdtemp(prefix="gcse_radicals_")
        atexit.register(shutil.rmtree, _tmpdir, ignore_errors=True)
    return _tmpdir


def get_radical_image(radicand: str, font_size: float, bold: bool, color: Color) -> RadicalImage:
    key = (radicand, round(font_size, 2), bold, round(color.red, 4), round(color.green, 4), round(color.blue, 4))
    cached = _cache.get(key)
    if cached is not None:
        return cached
    image = _render(radicand, font_size, bold, color)
    _cache[key] = image
    return image


def _render(radicand: str, font_size: float, bold: bool, color: Color) -> RadicalImage:
    global _next_id
    font_path = _FONT_BOLD if bold else _FONT_REGULAR
    digit_px = round(font_size * _DIGIT_SCALE * _SCALE)
    font = ImageFont.truetype(font_path, digit_px)

    r_l, r_t, r_r, r_b = font.getbbox(radicand)
    rad_w, rad_h = r_r - r_l, r_b - r_t
    rgb = (round(color.red * 255), round(color.green * 255), round(color.blue * 255), 255)

    stroke = max(1, round(0.9 * _SCALE))
    # Hook geometry, proportional to the radicand's own digit height - a
    # short downstroke ("tick") into a longer upstroke that meets the bar,
    # matching a real radical sign's shape (verified by spike render).
    tick_w = round(rad_h * 0.28)
    tick_drop = round(rad_h * 0.22)
    diag_w = round(rad_h * 0.42)
    pad_top = round(2 * _SCALE)
    pad_right = round(3 * _SCALE)
    overhang = round(1.5 * _SCALE)

    content_h = rad_h + pad_top
    bottom_y = content_h + tick_drop
    top_y = 0
    total_h = bottom_y + round(1 * _SCALE)

    hook_w = tick_w + diag_w
    bar_w = hook_w + rad_w + pad_right + overhang
    total_w = bar_w + round(1 * _SCALE)

    img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    mid_y = bottom_y - tick_drop // 2
    draw.line([(0, mid_y), (tick_w, bottom_y), (hook_w, top_y)], fill=rgb, width=stroke, joint="curve")
    draw.line([(hook_w, top_y), (bar_w, top_y)], fill=rgb, width=stroke)

    rad_x = hook_w + pad_right / 2 - r_l
    rad_y = pad_top - r_t
    draw.text((rad_x, rad_y), radicand, font=font, fill=rgb)

    path = os.path.join(_get_tmpdir(), f"radical_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return RadicalImage(path=path, width_pt=total_w / _SCALE, height_pt=total_h / _SCALE)
