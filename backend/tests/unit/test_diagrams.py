import pytest
from reportlab.graphics.shapes import Drawing

from app.core.models import DiagramSpec
from app.pdf.diagrams import render_diagram

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
    DiagramSpec(kind="rectangle_semicircle", params={"width": 10, "height": 8, "radius": 5}),
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
]


@pytest.mark.parametrize("spec", SAMPLE_SPECS, ids=lambda s: f"{s.kind}:{s.params.get('notch') or s.params.get('relation') or s.params.get('around_point') or ''}")
def test_render_diagram_produces_valid_drawing(spec):
    drawing = render_diagram(spec)
    assert isinstance(drawing, Drawing)
    assert drawing.width > 0
    assert drawing.height > 0
    assert len(drawing.contents) > 0


def test_unknown_kind_raises_clearly():
    with pytest.raises(ValueError, match="Unknown diagram kind"):
        render_diagram(DiagramSpec(kind="not_a_real_kind", params={}))
