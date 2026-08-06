"""Renders a recurring decimal with true dot marks over the repeating
digit(s) - the standard UK GCSE convention (a single dot over a lone
repeating digit, e.g. "0.3" with a dot over the 3; a dot over BOTH the first
and last digit of a longer repeating block, e.g. "0.142857" with dots over
the first "4" and the last "7") - as a small transparent PNG, for embedding
inline in ReportLab Paragraph markup via `<img>`. Mirrors
`app/pdf/fraction_images.py`/`app/pdf/radical_images.py`'s approach and for
the same reason: no Paragraph markup tag can place a mark above an arbitrary
character.

Rendered as ONE flat image covering the whole "prefix + block" digit string
(not built by compositing separate glyphs via Paragraph markup), since
placing the dot(s) accurately requires measuring each digit's own on-canvas
position - simplest and most robust done in a single PIL pass, exactly like
the other two image renderers in this package.

Results are cached in memory and written once per unique (prefix, block)
combination to a per-process temp directory - same precedent as
`fraction_images.py`/`radical_images.py`.
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

_SCALE = 4


@dataclass(frozen=True)
class RecurringDecimalImage:
    path: str
    width_pt: float
    height_pt: float


_cache: dict[tuple, RecurringDecimalImage] = {}
_tmpdir: Optional[str] = None
_next_id = 0


def _get_tmpdir() -> str:
    global _tmpdir
    if _tmpdir is None:
        _tmpdir = tempfile.mkdtemp(prefix="gcse_recurring_")
        atexit.register(shutil.rmtree, _tmpdir, ignore_errors=True)
    return _tmpdir


def get_recurring_decimal_image(
    prefix: str, block: str, font_size: float, bold: bool, color: Color
) -> RecurringDecimalImage:
    if not block:
        raise ValueError("get_recurring_decimal_image requires a non-empty recurring block")
    key = (prefix, block, round(font_size, 2), bold, round(color.red, 4), round(color.green, 4), round(color.blue, 4))
    cached = _cache.get(key)
    if cached is not None:
        return cached
    image = _render(prefix, block, font_size, bold, color)
    _cache[key] = image
    return image


def _render(prefix: str, block: str, font_size: float, bold: bool, color: Color) -> RecurringDecimalImage:
    global _next_id
    font_path = _FONT_BOLD if bold else _FONT_REGULAR
    digit_px = round(font_size * _SCALE)
    font = ImageFont.truetype(font_path, digit_px)

    full_text = prefix + block
    l, t, r, b = font.getbbox(full_text)
    text_w, text_h = r - l, b - t
    rgb = (round(color.red * 255), round(color.green * 255), round(color.blue * 255), 255)

    dot_r = max(1, round(font_size * 0.06 * _SCALE))
    dot_gap = round(font_size * 0.10 * _SCALE)
    top_pad = dot_r * 2 + dot_gap

    img = Image.new("RGBA", (text_w, text_h + top_pad), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-l, top_pad - t), full_text, font=font, fill=rgb)

    def digit_center_x(index: int) -> float:
        before = font.getlength(full_text[:index])
        this_w = font.getlength(full_text[index])
        return before - l + this_w / 2

    block_start_idx = len(prefix)
    block_end_idx = len(full_text) - 1
    dot_indices = [block_start_idx] if len(block) == 1 else [block_start_idx, block_end_idx]

    dot_y = dot_r
    for idx in dot_indices:
        cx = digit_center_x(idx)
        draw.ellipse([cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r], fill=rgb)

    path = os.path.join(_get_tmpdir(), f"recur_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return RecurringDecimalImage(path=path, width_pt=img.width / _SCALE, height_pt=img.height / _SCALE)
