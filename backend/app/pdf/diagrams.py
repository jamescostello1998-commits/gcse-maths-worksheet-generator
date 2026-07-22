"""Small, dependency-free ReportLab diagrams for Geometry (and some Algebra
graph) worksheet questions.

Each `draw_xxx(params)` function renders one diagram *kind* to a fixed-size
`Drawing` using the exact numeric values already used to build the matching
question's prompt/steps (no separate randomness). `render_diagram` dispatches
a `DiagramSpec` (see app/core/models.py) to the matching renderer.
"""

import math
import re
from typing import Callable

from reportlab.graphics.shapes import ArcPath, Circle, Drawing, Group, Line, PolyLine, Polygon, Rect, String, Wedge
from reportlab.pdfbase.pdfmetrics import stringWidth

from app.core.models import DiagramSpec
from app.pdf.styles import ACCENT, CHART_COLORS, GRID, HIGHLIGHT, INK, MUTED, PAPER

DIAGRAM_WIDTH = 200
DIAGRAM_HEIGHT = 130

_LABEL_SIZE = 9
_LABEL_FONT = "Helvetica"
_LABEL_FONT_ITALIC = "Helvetica-Oblique"


# Matches a lone x or n not glued to another letter (so "Green"/"box" are left
# alone) - mirrors app/pdf/mathtext.py's _VARIABLE_RE exactly.
_VARIABLE_RE = re.compile(r"(?<![A-Za-z])[xn](?![A-Za-z])")

# A bare numeric fraction like "3/4" or "-3/4" within a label is drawn as a
# stacked numerator/line/denominator (a vinculum) instead of inline "3/4" -
# mirrors app/pdf/renderer.py's handling of the same pattern in prose text.
_FRACTION_RE = re.compile(r"(-?)(\d+)/(\d+)")
_FRACTION_SCALE = 0.72
_FRACTION_PAD = 1.5


def _text_runs(text: str) -> list[tuple[str, str]]:
    """Split plain (non-fraction) text into (substring, fontName) runs,
    italicising the algebraic variables x and n (as standalone letters only,
    so words like "Green" or "box" are left alone) so diagram labels match
    standard maths typesetting (mirrors app/pdf/mathtext.py's handling of
    Paragraph text)."""
    runs: list[tuple[str, str]] = []
    pos = 0
    for m in _VARIABLE_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos : m.start()], _LABEL_FONT))
        runs.append((m.group(0), _LABEL_FONT_ITALIC))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], _LABEL_FONT))
    return runs


def _math_runs(text: str) -> list[tuple]:
    """Split label text into runs: `("text", substring, font)` for ordinary
    (x/n-italicised) text, or `("frac", sign, num, den)` for a bare numeric
    fraction to be drawn as a stacked vinculum."""
    runs: list[tuple] = []
    pos = 0
    for m in _FRACTION_RE.finditer(text):
        if m.start() > pos:
            runs.extend(("text", sub, font) for sub, font in _text_runs(text[pos : m.start()]))
        sign, num, den = m.groups()
        runs.append(("frac", sign, num, den))
        pos = m.end()
    if pos < len(text):
        runs.extend(("text", sub, font) for sub, font in _text_runs(text[pos:]))
    return runs


def _fraction_width(num: str, den: str, size: float) -> float:
    frac_size = size * _FRACTION_SCALE
    return max(stringWidth(num, _LABEL_FONT, frac_size), stringWidth(den, _LABEL_FONT, frac_size)) + 2 * _FRACTION_PAD


def _run_width(run: tuple, size: float) -> float:
    if run[0] == "text":
        return stringWidth(run[1], run[2], size)
    _, sign, num, den = run
    sign_width = stringWidth("-", _LABEL_FONT, size) if sign else 0.0
    return sign_width + _fraction_width(num, den, size)


def _draw_fraction(group: Group, x: float, y: float, sign: str, num: str, den: str, size: float, color) -> None:
    """Draw a stacked num/line/denom fraction (plus a leading sign, if any)
    with its left edge at x and its baseline at y."""
    cursor = x
    if sign:
        group.add(String(cursor, y, sign, textAnchor="start", fontSize=size, fillColor=color, fontName=_LABEL_FONT))
        cursor += stringWidth(sign, _LABEL_FONT, size)
    frac_size = size * _FRACTION_SCALE
    width = _fraction_width(num, den, size)
    mid_x = cursor + width / 2
    line_y = y + size * 0.32
    group.add(String(mid_x, line_y + 1.5, num, textAnchor="middle", fontSize=frac_size, fillColor=color, fontName=_LABEL_FONT))
    group.add(String(mid_x, line_y - frac_size - 0.5, den, textAnchor="middle", fontSize=frac_size, fillColor=color, fontName=_LABEL_FONT))
    group.add(Line(
        cursor + _FRACTION_PAD * 0.5, line_y, cursor + width - _FRACTION_PAD * 0.5, line_y,
        strokeColor=color, strokeWidth=0.7,
    ))


def _label(x: float, y: float, text: str, anchor: str = "middle", color=INK, size: int = _LABEL_SIZE) -> Group:
    runs = _math_runs(str(text))
    total_width = sum(_run_width(r, size) for r in runs)
    if anchor == "middle":
        cursor = x - total_width / 2
    elif anchor == "end":
        cursor = x - total_width
    else:
        cursor = x

    group = Group()
    for run in runs:
        if run[0] == "text":
            _, sub, font = run
            group.add(String(cursor, y, sub, textAnchor="start", fontSize=size, fillColor=color, fontName=font))
            cursor += stringWidth(sub, font, size)
        else:
            _, sign, num, den = run
            _draw_fraction(group, cursor, y, sign, num, den, size, color)
            cursor += _run_width(run, size)
    return group


def _angle_arc(cx: float, cy: float, angle1_deg: float, angle2_deg: float, radius: float = 12, color=INK) -> ArcPath:
    """An unfilled arc marking the (non-reflex) angle swept between two rays
    from (cx, cy) at angle1_deg and angle2_deg - standard maths convention,
    degrees measured counterclockwise from the positive x-axis."""
    diff = (angle2_deg - angle1_deg) % 360
    start, sweep = (angle1_deg, diff) if diff <= 180 else (angle2_deg, 360 - diff)
    arc = ArcPath(strokeColor=color, fillColor=None, strokeWidth=0.9)
    arc.addArc(cx, cy, radius, start, start + sweep, moveTo=True)
    return arc


def _vertex_angle_arc(vertex: tuple, other1: tuple, other2: tuple, radius: float = 12, color=INK) -> ArcPath:
    """The arc marking the angle at `vertex` between the two rays
    vertex->other1 and vertex->other2 (e.g. two sides of a triangle, or two
    radii/chords, meeting at that vertex)."""
    angle1 = math.degrees(math.atan2(other1[1] - vertex[1], other1[0] - vertex[0]))
    angle2 = math.degrees(math.atan2(other2[1] - vertex[1], other2[0] - vertex[0]))
    return _angle_arc(vertex[0], vertex[1], angle1, angle2, radius=radius, color=color)


def _sector_arc_for_label(
    cx: float, cy: float, ray_angles_deg: list[float], label_dx: float, label_dy: float,
    radius: float = 12, color=INK,
) -> ArcPath:
    """Given several rays from (cx, cy) and a label placed at offset
    (label_dx, label_dy) from that point, find which angular sector (the gap
    between two consecutive rays) the label sits in and return its arc -
    used where the labelled angle isn't one simple vertex-to-vertex pair
    (e.g. a transversal crossing two parallel lines)."""
    label_angle = math.degrees(math.atan2(label_dy, label_dx)) % 360
    sorted_angles = sorted(a % 360 for a in ray_angles_deg)
    for i in range(len(sorted_angles)):
        a1 = sorted_angles[i]
        a2 = sorted_angles[(i + 1) % len(sorted_angles)]
        span = (a2 - a1) % 360 or 360
        if (label_angle - a1) % 360 <= span:
            return _angle_arc(cx, cy, a1, a2, radius=radius, color=color)
    return _angle_arc(cx, cy, sorted_angles[0], sorted_angles[1], radius=radius, color=color)


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
    inner_text = f"{params['inner_labels'][0]} × {params['inner_labels'][1]}"
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
    d.add(_label(x0 + rw / 2, y0 - 14, params["width_label"]))
    d.add(_label(x0 - 10, y0 + rh / 2, params["height_label"], anchor="end"))
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
        d.add(_angle_arc(cx, cy, running, running + v, radius=15))
        if v < 20:
            label_radius = radius + 13  # narrow wedges: place the label just beyond the ray tips
        elif v < 35:
            label_radius = radius * 0.85
        else:
            label_radius = radius * 0.78
        mid_rad = math.radians(running + v / 2)
        lx, ly = cx + label_radius * math.cos(mid_rad), cy + label_radius * math.sin(mid_rad)
        d.add(_label(lx, ly, lbl, size=7.5))
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

    n = len(vertices)
    for i, (vertex, lbl) in enumerate(zip(vertices, params["angle_labels"])):
        other1, other2 = vertices[(i - 1) % n], vertices[(i + 1) % n]
        d.add(_vertex_angle_arc(vertex, other1, other2, radius=9))
        vx, vy = vertex
        # Pull wide algebraic labels (e.g. "(2x + 98)°") further in toward the
        # centroid than short ones like "31°" or "x", so they have more clearance
        # from the two sloped edges either side of the vertex - a fixed 0.58 inset
        # only worked while every label was short enough to fit near the vertex.
        width = stringWidth(str(lbl), _LABEL_FONT, 7.5)
        inset = min(0.8, 0.5 + width / 220)
        lx, ly = vx + (cx - vx) * inset, vy + (cy - vy) * inset
        d.add(_label(lx, ly, lbl, size=7.5))
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

    trans_angle = math.degrees(math.atan2(dy, dx))
    ray_angles = [0, 180, trans_angle, trans_angle + 180]

    offsets = {
        "corresponding": ((16, 12), (16, 12)),
        "alternate": ((16, -20), (-34, 14)),
        "co_interior": ((16, -20), (16, 14)),
    }
    (kx, ky), (ux2, uy2) = offsets[params["relation"]]
    d.add(_sector_arc_for_label(ix_top, y_top, ray_angles, kx, ky, radius=10))
    d.add(_sector_arc_for_label(ix_bottom, y_bottom, ray_angles, ux2, uy2, radius=10))
    # Anchor away from the vertex based on which side of it the label sits, so a
    # wide algebraic label (e.g. "(5x + 39)°") grows further from the transversal
    # instead of extending back across it - a fixed anchor="start" only worked
    # while every label was as short as "x".
    known_anchor = "start" if kx >= 0 else "end"
    unknown_anchor = "start" if ux2 >= 0 else "end"
    d.add(_label(ix_top + kx, y_top + ky, params["known_label"], anchor=known_anchor, size=8))
    d.add(_label(ix_bottom + ux2, y_bottom + uy2, params["unknown_label"], anchor=unknown_anchor, size=8))
    return d


def draw_exterior_triangle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    A, B, C = (35, 30), (150, 30), (75, 100)
    d.add(Polygon([A[0], A[1], B[0], B[1], C[0], C[1]], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    ext_x = B[0] + (B[0] - A[0]) * 0.4
    ext_y = B[1] + (B[1] - A[1]) * 0.4
    ext_point = (ext_x, ext_y)
    d.add(Line(B[0], B[1], ext_x, ext_y, strokeColor=INK, strokeWidth=1.2))

    d.add(_vertex_angle_arc(A, B, C, radius=9))
    d.add(_vertex_angle_arc(B, A, C, radius=9))
    d.add(_vertex_angle_arc(B, C, ext_point, radius=14))

    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)

    def _inset(vertex, factor=0.7):
        return (vertex[0] + (centroid[0] - vertex[0]) * factor, vertex[1] + (centroid[1] - vertex[1]) * factor)

    ax, ay = _inset(A)
    bx, by = _inset(B)
    d.add(_label(ax, ay, params["interior1_label"], size=8))
    d.add(_label(bx, by, params["interior2_label"], size=8))
    d.add(_label(B[0] + 20, B[1] + 10, params["exterior_label"], anchor="start", size=8))
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

    d.add(_vertex_angle_arc(vertices[0], vertices[-1], vertices[1], radius=8))
    vx, vy = vertices[0]
    lx, ly = vx + (cx - vx) * 0.45, vy + (cy - vy) * 0.45
    d.add(_label(lx, ly, params["marked_angle_label"], size=7.5))
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
    d.add(_vertex_angle_arc(B, A, C, radius=9))
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

    def inset(v, factor=0.55):
        return (v[0] + (centroid[0] - v[0]) * factor, v[1] + (centroid[1] - v[1]) * factor)

    for vertex, other1, other2, key in (
        (A, B, C, "angle_A_label"), (B, A, C, "angle_B_label"), (C, A, B, "angle_C_label"),
    ):
        if params.get(key):
            d.add(_vertex_angle_arc(vertex, other1, other2, radius=8))
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
    d.add(_vertex_angle_arc((cx, cy), A, B, radius=14))
    d.add(_vertex_angle_arc(C, A, B, radius=10))
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
    d.add(_vertex_angle_arc(C, A, B, radius=10))
    d.add(_vertex_angle_arc(A, B, C, radius=11))
    d.add(_vertex_angle_arc(B, A, C, radius=11))
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
    d.add(_vertex_angle_arc(A, Dp, B, radius=10))
    d.add(_vertex_angle_arc(C, B, Dp, radius=10))
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
    d.add(_vertex_angle_arc(T, A, B, radius=14))
    d.add(_vertex_angle_arc((cx, cy), A, B, radius=14))
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


GRAPH_WIDTH = 210
GRAPH_HEIGHT = 210

_GRAPH_MARGIN_L = 26
_GRAPH_MARGIN_R = 10
_GRAPH_MARGIN_T = 10
_GRAPH_MARGIN_B = 22


def _nice_tick_step(lo: float, hi: float) -> float:
    span = hi - lo
    if span <= 10:
        return 1
    if span <= 20:
        return 2
    if span <= 50:
        return 5
    return 10


def _draw_scaled_axes(
    d: Drawing, x_min: float, x_max: float, y_min: float, y_max: float,
    x_axis_label: str = "x", y_axis_label: str = "y",
) -> Callable[[float, float], tuple[float, float]]:
    """Draw a real-scale, gridded, numbered pair of axes into `d` and return
    the (x, y) -> (pixel_x, pixel_y) transform so callers can plot points/
    curves on the same scale."""
    # The axes must always cross at the true origin, so the visible window
    # always includes x=0 and y=0 - otherwise a curve/table that happens to
    # sit entirely on one side of an axis (e.g. y = x^2 + 4, never negative)
    # would have that axis drawn at the data's edge instead of at 0.
    x_min, x_max = min(x_min, 0), max(x_max, 0)
    y_min, y_max = min(y_min, 0), max(y_max, 0)

    plot_w = d.width - _GRAPH_MARGIN_L - _GRAPH_MARGIN_R
    plot_h = d.height - _GRAPH_MARGIN_T - _GRAPH_MARGIN_B

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = _GRAPH_MARGIN_L + (x - x_min) / (x_max - x_min) * plot_w
        py = _GRAPH_MARGIN_B + (y - y_min) / (y_max - y_min) * plot_h
        return px, py

    # Fine unit gridlines.
    x = math.ceil(x_min)
    while x <= x_max + 1e-9:
        px, y0 = to_px(x, y_min)
        _, y1 = to_px(x, y_max)
        d.add(Line(px, y0, px, y1, strokeColor=GRID, strokeWidth=0.4))
        x += 1
    y = math.ceil(y_min)
    while y <= y_max + 1e-9:
        x0, py = to_px(x_min, y)
        x1, _ = to_px(x_max, y)
        d.add(Line(x0, py, x1, py, strokeColor=GRID, strokeWidth=0.4))
        y += 1

    # Bold axis lines through the origin (guaranteed in range by the clamp above).
    axis_x0 = 0
    axis_y0 = 0
    ax0, ay0 = to_px(x_min, axis_y0)
    ax1, _ = to_px(x_max, axis_y0)
    d.add(Line(ax0, ay0, ax1, ay0, strokeColor=INK, strokeWidth=1.1))
    bx0, by0 = to_px(axis_x0, y_min)
    _, by1 = to_px(axis_x0, y_max)
    d.add(Line(bx0, by0, bx0, by1, strokeColor=INK, strokeWidth=1.1))

    # Numbered ticks, spaced out to avoid clutter on wide ranges.
    x_step = _nice_tick_step(x_min, x_max)
    xt = math.ceil(x_min / x_step) * x_step
    while xt <= x_max + 1e-9:
        if abs(xt) > 1e-9:
            px, py = to_px(xt, axis_y0)
            d.add(_label(px, py - 9, str(int(xt)), size=6.5))
        xt += x_step
    y_step = _nice_tick_step(y_min, y_max)
    yt = math.ceil(y_min / y_step) * y_step
    while yt <= y_max + 1e-9:
        if abs(yt) > 1e-9:
            px, py = to_px(axis_x0, yt)
            d.add(_label(px - 6, py - 2, str(int(yt)), anchor="end", size=6.5))
        yt += y_step

    d.add(_label(ax1 + 4, ay0 - 2, x_axis_label, anchor="start", size=8))
    d.add(_label(bx0 - 4, by1 + 6, y_axis_label, anchor="end", size=8))
    return to_px


def _fn_value(kind: str, x: float, params: dict) -> float:
    if kind == "linear":
        return params["m"] * x + params["c"]
    if kind == "quadratic":
        return params["a"] * x**2 + params["b"] * x + params["c"]
    if kind == "cubic":
        return params["a"] * x**3 + params["b"] * x
    if kind == "reciprocal":
        return params["a"] / x
    raise ValueError(f"unknown function graph kind: {kind!r}")


def draw_function_graph(params: dict) -> Drawing:
    """A real-scale, gridded plot of a linear/quadratic/cubic/reciprocal
    function. If params['blank'] is True, only the axes are drawn (used for
    the question page of a 'plot this graph' question, so the axes are
    always provided); otherwise the curve (and any table_points) are drawn
    too (used for that same question's worked solution, or as the stimulus
    diagram for a 'read this graph' question)."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    kind = params["kind"]
    x_min, x_max = params["x_min"], params["x_max"]
    y_min, y_max = params["y_min"], params["y_max"]
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max, params.get("x_label", "x"), params.get("y_label", "y"))

    if not params.get("blank", False):
        if kind == "reciprocal":
            gap = 0.2
            branches = [(x_min, -gap), (gap, x_max)] if x_min < 0 < x_max else [(x_min, x_max)]
        else:
            branches = [(x_min, x_max)]

        for lo, hi in branches:
            n = 40
            pts: list[float] = []
            for i in range(n + 1):
                x = lo + (hi - lo) * i / n
                y = max(min(_fn_value(kind, x, params), y_max), y_min)
                px, py = to_px(x, y)
                pts.extend([px, py])
            d.add(PolyLine(pts, strokeColor=INK, strokeWidth=1.3))

        for tx, ty in params.get("table_points", []):
            px, py = to_px(tx, ty)
            d.add(Circle(px, py, 2, strokeColor=INK, fillColor=INK))

    return d


def draw_piecewise_graph(params: dict) -> Drawing:
    """A real-scale, gridded time-series graph (distance-time / velocity-time)
    made of straight segments through params['points'] (a list of (time,
    value) pairs starting at t=0). Blank axes only if params['blank']."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_max, y_max = params["x_max"], params["y_max"]
    to_px = _draw_scaled_axes(d, 0, x_max, 0, y_max, params.get("x_label", "Time"), params.get("y_label", "Value"))

    if not params.get("blank", False):
        pts: list[float] = []
        for t, v in params["points"]:
            px, py = to_px(t, v)
            pts.extend([px, py])
        d.add(PolyLine(pts, strokeColor=INK, strokeWidth=1.3))
        for t, v in params["points"]:
            px, py = to_px(t, v)
            d.add(Circle(px, py, 1.8, strokeColor=INK, fillColor=INK))

    return d


_TRANSFORM_BASE_SHAPE = [(-3, 3), (-2, 0.5), (-1, -1), (0, -1.5), (1, -1), (2, 0.5), (3, 3)]


def _apply_transform(kind: str, shift: float, pt: tuple[float, float]) -> tuple[float, float]:
    x, y = pt
    if kind == "translate_up":
        return (x, y + shift)
    if kind == "translate_down":
        return (x, y - shift)
    if kind == "translate_left":
        return (x - shift, y)
    if kind == "translate_right":
        return (x + shift, y)
    if kind == "reflect_x":
        return (x, -y)
    if kind == "reflect_y":
        return (-x, y)
    raise ValueError(f"unknown graph transform: {kind!r}")


def draw_graph_transformation(params: dict) -> Drawing:
    """A schematic (not to scale) generic curve y = f(x), dashed, alongside
    its transformed image, solid, on the same axes."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_min, x_max, y_min, y_max = -6, 6, -6, 8
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max)

    def clamp(pt: tuple[float, float]) -> tuple[float, float]:
        x, y = pt
        return (max(min(x, x_max), x_min), max(min(y, y_max), y_min))

    orig_pts: list[float] = []
    for pt in _TRANSFORM_BASE_SHAPE:
        px, py = to_px(*clamp(pt))
        orig_pts.extend([px, py])
    d.add(PolyLine(orig_pts, strokeColor=MUTED, strokeWidth=1.1, strokeDashArray=[3, 2]))

    trans_pts: list[float] = []
    for pt in _TRANSFORM_BASE_SHAPE:
        tpt = _apply_transform(params["transform"], params.get("shift", 0), pt)
        px, py = to_px(*clamp(tpt))
        trans_pts.extend([px, py])
    d.add(PolyLine(trans_pts, strokeColor=INK, strokeWidth=1.3))

    d.add(_label(8, GRAPH_HEIGHT - 10, params.get("original_label", "y = f(x)"), anchor="start", color=MUTED, size=7))
    d.add(_label(8, GRAPH_HEIGHT - 20, params.get("transformed_label", ""), anchor="start", color=INK, size=7))
    _not_to_scale(d, x=GRAPH_WIDTH / 2, y=6)
    return d


def draw_tree_diagram(params: dict) -> Drawing:
    """A two-stage probability tree. stage1 = [(label, prob_str), ...];
    stage2 = one list of (label, prob_str) branches per stage1 node;
    leaf_probs (optional) = matching nested list of combined-outcome
    probability strings shown at each leaf."""
    stage1: list[tuple[str, str]] = params["stage1"]
    stage2: list[list[tuple[str, str]]] = params["stage2"]
    leaf_probs: list[list[str]] | None = params.get("leaf_probs")

    branch_counts = [len(b) for b in stage2]
    total_leaves = sum(branch_counts)
    width = 260
    height = max(120, total_leaves * 24 + 16)
    d = Drawing(width, height)

    root_x, root_y = 12.0, height / 2
    x1 = width * 0.32
    x2 = width * 0.62
    x3 = width * 0.86

    leaf_ys: list[list[float]] = []
    cursor = 8.0
    for count in branch_counts:
        ys = [cursor + i * 22 + 11 for i in range(count)]
        leaf_ys.append(ys)
        cursor += count * 22 + 8

    node1_ys = [sum(ys) / len(ys) for ys in leaf_ys]

    for i, ((label1, prob1), y1) in enumerate(zip(stage1, node1_ys)):
        d.add(Line(root_x, root_y, x1, y1, strokeColor=INK, strokeWidth=1.1))
        d.add(_label((root_x + x1) / 2, (root_y + y1) / 2 + 6, prob1, size=7))
        d.add(_label(x1 + 4, y1 + 3, label1, anchor="start", size=7.5))

        for j, ((label2, prob2), y2) in enumerate(zip(stage2[i], leaf_ys[i])):
            d.add(Line(x1, y1, x2, y2, strokeColor=INK, strokeWidth=1.1))
            d.add(_label((x1 + x2) / 2, (y1 + y2) / 2 + 6, prob2, size=7))
            d.add(_label(x2 + 4, y2 + 3, label2, anchor="start", size=7.5))
            if leaf_probs is not None:
                d.add(Line(x2, y2, x3, y2, strokeColor=MUTED, strokeWidth=0.5, strokeDashArray=[2, 2]))
                d.add(_label(x3 + 4, y2 + 3, leaf_probs[i][j], anchor="start", color=ACCENT, size=7))

    d.add(Circle(root_x, root_y, 1.8, strokeColor=INK, fillColor=INK))
    return d


def draw_two_way_table(params: dict) -> Drawing:
    """A grid table with row_labels down the side and col_labels across the
    top (typically including a trailing 'Total' row/column), filled with
    params['cells'] (a row_labels x col_labels 2D list of strings; blank
    entries render as empty cells for a 'complete the table' question)."""
    row_labels: list[str] = params["row_labels"]
    col_labels: list[str] = params["col_labels"]
    cells: list[list[str]] = params["cells"]

    header_w, cell_w, cell_h = 66, 44, 22
    n_rows, n_cols = len(row_labels), len(col_labels)
    width = header_w + cell_w * n_cols
    height = cell_h * (n_rows + 1)
    d = Drawing(width, height)

    top_y = height - cell_h
    d.add(Rect(0, top_y, header_w, cell_h, strokeColor=INK, fillColor=None, strokeWidth=0.8))
    for j, col_label in enumerate(col_labels):
        x0 = header_w + j * cell_w
        d.add(Rect(x0, top_y, cell_w, cell_h, strokeColor=INK, fillColor=None, strokeWidth=0.8))
        d.add(_label(x0 + cell_w / 2, top_y + cell_h / 2 - 3, col_label, size=7.5))

    for i, row_label in enumerate(row_labels):
        y0 = top_y - cell_h * (i + 1)
        d.add(Rect(0, y0, header_w, cell_h, strokeColor=INK, fillColor=None, strokeWidth=0.8))
        d.add(_label(header_w / 2, y0 + cell_h / 2 - 3, row_label, size=7.5))
        for j in range(n_cols):
            x0 = header_w + j * cell_w
            d.add(Rect(x0, y0, cell_w, cell_h, strokeColor=INK, fillColor=None, strokeWidth=0.8))
            d.add(_label(x0 + cell_w / 2, y0 + cell_h / 2 - 3, str(cells[i][j]), size=8))

    return d


def draw_sample_space_diagram(params: dict) -> Drawing:
    """A grid of row_values x col_values (e.g. two dice), filled with
    params['cells'] outcome text; params['highlight'] is an optional list of
    [row_index, col_index] pairs to shade (the favourable outcomes)."""
    row_values: list = params["row_values"]
    col_values: list = params["col_values"]
    cells: list[list[str]] = params["cells"]
    highlight = {tuple(p) for p in params.get("highlight", [])}

    header, cell = 24, 22
    n_rows, n_cols = len(row_values), len(col_values)
    width = header + cell * n_cols
    height = header + cell * n_rows
    d = Drawing(width, height)

    top_y = height - header
    d.add(Rect(0, top_y, header, header, strokeColor=INK, fillColor=None, strokeWidth=0.8))
    for j, cv in enumerate(col_values):
        x0 = header + j * cell
        d.add(Rect(x0, top_y, cell, header, strokeColor=INK, fillColor=None, strokeWidth=0.8))
        d.add(_label(x0 + cell / 2, top_y + header / 2 - 3, str(cv), size=7.5))

    for i, rv in enumerate(row_values):
        y0 = top_y - cell * (i + 1)
        d.add(Rect(0, y0, header, cell, strokeColor=INK, fillColor=None, strokeWidth=0.8))
        d.add(_label(header / 2, y0 + cell / 2 - 3, str(rv), size=7.5))
        for j in range(n_cols):
            x0 = header + j * cell
            fill = HIGHLIGHT if (i, j) in highlight else None
            d.add(Rect(x0, y0, cell, cell, strokeColor=INK, fillColor=fill, strokeWidth=0.6))
            d.add(_label(x0 + cell / 2, y0 + cell / 2 - 3, str(cells[i][j]), size=7.5))

    return d


# Two-circle Venn diagram: fixed equal-radius layout, overlap centred in a
# bounding "universal set" rectangle. Region keys used throughout:
# "a_only", "b_only", "both" (the A-cap-B lens), "neither" (inside the
# rectangle, outside both circles).
_VENN_CX_A, _VENN_CX_B, _VENN_CY, _VENN_R = 82.0, 138.0, 68.0, 44.0
_VENN_RECT = (8.0, 8.0, 212.0, 132.0)  # x0, y0, x1, y1


def _venn_half_angle() -> float:
    d = _VENN_CX_B - _VENN_CX_A
    return math.degrees(math.acos((d / 2) / _VENN_R))


def _venn_lens_path(color) -> ArcPath:
    half = _venn_half_angle()
    path = ArcPath(fillColor=color, strokeColor=None)
    path.addArc(_VENN_CX_A, _VENN_CY, _VENN_R, -half, half, moveTo=True)
    path.addArc(_VENN_CX_B, _VENN_CY, _VENN_R, 180 - half, 180 + half, moveTo=False)
    path.closePath()
    return path


def _venn_a_only_path(color) -> ArcPath:
    half = _venn_half_angle()
    path = ArcPath(fillColor=color, strokeColor=None)
    path.addArc(_VENN_CX_A, _VENN_CY, _VENN_R, half, 360 - half, moveTo=True)
    path.addArc(_VENN_CX_B, _VENN_CY, _VENN_R, 180 - half, 180 + half, moveTo=False, reverse=True)
    path.closePath()
    return path


def _venn_b_only_path(color) -> ArcPath:
    half = _venn_half_angle()
    path = ArcPath(fillColor=color, strokeColor=None)
    path.addArc(_VENN_CX_B, _VENN_CY, _VENN_R, 180 + half, 540 - half, moveTo=True)
    path.addArc(_VENN_CX_A, _VENN_CY, _VENN_R, -half, half, moveTo=False, reverse=True)
    path.closePath()
    return path


def draw_venn_diagram(params: dict) -> Drawing:
    """A two-circle Venn diagram (sets A and B inside a universal-set
    rectangle). params:
    - "labels": [name_a, name_b] (default ["A", "B"]) - the circle names.
    - "universal_label": corner label for the universal set (default "S").
    - "region_text": dict with optional keys "a_only"/"b_only"/"both"/
      "neither" -> string shown inside that region (element counts, an
      algebraic expression, etc.) - used by the notation/algebra/probability
      Venn topics.
    - "shade": list of region keys to fill (any of "a_only"/"b_only"/"both"/
      "neither") - used by the shading topic. Filling is done per-region
      (not per-name like "A" or "A union B") so any named region from the
      real specs can be built by shading the right combination of these
      four atomic regions.
    """
    labels = params.get("labels", ["A", "B"])
    universal_label = params.get("universal_label", "S")
    region_text: dict = params.get("region_text", {})
    shade = set(params.get("shade", []))

    x0, y0, x1, y1 = _VENN_RECT
    d = Drawing(x1 + 8, y1 + 8)

    if "neither" in shade:
        d.add(Rect(x0, y0, x1 - x0, y1 - y0, fillColor=HIGHLIGHT, strokeColor=None))
        d.add(Circle(_VENN_CX_A, _VENN_CY, _VENN_R, fillColor=PAPER, strokeColor=None))
        d.add(Circle(_VENN_CX_B, _VENN_CY, _VENN_R, fillColor=PAPER, strokeColor=None))
    if "both" in shade:
        d.add(_venn_lens_path(HIGHLIGHT))
    if "a_only" in shade:
        d.add(_venn_a_only_path(HIGHLIGHT))
    if "b_only" in shade:
        d.add(_venn_b_only_path(HIGHLIGHT))

    d.add(Rect(x0, y0, x1 - x0, y1 - y0, fillColor=None, strokeColor=INK, strokeWidth=0.9))
    d.add(Circle(_VENN_CX_A, _VENN_CY, _VENN_R, fillColor=None, strokeColor=INK, strokeWidth=0.9))
    d.add(Circle(_VENN_CX_B, _VENN_CY, _VENN_R, fillColor=None, strokeColor=INK, strokeWidth=0.9))

    d.add(_label(x0 + 8, y1 - 10, universal_label, anchor="start", size=9))
    d.add(_label(_VENN_CX_A - 20, _VENN_CY + _VENN_R - 12, str(labels[0]), size=9))
    d.add(_label(_VENN_CX_B + 20, _VENN_CY + _VENN_R - 12, str(labels[1]), size=9))

    region_positions = {
        "a_only": (_VENN_CX_A - 22, _VENN_CY - 4),
        "b_only": (_VENN_CX_B + 22, _VENN_CY - 4),
        "both": ((_VENN_CX_A + _VENN_CX_B) / 2, _VENN_CY - 4),
        "neither": ((x0 + x1) / 2, y0 + 8),
    }
    for key, (rx, ry) in region_positions.items():
        if key in region_text:
            d.add(_label(rx, ry, str(region_text[key]), size=8.5))

    return d


def _fmt_tick(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:.1f}"


def _draw_stats_axes(
    d: Drawing, x0: float, y0: float, plot_w: float, plot_h: float,
    x_min: float, x_max: float, y_min: float, y_max: float,
    x_label: str = "", y_label: str = "",
    x_ticks: "list[float] | None" = None, y_ticks: "list[float] | None" = None,
    y_step: "float | None" = None, show_y_axis: bool = True,
) -> Callable[[float, float], tuple[float, float]]:
    """Draw a plain linear pair of axes (bold axis lines, a handful of ticks
    spaced via `_nice_tick_step` so the tick/gridline count never depends on
    the data's raw scale - unlike `_draw_scaled_axes`, which is deliberately
    only used for algebra graphs with small integer ranges) at the given
    plot-area rectangle, and return the (x, y) -> (pixel_x, pixel_y)
    transform. `x_ticks`/`y_ticks`, if given, are drawn at those exact
    positions instead of a computed 'nice' spacing (for class-boundary style
    x-axes, e.g. histograms and cumulative frequency graphs) - pass `[]` to
    suppress ticks on that axis entirely. `show_y_axis=False` omits the
    vertical axis line and all y-axis ticks/labels (for a chart with no
    meaningful y-scale, e.g. a box plot)."""

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = x0 + (x - x_min) / (x_max - x_min) * plot_w
        py = y0 + (y - y_min) / (y_max - y_min) * plot_h
        return px, py

    ax0, ay0 = to_px(x_min, y_min)
    ax1, _ = to_px(x_max, y_min)
    _, ay1 = to_px(x_min, y_max)
    d.add(Line(ax0, ay0, ax1, ay0, strokeColor=INK, strokeWidth=1.1))
    if show_y_axis:
        d.add(Line(ax0, ay0, ax0, ay1, strokeColor=INK, strokeWidth=1.1))

    if x_ticks is not None:
        for xt in x_ticks:
            px, py = to_px(xt, y_min)
            d.add(Line(px, py - 3, px, py, strokeColor=INK, strokeWidth=0.7))
            d.add(_label(px, py - 11, _fmt_tick(xt), size=6.5))
    else:
        step = _nice_tick_step(x_min, x_max)
        xt = math.ceil(x_min / step) * step
        while xt <= x_max + 1e-9:
            px, py = to_px(xt, y_min)
            d.add(Line(px, py - 3, px, py, strokeColor=INK, strokeWidth=0.7))
            d.add(_label(px, py - 11, _fmt_tick(xt), size=6.5))
            xt += step

    if show_y_axis:
        if y_ticks is not None:
            for yt in y_ticks:
                px, py = to_px(x_min, yt)
                d.add(Line(px - 3, py, px, py, strokeColor=INK, strokeWidth=0.7))
                d.add(_label(px - 6, py - 2, _fmt_tick(yt), anchor="end", size=6.5))
                if yt > y_min + 1e-9:
                    d.add(Line(px, py, to_px(x_max, yt)[0], py, strokeColor=GRID, strokeWidth=0.3))
        else:
            step_y = y_step or _nice_tick_step(y_min, y_max)
            yt = math.ceil(y_min / step_y) * step_y
            while yt <= y_max + 1e-9:
                px, py = to_px(x_min, yt)
                d.add(Line(px - 3, py, px, py, strokeColor=INK, strokeWidth=0.7))
                d.add(_label(px - 6, py - 2, _fmt_tick(yt), anchor="end", size=6.5))
                if yt > y_min + 1e-9:
                    d.add(Line(px, py, to_px(x_max, yt)[0], py, strokeColor=GRID, strokeWidth=0.3))
                yt += step_y

    if x_label:
        d.add(_label(ax1 + 4, ay0 - 2, x_label, anchor="start", size=7.5))
    if y_label and show_y_axis:
        d.add(_label(ax0 - 4, ay1 + 6, y_label, anchor="end", size=7.5))

    return to_px


def draw_bar_chart(params: dict) -> Drawing:
    """A bar chart. params['categories'] is a list of category labels.
    params['series'] is either a flat list[number] (a plain bar chart) or a
    list[list[number]] - one list of segment values per category (a stacked
    "composite" bar chart) - with params['series_labels'] naming each
    segment for the legend. params['blank'] (bool) draws axes and category
    labels only, no bars (for a "construct the chart" question)."""
    categories: list = params["categories"]
    series: list = params["series"]
    series_labels: "list[str] | None" = params.get("series_labels")
    y_label = params.get("y_label", "Frequency")
    blank = params.get("blank", False)

    stacked = len(series) > 0 and isinstance(series[0], list)
    totals = [sum(seg) for seg in series] if stacked else list(series)
    raw_max = max(totals) if totals else 1
    y_max = params.get("y_max")
    if y_max is None:
        step = _nice_tick_step(0, raw_max * 1.15 or 1)
        y_max = math.ceil((raw_max * 1.15 or step) / step) * step

    width, height = 230, 150
    margin_l, margin_r, margin_t, margin_b = 30, 12, 10, 24
    plot_w, plot_h = width - margin_l - margin_r, height - margin_t - margin_b
    d = Drawing(width, height + (12 if stacked and series_labels else 0))
    y0 = margin_b + (12 if stacked and series_labels else 0)

    n = len(categories)
    bar_slot = plot_w / n
    bar_w = bar_slot * 0.6

    to_px = _draw_stats_axes(
        d, margin_l, y0, plot_w, plot_h, 0, n, 0, y_max, y_label=y_label,
        x_ticks=[],
    )

    if not blank:
        for i in range(n):
            bx = margin_l + i * bar_slot + (bar_slot - bar_w) / 2
            if stacked:
                cursor = 0.0
                for seg_idx, seg_val in enumerate(series[i]):
                    _, py0 = to_px(0, cursor)
                    _, py1 = to_px(0, cursor + seg_val)
                    color = CHART_COLORS[seg_idx % len(CHART_COLORS)]
                    d.add(Rect(bx, py0, bar_w, py1 - py0, fillColor=color, strokeColor=INK, strokeWidth=0.6))
                    cursor += seg_val
            else:
                _, py0 = to_px(0, 0)
                _, py1 = to_px(0, series[i])
                d.add(Rect(bx, py0, bar_w, py1 - py0, fillColor=HIGHLIGHT, strokeColor=INK, strokeWidth=0.6))

    for i, cat in enumerate(categories):
        cx = margin_l + i * bar_slot + bar_slot / 2
        d.add(_label(cx, y0 - 10, str(cat), size=7))

    if stacked and series_labels:
        lx, ly = margin_l, height - 2
        for idx, lbl in enumerate(series_labels):
            color = CHART_COLORS[idx % len(CHART_COLORS)]
            d.add(Rect(lx, ly - 6, 8, 8, fillColor=color, strokeColor=INK, strokeWidth=0.5))
            d.add(_label(lx + 11, ly - 5, str(lbl), anchor="start", size=6.5))
            lx += 11 + stringWidth(str(lbl), _LABEL_FONT, 6.5) + 12

    return d


def draw_pie_chart(params: dict) -> Drawing:
    """A pie chart. params['categories']: list of slice names. params['values']:
    list of numbers (proportional to slice angle). params['show'] controls
    what's written on each slice: "value" (default), "percentage", or "none"
    (blank slices with only a legend - for a "construct the chart" question,
    combined with params['blank']=True to omit the legend colours' meaning
    from the values shown)."""
    categories: list = params["categories"]
    values: list = params["values"]
    show = params.get("show", "value")
    blank = params.get("blank", False)

    total = sum(values)
    cx, cy, r = 90, 75, 60
    d = Drawing(230, 150)

    cumulative = 0.0
    for i, v in enumerate(values):
        start = 90 + cumulative / total * 360
        cumulative += v
        end = 90 + cumulative / total * 360
        color = PAPER if blank else CHART_COLORS[i % len(CHART_COLORS)]
        d.add(Wedge(cx, cy, r, start, end, fillColor=color, strokeColor=INK, strokeWidth=0.8))

    lx, ly = 170, 130
    for i, cat in enumerate(categories):
        color = PAPER if blank else CHART_COLORS[i % len(CHART_COLORS)]
        d.add(Rect(lx, ly - 6, 8, 8, fillColor=color, strokeColor=INK, strokeWidth=0.5))
        label_text = str(cat)
        if not blank and show != "none":
            if show == "percentage":
                label_text += f" ({round(values[i] / total * 100)}%)"
            else:
                label_text += f" ({values[i]})"
        d.add(_label(lx + 11, ly - 5, label_text, anchor="start", size=7))
        ly -= 13

    return d


def draw_box_plot(params: dict) -> Drawing:
    """One or more box plots sharing a numeric axis. params['box_plots'] is a
    list of {"label": str (optional), "min", "q1", "median", "q3", "max"}."""
    box_plots: list = params["box_plots"]
    x_label = params.get("x_label", "")

    all_values = [v for bp in box_plots for v in (bp["min"], bp["max"])]
    x_min, x_max = min(all_values), max(all_values)
    span = (x_max - x_min) or 1
    x_min -= span * 0.08
    x_max += span * 0.08

    has_labels = any(bp.get("label") for bp in box_plots)
    label_col_w = 42 if has_labels else 0

    row_h = 34
    width, height = 230 + label_col_w, 34 + row_h * len(box_plots) + 10
    margin_l, margin_r = 14 + label_col_w, 14
    plot_w = width - margin_l - margin_r
    d = Drawing(width, height)

    axis_y = 24
    to_px = _draw_stats_axes(
        d, margin_l, axis_y, plot_w, 1, x_min, x_max, 0, 1, x_label=x_label,
        show_y_axis=False,
    )

    for i, bp in enumerate(box_plots):
        mid_y = axis_y + 30 + i * row_h
        box_h = 18
        xmin, _ = to_px(bp["min"], 0)
        xq1, _ = to_px(bp["q1"], 0)
        xmed, _ = to_px(bp["median"], 0)
        xq3, _ = to_px(bp["q3"], 0)
        xmax, _ = to_px(bp["max"], 0)

        d.add(Line(xmin, mid_y, xq1, mid_y, strokeColor=INK, strokeWidth=1))
        d.add(Line(xq3, mid_y, xmax, mid_y, strokeColor=INK, strokeWidth=1))
        d.add(Line(xmin, mid_y - box_h / 4, xmin, mid_y + box_h / 4, strokeColor=INK, strokeWidth=1))
        d.add(Line(xmax, mid_y - box_h / 4, xmax, mid_y + box_h / 4, strokeColor=INK, strokeWidth=1))
        d.add(Rect(
            xq1, mid_y - box_h / 2, xq3 - xq1, box_h,
            fillColor=HIGHLIGHT, strokeColor=INK, strokeWidth=1,
        ))
        d.add(Line(xmed, mid_y - box_h / 2, xmed, mid_y + box_h / 2, strokeColor=INK, strokeWidth=1.3))

        if bp.get("label"):
            d.add(_label(margin_l - 8, mid_y - 3, str(bp["label"]), anchor="end", size=7.5, color=MUTED))

    return d


def draw_number_line(params: dict) -> Drawing:
    """A number line showing the solution set of an inequality.
    params['range'] is [lo, hi] (int bounds for the visible, ticked line).
    params['boundaries'] is a list of 1 or 2 {"value", "closed"} dicts (an
    open boundary gets a hollow circle, a closed one a filled circle).
    params['shade'] says which part of the line is marked: "left"/"right"
    (one boundary, a ray with an arrowhead extending off the visible range),
    or - with two boundaries - "between" (a segment joining them) or
    "outside" (two rays, each with an arrowhead, one off each end).
    params['blank'] (bool) draws the bare ticked line only, no circles/
    shading (for a "draw this yourself" question page, matching the
    question/solution_diagram split used by the Plotting Graphs topics)."""
    lo, hi = params["range"]
    boundaries: list = params.get("boundaries", [])
    shade = params.get("shade")
    blank = params.get("blank", False)

    width, height = 200, 40
    margin_l, margin_r = 16, 14
    plot_w = width - margin_l - margin_r
    d = Drawing(width, height)

    axis_y = 22
    to_px = _draw_stats_axes(
        d, margin_l, axis_y, plot_w, 1, lo, hi, 0, 1,
        x_ticks=list(range(lo, hi + 1)), show_y_axis=False,
    )
    x0, _ = to_px(lo, 0)
    x1, _ = to_px(hi, 0)

    if blank or not boundaries:
        return d

    ARROW_LEN, ARROW_HALF_W = 6, 3.5

    def _arrow(tip_x: float, direction: int) -> None:
        back_x = tip_x - direction * ARROW_LEN
        d.add(Polygon(
            [tip_x, axis_y, back_x, axis_y + ARROW_HALF_W, back_x, axis_y - ARROW_HALF_W],
            fillColor=ACCENT, strokeColor=ACCENT,
        ))

    def _segment(xa: float, xb: float) -> None:
        d.add(Line(xa, axis_y, xb, axis_y, strokeColor=ACCENT, strokeWidth=2.8))

    if len(boundaries) == 1:
        value, closed = boundaries[0]["value"], boundaries[0]["closed"]
        px, _ = to_px(value, 0)
        if shade == "right":
            _segment(px, x1 + ARROW_LEN)
            _arrow(x1 + ARROW_LEN, 1)
        else:
            _segment(x0 - ARROW_LEN, px)
            _arrow(x0 - ARROW_LEN, -1)
        d.add(Circle(px, axis_y, 3.2, fillColor=(PAPER if not closed else ACCENT), strokeColor=INK, strokeWidth=1.2))
    else:
        v1, c1 = boundaries[0]["value"], boundaries[0]["closed"]
        v2, c2 = boundaries[1]["value"], boundaries[1]["closed"]
        lo_val, lo_closed = (v1, c1) if v1 <= v2 else (v2, c2)
        hi_val, hi_closed = (v2, c2) if v1 <= v2 else (v1, c1)
        px_lo, _ = to_px(lo_val, 0)
        px_hi, _ = to_px(hi_val, 0)
        if shade == "outside":
            _segment(x0 - ARROW_LEN, px_lo)
            _arrow(x0 - ARROW_LEN, -1)
            _segment(px_hi, x1 + ARROW_LEN)
            _arrow(x1 + ARROW_LEN, 1)
        else:
            _segment(px_lo, px_hi)
        d.add(Circle(px_lo, axis_y, 3.2, fillColor=(PAPER if not lo_closed else ACCENT), strokeColor=INK, strokeWidth=1.2))
        d.add(Circle(px_hi, axis_y, 3.2, fillColor=(PAPER if not hi_closed else ACCENT), strokeColor=INK, strokeWidth=1.2))

    return d


def draw_histogram(params: dict) -> Drawing:
    """A histogram: params['boundaries'] is a list of n+1 class boundaries,
    params['frequency_densities'] is a list of n bar heights (one per
    class). params['blank'] draws axes only, no bars."""
    boundaries: list = params["boundaries"]
    densities: list = params["frequency_densities"]
    blank = params.get("blank", False)
    x_label = params.get("x_label", "")
    y_label = params.get("y_label", "Frequency density")

    x_min, x_max = boundaries[0], boundaries[-1]
    y_max_raw = max(densities) if densities else 1
    step = _nice_tick_step(0, y_max_raw * 1.15 or 1)
    y_max = math.ceil((y_max_raw * 1.15 or step) / step) * step

    width, height = 230, 150
    margin_l, margin_r, margin_t, margin_b = 34, 12, 10, 24
    plot_w, plot_h = width - margin_l - margin_r, height - margin_t - margin_b
    d = Drawing(width, height)

    to_px = _draw_stats_axes(
        d, margin_l, margin_b, plot_w, plot_h, x_min, x_max, 0, y_max,
        x_label=x_label, y_label=y_label, x_ticks=boundaries,
    )

    if not blank:
        for i in range(len(boundaries) - 1):
            x0, y0 = to_px(boundaries[i], 0)
            x1, y1 = to_px(boundaries[i + 1], densities[i])
            d.add(Rect(x0, y0, x1 - x0, y1 - y0, fillColor=HIGHLIGHT, strokeColor=INK, strokeWidth=0.7))

    return d


def draw_cumulative_frequency(params: dict) -> Drawing:
    """A cumulative frequency curve through params['points'] (a list of
    (upper_class_boundary, cumulative_frequency) pairs, the first
    conventionally at cumulative frequency 0). params['blank'] draws axes
    only, no curve."""
    points: list = params["points"]
    blank = params.get("blank", False)
    x_label = params.get("x_label", "")
    y_label = params.get("y_label", "Cumulative frequency")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_max_raw = max(ys) if ys else 1
    step = _nice_tick_step(0, y_max_raw * 1.1 or 1)
    y_max = math.ceil((y_max_raw * 1.1 or step) / step) * step

    width, height = 230, 150
    margin_l, margin_r, margin_t, margin_b = 30, 12, 10, 24
    plot_w, plot_h = width - margin_l - margin_r, height - margin_t - margin_b
    d = Drawing(width, height)

    to_px = _draw_stats_axes(
        d, margin_l, margin_b, plot_w, plot_h, x_min, x_max, 0, y_max,
        x_label=x_label, y_label=y_label, x_ticks=xs,
    )

    if not blank:
        px_points = [to_px(x, y) for x, y in points]
        d.add(PolyLine(
            [c for pt in px_points for c in pt], strokeColor=ACCENT, strokeWidth=1.3,
        ))
        for px, py in px_points:
            d.add(Circle(px, py, 1.6, fillColor=ACCENT, strokeColor=None))

    return d


def draw_time_series(params: dict) -> Drawing:
    """A time series line graph through params['points'] (a list of (period,
    value) pairs, period usually a small integer index). params['blank']
    draws axes only, no line."""
    points: list = params["points"]
    blank = params.get("blank", False)
    x_label = params.get("x_label", "Time period")
    y_label = params.get("y_label", "Value")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min_raw, y_max_raw = min(ys), max(ys)
    span = (y_max_raw - y_min_raw) or 1
    y_min = max(0, y_min_raw - span * 0.15) if y_min_raw >= 0 else y_min_raw - span * 0.15
    y_max = y_max_raw + span * 0.15

    width, height = 230, 150
    margin_l, margin_r, margin_t, margin_b = 30, 12, 10, 24
    plot_w, plot_h = width - margin_l - margin_r, height - margin_t - margin_b
    d = Drawing(width, height)

    to_px = _draw_stats_axes(
        d, margin_l, margin_b, plot_w, plot_h, x_min, x_max, y_min, y_max,
        x_label=x_label, y_label=y_label, x_ticks=sorted(set(xs)),
    )

    if not blank:
        px_points = [to_px(x, y) for x, y in points]
        d.add(PolyLine(
            [c for pt in px_points for c in pt], strokeColor=ACCENT, strokeWidth=1.3,
        ))
        for px, py in px_points:
            d.add(Circle(px, py, 1.6, fillColor=ACCENT, strokeColor=None))

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
    "function_graph": draw_function_graph,
    "piecewise_graph": draw_piecewise_graph,
    "graph_transformation": draw_graph_transformation,
    "tree_diagram": draw_tree_diagram,
    "two_way_table": draw_two_way_table,
    "sample_space_diagram": draw_sample_space_diagram,
    "venn_diagram": draw_venn_diagram,
    "bar_chart": draw_bar_chart,
    "pie_chart": draw_pie_chart,
    "box_plot": draw_box_plot,
    "histogram": draw_histogram,
    "cumulative_frequency": draw_cumulative_frequency,
    "time_series": draw_time_series,
    "number_line": draw_number_line,
}


def render_diagram(spec: DiagramSpec) -> Drawing:
    try:
        renderer = _RENDERERS[spec.kind]
    except KeyError:
        raise ValueError(f"Unknown diagram kind: {spec.kind!r}") from None
    return renderer(spec.params)
