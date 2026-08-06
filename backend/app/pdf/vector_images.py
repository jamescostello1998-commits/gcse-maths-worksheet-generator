"""Renders a column vector, e.g. "(2, 3)" -> a real two-row bracket notation
(two stacked numbers enclosed in a single pair of tall round brackets), as a
small transparent PNG for embedding inline in ReportLab Paragraph markup via
`<img>` - the same rationale and architecture as `fraction_images.py`/
`radical_images.py`: Paragraph markup has no tag for "two stacked rows inside
one shared bracket", and ReportLab's own vector-to-bitmap rasteriser
(`renderPM`) isn't installed here, so PIL draws it directly instead.

The brackets themselves are real "(" / ")" glyphs from the same TrueType font
already used elsewhere in this app, rendered at a larger point size chosen so
the glyph's own ink height spans the two stacked numbers (plus a little
overhang, matching real typeset bracket notation) - not hand-drawn curves.
This mirrors how `mathtext.py` already reuses ordinary font glyphs wherever
possible (e.g. the plain Unicode "√"/"°" characters) rather than building new
vector-drawing code for shapes a font can already produce; a glyph scales
cleanly to any height needed, so no curve-fitting logic is needed here.

Results are cached in memory (keyed by every visual parameter) and written
once per unique (top, bottom) pair to a per-process temp directory, mirroring
`fraction_images.py`'s own cache/tempdir precedent.
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

# Pixels rendered per PDF point - same supersampling precedent as
# fraction_images.py/radical_images.py.
_SCALE = 4

# Numerator/denominator-style rows are drawn smaller than the surrounding
# text, same precedent as fraction_images.py's own _DIGIT_SCALE - keeps the
# whole two-row image close enough to a single line's own leading that it
# doesn't need special-cased paragraph spacing wherever it's used inline.
_DIGIT_SCALE = 0.72

# Vertical gap between the two stacked numbers, and how much taller than the
# stacked numbers the bracket glyphs stand (top+bottom overhang combined),
# both as fractions of one digit-row's own height - confirmed by a real
# rendered-PDF spike before shipping (see chronology).
_ROW_GAP_SCALE = 0.22
_BRACKET_OVERHANG_SCALE = 0.18
# Horizontal breathing room between each bracket's own ink and the number
# stack, as a fraction of the font size.
_BRACKET_GAP_SCALE = 0.2


@dataclass(frozen=True)
class ColumnVectorImage:
    path: str
    width_pt: float
    height_pt: float


_cache: dict[tuple, ColumnVectorImage] = {}
_tmpdir: Optional[str] = None
_next_id = 0


def _get_tmpdir() -> str:
    global _tmpdir
    if _tmpdir is None:
        _tmpdir = tempfile.mkdtemp(prefix="gcse_vectors_")
        atexit.register(shutil.rmtree, _tmpdir, ignore_errors=True)
    return _tmpdir


def get_column_vector_image(top: str, bottom: str, font_size: float, bold: bool, color: Color) -> ColumnVectorImage:
    key = (top, bottom, round(font_size, 2), bold, round(color.red, 4), round(color.green, 4), round(color.blue, 4))
    cached = _cache.get(key)
    if cached is not None:
        return cached
    image = _render(top, bottom, font_size, bold, color)
    _cache[key] = image
    return image


def _extent(font, text: str) -> tuple[float, int, int, int]:
    """Return (advance width, left, top, bottom) for `text` via font.getbbox,
    assuming it's drawn at origin (0, 0)."""
    left, top, right, bottom = font.getbbox(text)
    return right - left, left, top, bottom


def _render(top: str, bottom: str, font_size: float, bold: bool, color: Color) -> ColumnVectorImage:
    global _next_id
    font_path = _FONT_BOLD if bold else _FONT_REGULAR
    digit_px = round(font_size * _DIGIT_SCALE * _SCALE)
    font = ImageFont.truetype(font_path, digit_px)

    top_w, top_l, top_t, top_b = _extent(font, top)
    bot_w, bot_l, bot_t, bot_b = _extent(font, bottom)
    top_h, bot_h = top_b - top_t, bot_b - bot_t

    gap_px = round(digit_px * _ROW_GAP_SCALE)
    stack_w = max(top_w, bot_w)
    stack_h = top_h + gap_px + bot_h
    total_h = round(stack_h * (1 + _BRACKET_OVERHANG_SCALE))
    overhang = (total_h - stack_h) / 2

    # Find a bracket point size whose own glyph ink height matches
    # `total_h` - font metrics scale linearly with point size, so one probe
    # render is enough to compute the right size directly.
    probe_px = digit_px
    _, _, probe_t, probe_b = _extent(font, "(")
    probe_h = probe_b - probe_t
    bracket_px = max(1, round(probe_px * total_h / probe_h))
    bracket_font = ImageFont.truetype(font_path, bracket_px)
    lp_w, lp_l, lp_t, lp_b = _extent(bracket_font, "(")
    rp_w, rp_l, rp_t, rp_b = _extent(bracket_font, ")")

    bracket_gap_px = round(digit_px * _BRACKET_GAP_SCALE)
    total_w = round(lp_w + bracket_gap_px + stack_w + bracket_gap_px + rp_w)

    img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgb = (round(color.red * 255), round(color.green * 255), round(color.blue * 255), 255)

    stack_x = lp_w + bracket_gap_px
    draw.text((stack_x + (stack_w - top_w) / 2 - top_l, overhang - top_t), top, font=font, fill=rgb)
    draw.text(
        (stack_x + (stack_w - bot_w) / 2 - bot_l, overhang + top_h + gap_px - bot_t),
        bottom, font=font, fill=rgb,
    )

    bracket_y = (total_h - (lp_b - lp_t)) / 2
    draw.text((-lp_l, bracket_y - lp_t), "(", font=bracket_font, fill=rgb)
    draw.text((total_w - rp_w - rp_l, bracket_y - rp_t), ")", font=bracket_font, fill=rgb)

    path = os.path.join(_get_tmpdir(), f"vec_{_next_id}.png")
    _next_id += 1
    img.save(path)

    return ColumnVectorImage(path=path, width_pt=total_w / _SCALE, height_pt=total_h / _SCALE)
