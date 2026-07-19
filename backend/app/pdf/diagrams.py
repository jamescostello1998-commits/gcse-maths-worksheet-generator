"""Small, dependency-free ReportLab diagrams for Geometry worksheet questions.

Each `draw_xxx(params)` function renders one diagram *kind* to a fixed-size
`Drawing` using the exact numeric values already used to build the matching
question's prompt/steps (no separate randomness). `render_diagram` dispatches
a `DiagramSpec` (see app/core/models.py) to the matching renderer.
"""

import math
from typing import Callable

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String, Wedge

from app.core.models import DiagramSpec
from app.pdf.styles import INK, MUTED

DIAGRAM_WIDTH = 200
DIAGRAM_HEIGHT = 130

_LABEL_SIZE = 9


def _label(x: float, y: float, text: str, anchor: str = "middle", color=INK, size: int = _LABEL_SIZE) -> String:
    return String(x, y, str(text), textAnchor=anchor, fontSize=size, fillColor=color, fontName="Helvetica")


def draw_rectangle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    w_val, h_val = params["width"], params["height"]
    margin = 32
    scale = min((DIAGRAM_WIDTH - 2 * margin) / w_val, (DIAGRAM_HEIGHT - 2 * margin) / h_val)
    rw, rh = w_val * scale, h_val * scale
    x0, y0 = (DIAGRAM_WIDTH - rw) / 2, (DIAGRAM_HEIGHT - rh) / 2

    d.add(Rect(x0, y0, rw, rh, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(_label(x0 + rw / 2, y0 - 14, params["width_label"]))
    d.add(_label(x0 + rw + 10, y0 + rh / 2, params["height_label"], anchor="start"))
    return d


def draw_triangle_area(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    base_val, height_val = params["base"], params["height"]
    margin = 32
    scale = min((DIAGRAM_WIDTH - 2 * margin) / base_val, (DIAGRAM_HEIGHT - 2 * margin) / height_val)
    bw, bh = base_val * scale, height_val * scale
    x0, y0 = (DIAGRAM_WIDTH - bw) / 2, (DIAGRAM_HEIGHT - bh) / 2 - 5
    apex_x = x0 + bw * 0.35

    d.add(Polygon([x0, y0, x0 + bw, y0, apex_x, y0 + bh], strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(apex_x, y0 + bh, apex_x, y0, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(_label(x0 + bw / 2, y0 - 14, params["base_label"]))
    d.add(_label(apex_x + 6, y0 + bh / 2, params["height_label"], anchor="start"))
    return d


def draw_l_shape(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ow, oh = params["outer_w"], params["outer_h"]
    iw, ih = params["inner_w"], params["inner_h"]
    margin = 28
    scale = min((DIAGRAM_WIDTH - 2 * margin) / ow, (DIAGRAM_HEIGHT - 2 * margin) / oh)
    ow_s, oh_s, iw_s, ih_s = ow * scale, oh * scale, iw * scale, ih * scale
    x0, y0 = (DIAGRAM_WIDTH - ow_s) / 2, (DIAGRAM_HEIGHT - oh_s) / 2

    if params.get("notch") == "corner":
        pts = [
            x0, y0,
            x0 + ow_s, y0,
            x0 + ow_s, y0 + oh_s - ih_s,
            x0 + ow_s - iw_s, y0 + oh_s - ih_s,
            x0 + ow_s - iw_s, y0 + oh_s,
            x0, y0 + oh_s,
        ]
        d.add(Polygon(pts, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    else:
        d.add(Rect(x0, y0, ow_s, oh_s, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        ix0, iy0 = x0 + (ow_s - iw_s) / 2, y0 + (oh_s - ih_s) / 2
        d.add(Rect(ix0, iy0, iw_s, ih_s, strokeColor=INK, fillColor=None, strokeWidth=1.0))

    d.add(_label(x0 + ow_s / 2, y0 - 14, params["outer_labels"][0]))
    d.add(_label(x0 - 10, y0 + oh_s / 2, params["outer_labels"][1], anchor="end"))
    inner_text = f"{params['inner_labels'][0]} x {params['inner_labels'][1]}"
    d.add(_label(x0 + ow_s / 2, y0 + oh_s + 12, inner_text, color=MUTED, size=8))
    return d


def draw_circle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2
    r = min(DIAGRAM_WIDTH, DIAGRAM_HEIGHT) / 2 - 25

    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(cx, cy, cx + r, cy, strokeColor=INK, strokeWidth=1))
    d.add(_label(cx + r / 2, cy + 5, params["label"]))
    return d


def draw_rectangle_semicircle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    w_val, h_val, r_val = params["width"], params["height"], params["radius"]
    total_h_val = h_val + r_val
    margin = 28
    scale = min((DIAGRAM_WIDTH - 2 * margin) / w_val, (DIAGRAM_HEIGHT - 2 * margin) / total_h_val)
    rw, rh, rr = w_val * scale, h_val * scale, r_val * scale
    x0, y0 = (DIAGRAM_WIDTH - rw) / 2, (DIAGRAM_HEIGHT - (rh + rr)) / 2

    d.add(Rect(x0, y0, rw, rh, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Wedge(x0 + rw / 2, y0 + rh, rr, 0, 180, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(_label(x0 + rw / 2, y0 - 14, params["width"]))
    d.add(_label(x0 - 10, y0 + rh / 2, params["height"], anchor="end"))
    return d


def draw_angle_line(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    around_point = params["around_point"]
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2 - (0 if around_point else 10)
    radius = 65
    angle_values = params["angle_values"]
    labels = params["labels"]

    ray_angles = [0.0]
    cum = 0.0
    for v in angle_values:
        cum += v
        ray_angles.append(cum)

    for ang in ray_angles:
        rad = math.radians(ang)
        d.add(Line(cx, cy, cx + radius * math.cos(rad), cy + radius * math.sin(rad), strokeColor=INK, strokeWidth=1.2))

    running = 0.0
    for v, lbl in zip(angle_values, labels):
        mid_rad = math.radians(running + v / 2)
        lx, ly = cx + (radius * 0.55) * math.cos(mid_rad), cy + (radius * 0.55) * math.sin(mid_rad)
        d.add(_label(lx, ly, lbl))
        running += v

    d.add(Circle(cx, cy, 2, strokeColor=INK, fillColor=INK))
    return d


def draw_triangle_angles(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2 - 5
    r = 45
    vertices = []
    for ang in (90, 210, 330):
        rad = math.radians(ang)
        vertices.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))

    pts = [coord for vertex in vertices for coord in vertex]
    d.add(Polygon(pts, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    for (vx, vy), lbl in zip(vertices, params["angle_labels"]):
        lx, ly = vx + (cx - vx) * 0.45, vy + (cy - vy) * 0.45
        d.add(_label(lx, ly, lbl))
    return d


def draw_parallel_lines(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    x_left, x_right = 15, DIAGRAM_WIDTH - 15
    y_top, y_bottom = DIAGRAM_HEIGHT - 35, 35
    d.add(Line(x_left, y_top, x_right, y_top, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(x_left, y_bottom, x_right, y_bottom, strokeColor=INK, strokeWidth=1.2))

    ix_top, ix_bottom = DIAGRAM_WIDTH * 0.4, DIAGRAM_WIDTH * 0.62
    dx, dy = ix_bottom - ix_top, y_bottom - y_top
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    ext = 15
    d.add(Line(ix_top - ux * ext, y_top - uy * ext, ix_bottom + ux * ext, y_bottom + uy * ext, strokeColor=INK, strokeWidth=1.2))

    offsets = {
        "corresponding": ((10, 8), (10, 8)),
        "alternate": ((10, -14), (-24, 10)),
        "co_interior": ((10, -14), (10, 10)),
    }
    (kx, ky), (ux2, uy2) = offsets[params["relation"]]
    d.add(_label(ix_top + kx, y_top + ky, params["known_label"], anchor="start", size=8))
    d.add(_label(ix_bottom + ux2, y_bottom + uy2, params["unknown_label"], anchor="start", size=8))
    return d


def draw_exterior_triangle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    A, B, C = (35, 30), (150, 30), (75, 100)
    d.add(Polygon([A[0], A[1], B[0], B[1], C[0], C[1]], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    ext_x = B[0] + (B[0] - A[0]) * 0.4
    ext_y = B[1] + (B[1] - A[1]) * 0.4
    d.add(Line(B[0], B[1], ext_x, ext_y, strokeColor=INK, strokeWidth=1.2))

    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)

    def _inset(vertex, factor=0.5):
        return (vertex[0] + (centroid[0] - vertex[0]) * factor, vertex[1] + (centroid[1] - vertex[1]) * factor)

    ax, ay = _inset(A)
    bx, by = _inset(B)
    d.add(_label(ax, ay, params["interior1_label"], size=8))
    d.add(_label(bx, by, params["interior2_label"], size=8))
    d.add(_label(B[0] + 16, B[1] + 8, params["exterior_label"], anchor="start", size=8))
    return d


def draw_polygon(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    n = params["n_sides"]
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2
    r = 45
    vertices = []
    for i in range(n):
        rad = math.radians(90 + i * 360 / n)
        vertices.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))

    pts = [coord for vertex in vertices for coord in vertex]
    d.add(Polygon(pts, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    vx, vy = vertices[0]
    lx, ly = vx + (cx - vx) * 0.3, vy + (cy - vy) * 0.3
    d.add(_label(lx, ly, params["marked_angle_label"]))
    return d


def draw_right_triangle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    A, B, C = (40, 25), (165, 25), (40, 105)
    d.add(Polygon([A[0], A[1], B[0], B[1], C[0], C[1]], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    s = 8
    d.add(Rect(A[0], A[1], s, s, strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(_label((A[0] + B[0]) / 2, A[1] - 14, params["leg1_label"]))
    d.add(_label(A[0] - 10, (A[1] + C[1]) / 2, params["leg2_label"], anchor="end"))
    d.add(_label((B[0] + C[0]) / 2 + 12, (B[1] + C[1]) / 2 + 6, params["hyp_label"], anchor="start"))
    return d


_RENDERERS: dict[str, Callable[[dict], Drawing]] = {
    "rectangle": draw_rectangle,
    "triangle_area": draw_triangle_area,
    "l_shape": draw_l_shape,
    "circle": draw_circle,
    "rectangle_semicircle": draw_rectangle_semicircle,
    "angle_line": draw_angle_line,
    "triangle_angles": draw_triangle_angles,
    "parallel_lines": draw_parallel_lines,
    "exterior_triangle": draw_exterior_triangle,
    "polygon": draw_polygon,
    "right_triangle": draw_right_triangle,
}


def render_diagram(spec: DiagramSpec) -> Drawing:
    try:
        renderer = _RENDERERS[spec.kind]
    except KeyError:
        raise ValueError(f"Unknown diagram kind: {spec.kind!r}") from None
    return renderer(spec.params)
