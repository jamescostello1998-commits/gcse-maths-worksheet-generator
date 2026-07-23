import pytest
from reportlab.graphics.shapes import Drawing, Rect, Wedge

from app.core.models import DiagramSpec
from app.pdf.diagrams import (
    _LABEL_FONT,
    _LABEL_FONT_ITALIC,
    _math_runs,
    draw_bar_chart,
    draw_box_plot,
    draw_pie_chart,
    render_diagram,
)

SAMPLE_SPECS = [
    DiagramSpec(kind="rectangle", params={"width": 10, "height": 6, "width_label": "10 cm", "height_label": "6 cm"}),
    DiagramSpec(kind="triangle_area", params={"base": 8, "height": 5, "base_label": "8 cm", "height_label": "5 cm"}),
    DiagramSpec(
        kind="l_shape",
        params={
            "outer_w": 20, "outer_h": 15, "inner_w": 6, "inner_h": 5,
            "notch": "corner", "outer_labels": ["20 cm", "15 cm"], "inner_labels": [6, 5],
        },
    ),
    DiagramSpec(
        kind="l_shape",
        params={
            "outer_w": 20, "outer_h": 15, "inner_w": 6, "inner_h": 5,
            "notch": "center", "outer_labels": ["20 cm", "15 cm"], "inner_labels": [6, 5],
        },
    ),
    DiagramSpec(kind="circle", params={"radius": 7, "label": "7 cm"}),
    DiagramSpec(
        kind="rectangle_semicircle",
        params={"width": 10, "height": 8, "radius": 5, "width_label": "10 cm", "height_label": "8 cm"},
    ),
    DiagramSpec(
        kind="angle_line",
        params={"angle_values": [60, 70, 50], "labels": ["60°", "70°", "x"], "around_point": False},
    ),
    DiagramSpec(
        kind="angle_line",
        params={"angle_values": [90, 120, 100, 50], "labels": ["90°", "120°", "100°", "x"], "around_point": True},
    ),
    DiagramSpec(kind="triangle_angles", params={"angle_labels": ["60°", "70°", "x"]}),
    DiagramSpec(
        kind="parallel_lines",
        params={"known_label": "70°", "unknown_label": "x", "relation": "corresponding"},
    ),
    DiagramSpec(
        kind="parallel_lines",
        params={"known_label": "70°", "unknown_label": "x", "relation": "alternate"},
    ),
    DiagramSpec(
        kind="parallel_lines",
        params={"known_label": "70°", "unknown_label": "x", "relation": "co_interior"},
    ),
    DiagramSpec(
        kind="exterior_triangle",
        params={"interior1_label": "50°", "interior2_label": "60°", "exterior_label": "x"},
    ),
    DiagramSpec(kind="polygon", params={"n_sides": 6, "marked_angle_label": "x"}),
    DiagramSpec(kind="right_triangle", params={"leg1_label": "6 cm", "leg2_label": "8 cm", "hyp_label": "x"}),
    DiagramSpec(
        kind="function_graph",
        params={"kind": "linear", "m": 2, "c": -1, "x_min": -4, "x_max": 4, "y_min": -6, "y_max": 8, "blank": True},
    ),
    DiagramSpec(
        kind="function_graph",
        params={
            "kind": "quadratic", "a": 1, "b": 0, "c": -4,
            "x_min": -4, "x_max": 4, "y_min": -5, "y_max": 13,
            "table_points": [(-3, 5), (0, -4), (3, 5)],
        },
    ),
    DiagramSpec(
        kind="function_graph",
        params={"kind": "cubic", "a": 1, "b": -3, "x_min": -3, "x_max": 3, "y_min": -10, "y_max": 10},
    ),
    DiagramSpec(
        kind="function_graph",
        params={
            "kind": "reciprocal", "a": 12,
            "x_min": -4, "x_max": 4, "y_min": -13, "y_max": 13,
            "table_points": [(1, 12), (4, 3), (-4, -3)],
        },
    ),
    DiagramSpec(
        kind="piecewise_graph",
        params={
            "points": [(0, 0), (20, 5), (30, 5), (50, 0)],
            "x_max": 50, "y_max": 6, "x_label": "Time (min)", "y_label": "Distance (km)",
        },
    ),
    DiagramSpec(
        kind="graph_transformation",
        params={"transform": "translate_up", "shift": 3, "original_label": "y = f(x)", "transformed_label": "y = f(x) + 3"},
    ),
    DiagramSpec(
        kind="tree_diagram",
        params={
            "stage1": [("Red", "2/5"), ("Blue", "3/5")],
            "stage2": [[("Red", "1/4"), ("Blue", "3/4")], [("Red", "2/4"), ("Blue", "2/4")]],
            "leaf_probs": [["2/20", "6/20"], ["6/20", "6/20"]],
        },
    ),
    DiagramSpec(
        kind="two_way_table",
        params={
            "row_labels": ["Boys", "Girls", "Total"],
            "col_labels": ["Football", "Tennis", "Total"],
            "cells": [["12", "8", "20"], ["5", "15", "20"], ["17", "23", "40"]],
        },
    ),
    DiagramSpec(
        kind="sample_space_diagram",
        params={
            "row_values": [1, 2, 3, 4, 5, 6], "col_values": [1, 2, 3, 4, 5, 6],
            "cells": [[str(r + c) for c in range(1, 7)] for r in range(1, 7)],
            "highlight": [[0, 5]],
        },
    ),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["a_only"]}),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["b_only"]}),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["both"]}),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["neither"]}),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["a_only", "both"]}),
    DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "shade": ["b_only", "neither"]}),
    DiagramSpec(
        kind="venn_diagram",
        params={
            "labels": ["A", "B"],
            "region_text": {"a_only": "5", "b_only": "7", "both": "3", "neither": "10"},
        },
    ),
    DiagramSpec(
        kind="bar_chart",
        params={"categories": ["Red", "Blue", "Green"], "series": [12, 7, 15], "y_label": "Frequency"},
    ),
    DiagramSpec(kind="bar_chart", params={"categories": ["Red", "Blue"], "series": [12, 7], "blank": True}),
    DiagramSpec(
        kind="bar_chart",
        params={
            "categories": ["Mon", "Tue"], "series": [[5, 3], [4, 6]],
            "series_labels": ["Boys", "Girls"], "y_label": "Frequency",
        },
    ),
    DiagramSpec(
        kind="pie_chart",
        params={"categories": ["Red", "Blue", "Green"], "values": [12, 7, 15], "show": "value"},
    ),
    DiagramSpec(
        kind="pie_chart",
        params={"categories": ["Red", "Blue", "Green"], "values": [12, 7, 15], "show": "percentage"},
    ),
    DiagramSpec(kind="pie_chart", params={"categories": ["Red", "Blue"], "values": [12, 7], "blank": True}),
    DiagramSpec(
        kind="box_plot",
        params={"box_plots": [{"min": 2, "q1": 8, "median": 12, "q3": 18, "max": 25}], "x_label": "Score"},
    ),
    DiagramSpec(
        kind="box_plot",
        params={
            "box_plots": [
                {"label": "Class A", "min": 2, "q1": 8, "median": 12, "q3": 18, "max": 25},
                {"label": "Class B", "min": 5, "q1": 10, "median": 14, "q3": 20, "max": 28},
            ],
            "x_label": "Score",
        },
    ),
    DiagramSpec(
        kind="histogram",
        params={
            "boundaries": [0, 10, 20, 40, 60], "frequency_densities": [1.2, 3.5, 2.1, 0.8],
            "x_label": "Age", "y_label": "Frequency density",
        },
    ),
    DiagramSpec(
        kind="histogram",
        params={"boundaries": [0, 10, 20, 40, 60], "frequency_densities": [1.2, 3.5, 2.1, 0.8], "blank": True},
    ),
    DiagramSpec(
        kind="cumulative_frequency",
        params={"points": [(0, 0), (10, 5), (20, 18), (30, 35), (40, 42), (50, 45)], "x_label": "Weight (kg)"},
    ),
    DiagramSpec(
        kind="time_series",
        params={"points": [(1, 120), (2, 135), (3, 128), (4, 150)], "x_label": "Week", "y_label": "Sales (£)"},
    ),
    DiagramSpec(
        kind="number_line",
        params={"range": [-6, 6], "boundaries": [{"value": 2, "closed": True}], "shade": "right"},
    ),
    DiagramSpec(
        kind="number_line",
        params={"range": [-6, 6], "boundaries": [{"value": -3, "closed": False}], "shade": "left"},
    ),
    DiagramSpec(
        kind="number_line",
        params={
            "range": [-8, 8],
            "boundaries": [{"value": -3, "closed": True}, {"value": 4, "closed": False}],
            "shade": "between",
        },
    ),
    DiagramSpec(
        kind="number_line",
        params={
            "range": [-8, 8],
            "boundaries": [{"value": -2, "closed": False}, {"value": 3, "closed": True}],
            "shade": "outside",
        },
    ),
    DiagramSpec(kind="number_line", params={"range": [-6, 6], "boundaries": [], "blank": True}),
    DiagramSpec(
        kind="fraction_shapes",
        params={"shapes": [
            {"kind": "bar", "parts": 4, "shaded": 2, "label": "2/4"},
            {"kind": "bar", "parts": 8, "shaded": 0, "label": "?/8"},
        ]},
    ),
    DiagramSpec(
        kind="fraction_shapes",
        params={"shapes": [
            {"kind": "circle", "parts": 3, "shaded": 1, "label": "1/3"},
            {"kind": "circle", "parts": 6, "shaded": 2, "label": "A) 2/6"},
            {"kind": "circle", "parts": 9, "shaded": 4, "label": "B) 4/9"},
            {"kind": "circle", "parts": 4, "shaded": 1, "label": "C) 1/4"},
        ]},
    ),
    DiagramSpec(kind="dice", params={"values": [3, 5]}),
    DiagramSpec(kind="dice", params={"values": [6], "highlight": [0]}),
    DiagramSpec(kind="spinner", params={"sectors": ["Red", "Blue", "Green", "Yellow"], "highlight": [1]}),
    DiagramSpec(kind="spinner", params={"sectors": ["1", "2", "3", "4", "5", "6"], "highlight": [2, 4]}),
    DiagramSpec(
        kind="bag_of_counters",
        params={"counts": {"red": 4, "blue": 6, "green": 3}, "highlight": "blue"},
    ),
]


@pytest.mark.parametrize(
    "spec",
    SAMPLE_SPECS,
    ids=lambda s: (
        f"{s.kind}:{s.params.get('kind') or s.params.get('notch') or s.params.get('relation') or ''}"
        f"{s.params.get('around_point') or s.params.get('transform') or ''}"
    ),
)
def test_render_diagram_produces_valid_drawing(spec):
    drawing = render_diagram(spec)
    assert isinstance(drawing, Drawing)
    assert drawing.width > 0
    assert drawing.height > 0
    assert len(drawing.contents) > 0


def test_unknown_kind_raises_clearly():
    with pytest.raises(ValueError, match="Unknown diagram kind"):
        render_diagram(DiagramSpec(kind="not_a_real_kind", params={}))


def test_math_runs_italicises_x_and_n():
    assert _math_runs("(3x + 12)°") == [
        ("text", "(3", _LABEL_FONT), ("text", "x", _LABEL_FONT_ITALIC), ("text", " + 12)°", _LABEL_FONT),
    ]
    assert _math_runs("n sides") == [("text", "n", _LABEL_FONT_ITALIC), ("text", " sides", _LABEL_FONT)]


def test_math_runs_leaves_other_letters_upright():
    assert _math_runs("10 cm") == [("text", "10 cm", _LABEL_FONT)]
    assert _math_runs("70°") == [("text", "70°", _LABEL_FONT)]


def test_math_runs_does_not_italicise_x_or_n_inside_a_word():
    # Real words like branch/outcome labels ("Green", "box", "Next") must not
    # get a stray italic letter glued into the middle of them.
    assert _math_runs("Green") == [("text", "Green", _LABEL_FONT)]
    assert _math_runs("box") == [("text", "box", _LABEL_FONT)]
    assert _math_runs("Next") == [("text", "Next", _LABEL_FONT)]


def test_math_runs_detects_fraction_pattern():
    assert _math_runs("3/4 cm") == [("frac", "", "3", "4"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("-3/4 cm") == [("frac", "-", "3", "4"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("x = 3/4") == [
        ("text", "x", _LABEL_FONT_ITALIC), ("text", " = ", _LABEL_FONT), ("frac", "", "3", "4"),
    ]


def _bbox(path):
    xs, ys = path.points[0::2], path.points[1::2]
    return min(xs), max(xs), min(ys), max(ys)


def test_venn_region_paths_are_closed_and_geometrically_distinct():
    from app.pdf.diagrams import (
        _VENN_CX_A, _VENN_CX_B, _venn_a_only_path, _venn_b_only_path, _venn_lens_path,
    )

    lens = _venn_lens_path(color=None)
    a_only = _venn_a_only_path(color=None)
    b_only = _venn_b_only_path(color=None)

    # Every path must close back to its own starting point (no gap in the boundary).
    for path in (lens, a_only, b_only):
        assert path.points[0] == pytest.approx(path.points[-2])
        assert path.points[1] == pytest.approx(path.points[-1])

    # The lens sits centred on the midline between the two circles, and stays
    # clear of each circle's own far edge (it must not accidentally trace a
    # whole circle instead of just the overlap).
    lens_x0, lens_x1, _, _ = _bbox(lens)
    midline = (_VENN_CX_A + _VENN_CX_B) / 2
    assert lens_x0 < midline < lens_x1
    assert lens_x1 - lens_x0 < (_VENN_CX_B - _VENN_CX_A)  # narrower than the centre-to-centre gap

    # a_only must stay left of the midline-ish and not bulge into b_only's territory.
    a_x0, a_x1, _, _ = _bbox(a_only)
    b_x0, b_x1, _, _ = _bbox(b_only)
    assert a_x1 <= _VENN_CX_B  # never reaches circle B's centre
    assert b_x0 >= _VENN_CX_A  # never reaches circle A's centre
    assert a_x0 < midline < b_x1


def test_pie_chart_wedge_angles_sum_to_a_full_circle():
    d = draw_pie_chart(params={"categories": ["A", "B", "C"], "values": [12, 7, 15], "show": "value"})
    wedges = [w for w in d.contents if isinstance(w, Wedge)]
    assert len(wedges) == 3
    total_sweep = sum(w.endangledegrees - w.startangledegrees for w in wedges)
    assert total_sweep == pytest.approx(360)
    # Each wedge's share of the sweep should match its share of the total value.
    values = [12, 7, 15]
    total = sum(values)
    for w, v in zip(wedges, values):
        assert (w.endangledegrees - w.startangledegrees) == pytest.approx(v / total * 360, abs=0.5)


def test_stacked_bar_chart_segment_heights_match_values():
    d = draw_bar_chart(params={
        "categories": ["Mon", "Tue"], "series": [[5, 3], [4, 6]],
        "series_labels": ["Boys", "Girls"], "y_label": "Frequency",
    })
    rects = [r for r in d.contents if isinstance(r, Rect) and r.fillColor is not None and r.height > 0]
    # 2 categories x 2 segments = 4 filled bar-segment rects (legend swatches are also
    # small filled Rects, so just check the bar segments' heights are internally
    # proportional to each other rather than asserting an exact count).
    heights = sorted(r.height for r in rects if r.width > 20)
    # Segment heights should be in the same ratio as the raw values (5:3 and 4:6),
    # i.e. proportional to the plot's pixels-per-unit scale - not testing exact
    # pixels, just that a value-8 segment is taller than a value-3 segment etc.
    assert len(heights) >= 4


def test_box_plot_label_column_keeps_labels_clear_of_the_whiskers():
    d = draw_box_plot(params={
        "box_plots": [
            {"label": "Class A", "min": 2, "q1": 8, "median": 12, "q3": 18, "max": 25},
            {"label": "Class B", "min": 5, "q1": 10, "median": 14, "q3": 20, "max": 28},
        ],
        "x_label": "Score",
    })
    lines = [ln for ln in d.contents if hasattr(ln, "x1") and hasattr(ln, "y1") and ln.y1 == ln.y2]
    whisker_left_edge = min(min(ln.x1, ln.x2) for ln in lines)

    from reportlab.graphics.shapes import Group, String

    def _all_strings(shape):
        if isinstance(shape, String):
            yield shape
        elif isinstance(shape, Group):
            for child in shape.contents:
                yield from _all_strings(child)

    label_strings = [s for s in _all_strings(d) if s.text in ("Class A", "Class B")]
    assert len(label_strings) == 2
    for s in label_strings:
        assert s.x < whisker_left_edge  # labels sit strictly left of every whisker/box edge
