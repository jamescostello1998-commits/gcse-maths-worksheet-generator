import pytest

from app.bell_tasks.layout import (
    BOX_TO_ROW_COL,
    COLUMN_WIDTHS,
    EMU_PER_PT,
    GEOMETRY_YEAR_10,
    GEOMETRY_YEAR_11,
    ROW_HEIGHT,
    TABLE_LEFT,
    TABLE_TOP,
    box_bounds,
    cell_bounds,
    diagram_rect,
    estimate_text_line_count,
)

SHORT_PROMPT = "Find x."
# A real prompt (bar_chart_construct) that visibly overlapped a diagram placed
# at a fixed height fraction during manual visual QA in real PowerPoint,
# before this text-aware shrink/skip behaviour was added.
LONG_PROMPT = (
    "The table shows the day of the week absent of a group of students: "
    "Wed: 8, Mon: 20, Fri: 8. Draw a bar chart to show this information."
)

# app/pdf/diagrams.py's own default Drawing size (DIAGRAM_WIDTH/DIAGRAM_HEIGHT).
DEFAULT_NATIVE_SIZE = (200.0, 130.0)


def test_cell_bounds_col0_row0_matches_table_origin():
    left, top, width, height = cell_bounds(0, 0)
    assert (left, top) == (TABLE_LEFT, TABLE_TOP)
    assert width == COLUMN_WIDTHS[0]
    assert height == ROW_HEIGHT


def test_cell_bounds_row1_is_offset_by_one_row_height():
    top_row0 = cell_bounds(0, 1)[1]
    top_row1 = cell_bounds(1, 1)[1]
    assert top_row1 - top_row0 == ROW_HEIGHT


def test_cell_bounds_columns_are_contiguous_left_to_right():
    lefts = [cell_bounds(0, c)[0] for c in range(3)]
    widths = [cell_bounds(0, c)[2] for c in range(3)]
    assert lefts[1] == lefts[0] + widths[0]
    assert lefts[2] == lefts[1] + widths[1]


def test_cell_bounds_last_cell_reaches_table_right_and_bottom_edge():
    left, top, width, height = cell_bounds(1, 2)
    table_right = TABLE_LEFT + sum(COLUMN_WIDTHS)
    table_bottom = TABLE_TOP + 2 * ROW_HEIGHT
    assert left + width == table_right
    assert top + height == table_bottom


@pytest.mark.parametrize("row,col", [(r, c) for r in range(2) for c in range(3)])
def test_cell_bounds_rejects_out_of_range_not_this_one(row, col):
    # Every in-range (row, col) must succeed without raising.
    cell_bounds(row, col)


@pytest.mark.parametrize("row,col", [(-1, 0), (2, 0), (0, -1), (0, 3)])
def test_cell_bounds_rejects_out_of_range(row, col):
    with pytest.raises(ValueError):
        cell_bounds(row, col)


def test_box_bounds_matches_column_major_numbering():
    # Box 1 = row0/col0, box 2 = row1/col0, box 3 = row0/col1, ...
    for box, (row, col) in BOX_TO_ROW_COL.items():
        assert box_bounds(box) == cell_bounds(row, col)


def test_box_bounds_rejects_invalid_box_number():
    for bad_box in (0, 7, -1):
        with pytest.raises(ValueError):
            box_bounds(bad_box)


@pytest.mark.parametrize("row,col", [(r, c) for r in range(2) for c in range(3)])
def test_diagram_rect_stays_within_cell_bounds_for_a_short_prompt(row, col):
    cell_left, cell_top, cell_width, cell_height = cell_bounds(row, col)
    rect = diagram_rect(cell_bounds(row, col), SHORT_PROMPT, *DEFAULT_NATIVE_SIZE)
    assert rect is not None
    d_left, d_top, d_width, d_height = rect

    assert d_left >= cell_left
    assert d_top >= cell_top
    assert d_left + d_width <= cell_left + cell_width
    assert d_top + d_height <= cell_top + cell_height
    assert d_width > 0
    assert d_height > 0


def test_diagram_rect_sits_in_bottom_portion_of_cell_for_a_short_prompt():
    bounds = cell_bounds(0, 1)
    _cell_left, cell_top, _cell_width, cell_height = bounds
    _d_left, d_top, _d_width, _d_height = diagram_rect(bounds, SHORT_PROMPT, *DEFAULT_NATIVE_SIZE)
    # The picture's top edge should be at or below the cell's vertical midpoint.
    assert d_top >= cell_top + cell_height / 2


def test_diagram_rect_shrinks_for_a_longer_prompt():
    bounds = cell_bounds(0, 1)
    _l, _t, _w, short_height = diagram_rect(bounds, SHORT_PROMPT, *DEFAULT_NATIVE_SIZE)
    rect_long = diagram_rect(bounds, LONG_PROMPT, *DEFAULT_NATIVE_SIZE)
    assert rect_long is not None
    _l2, _t2, _w2, long_height = rect_long
    assert long_height < short_height


def test_diagram_rect_returns_none_when_prompt_leaves_no_room():
    bounds = cell_bounds(0, 1)
    absurdly_long_prompt = "word " * 200
    assert diagram_rect(bounds, absurdly_long_prompt, *DEFAULT_NATIVE_SIZE) is None


def test_diagram_rect_still_within_bounds_for_a_long_prompt():
    bounds = cell_bounds(0, 1)
    cell_left, cell_top, cell_width, cell_height = bounds
    rect = diagram_rect(bounds, LONG_PROMPT, *DEFAULT_NATIVE_SIZE)
    assert rect is not None
    d_left, d_top, d_width, d_height = rect
    assert d_left >= cell_left
    assert d_top >= cell_top
    assert d_left + d_width <= cell_left + cell_width
    assert d_top + d_height <= cell_top + cell_height


def test_diagram_rect_preserves_aspect_ratio_for_a_wide_short_diagram():
    bounds = cell_bounds(0, 1)
    native_width, native_height = 400.0, 100.0  # 4:1, unusually wide/short
    rect = diagram_rect(bounds, SHORT_PROMPT, native_width, native_height)
    assert rect is not None
    _left, _top, width, height = rect
    assert abs(width / height - native_width / native_height) < 0.01


def test_diagram_rect_preserves_aspect_ratio_for_a_tall_narrow_diagram():
    bounds = cell_bounds(0, 1)
    native_width, native_height = 100.0, 300.0  # 1:3, unusually tall/narrow
    rect = diagram_rect(bounds, SHORT_PROMPT, native_width, native_height)
    assert rect is not None
    _left, _top, width, height = rect
    assert abs(width / height - native_width / native_height) < 0.01


def test_diagram_rect_never_upscales_beyond_native_size():
    bounds = cell_bounds(0, 1)
    # A tiny native diagram, far smaller than the reserved zone - must not be
    # blown up past its own real resolution.
    native_width_pt, native_height_pt = 20.0, 15.0
    rect = diagram_rect(bounds, SHORT_PROMPT, native_width_pt, native_height_pt)
    assert rect is not None
    _left, _top, width, height = rect
    assert width <= native_width_pt * EMU_PER_PT
    assert height <= native_height_pt * EMU_PER_PT


def test_diagram_rect_centres_horizontally_within_the_cell():
    bounds = cell_bounds(0, 1)
    cell_left, _cell_top, cell_width, _cell_height = bounds
    # A diagram much narrower than the cell should be roughly centred, not
    # pinned to the left edge.
    rect = diagram_rect(bounds, SHORT_PROMPT, 60.0, 100.0)
    assert rect is not None
    left, _top, width, _height = rect
    left_gap = left - cell_left
    right_gap = (cell_left + cell_width) - (left + width)
    assert abs(left_gap - right_gap) < EMU_PER_PT * 2


def test_estimate_text_line_count_grows_with_prompt_length():
    bounds = cell_bounds(0, 1)
    cell_width = bounds[2]
    assert estimate_text_line_count(SHORT_PROMPT, cell_width) < estimate_text_line_count(
        LONG_PROMPT, cell_width
    )


# ---------------------------------------------------------------------------
# GEOMETRY_YEAR_11 (the 4x2, 8-box grid) - cell_bounds/box_bounds accept a
# geometry explicitly rather than relying on the Year 10 default.
# ---------------------------------------------------------------------------


def test_geometry_year_10_matches_the_original_bare_module_constants():
    # The bare TABLE_LEFT/TABLE_TOP/etc constants (kept for backward
    # compatibility - see the module docstring) must stay in sync with
    # GEOMETRY_YEAR_10, which every existing call site's default resolves to.
    assert GEOMETRY_YEAR_10.table_left == TABLE_LEFT
    assert GEOMETRY_YEAR_10.column_widths == COLUMN_WIDTHS
    assert GEOMETRY_YEAR_10.row_height == ROW_HEIGHT
    assert GEOMETRY_YEAR_10.box_to_row_col == BOX_TO_ROW_COL


def test_geometry_year_11_is_a_4_column_2_row_grid():
    assert GEOMETRY_YEAR_11.num_rows == 2
    assert GEOMETRY_YEAR_11.num_cols == 4
    assert len(GEOMETRY_YEAR_11.column_widths) == 4


def test_geometry_year_11_cell_bounds_col0_row0_matches_table_origin():
    left, top, width, height = cell_bounds(0, 0, GEOMETRY_YEAR_11)
    assert (left, top) == (GEOMETRY_YEAR_11.table_left, GEOMETRY_YEAR_11.table_top)
    assert width == GEOMETRY_YEAR_11.column_widths[0]
    assert height == GEOMETRY_YEAR_11.row_height


def test_geometry_year_11_cell_bounds_columns_are_contiguous_left_to_right():
    lefts = [cell_bounds(0, c, GEOMETRY_YEAR_11)[0] for c in range(4)]
    widths = [cell_bounds(0, c, GEOMETRY_YEAR_11)[2] for c in range(4)]
    for i in range(3):
        assert lefts[i + 1] == lefts[i] + widths[i]


def test_geometry_year_11_cell_bounds_last_cell_reaches_table_right_and_bottom_edge():
    left, top, width, height = cell_bounds(1, 3, GEOMETRY_YEAR_11)
    table_right = GEOMETRY_YEAR_11.table_left + sum(GEOMETRY_YEAR_11.column_widths)
    table_bottom = GEOMETRY_YEAR_11.table_top + 2 * GEOMETRY_YEAR_11.row_height
    assert left + width == table_right
    assert top + height == table_bottom


@pytest.mark.parametrize("row,col", [(-1, 0), (2, 0), (0, -1), (0, 4)])
def test_geometry_year_11_cell_bounds_rejects_out_of_range(row, col):
    with pytest.raises(ValueError):
        cell_bounds(row, col, GEOMETRY_YEAR_11)


def test_geometry_year_11_box_bounds_matches_row_major_numbering():
    for box, (row, col) in GEOMETRY_YEAR_11.box_to_row_col.items():
        assert box_bounds(box, GEOMETRY_YEAR_11) == cell_bounds(row, col, GEOMETRY_YEAR_11)


def test_geometry_year_11_box_bounds_rejects_invalid_box_number():
    for bad_box in (0, 9, -1):
        with pytest.raises(ValueError):
            box_bounds(bad_box, GEOMETRY_YEAR_11)


def test_geometry_year_11_box_bounds_defaults_to_year_10_geometry_when_omitted():
    # box_bounds(1) with no geometry arg must still mean Year 10's box 1 -
    # existing callers/tests never pass a geometry at all - and the two
    # templates' geometries are genuinely different (confirmed distinct row
    # heights), so this is a real behavioural check, not a coincidence.
    assert GEOMETRY_YEAR_10.row_height != GEOMETRY_YEAR_11.row_height
    assert box_bounds(1) == box_bounds(1, GEOMETRY_YEAR_10)
    assert box_bounds(1) != box_bounds(1, GEOMETRY_YEAR_11)
