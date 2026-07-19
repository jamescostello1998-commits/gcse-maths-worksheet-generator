"""Small, dependency-free ReportLab diagrams for Geometry (and some Algebra
graph) worksheet questions.

Each `draw_xxx(params)` function renders one diagram *kind* to a fixed-size
`Drawing` using the exact numeric values already used to build the matching
question's prompt/steps (no separate randomness). `render_diagram` dispatches
a `DiagramSpec` (see app/core/models.py) to the matching renderer.
"""

import math
from typing import Callable

from reportlab.graphics.shapes import Circle, Drawing, Group, Line, PolyLine, Polygon, Rect, String, Wedge
from reportlab.pdfbase.pdfmetrics import stringWidth

from app.core.models import DiagramSpec
from app.pdf.styles import INK, MUTED

DIAGRAM_WIDTH = 200
DIAGRAM_HEIGHT = 130

_LABEL_SIZE = 9
_LABEL_FONT = "Helvetica"
_LABEL_FONT_ITALIC = "Helvetica-Oblique"


def _math_runs(text: str) -> list[tuple[str, str]]:
    """Split label text into (substring, fontName) runs, italicising the
    algebraic variable x so diagram labels match standard maths typesetting
    (mirrors app/pdf/mathtext.py's handling of Paragraph text)."""
    runs: list[tuple[str, str]] = []
    buf = ""
    for ch in text:
        if ch == "x":
            if buf:
                runs.append((buf, _LABEL_FONT))
                buf = ""
            runs.append((ch, _LABEL_FONT_ITALIC))
        else:
            buf += ch
    if buf:
        runs.append((buf, _LABEL_FONT))
    return runs


def _label(x: float, y: float, text: str, anchor: str = "middle", color=INK, size: int = _LABEL_SIZE) -> Group:
    runs = _math_runs(str(text))
    total_width = sum(stringWidth(t, font, size) for t, font in runs)
    if anchor == "middle":
        cursor = x - total_width / 2
    elif anchor == "end":
        cursor = x - total_width
    else:
        cursor = x

    group = Group()
    for t, font in runs:
        group.add(String(cursor, y, t, textAnchor="start", fontSize=size, fillColor=color, fontName=font))
        cursor += stringWidth(t, font, size)
    return group


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


def _not_to_scale(d: Drawing, x: float = DIAGRAM_WIDTH / 2, y: float = 10) -> None:
    d.add(_label(x, y, "Diagram NOT accurately drawn", color=MUTED, size=6.5))


def draw_trig_triangle(params: dict) -> Drawing:
    """Right triangle for SOH CAH TOA questions: right angle at A (bottom-left),
    marked angle at B (bottom-right). Opposite/adjacent are relative to that angle."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    A, B, C = (40, 25), (165, 25), (40, 105)
    d.add(Polygon([A[0], A[1], B[0], B[1], C[0], C[1]], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    s = 8
    d.add(Rect(A[0], A[1], s, s, strokeColor=INK, fillColor=None, strokeWidth=1))
    if params.get("adjacent_label"):
        d.add(_label((A[0] + B[0]) / 2, A[1] - 14, params["adjacent_label"]))
    if params.get("opposite_label"):
        d.add(_label(A[0] - 10, (A[1] + C[1]) / 2, params["opposite_label"], anchor="end"))
    if params.get("hyp_label"):
        d.add(_label((B[0] + C[0]) / 2 + 12, (B[1] + C[1]) / 2 + 6, params["hyp_label"], anchor="start"))
    d.add(_label(B[0] - 20, B[1] + 9, params["angle_label"], size=8))
    return d


def draw_general_triangle(params: dict) -> Drawing:
    """Scalene triangle (not to scale) for sine rule / cosine rule / area
    questions, with any combination of the three sides and three angles
    labelled by the caller."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    A, B, C = (30, 28), (172, 28), (95, 108)
    d.add(Polygon([A[0], A[1], B[0], B[1], C[0], C[1]], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    def midpoint(p, q):
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)

    mid_bc, mid_ac, mid_ab = midpoint(B, C), midpoint(A, C), midpoint(A, B)
    if params.get("side_a_label"):
        d.add(_label(mid_bc[0] + 14, mid_bc[1] + 2, params["side_a_label"], anchor="start", size=8))
    if params.get("side_b_label"):
        d.add(_label(mid_ac[0] - 12, mid_ac[1] + 2, params["side_b_label"], anchor="end", size=8))
    if params.get("side_c_label"):
        d.add(_label(mid_ab[0], mid_ab[1] - 12, params["side_c_label"], size=8))

    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)

    def inset(v, factor=0.4):
        return (v[0] + (centroid[0] - v[0]) * factor, v[1] + (centroid[1] - v[1]) * factor)

    for vertex, key in ((A, "angle_A_label"), (B, "angle_B_label"), (C, "angle_C_label")):
        if params.get(key):
            px, py = inset(vertex)
            d.add(_label(px, py, params[key], size=8))

    _not_to_scale(d)
    return d


def draw_vector_triangle(params: dict) -> Drawing:
    """Triangle OAB with position vectors a = OA, b = OB, and a point P on AB
    at a given ratio AP:PB, for geometric-vector questions."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    O, A, B = (30, 25), (65, 108), (175, 25)
    d.add(Line(O[0], O[1], A[0], A[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(O[0], O[1], B[0], B[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(A[0], A[1], B[0], B[1], strokeColor=INK, strokeWidth=1.2))

    m, n = params["ratio"]
    t = m / (m + n)
    P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)
    d.add(Circle(P[0], P[1], 1.8, strokeColor=INK, fillColor=INK))
    d.add(_label(P[0], P[1] + 8, params["point_label"], size=8))

    d.add(_label((O[0] + A[0]) / 2 - 10, (O[1] + A[1]) / 2, params["a_label"], anchor="end", size=9))
    d.add(_label((O[0] + B[0]) / 2, O[1] - 14, params["b_label"], size=9))
    d.add(_label(O[0] - 8, O[1] - 10, params["origin_label"], size=8, anchor="end"))
    return d


def _circle_point(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def draw_circle_angle_centre(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 74, 42
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    A, B, C = _circle_point(cx, cy, r, 200), _circle_point(cx, cy, r, 340), _circle_point(cx, cy, r, 90)
    d.add(Line(cx, cy, A[0], A[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(cx, cy, B[0], B[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(C[0], C[1], A[0], A[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(C[0], C[1], B[0], B[1], strokeColor=INK, strokeWidth=1))
    d.add(Circle(cx, cy, 1.5, strokeColor=INK, fillColor=INK))
    d.add(_label(cx, cy - 16, params["centre_label"], size=8))
    d.add(_label(C[0], C[1] - 16, params["circumference_label"], size=8))
    _not_to_scale(d)
    return d


def draw_circle_semicircle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 76, 42
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    A, B = (cx - r, cy), (cx + r, cy)
    C = _circle_point(cx, cy, r, 125)
    d.add(Line(A[0], A[1], B[0], B[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(A[0], A[1], C[0], C[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(B[0], B[1], C[0], C[1], strokeColor=INK, strokeWidth=1))
    d.add(_label(C[0], C[1] + 10, params["apex_label"], size=8))
    d.add(_label(A[0] + 4, A[1] + 8, params["angle_a_label"], size=7, anchor="start"))
    d.add(_label(B[0] - 4, B[1] + 8, params["angle_b_label"], size=7, anchor="end"))
    _not_to_scale(d)
    return d


def draw_circle_cyclic_quad(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 70, 42
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    A, B = _circle_point(cx, cy, r, 150), _circle_point(cx, cy, r, 60)
    C, Dp = _circle_point(cx, cy, r, -40), _circle_point(cx, cy, r, 220)
    for p, q in ((A, B), (B, C), (C, Dp), (Dp, A)):
        d.add(Line(p[0], p[1], q[0], q[1], strokeColor=INK, strokeWidth=1))
    d.add(_label(A[0] - 8, A[1] + 4, params["angle_A_label"], size=7, anchor="end"))
    d.add(_label(C[0] + 8, C[1] - 6, params["angle_C_label"], size=7, anchor="start"))
    _not_to_scale(d)
    return d


def draw_circle_two_tangents(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 60, 34
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    A, B = _circle_point(cx, cy, r, 145), _circle_point(cx, cy, r, 35)
    T = (cx, cy + r + 38)
    d.add(Line(cx, cy, A[0], A[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(cx, cy, B[0], B[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(T[0], T[1], A[0], A[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(T[0], T[1], B[0], B[1], strokeColor=INK, strokeWidth=1.2))
    d.add(_label(T[0], T[1] + 12, params["external_label"], size=8))
    d.add(_label(cx, cy - 14, params["centre_label"], size=8))
    _not_to_scale(d)
    return d


def _draw_axes(d: Drawing, ox: float, oy: float, axis_len_x: float, axis_len_y: float) -> None:
    d.add(Line(ox, oy, ox + axis_len_x, oy, strokeColor=INK, strokeWidth=1))
    d.add(Line(ox, oy, ox, oy + axis_len_y, strokeColor=INK, strokeWidth=1))
    d.add(_label(ox + axis_len_x + 6, oy - 2, "x", anchor="start", size=8))
    d.add(_label(ox - 6, oy + axis_len_y + 4, "y", anchor="end", size=8))


def draw_parabola(params: dict) -> Drawing:
    """A schematic upward parabola (not to scale) with its turning point marked."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ox, oy = 25, 20
    axis_len_x, axis_len_y = DIAGRAM_WIDTH - 45, DIAGRAM_HEIGHT - 35
    _draw_axes(d, ox, oy, axis_len_x, axis_len_y)

    vx, vy = ox + axis_len_x * 0.55, oy + 16
    half_width, max_rise = axis_len_x * 0.42, axis_len_y * 0.85
    n = 16
    points: list[float] = []
    for i in range(-n, n + 1):
        t = i / n
        x = vx + t * half_width
        y = min(vy + max_rise * (t**2), oy + axis_len_y)
        points.extend([x, y])
    d.add(PolyLine(points, strokeColor=INK, strokeWidth=1.2))
    d.add(Circle(vx, vy, 2, strokeColor=INK, fillColor=INK))
    d.add(_label(vx, vy - 12, params["vertex_label"], size=8))
    _not_to_scale(d)
    return d


def draw_linear_graph_pair(params: dict) -> Drawing:
    """Two schematic straight lines (not to scale) crossing at a marked point."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ox, oy = 25, 20
    axis_len_x, axis_len_y = DIAGRAM_WIDTH - 45, DIAGRAM_HEIGHT - 35
    _draw_axes(d, ox, oy, axis_len_x, axis_len_y)

    ix, iy = ox + axis_len_x * 0.55, oy + axis_len_y * 0.55
    d.add(Line(ox + 5, oy + axis_len_y * 0.15, ox + axis_len_x - 5, oy + axis_len_y * 0.75, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(ox + 5, oy + axis_len_y * 0.85, ox + axis_len_x - 15, oy + 5, strokeColor=INK, strokeWidth=1.2))
    d.add(Circle(ix, iy, 2, strokeColor=INK, fillColor=INK))
    d.add(_label(ix + 10, iy + 6, params["intersection_label"], anchor="start", size=8))
    d.add(_label(ox + axis_len_x * 0.88, oy + axis_len_y * 0.7, params["label1"], size=8))
    d.add(_label(ox + axis_len_x * 0.25, oy + axis_len_y * 0.92, params["label2"], size=8))
    _not_to_scale(d)
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
    "trig_triangle": draw_trig_triangle,
    "general_triangle": draw_general_triangle,
    "vector_triangle": draw_vector_triangle,
    "circle_angle_centre": draw_circle_angle_centre,
    "circle_semicircle": draw_circle_semicircle,
    "circle_cyclic_quad": draw_circle_cyclic_quad,
    "circle_two_tangents": draw_circle_two_tangents,
    "parabola": draw_parabola,
    "linear_graph_pair": draw_linear_graph_pair,
}


def render_diagram(spec: DiagramSpec) -> Drawing:
    try:
        renderer = _RENDERERS[spec.kind]
    except KeyError:
        raise ValueError(f"Unknown diagram kind: {spec.kind!r}") from None
    return renderer(spec.params)
