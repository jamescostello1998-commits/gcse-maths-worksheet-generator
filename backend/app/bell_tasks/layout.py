"""EMU geometry for the Bell Tasks template's 3x2 question grid.

All numbers below are read directly from `assets/bell_task_template.pptx`'s own
table graphic frame (confirmed via python-pptx: `left=331769, top=2722277,
width=11548782, height=3937202`; 3 columns of widths `3442393, 4053195,
4053194`; 2 rows, each height `1968601`) - not guessed, transcribed from the
real template so a picture placed via these helpers lines up with the actual
cell boundaries PowerPoint will render.

Box numbering is column-major, matching the template's own existing "1."/"3."/
"5." (row 0) / "2."/"4."/"6." (row 1) cell content: box 1 is (row 0, col 0),
box 2 is (row 1, col 0), box 3 is (row 0, col 1), and so on.
"""

import math

TABLE_LEFT = 331769
TABLE_TOP = 2722277
COLUMN_WIDTHS = (3442393, 4053195, 4053194)
ROW_HEIGHT = 1968601
NUM_ROWS = 2
NUM_COLS = 3

BOX_TO_ROW_COL = {
    1: (0, 0),
    2: (1, 0),
    3: (0, 1),
    4: (1, 1),
    5: (0, 2),
    6: (1, 2),
}

# How much of a cell's height/width to reserve for an embedded diagram picture,
# and the margin kept clear around it so it never touches the cell's own grid
# lines. A starting point, not a final answer - refined after the first real
# visual check in PowerPoint found a genuine overlap (see `diagram_rect` below).
DIAGRAM_HEIGHT_FRACTION = 0.45
MARGIN_X = 91440  # 0.1 inch
MARGIN_Y = 45720  # 0.05 inch

EMU_PER_PT = 12700
EMU_PER_INCH = 914400
FONT_SIZE_PT = 18.0
# Calibri's average glyph width at a given point size is roughly half its
# point size in points - a standard typesetting rule of thumb, not measured
# per-glyph (good enough for a soft "will this prompt need N lines?" estimate,
# not for exact text layout).
_AVG_CHAR_WIDTH_PT = FONT_SIZE_PT * 0.52
_LINE_HEIGHT_EMU = int(FONT_SIZE_PT * 1.2 * EMU_PER_PT)
# Below this, a diagram thumbnail is too small to be legible - skip it for
# that one question rather than render an illegible sliver.
MIN_DIAGRAM_HEIGHT_EMU = int(0.3 * EMU_PER_INCH)


def _column_left(col: int) -> int:
    return TABLE_LEFT + sum(COLUMN_WIDTHS[:col])


def cell_bounds(row: int, col: int) -> tuple[int, int, int, int]:
    """Returns (left, top, width, height) in EMU for a given (row, col) cell."""
    if row not in range(NUM_ROWS) or col not in range(NUM_COLS):
        raise ValueError(f"cell ({row}, {col}) is out of range for a {NUM_ROWS}x{NUM_COLS} grid")
    left = _column_left(col)
    top = TABLE_TOP + row * ROW_HEIGHT
    width = COLUMN_WIDTHS[col]
    return left, top, width, ROW_HEIGHT


def estimate_text_line_count(prompt: str, cell_width: int) -> int:
    """Rough estimate of how many wrapped lines `prompt` needs at 18pt Calibri
    in a box `cell_width` EMU wide - not exact text layout, just enough to
    decide whether a diagram thumbnail has real room left underneath it."""
    chars_per_line = max(1, int((cell_width / EMU_PER_PT) / _AVG_CHAR_WIDTH_PT))
    return max(1, math.ceil(len(prompt) / chars_per_line))


def diagram_rect(
    bounds: tuple[int, int, int, int],
    prompt: str,
    native_width_pt: float,
    native_height_pt: float,
) -> tuple[int, int, int, int] | None:
    """Returns (left, top, width, height) in EMU for a picture placed in the
    bottom portion of the given cell bounds, sized to preserve the diagram's
    own true proportions - or `None` if `prompt` is estimated to need so many
    wrapped lines that no legible diagram would fit underneath it without
    overlapping the text.

    A first visual check in real PowerPoint (see CLAUDE.md's own "render and
    look closely" precedent for every diagram kind this project has added)
    found a genuine overlap: a long, data-listing prompt (e.g. a bar-chart
    "construct" question spelling out several category:value pairs) wrapped
    to 4 lines and ran straight into a diagram placed at a fixed height
    fraction with no regard for how much text sat above it. This estimates
    the text's own height first and shrinks - or, below a legible minimum,
    entirely omits - the diagram to make genuine room for it, rather than
    always reserving the same fixed fraction regardless of prompt length.

    A second real bug, found via user report after that fix shipped: this
    function used to compute a (width, height) box from the cell alone and
    hand both dimensions straight to `add_picture`, which does not preserve
    an image's own aspect ratio when both dimensions are given explicitly -
    it stretches the image to fill whatever box it's told, regardless of
    the diagram's real shape. Since diagram kinds vary in native proportions
    (`app/pdf/diagrams.py`'s `Drawing` width/height differ per kind - not
    always the module's own `DIAGRAM_WIDTH`/`DIAGRAM_HEIGHT` defaults), this
    visibly squashed diagrams flat. Fixed by treating the cell-derived box as
    a maximum bounding area only, then scaling the diagram's own
    `native_width_pt`/`native_height_pt` down (never up) to the largest size
    that fits inside it without distortion - the diagram may end up smaller
    than the old behaviour's box, but never stretched."""
    cell_left, cell_top, cell_width, cell_height = bounds

    # +1 line of headroom on top of the raw estimate: word-wrap boundaries
    # (and this project's own average-glyph-width approximation) can legitimately
    # run a touch longer than predicted, and a diagram sitting flush against the
    # last line of text reads as cramped even when it technically doesn't overlap.
    lines = estimate_text_line_count(prompt, cell_width) + 1
    text_height = lines * _LINE_HEIGHT_EMU + MARGIN_Y
    available_height = cell_height - text_height - MARGIN_Y

    default_height = int(cell_height * DIAGRAM_HEIGHT_FRACTION) - MARGIN_Y
    max_height = min(default_height, available_height)
    if max_height < MIN_DIAGRAM_HEIGHT_EMU:
        return None
    max_width = cell_width - 2 * MARGIN_X

    native_width_emu = native_width_pt * EMU_PER_PT
    native_height_emu = native_height_pt * EMU_PER_PT
    scale = min(max_width / native_width_emu, max_height / native_height_emu, 1.0)
    width = int(native_width_emu * scale)
    height = int(native_height_emu * scale)

    # Centred horizontally within the available width, flush to the bottom of
    # the reserved zone (matching the original bottom-anchored placement).
    left = cell_left + MARGIN_X + (max_width - width) // 2
    top = cell_top + cell_height - height - MARGIN_Y
    return left, top, width, height


def box_bounds(box: int) -> tuple[int, int, int, int]:
    """Convenience wrapper: cell_bounds for a 1-based box number (1-6)."""
    if box not in BOX_TO_ROW_COL:
        raise ValueError(f"box must be 1-6, got {box}")
    row, col = BOX_TO_ROW_COL[box]
    return cell_bounds(row, col)
