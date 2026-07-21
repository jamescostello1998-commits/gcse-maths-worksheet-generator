import pytest
from reportlab.graphics.shapes import Drawing

from app.core.models import DiagramSpec
from app.pdf.diagrams import _LABEL_FONT, _LABEL_FONT_ITALIC, _math_runs, render_diagram

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


def test_math_runs_detects_fraction_pattern():
    assert _math_runs("3/4 cm") == [("frac", "", "3", "4"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("-3/4 cm") == [("frac", "-", "3", "4"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("x = 3/4") == [
        ("text", "x", _LABEL_FONT_ITALIC), ("text", " = ", _LABEL_FONT), ("frac", "", "3", "4"),
    ]
