import pytest
from reportlab.graphics.shapes import Drawing, Rect, Wedge

from app.core.models import DiagramSpec
from app.pdf.diagrams import (
    _LABEL_FONT,
    _LABEL_FONT_BOLD,
    _LABEL_FONT_ITALIC,
    _math_runs,
    draw_bar_chart,
    draw_box_plot,
    draw_grid_transformation,
    draw_pie_chart,
    draw_symmetry_shape,
    render_diagram,
)

SAMPLE_SPECS = [
    DiagramSpec(kind="rectangle", params={"width": 10, "height": 6, "width_label": "10 cm", "height_label": "6 cm"}),
    DiagramSpec(
        kind="two_similar_rectangles",
        params={
            "a_width_label": "6 cm", "a_height_label": "9 cm",
            "b_width_label": "8 cm", "b_height_label": "x",
        },
    ),
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
            "notch": "center", "shade_frame": True,
            "outer_labels": ["20 cm", "15 cm"], "inner_labels": ["6 cm", "5 cm"],
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
    DiagramSpec(kind="spinner_pair", params={"sectors_a": ["1", "2", "3"], "sectors_b": ["R", "B", "G", "Y"]}),
    DiagramSpec(
        kind="bag_of_counters",
        params={"counts": {"red": 4, "blue": 6, "green": 3}},
    ),
    DiagramSpec(
        kind="parallelogram",
        params={"base": 12, "height": 7, "base_label": "12 cm", "height_label": "7 cm"},
    ),
    DiagramSpec(
        kind="trapezium",
        params={"a": 6, "b": 14, "height": 8, "a_label": "6 cm", "b_label": "14 cm", "height_label": "8 cm"},
    ),
    DiagramSpec(kind="sector", params={"angle": 60, "radius_label": "9 cm", "angle_label": "60°"}),
    DiagramSpec(kind="sector", params={"angle": 290, "radius_label": "5 cm", "angle_label": "290°"}),
    DiagramSpec(
        kind="mixed_compound",
        params={
            "width": 16, "height": 10, "top_kind": "triangle", "cut_kind": "quarter_circle",
            "roof_height": 5, "cut_radius": 4,
            "width_label": "16 cm", "height_label": "10 cm", "top_label": "5 cm", "cut_label": "4 cm",
        },
    ),
    DiagramSpec(
        kind="mixed_compound",
        params={
            "width": 16, "height": 10, "top_kind": "semicircle", "cut_kind": "quarter_circle",
            "top_radius": 8, "cut_radius": 4,
            "width_label": "16 cm", "height_label": "10 cm", "top_label": "8 cm", "cut_label": "4 cm",
        },
    ),
    DiagramSpec(
        kind="mixed_compound",
        params={
            "width": 16, "height": 10, "top_kind": "triangle", "cut_kind": "semicircle_notch",
            "roof_height": 5, "notch_radius": 3,
            "width_label": "16 cm", "height_label": "10 cm", "top_label": "5 cm", "cut_label": "3 cm",
        },
    ),
    DiagramSpec(
        kind="mixed_compound",
        params={
            "width": 16, "height": 10, "top_kind": "semicircle", "cut_kind": "semicircle_notch",
            "top_radius": 8, "notch_radius": 3,
            "width_label": "16 cm", "height_label": "10 cm", "top_label": "8 cm", "cut_label": "3 cm",
        },
    ),
    DiagramSpec(
        kind="grid_transformation",
        params={
            "x_min": -8, "x_max": 8, "y_min": -8, "y_max": 8,
            "original_vertices": [(1, 1), (3, 1), (3, 2), (1, 2)], "original_labels": ["A", "B", "C", "D"],
            "mirror_line": {"type": "vertical", "x": -1, "label": "x = -1"},
        },
    ),
    DiagramSpec(
        kind="grid_transformation",
        params={
            "x_min": -8, "x_max": 8, "y_min": -8, "y_max": 8,
            "original_vertices": [(1, 1), (3, 1), (3, 2), (1, 2)], "original_labels": ["A", "B", "C", "D"],
            "image_vertices": [(-3, 1), (-5, 1), (-5, 2), (-3, 2)], "image_labels": ["A'", "B'", "C'", "D'"],
            "centre": (0, 0), "translation_vector": (4, 3), "vector_label": "(4, 3)",
        },
    ),
    DiagramSpec(
        kind="symmetry_shape",
        params={"vertices": [(0, 0), (6, 0), (6, 4), (0, 4)], "blank": True},
    ),
    DiagramSpec(
        kind="symmetry_shape",
        params={
            "vertices": [(0, 0), (6, 0), (6, 4), (0, 4)],
            "symmetry_lines": [{"p1": (3, -1), "p2": (3, 5)}, {"p1": (-1, 2), "p2": (7, 2)}],
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


def test_two_similar_rectangles_omits_unlabelled_sides():
    # ratio_shape_similar_higher only ever gives one length pair (the
    # area/volume, not a second length, is what's given/asked for) - the
    # diagram must not crash or draw a placeholder when a_height_label/
    # b_height_label are simply absent from params.
    spec = DiagramSpec(
        kind="two_similar_rectangles",
        params={"a_width_label": "6 cm", "b_width_label": "8 cm"},
    )
    drawing = render_diagram(spec)
    assert isinstance(drawing, Drawing)
    assert len(drawing.contents) > 0


def test_rectangle_height_label_stays_within_the_canvas():
    # A wide rectangle (width scale-bound, pushing the rectangle's own right
    # edge close to the canvas edge) combined with a two-digit height_label
    # previously overflowed past DIAGRAM_WIDTH by a couple of points, since
    # draw_rectangle had no stringWidth awareness at all - found via a real
    # rendered-PDF check, not a unit test written in advance.
    from reportlab.pdfbase.pdfmetrics import stringWidth

    from app.pdf.diagrams import DIAGRAM_WIDTH, _LABEL_FONT, _LABEL_SIZE, draw_rectangle

    spec_params = {"width": 28, "height": 12, "width_label": "(x + 10) cm", "height_label": "12 cm"}
    drawing = draw_rectangle(spec_params)

    def _walk(shapes):
        for s in shapes:
            if hasattr(s, "text"):
                yield s
            elif hasattr(s, "contents"):
                yield from _walk(s.contents)

    height_label_strings = [s for s in _walk(drawing.contents) if s.text.strip() == "12 cm"]
    assert height_label_strings
    for s in height_label_strings:
        w = stringWidth(s.text, _LABEL_FONT, _LABEL_SIZE)
        x1 = s.x + w if s.textAnchor == "start" else s.x
        assert x1 <= DIAGRAM_WIDTH


def test_angle_line_narrow_wedge_label_stays_within_the_canvas():
    # A narrow (<20 degree) wedge in the "around_point" layout can orient its
    # label near-vertically with no headroom - previously pushed the label
    # past the top edge by ~20pt, found via a real rendered-PDF check across
    # many seeds, not assumed.
    from app.pdf.diagrams import DIAGRAM_HEIGHT, draw_angle_line

    spec_params = {"around_point": True, "angle_values": [87.5, 5, 267.5], "labels": ["87.5°", "5°", "267.5°"]}
    drawing = draw_angle_line(spec_params)

    def _walk(shapes):
        for s in shapes:
            if hasattr(s, "text"):
                yield s
            elif hasattr(s, "contents"):
                yield from _walk(s.contents)

    for s in _walk(drawing.contents):
        assert 0 <= s.y <= DIAGRAM_HEIGHT


def test_math_runs_italicises_x_and_n():
    assert _math_runs("(3x + 12)°") == [
        ("text", "(3", _LABEL_FONT), ("text", "x", _LABEL_FONT_ITALIC), ("text", " + 12)°", _LABEL_FONT),
    ]
    assert _math_runs("n sides") == [("text", "n", _LABEL_FONT_ITALIC), ("text", " sides", _LABEL_FONT)]


def test_math_runs_leaves_other_letters_upright():
    assert _math_runs("10 cm") == [("text", "10 cm", _LABEL_FONT)]
    assert _math_runs("70°") == [("text", "70°", _LABEL_FONT)]


def test_math_runs_bolds_the_vec_marker_down_to_just_its_letter():
    # \vec{a}/\vec{b} (see app/topics/vectors.py) bolds only the bare letter -
    # the marker itself never appears in the rendered run.
    assert _math_runs("\\vec{a}") == [("text", "a", _LABEL_FONT_BOLD)]
    assert _math_runs("\\vec{a} = (3, -2)") == [
        ("text", "a", _LABEL_FONT_BOLD), ("text", " = (3, -2)", _LABEL_FONT),
    ]


def test_math_runs_does_not_italicise_x_or_n_inside_a_word():
    # Real words like branch/outcome labels ("Green", "box", "Next") must not
    # get a stray italic letter glued into the middle of them.
    assert _math_runs("Green") == [("text", "Green", _LABEL_FONT)]
    assert _math_runs("box") == [("text", "box", _LABEL_FONT)]
    assert _math_runs("Next") == [("text", "Next", _LABEL_FONT)]


def test_math_runs_detects_fraction_pattern():
    assert _math_runs("3/4 cm") == [("frac", "", "3", "4"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("-3/4 cm") == [("frac", "-", "3", "4"), ("text", " cm", _LABEL_FONT)]


def test_math_runs_detects_radical_pattern():
    assert _math_runs("7√6 cm") == [("text", "7", _LABEL_FONT), ("radical", "6"), ("text", " cm", _LABEL_FONT)]
    assert _math_runs("√15") == [("radical", "15")]


def test_radical_label_draws_a_true_hook_and_bar_and_stays_on_canvas():
    # A surd side-length label (e.g. surds_rectangle_H) previously rendered
    # "√" as a bare literal glyph with no bar over its radicand at all - the
    # diagram label engine only ever handled fraction vinculums, never
    # radicals, since no diagram had needed one until this topic surfaced it.
    # Confirms a real hook (2 diagonal Lines) + bar (1 horizontal Line) are
    # drawn per radical, and the whole label stays within the canvas.
    from app.pdf.diagrams import DIAGRAM_HEIGHT, DIAGRAM_WIDTH, draw_rectangle

    spec_params = {
        "width": 4 * 6**0.5, "height": 7 * 6**0.5, "width_label": "4√6 cm", "height_label": "7√6 cm",
    }
    drawing = draw_rectangle(spec_params)

    def _walk(shapes):
        for s in shapes:
            yield s
            if hasattr(s, "contents"):
                yield from _walk(s.contents)

    lines = [s for s in _walk(drawing.contents) if type(s).__name__ == "Line"]
    strings = [s for s in _walk(drawing.contents) if hasattr(s, "text")]
    assert len(lines) >= 6  # 3 per radical (hook tick, hook diagonal, bar) x 2 labels
    for s in strings:
        assert 0 <= s.x <= DIAGRAM_WIDTH
    for ln in lines:
        assert 0 <= ln.x1 <= DIAGRAM_WIDTH
        assert 0 <= ln.x2 <= DIAGRAM_WIDTH
        assert 0 <= ln.y1 <= DIAGRAM_HEIGHT
        assert 0 <= ln.y2 <= DIAGRAM_HEIGHT
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


def test_plans_and_elevations_captions_never_overlap_for_a_small_solid():
    # A small solid (well under the ~60pt target cell size) used to leave
    # "Front elevation"/"Side elevation" with no gap at all between them,
    # running together as "Front elevationSide elevation" - found via
    # rendering an actual modelled-example page and looking closely, not by
    # any unit test written in advance.
    from reportlab.graphics.shapes import Group, String
    from reportlab.pdfbase.pdfmetrics import stringWidth

    from app.pdf.diagrams import draw_plans_and_elevations

    def _all_strings(shape):
        if isinstance(shape, String):
            yield shape
        elif isinstance(shape, Group):
            for child in shape.contents:
                yield from _all_strings(child)

    d = draw_plans_and_elevations({
        "shape": "triangular_prism",
        "base": 5, "tri_height": 8, "length": 3,
        "base_label": "5 cm", "tri_height_label": "8 cm", "length_label": "3 cm",
    })
    strings = list(_all_strings(d))
    # Captions are built from single-run _label() calls (plain text, no
    # math substitution), so each is one String with the full caption text.
    front_label = next(s for s in strings if s.text == "Front elevation")
    side_label = next(s for s in strings if s.text == "Side elevation")
    front_right = front_label.x + stringWidth(front_label.text, front_label.fontName, front_label.fontSize)
    assert front_right < side_label.x


def test_grid_transformation_blank_omits_the_image_but_keeps_given_annotations():
    base_params = {
        "x_min": -8, "x_max": 8, "y_min": -8, "y_max": 8,
        "original_vertices": [(1, 1), (3, 1), (3, 2), (1, 2)], "original_labels": ["A", "B", "C", "D"],
        "mirror_line": {"type": "vertical", "x": -1, "label": "x = -1"},
    }
    blank = draw_grid_transformation(params=base_params)
    solution = draw_grid_transformation(params={
        **base_params,
        "image_vertices": [(-3, 1), (-5, 1), (-5, 2), (-3, 2)],
        "image_labels": ["A'", "B'", "C'", "D'"],
    })
    from reportlab.graphics.shapes import Group, Polygon, String

    def _all(shape, cls):
        if isinstance(shape, cls):
            yield shape
        elif isinstance(shape, Group):
            for child in shape.contents:
                yield from _all(child, cls)

    # The mirror line (given information) is drawn on both the blank question-page
    # version and the completed solution-page version. The label "x = -1" is split
    # into separate runs by the standalone-x italiciser, so match on the
    # un-italicised remainder " = -1" rather than the whole string.
    assert any(s.text == " = -1" for s in _all(blank, String))
    assert any(s.text == " = -1" for s in _all(solution, String))
    # Only the solution has the image polygon and its primed vertex labels.
    assert len(list(_all(blank, Polygon))) == 1
    assert len(list(_all(solution, Polygon))) == 2
    assert not any(s.text == "A'" for s in _all(blank, String))
    assert any(s.text == "A'" for s in _all(solution, String))


def test_grid_transformation_mirror_line_only_appears_when_passed():
    from reportlab.graphics.shapes import Group, Line

    def _all_lines(shape):
        if isinstance(shape, Line):
            yield shape
        elif isinstance(shape, Group):
            for child in shape.contents:
                yield from _all_lines(child)

    no_mirror = draw_grid_transformation(params={
        "x_min": -8, "x_max": 8, "y_min": -8, "y_max": 8,
        "original_vertices": [(1, 1), (3, 1), (3, 2), (1, 2)], "original_labels": ["A", "B", "C", "D"],
    })
    with_mirror = draw_grid_transformation(params={
        "x_min": -8, "x_max": 8, "y_min": -8, "y_max": 8,
        "original_vertices": [(1, 1), (3, 1), (3, 2), (1, 2)], "original_labels": ["A", "B", "C", "D"],
        "mirror_line": {"type": "horizontal", "y": -2, "label": "y = -2"},
    })
    dashed_no_mirror = [ln for ln in _all_lines(no_mirror) if ln.strokeDashArray]
    dashed_with_mirror = [ln for ln in _all_lines(with_mirror) if ln.strokeDashArray]
    assert len(dashed_no_mirror) == 0
    assert len(dashed_with_mirror) == 1


def test_symmetry_shape_blank_omits_symmetry_lines():
    params = {
        "vertices": [(0, 0), (6, 0), (6, 4), (0, 4)],
        "symmetry_lines": [{"p1": (3, -1), "p2": (3, 5)}, {"p1": (-1, 2), "p2": (7, 2)}],
    }
    blank = draw_symmetry_shape(params={**params, "blank": True})
    solution = draw_symmetry_shape(params=params)

    from reportlab.graphics.shapes import Group, Line

    def _all_lines(shape):
        if isinstance(shape, Line):
            yield shape
        elif isinstance(shape, Group):
            for child in shape.contents:
                yield from _all_lines(child)

    assert len(list(_all_lines(blank))) == 0
    assert len(list(_all_lines(solution))) == 2


def test_clip_curve_segments_stops_at_window_edge_no_flat_cap():
    # A curve running past the window is split into in-window segments with the
    # exact boundary crossing inserted - never a flat horizontal cap.
    from app.pdf.diagrams import _clip_curve_segments

    pts = [(x, x) for x in range(-5, 6)]  # y = x, exits [-2, 2] at both ends
    segs = _clip_curve_segments(pts, -2, 2)
    assert len(segs) == 1
    seg = segs[0]
    assert all(-2 - 1e-9 <= y <= 2 + 1e-9 for _, y in seg)
    # crossings are exact, not clamped-and-flat
    assert seg[0] == pytest.approx((-2.0, -2.0))
    assert seg[-1] == pytest.approx((2.0, 2.0))

    # a segment that passes straight through the window (both ends outside)
    through = _clip_curve_segments([(0, -10), (0, 10)], -2, 2)
    assert len(through) == 1 and len(through[0]) == 2


def test_function_graph_curve_never_flatlines_at_window_edge():
    # y = x^3 over -3..3 far exceeds a +/-10 window; the drawn polyline must
    # not contain a run of points pinned at the window's top/bottom (the old
    # clamp bug), i.e. its points stay strictly inside except at true crossings.
    from reportlab.graphics.shapes import Group, PolyLine

    from app.pdf.diagrams import draw_function_graph

    d = draw_function_graph({
        "kind": "cubic", "a": 1, "b": 0,
        "x_min": -3, "x_max": 3, "y_min": -10, "y_max": 10,
    })

    def polylines(shape):
        if isinstance(shape, PolyLine):
            yield shape
        elif isinstance(shape, (Group, Drawing)):
            for c in shape.contents:
                yield from polylines(c)

    pls = list(polylines(d))
    assert pls, "expected at least one curve polyline"
    # No polyline should have 3+ consecutive points at the same y (a flat cap).
    for pl in pls:
        ys = pl.points[1::2]
        runs = 1
        for a, b in zip(ys, ys[1:]):
            runs = runs + 1 if abs(a - b) < 1e-6 else 1
            assert runs < 3, "curve flatlines at the window edge (clamp bug)"


def test_scaled_axes_cells_are_square():
    # The minor grid squares must be square pixels (equal width and height),
    # never rectangles, even for a lopsided range.
    from reportlab.graphics.shapes import Line

    from app.pdf.diagrams import GRID, _draw_scaled_axes

    d = Drawing(210, 210)
    _draw_scaled_axes(d, -4, 4, -20, 20)  # steep/lopsided
    xs = sorted({round(s.x1, 3) for s in d.contents if isinstance(s, Line) and abs(s.x1 - s.x2) < 1e-6})
    ys = sorted({round(s.y1, 3) for s in d.contents if isinstance(s, Line) and abs(s.y1 - s.y2) < 1e-6})
    x_gaps = [b - a for a, b in zip(xs, xs[1:])]
    y_gaps = [b - a for a, b in zip(ys, ys[1:])]
    # the smallest (minor) gap on each axis should match: square cells
    assert min(x_gaps) == pytest.approx(min(y_gaps), abs=0.5)


def test_cumulative_frequency_starts_at_origin_with_square_cells():
    from reportlab.graphics.shapes import Line

    from app.pdf.diagrams import draw_cumulative_frequency

    d = draw_cumulative_frequency({
        "points": [(10, 0), (20, 3), (30, 12), (40, 26), (50, 39), (60, 53)],
        "x_label": "Weight (kg)",
    })
    vlines = [round(s.x1, 2) for s in d.contents if isinstance(s, Line) and abs(s.x1 - s.x2) < 1e-6]
    hlines = [round(s.y1, 2) for s in d.contents if isinstance(s, Line) and abs(s.y1 - s.y2) < 1e-6]
    # x-axis origin (x=0) is drawn, and minor cells are square
    x_gaps = [round(b - a, 2) for a, b in zip(sorted(set(vlines)), sorted(set(vlines))[1:])]
    y_gaps = [round(b - a, 2) for a, b in zip(sorted(set(hlines)), sorted(set(hlines))[1:])]
    assert min(x_gaps) == pytest.approx(min(y_gaps), abs=0.5), "cumulative frequency cells not square"


def test_pie_chart_marks_a_right_angle_wedge_with_a_square_not_an_arc():
    from reportlab.graphics.shapes import ArcPath, Line, PolyLine

    from app.pdf.diagrams import draw_pie_chart

    # 90/270 split: the 90-degree wedge gets a right-angle square marker (a
    # 3-point PolyLine) instead of an angle arc; the other (270-degree, not a
    # right angle) wedge still gets a normal arc.
    d = draw_pie_chart(params={"categories": ["A", "B"], "values": [1, 3]})
    polylines = [s for s in d.contents if isinstance(s, PolyLine)]
    arcs = [s for s in d.contents if isinstance(s, ArcPath)]
    assert len(polylines) == 1  # the right-angle marker, not an arc
    assert len(arcs) == 1  # the other wedge's own (non-right-angle) arc
    # a centre cross (two short crossing lines) is always present
    lines = [s for s in d.contents if isinstance(s, Line)]
    assert len(lines) == 2


def test_pie_chart_narrow_wedge_falls_back_to_a_combined_label():
    from app.pdf.diagrams import draw_pie_chart

    d = draw_pie_chart(params={"categories": ["A", "B", "C"], "values": [1, 1, 34]})
    texts = []
    for s in d.contents:
        if hasattr(s, "contents"):
            for c in s.contents:
                if hasattr(c, "text"):
                    texts.append(c.text)
    # the two ~10-degree wedges are too narrow for a separate arc + name, so
    # they fall back to one combined "Category (n°)" label
    assert any("A (" in t for t in texts)
    assert any("B (" in t for t in texts)


def test_pie_chart_blank_draws_only_the_outline_start_radius_and_centre_cross():
    from reportlab.graphics.shapes import Circle, Line, Wedge

    from app.pdf.diagrams import draw_pie_chart

    d = draw_pie_chart(params={"categories": ["A", "B"], "values": [1, 1], "blank": True})
    assert len([s for s in d.contents if isinstance(s, Wedge)]) == 0
    assert len([s for s in d.contents if isinstance(s, Circle)]) == 1
    # the starting radius line + the two centre-cross lines
    assert len([s for s in d.contents if isinstance(s, Line)]) == 3


def test_bar_chart_blank_omits_category_labels_but_keeps_them_when_solved():
    from app.pdf.diagrams import draw_bar_chart

    def category_texts(d):
        texts = []
        for s in d.contents:
            if hasattr(s, "contents"):
                for c in s.contents:
                    if hasattr(c, "text"):
                        texts.append(c.text)
        return texts

    params = {"categories": ["Red", "Blue", "Yellow"], "series": [11, 10, 8]}
    blank = draw_bar_chart(params={**params, "blank": True})
    solved = draw_bar_chart(params=params)

    blank_texts = category_texts(blank)
    solved_texts = category_texts(solved)
    for cat in params["categories"]:
        assert cat not in blank_texts
        assert cat in solved_texts


def test_two_way_table_corner_label_renders_when_given_but_stays_blank_otherwise():
    from app.pdf.diagrams import draw_two_way_table

    def texts(d):
        return [c.text for s in d.contents if hasattr(s, "contents") for c in s.contents if hasattr(c, "text")]

    with_label = draw_two_way_table(params={
        "row_labels": ["0", "1"], "col_labels": ["Frequency"], "cells": [["3"], ["5"]],
        "corner_label": "Number of pets",
    })
    without_label = draw_two_way_table(params={
        "row_labels": ["0", "1"], "col_labels": ["Frequency"], "cells": [["3"], ["5"]],
    })
    assert "Number of pets" in texts(with_label)
    assert "Number of pets" not in texts(without_label)
