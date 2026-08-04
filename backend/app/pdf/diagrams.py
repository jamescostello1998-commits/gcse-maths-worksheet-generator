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

from reportlab.graphics.shapes import ArcPath, Circle, Drawing, Ellipse, Group, Line, PolyLine, Polygon, Rect, String, Wedge
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from app.core.models import DiagramSpec
from app.pdf.mathtext import _VAR_FONT_ITALIC
from app.pdf.styles import ACCENT, CHART_COLORS, GRID, HIGHLIGHT, INK, MUTED, PAPER

DIAGRAM_WIDTH = 200
DIAGRAM_HEIGHT = 130

_LABEL_SIZE = 9
_LABEL_FONT = "Helvetica"
# Same registered curved-italic TTF used by app/pdf/mathtext.py's prose text
# (imported directly so both call sites always agree, and so the font is
# guaranteed registered with ReportLab before any diagram label uses it -
# see mathtext.py's module docstring for why <i>/Helvetica-Oblique was
# replaced with an explicit registered font).
_LABEL_FONT_ITALIC = _VAR_FONT_ITALIC
_LABEL_FONT_BOLD = "Helvetica-Bold"


# Matches, in one combined pass so each span is claimed exactly once: (1) the
# explicit vector-letter marker \vec{a}/\vec{b} (see app/topics/vectors.py -
# written directly in generator source, not matched by a blanket letter
# pattern, since "a" collides constantly with the English indefinite
# article), or (2) a lone x or n not glued to another letter (so "Green"/
# "box" are left alone) - mirrors app/pdf/mathtext.py's _VARIABLE_RE/
# _VECTOR_RE exactly.
_TEXT_RUN_RE = re.compile(
    r"\\vec\{(?P<vec>[ab])\}"
    r"|(?<![A-Za-z])(?P<var>[xn])(?![A-Za-z])"
)

# A bare numeric fraction like "3/4" or "-3/4" within a label is drawn as a
# stacked numerator/line/denominator (a vinculum) instead of inline "3/4" -
# mirrors app/pdf/renderer.py's handling of the same pattern in prose text.
_FRACTION_RE = re.compile(r"(-?)(\d+)/(\d+)")
_FRACTION_SCALE = 0.72
_FRACTION_PAD = 1.5


def _text_runs(text: str) -> list[tuple[str, str]]:
    """Split plain (non-fraction) text into (substring, fontName) runs:
    italicising the algebraic variables x and n (as standalone letters only,
    so words like "Green" or "box" are left alone), and bolding an explicit
    \\vec{a}/\\vec{b} vector marker down to just its bare letter - so diagram
    labels match standard maths typesetting (mirrors app/pdf/mathtext.py's
    handling of Paragraph text)."""
    runs: list[tuple[str, str]] = []
    pos = 0
    for m in _TEXT_RUN_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos : m.start()], _LABEL_FONT))
        if m.group("vec") is not None:
            runs.append((m.group("vec"), _LABEL_FONT_BOLD))
        else:
            runs.append((m.group("var"), _LABEL_FONT_ITALIC))
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


def draw_two_similar_rectangles(params: dict) -> Drawing:
    """Two separate rectangles - "Shape A" and "Shape B" - side by side, for
    a similar-shapes ratio question where the student must identify
    corresponding sides themselves (same orientation, so width<->width and
    height<->height, but the two rectangles are NOT drawn in their true
    relative proportions - one side is often the unknown the student must
    find, and drawing it at its real scaled size would let a careful
    ruler-measurement leak the answer - see `_not_to_scale`).

    params: a_width_label/a_height_label (Shape A's two side labels), b_width_label/
    b_height_label (Shape B's two corresponding side labels - one is the known
    scale-factor partner, the other may be the unknown, e.g. "x"). Any of the
    four is optional (omit a key entirely to leave that side unlabelled) -
    the area/volume version of this question only ever states ONE
    corresponding length pair (the area/volume itself, not a second length,
    is what's given/asked for), so only one width/height pair is passed."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ax0, ay0, aw, ah = 8, 38, 48, 42
    bx0, by0, bw, bh = 96, 34, 55, 58

    d.add(Rect(ax0, ay0, aw, ah, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Rect(bx0, by0, bw, bh, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    d.add(_label(ax0 + aw / 2, ay0 + ah + 8, "Shape A", size=8, color=MUTED))
    d.add(_label(bx0 + bw / 2, by0 + bh + 8, "Shape B", size=8, color=MUTED))

    if params.get("a_width_label"):
        d.add(_label(ax0 + aw / 2, ay0 - 14, params["a_width_label"]))
    if params.get("a_height_label"):
        d.add(_label(ax0 + aw + 8, ay0 + ah / 2, params["a_height_label"], anchor="start"))
    if params.get("b_width_label"):
        d.add(_label(bx0 + bw / 2, by0 - 14, params["b_width_label"]))
    if params.get("b_height_label"):
        d.add(_label(bx0 + bw + 8, by0 + bh / 2, params["b_height_label"], anchor="start"))

    _not_to_scale(d)
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
    # Outside the triangle entirely, not just past the dashed line - a
    # narrow/tall triangle's sloped right edge can sit closer to the dashed
    # height line than the label's own text width, so a small fixed offset
    # from the line still crossed the sloped edge (found by rendering a
    # narrow case, not assumed up front).
    d.add(_label(x0 + bw + 8, y0 + bh / 2, params["height_label"], anchor="start"))
    return d


def draw_l_shape(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ow, oh = params["outer_w"], params["outer_h"]
    iw, ih = params["inner_w"], params["inner_h"]
    margin = 28
    scale = min((DIAGRAM_WIDTH - 2 * margin) / ow, (DIAGRAM_HEIGHT - 2 * margin) / oh)
    ow_s, oh_s, iw_s, ih_s = ow * scale, oh * scale, iw * scale, ih * scale
    x0, y0 = (DIAGRAM_WIDTH - ow_s) / 2, (DIAGRAM_HEIGHT - oh_s) / 2

    ix0, iy0 = x0 + (ow_s - iw_s) / 2, y0 + (oh_s - ih_s) / 2

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
    elif params.get("shade_frame"):
        # Shade the remaining "frame" region (outer minus the inner hole) so
        # the question can ask for the shaded area directly - fill-then-erase,
        # the same trick already used elsewhere in this file (e.g.
        # draw_mixed_compound's quarter-circle cut, draw_venn_diagram's
        # "neither" region).
        d.add(Rect(x0, y0, ow_s, oh_s, fillColor=HIGHLIGHT, strokeColor=None))
        d.add(Rect(ix0, iy0, iw_s, ih_s, fillColor=PAPER, strokeColor=None))
        d.add(Rect(x0, y0, ow_s, oh_s, fillColor=None, strokeColor=INK, strokeWidth=1.2))
        d.add(Rect(ix0, iy0, iw_s, ih_s, fillColor=None, strokeColor=INK, strokeWidth=1.0))
    else:
        d.add(Rect(x0, y0, ow_s, oh_s, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        d.add(Rect(ix0, iy0, iw_s, ih_s, strokeColor=INK, fillColor=None, strokeWidth=1.0))

    d.add(_label(x0 + ow_s / 2, y0 - 14, params["outer_labels"][0]))
    if params.get("notch") == "corner" and params.get("right_labels"):
        # The notch genuinely splits the right-hand edge into two real
        # segments - label each one directly instead of a single combined
        # "outer height" label, so students see two real side lengths
        # rather than unevaluated arithmetic like "(12 + 12) cm".
        upper_label, lower_label = params["right_labels"]
        d.add(_label(x0 + ow_s + 8, y0 + (oh_s - ih_s) / 2, upper_label, anchor="start", size=7.5))
        d.add(_label(x0 + ow_s - iw_s + 8, y0 + oh_s - ih_s / 2, lower_label, anchor="start", size=7.5))
    else:
        d.add(_label(x0 - 10, y0 + oh_s / 2, params["outer_labels"][1], anchor="end"))
    if params.get("shade_frame") and params.get("inner_labels"):
        # Two real edge labels for the inner (hole) rectangle, placed inside
        # its own unshaded interior where they're always legible - replaces
        # the old combined "6 × 5" caption, which only ever stated the hole's
        # two numbers together rather than attaching each to a real side.
        # Stacking them vertically only works when the hole is tall enough;
        # a short/wide hole needs them side by side instead, or they cross
        # the hole's own top/bottom edges (found via rendering a thin-hole
        # case, not assumed up front).
        cx, cy = ix0 + iw_s / 2, iy0 + ih_s / 2
        w_label, h_label = params["inner_labels"]
        label_size = 7.5 if min(iw_s, ih_s) >= 24 else 6.5
        if ih_s < 26:
            d.add(_label(cx - iw_s * 0.22, cy, w_label, size=label_size))
            d.add(_label(cx + iw_s * 0.22, cy, h_label, size=label_size))
        else:
            d.add(_label(cx, cy + 6, w_label, size=label_size))
            d.add(_label(cx, cy - 10, h_label, size=label_size))
    elif params.get("inner_labels"):
        inner_text = f"{params['inner_labels'][0]} × {params['inner_labels'][1]}"
        d.add(_label(x0 + ow_s / 2, y0 + oh_s + 12, inner_text, color=MUTED, size=8))
    return d


def draw_circle(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2
    r = min(DIAGRAM_WIDTH, DIAGRAM_HEIGHT) / 2 - 25

    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(cx, cy, cx + r, cy, strokeColor=INK, strokeWidth=1))
    # Above the radius line, not touching it - a +5 offset wasn't enough
    # clearance and visibly crossed the line (found by rendering, now that
    # this label is often the only place the radius value appears at all).
    d.add(_label(cx + r / 2, cy + 9, params["label"]))
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


def draw_parallelogram(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    base_val, height_val = params["base"], params["height"]
    margin = 32
    slant_frac = 0.3
    scale = min(
        (DIAGRAM_WIDTH - 2 * margin) / (base_val * (1 + slant_frac)),
        (DIAGRAM_HEIGHT - 2 * margin) / height_val,
    )
    bw, bh = base_val * scale, height_val * scale
    slant = bw * slant_frac
    x0, y0 = (DIAGRAM_WIDTH - (bw + slant)) / 2, (DIAGRAM_HEIGHT - bh) / 2

    d.add(Polygon(
        [x0, y0, x0 + bw, y0, x0 + bw + slant, y0 + bh, x0 + slant, y0 + bh],
        strokeColor=INK, fillColor=None, strokeWidth=1.2,
    ))
    d.add(Line(x0 + slant, y0 + bh, x0 + slant, y0, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(_label(x0 + bw / 2, y0 - 14, params["base_label"]))
    d.add(_label(x0 + slant - 8, y0 + bh / 2, params["height_label"], anchor="end"))
    return d


def draw_trapezium(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    a_val, b_val, height_val = params["a"], params["b"], params["height"]
    margin = 32
    scale = min((DIAGRAM_WIDTH - 2 * margin) / max(a_val, b_val), (DIAGRAM_HEIGHT - 2 * margin) / height_val)
    aw, bw, bh = a_val * scale, b_val * scale, height_val * scale
    x0, y0 = (DIAGRAM_WIDTH - bw) / 2, (DIAGRAM_HEIGHT - bh) / 2
    top_x0 = x0 + (bw - aw) / 2

    d.add(Polygon(
        [x0, y0, x0 + bw, y0, top_x0 + aw, y0 + bh, top_x0, y0 + bh],
        strokeColor=INK, fillColor=None, strokeWidth=1.2,
    ))
    d.add(Line(top_x0, y0 + bh, top_x0, y0, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(_label(top_x0 + aw / 2, y0 + bh + 14, params["a_label"]))
    d.add(_label(x0 + bw / 2, y0 - 16, params["b_label"]))
    # The dashed height line sits at top_x0, which can land very close to
    # (or even left of) the shape's own bottom-left corner x0 when the
    # slant is shallow (a close to b) or reversed (a > b) - anchoring the
    # height label a fixed 8px left of top_x0 alone let it sit on top of
    # the sloped left edge. Anchor left of whichever of x0/top_x0 is
    # further left instead, so it always clears the edge regardless of
    # slope direction.
    left_edge = min(x0, top_x0)
    d.add(_label(left_edge - 8, y0 + bh / 2, params["height_label"], anchor="end"))
    return d


def draw_sector(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2
    # No full-circle outline any more (see below) - the sector itself is the
    # only thing that needs to fit, so it can fill noticeably more of the
    # canvas than when a same-radius dashed circle also had to fit.
    r = min(DIAGRAM_WIDTH, DIAGRAM_HEIGHT) / 2 - 14
    angle = params["angle"]
    start, end = 90 - angle, 90

    d.add(Wedge(cx, cy, r, start, end, fillColor=HIGHLIGHT, strokeColor=INK, strokeWidth=1.2))
    # Mark the sector's own angle at the centre with a small arc, matching
    # every other angle-labelling diagram kind in this file (there was
    # previously no arc here at all, just the numeric label). Built directly
    # (not via _angle_arc, which always takes the shortest of the two
    # possible sweeps between the rays) since a sector's own angle is
    # routinely reflex (>180°) - _angle_arc would draw the short
    # complementary arc outside the wedge instead of tracing the sector's
    # actual angle, which is exactly wrong for a reflex sector.
    arc_r = min(18, r * 0.35)
    arc = ArcPath(strokeColor=INK, fillColor=None, strokeWidth=0.9)
    arc.addArc(cx, cy, arc_r, start, end, moveTo=True)
    d.add(arc)
    d.add(_label(cx + 4, cy + r + 10, params["radius_label"], anchor="start"))
    mid = math.radians((start + end) / 2)
    # A narrow sector's own straight width (2 x radius x sin(angle/2)) can be
    # far smaller than the label text at any radius up to the sector's own
    # edge, and the sector always opens toward the fixed top ray (end=90) -
    # so "just outside the arc, along the bisector" (tried first) still
    # collides with the radius_label above, which anchors near that same
    # top ray's tip regardless of angle. Instead, for a narrow angle, place
    # the label just behind the vertex - directly opposite the wedge's own
    # opening direction - where there is always clear space, matching real
    # exam diagrams' convention of writing a narrow angle's value beside the
    # sharp point rather than cramming it inside the sliver.
    if angle < 40:
        label_r = 20
        label_angle = mid + math.pi
        label_size = 8 if angle < 22 else 9
    else:
        label_r = arc_r + 15
        label_angle = mid
        label_size = 10
    lx = cx + label_r * math.cos(label_angle)
    ly = cy + label_r * math.sin(label_angle)
    lx = max(10, min(DIAGRAM_WIDTH - 10, lx))
    ly = max(8, min(DIAGRAM_HEIGHT - 8, ly))
    d.add(_label(lx, ly, params["angle_label"], size=label_size))
    return d


def draw_mixed_compound(params: dict) -> Drawing:
    """A 3-piece compound shape: a rectangle 'body', with a top piece added
    (a triangular roof or a semicircular dome, params['top_kind']) and a
    bottom piece removed (a quarter-circle corner cut or a semicircular edge
    notch, params['cut_kind']) - genuinely mixing rectangles/triangles/
    circle-parts rather than always the same fixed combination."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    w_val, h_val = params["width"], params["height"]
    top_kind = params["top_kind"]
    cut_kind = params["cut_kind"]
    top_extent_val = params["roof_height"] if top_kind == "triangle" else params["top_radius"]

    total_h_val = h_val + top_extent_val
    margin = 28
    scale = min((DIAGRAM_WIDTH - 2 * margin) / w_val, (DIAGRAM_HEIGHT - 2 * margin) / total_h_val)
    rw, rh, top_extent = w_val * scale, h_val * scale, top_extent_val * scale
    x0, y0 = (DIAGRAM_WIDTH - rw) / 2, (DIAGRAM_HEIGHT - (rh + top_extent)) / 2
    apex_x = x0 + rw / 2

    d.add(Rect(x0, y0, rw, rh, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    if top_kind == "triangle":
        d.add(Polygon(
            [x0, y0 + rh, x0 + rw, y0 + rh, apex_x, y0 + rh + top_extent],
            strokeColor=INK, fillColor=None, strokeWidth=1.2,
        ))
        # Offset outward, perpendicular to the right roof edge, rather than a
        # fixed (dx, dy) - a fixed offset sits well inside a shallow/wide
        # roof (small top_extent relative to rw), landing on top of the
        # sloped edge instead of clear of it (found by rendering a shallow
        # case, not assumed up front).
        mid_x, mid_y = apex_x + rw / 4, y0 + rh + top_extent / 2
        edge_dx, edge_dy = rw / 2, -top_extent
        norm = math.hypot(edge_dx, edge_dy) or 1.0
        perp_x, perp_y = -edge_dy / norm, edge_dx / norm
        d.add(_label(mid_x + perp_x * 8, mid_y + perp_y * 8, params["top_label"], anchor="start"))
    else:
        d.add(Wedge(apex_x, y0 + rh, rw / 2, 0, 180, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        d.add(Line(apex_x, y0 + rh, apex_x, y0 + rh + top_extent, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        # Above the apex, in the always-clear canvas margin, rather than
        # beside the radius line - the horizontal clearance between the line
        # and the dome's own curve shrinks the higher up the line you go
        # (and depends on the dome's radius), so no single fixed side offset
        # reliably avoided the curve for every radius (found via rendering
        # several sizes, not assumed up front).
        d.add(_label(apex_x, y0 + rh + top_extent + 8, params["top_label"], size=8))

    if cut_kind == "quarter_circle":
        # Erase that corner's pie slice in the page background colour, then
        # stroke the arc as the new visible boundary - the straight
        # rectangle edges already drawn above stop cleanly at the two
        # tangent points.
        cut_r = params["cut_radius"] * scale
        d.add(Wedge(x0, y0, cut_r, 0, 90, fillColor=PAPER, strokeColor=None))
        d.add(Wedge(x0, y0, cut_r, 0, 90, fillColor=None, strokeColor=INK, strokeWidth=1.2))
        d.add(_label(x0 - 4, y0 - 2, params["cut_label"], size=7, color=MUTED, anchor="end"))
    else:
        # A semicircular bite taken out of the middle of the bottom edge,
        # same fill-then-erase-then-stroke-arc trick as the corner cut.
        notch_r = params["notch_radius"] * scale
        d.add(Wedge(apex_x, y0, notch_r, 0, 180, fillColor=PAPER, strokeColor=None))
        d.add(Wedge(apex_x, y0, notch_r, 0, 180, fillColor=None, strokeColor=INK, strokeWidth=1.2))
        d.add(_label(apex_x + notch_r + 6, y0 + 4, params["cut_label"], size=7, color=MUTED, anchor="start"))

    d.add(_label(x0 + rw / 2, y0 - 14, params["width_label"]))
    d.add(_label(x0 - 10, y0 + rh / 2, params["height_label"], anchor="end"))
    return d


def draw_angle_line(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    around_point = params["around_point"]
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2 - (0 if around_point else 10)
    radius = 65
    arc_r = 15
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
        d.add(_angle_arc(cx, cy, running, running + v, radius=arc_r))
        if v < 20:
            # Narrow wedges: the arc itself has little room, so place the
            # label just beyond the ray tips entirely rather than cramming
            # it into the wedge.
            label_radius = radius + 13
        elif v < 35:
            label_radius = arc_r + 20
        else:
            # Sit close to the arc rather than most of the way out to the
            # ray tips - a fixed radius*0.78 (~51 units, vs. this arc's own
            # 15) read as "far higher than the angle it's labelling".
            label_radius = arc_r + 15
        mid_rad = math.radians(running + v / 2)
        lx, ly = cx + label_radius * math.cos(mid_rad), cy + label_radius * math.sin(mid_rad)
        d.add(_label(lx, ly, lbl, size=9.5))
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
        width = stringWidth(str(lbl), _LABEL_FONT, 9.5)
        inset = min(0.8, 0.5 + width / 220)
        lx, ly = vx + (cx - vx) * inset, vy + (cy - vy) * inset
        d.add(_label(lx, ly, lbl, size=9.5))
    return d


def draw_polygon_angles(params: dict) -> Drawing:
    """A schematic n-sided polygon with every interior angle labelled - a
    generalisation of draw_triangle_angles to params['n_sides'] vertices
    (e.g. 4 for a quadrilateral), reusing the same vertex-arc + centroid-
    inset label placement so wide algebraic labels get the same
    collision-safe treatment triangles already have."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2 - 5
    n = params["n_sides"]
    r = 45
    vertices = []
    for i in range(n):
        rad = math.radians(90 + i * 360 / n)
        vertices.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))

    pts = [coord for vertex in vertices for coord in vertex]
    d.add(Polygon(pts, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    for i, (vertex, lbl) in enumerate(zip(vertices, params["angle_labels"])):
        other1, other2 = vertices[(i - 1) % n], vertices[(i + 1) % n]
        d.add(_vertex_angle_arc(vertex, other1, other2, radius=9))
        vx, vy = vertex
        width = stringWidth(str(lbl), _LABEL_FONT, 9.5)
        inset = min(0.8, 0.5 + width / 220)
        lx, ly = vx + (cx - vx) * inset, vy + (cy - vy) * inset
        d.add(_label(lx, ly, lbl, size=9.5))
    return d


def _parallel_arrow_mark(cx: float, cy: float, size: float = 5, color=INK) -> Group:
    """A double-chevron ('>>') tick mark centred at (cx, cy) on a horizontal
    line, pointing right - the standard GCSE convention marking two lines as
    parallel. Two small '>' chevrons side by side, each made of two strokes
    meeting at an apex."""
    group = Group()
    for dx in (-3.5, 3.5):
        apex = (cx + dx + size * 0.6, cy)
        group.add(Line(cx + dx - size * 0.4, cy - size * 0.6, apex[0], apex[1], strokeColor=color, strokeWidth=1.1))
        group.add(Line(apex[0], apex[1], cx + dx - size * 0.4, cy + size * 0.6, strokeColor=color, strokeWidth=1.1))
    return group


def draw_parallel_lines(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    x_left, x_right = 15, DIAGRAM_WIDTH - 15
    y_top, y_bottom = DIAGRAM_HEIGHT - 35, 35
    d.add(Line(x_left, y_top, x_right, y_top, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(x_left, y_bottom, x_right, y_bottom, strokeColor=INK, strokeWidth=1.2))
    # Double-chevron arrow marks on both lines, standard GCSE convention for
    # "these two lines are parallel" - placed near the left edge, well away
    # from the transversal intersection points so they never collide with
    # the angle arcs.
    d.add(_parallel_arrow_mark(x_left + 28, y_top))
    d.add(_parallel_arrow_mark(x_left + 28, y_bottom))

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
    d.add(_label(ix_top + kx, y_top + ky, params["known_label"], anchor=known_anchor, size=10))
    d.add(_label(ix_bottom + ux2, y_bottom + uy2, params["unknown_label"], anchor=unknown_anchor, size=10))
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

    def _inset(vertex, factor=0.35):
        return (vertex[0] + (centroid[0] - vertex[0]) * factor, vertex[1] + (centroid[1] - vertex[1]) * factor)

    # A 0.7 inset (most of the way to the centroid) sat much further from
    # each vertex's own arc (radius=9) than the arc itself - "far away from
    # the angles" - brought in close enough to read as attached to the arc
    # while still clearing the vertex point itself.
    ax, ay = _inset(A)
    bx, by = _inset(B)
    d.add(_label(ax, ay, params["interior1_label"], size=10))
    d.add(_label(bx, by, params["interior2_label"], size=10))
    d.add(_label(B[0] + 20, B[1] + 10, params["exterior_label"], anchor="start", size=10))
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

    if params.get("mode") == "exterior":
        # Mark the exterior angle at vertices[0]: extend the side coming
        # into it (from vertices[-1]) past the vertex, then arc between
        # that extension and the outgoing side to vertices[1] - mirrors
        # draw_exterior_triangle's own extend-a-side approach.
        prev_v, v0, v1 = vertices[-1], vertices[0], vertices[1]
        ext_x = v0[0] + (v0[0] - prev_v[0]) * 0.5
        ext_y = v0[1] + (v0[1] - prev_v[1]) * 0.5
        ext_point = (ext_x, ext_y)
        d.add(Line(v0[0], v0[1], ext_x, ext_y, strokeColor=INK, strokeWidth=1.2))
        d.add(_vertex_angle_arc(v0, ext_point, v1, radius=10))
        lx, ly = ext_x + (v1[0] - v0[0]) * 0.18, ext_y + (v1[1] - v0[1]) * 0.18
        d.add(_label(lx, ly, params["marked_angle_label"], size=9.5))
    else:
        d.add(_vertex_angle_arc(vertices[0], vertices[-1], vertices[1], radius=8))
        vx, vy = vertices[0]
        lx, ly = vx + (cx - vx) * 0.45, vy + (cy - vy) * 0.45
        d.add(_label(lx, ly, params["marked_angle_label"], size=9.5))
    return d


def _rotation_indicator(cx: float, cy: float, radius: float = 18, color=ACCENT) -> Group:
    """A centre dot plus a curved arc (270 degrees, counterclockwise) marking
    rotational symmetry about (cx, cy) - the order label is added separately
    by the caller so its position can be chosen per-diagram."""
    group = Group()
    group.add(Circle(cx, cy, 2.2, fillColor=color, strokeColor=color))
    group.add(_angle_arc(cx, cy, 0, 270, radius=radius, color=color))
    return group


def draw_symmetry_shape(params: dict) -> Drawing:
    """A single named polygon (schematic, auto-scaled to fit the diagram box)
    for line/rotational symmetry questions. params['vertices'] is a list of
    (x, y) local coordinates in any scale/origin - auto-fit to the box.
    params['blank'] (question page) draws the outline only; the solution
    page (blank False/omitted) overlays dashed line(s) of symmetry
    (params['symmetry_lines'], a list of {"p1": (x, y), "p2": (x, y)} in the
    same local coordinate space) or, for rotational symmetry, a centre dot +
    curved arrow (params['rotation_centre'], params['rotation_order'])."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    vertices = params["vertices"]
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    pad = 26
    span_x = max(x_hi - x_lo, 1e-6)
    span_y = max(y_hi - y_lo, 1e-6)
    scale = min((DIAGRAM_WIDTH - 2 * pad) / span_x, (DIAGRAM_HEIGHT - 2 * pad) / span_y)
    mid_x, mid_y = (x_lo + x_hi) / 2, (y_lo + y_hi) / 2
    box_cx, box_cy = DIAGRAM_WIDTH / 2, DIAGRAM_HEIGHT / 2

    def fit(pt: tuple) -> tuple:
        return (box_cx + (pt[0] - mid_x) * scale, box_cy + (pt[1] - mid_y) * scale)

    px_vertices = [fit(v) for v in vertices]
    pts = [coord for vertex in px_vertices for coord in vertex]
    d.add(Polygon(pts, strokeColor=INK, fillColor=None, strokeWidth=1.3))

    if not params.get("blank", False):
        for line in params.get("symmetry_lines") or []:
            x0, y0 = fit(line["p1"])
            x1, y1 = fit(line["p2"])
            d.add(Line(x0, y0, x1, y1, strokeColor=ACCENT, strokeWidth=1.1, strokeDashArray=[3, 2]))
        centre = params.get("rotation_centre")
        if centre is not None:
            cxp, cyp = fit(centre)
            d.add(_rotation_indicator(cxp, cyp))
            if params.get("rotation_order"):
                d.add(_label(cxp, cyp - 26, f"order {params['rotation_order']}", color=ACCENT, size=7.5))

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
    """No-op by user request - the "Diagram NOT accurately drawn" caption is
    no longer rendered anywhere. Every diagram this is called from is still
    genuinely schematic (not drawn to true relative scale), so nothing about
    correctness/scale-cheating risk changes - only the caption text itself
    is gone. Kept as a real function (not deleted, not its ~20 call sites
    stripped out) so re-enabling it later is a one-line change."""
    return


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
        # Push the label outward from the hypotenuse's midpoint, away from
        # the third vertex A (i.e. away from the triangle's interior) rather
        # than always growing rightward from a fixed offset - a wide
        # hypotenuse label previously swung back toward B's own corner,
        # where the angle label also sits.
        mid_x, mid_y = (B[0] + C[0]) / 2, (B[1] + C[1]) / 2
        ox, oy = mid_x - A[0], mid_y - A[1]
        norm = math.hypot(ox, oy) or 1.0
        ox, oy = ox / norm, oy / norm
        lx, ly = mid_x + ox * 12, mid_y + oy * 12
        d.add(_label(lx, ly, params["hyp_label"], anchor="start" if ox >= 0 else "end"))
    d.add(_vertex_angle_arc(B, A, C, radius=9))
    # Push the angle label from B toward the triangle's centroid rather than
    # a fixed (dx, dy) offset - a fixed offset doesn't track the wedge's own
    # bisector direction, so for some adjacent/opposite ratios it swung
    # close enough to the hypotenuse (B-C) to visibly overlap it. The
    # direction to the centroid always sits inside the wedge at B, matching
    # the same fix already used by draw_general_triangle's angle labels.
    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)
    bx, by = B[0] + (centroid[0] - B[0]) * 0.4, B[1] + (centroid[1] - B[1]) * 0.4
    d.add(_label(bx, by, params["angle_label"], size=10))
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
        # Kept closer to the base than the original -12 offset - with only
        # 28 units of canvas below the base (A/B sit at y=28, canvas bottom
        # at y=0) a -12 offset left just 6 units of clearance above the
        # "Diagram NOT accurately drawn" caption at y=10, which visibly
        # overlapped it once a real caller labelled all three sides at once
        # (found by rendering the formulae-sheet triangle, not a unit test).
        d.add(_label(mid_ab[0], mid_ab[1] - 8, params["side_c_label"], size=8))

    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)

    def inset(v, factor):
        return (v[0] + (centroid[0] - v[0]) * factor, v[1] + (centroid[1] - v[1]) * factor)

    for vertex, other1, other2, key in (
        (A, B, C, "angle_A_label"), (B, A, C, "angle_B_label"), (C, A, B, "angle_C_label"),
    ):
        if params.get(key):
            d.add(_vertex_angle_arc(vertex, other1, other2, radius=8))
            # Scale the inward pull by the label's own text width (same fix
            # already used by draw_triangle_angles/draw_polygon_angles) - a
            # fixed 0.55 factor only worked while every angle label was
            # short; a wide one (e.g. from sine/cosine rule with an
            # algebraic or decimal value) needs more clearance from the two
            # sloped edges either side of the vertex.
            lbl = params[key]
            width = stringWidth(str(lbl), _LABEL_FONT, 10)
            factor = min(0.75, 0.45 + width / 220)
            px, py = inset(vertex, factor)
            d.add(_label(px, py, lbl, size=10))

    _not_to_scale(d)
    return d


def _bearing_arc(cx: float, cy: float, bearing_deg: float, radius: float = 11, color=INK) -> ArcPath:
    """An unfilled arc from north, swept *clockwise* by exactly bearing_deg
    (0-360) - the full compass sweep, reflex or not, unlike _angle_arc's
    shortest-arc-only behaviour. ray_angle converts the bearing into this
    file's usual CCW-from-positive-x-axis convention (north = 90 degrees);
    ArcPath.addArc always sweeps CCW/increasing, so addArc(cx, cy, r,
    ray_angle, ray_angle + bearing_deg) traces the exact same physical arc as
    the true clockwise-from-north sweep, for any bearing including reflex
    ones (confirmed by reading reportlab's own getArcPoints source)."""
    ray_angle = (90 - bearing_deg) % 360
    arc = ArcPath(strokeColor=color, fillColor=None, strokeWidth=0.8)
    arc.addArc(cx, cy, radius, ray_angle, ray_angle + bearing_deg, moveTo=True)
    return arc


def _north_arrow(x: float, y: float, length: float = 20, color=INK) -> Group:
    """A short vertical line with an arrowhead pointing to true north (up the
    page) plus an 'N' label - the standard bearings-diagram convention for
    marking the reference direction at a point."""
    group = Group()
    tip = (x, y + length)
    group.add(Line(x, y, tip[0], tip[1], strokeColor=color, strokeWidth=0.8))
    group.add(_arrowhead(tip, (0.0, 1.0), color=color, length=5, half_width=2.3))
    group.add(_label(x, tip[1] + 3, "N", color=color, size=7))
    return group


def _draw_bearings_single_leg(params: dict) -> Drawing:
    """A simpler 2-point bearings diagram (a single leg from A to B), for
    Foundation-level bearings questions (back bearings / reading a bearing
    directly) that don't need the full cosine-rule triangle - draw_bearings
    always drawing a third point/second leg/second arc had no clean way to
    represent just one leg through params alone (found while adding this
    mode: setting bearing_at_B to the back bearing degenerates point C onto
    A instead of omitting it). North arrow + bearing arc are always drawn at
    A (the given bearing); an arc at B is only added if
    answer_bearing_at_B is given (the solution page revealing a derived
    bearing, e.g. a back bearing - never shown on the question page)."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    label_A, label_B = params["labels"]
    bearing_at_A = params["bearing_at_A"]
    answer_bearing_at_B = params.get("answer_bearing_at_B")

    def unit_vector(bearing_deg: float) -> tuple:
        rad = math.radians(bearing_deg)
        return (math.sin(rad), math.cos(rad))

    A = (0.0, 0.0)
    B = unit_vector(bearing_at_A)

    xs, ys = (A[0], B[0]), (A[1], B[1])
    x_span, y_span = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    margin_side, margin_top, margin_bottom = 40, 38, 34
    scale = min(
        (DIAGRAM_WIDTH - 2 * margin_side) / x_span,
        (DIAGRAM_HEIGHT - margin_top - margin_bottom) / y_span,
    )
    ox = (DIAGRAM_WIDTH - x_span * scale) / 2 - min(xs) * scale
    oy = margin_bottom - min(ys) * scale

    def to_px(p: tuple) -> tuple:
        return (p[0] * scale + ox, p[1] * scale + oy)

    pA, pB = to_px(A), to_px(B)

    d.add(Line(pA[0], pA[1], pB[0], pB[1], strokeColor=INK, strokeWidth=1.2))

    mx, my = (pA[0] + pB[0]) / 2, (pA[1] + pB[1]) / 2
    vx, vy = pB[0] - pA[0], pB[1] - pA[1]
    length = math.hypot(vx, vy) or 1.0
    perp = (-vy / length, vx / length)
    anchor = "start" if perp[0] >= 0 else "end"
    d.add(_label(mx + perp[0] * 14, my + perp[1] * 14, params["leg1_label"], anchor=anchor, size=8))

    for p, label in ((pA, label_A), (pB, label_B)):
        d.add(Circle(p[0], p[1], 1.8, strokeColor=INK, fillColor=INK))
        vx2, vy2 = p[0] - mx, p[1] - my
        vdist = math.hypot(vx2, vy2) or 1.0
        ux, uy = vx2 / vdist, vy2 / vdist
        if uy > 0.6:
            # Same fix as the two-leg diagram: don't push a vertex label
            # straight up into that point's own north arrow/arc/"N" label.
            ux, uy = (1.0 if ux >= 0 else -1.0), 0.2
            norm = math.hypot(ux, uy)
            ux, uy = ux / norm, uy / norm
        d.add(_label(p[0] + ux * 14, p[1] + uy * 14, label, size=8))

    d.add(_north_arrow(pA[0], pA[1]))
    d.add(_bearing_arc(pA[0], pA[1], bearing_at_A))
    if answer_bearing_at_B is not None:
        d.add(_north_arrow(pB[0], pB[1]))
        d.add(_bearing_arc(pB[0], pB[1], answer_bearing_at_B, color=ACCENT))

    _not_to_scale(d)
    return d


def draw_bearings(params: dict) -> Drawing:
    """Schematic (not to scale) diagram for a two-leg bearings problem: from
    A, travel on a given bearing to B, then from B on a second bearing to C.
    Both legs are drawn solid, the direct A-to-C distance dashed (labelled
    with the caller's unknown_label - never the real answer on the question
    page, see bearings.py), and a north arrow + full clockwise-from-north
    bearing arc is drawn at *both* A and B (not just the start point),
    matching real exam bearings diagrams. Vertex/side labels are pushed
    outward from the triangle's own centroid (same idiom as
    draw_general_triangle/draw_grid_transformation) since the shape's
    orientation varies with the random bearings, unlike those diagrams'
    fixed schematic vertices.

    A single-leg (2-point) variant is used instead whenever bearing_at_B is
    omitted - see _draw_bearings_single_leg."""
    if params.get("bearing_at_B") is None:
        return _draw_bearings_single_leg(params)

    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    label_A, label_B, label_C = params["labels"]
    bearing_at_A, bearing_at_B = params["bearing_at_A"], params["bearing_at_B"]

    def unit_vector(bearing_deg: float) -> tuple:
        rad = math.radians(bearing_deg)
        return (math.sin(rad), math.cos(rad))

    A = (0.0, 0.0)
    B = unit_vector(bearing_at_A)
    dx, dy = unit_vector(bearing_at_B)
    C = (B[0] + dx, B[1] + dy)

    xs, ys = (A[0], B[0], C[0]), (A[1], B[1], C[1])
    x_span, y_span = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    # Asymmetric margins: extra headroom above the topmost point (whichever
    # of A/B/C that turns out to be) for that point's north arrow + arc + "N"
    # label, which extend further up the page than any other diagram element;
    # extra headroom below the bottommost point too, so an outward-pushed
    # vertex/side label there still clears the "Diagram NOT accurately
    # drawn" caption along the bottom edge - both found via this diagram
    # kind's visual spike (a vertex/side label pushed straight down from a
    # point sitting right at the un-padded margin landed on top of the
    # caption text).
    margin_side, margin_top, margin_bottom = 30, 38, 34
    scale = min(
        (DIAGRAM_WIDTH - 2 * margin_side) / x_span,
        (DIAGRAM_HEIGHT - margin_top - margin_bottom) / y_span,
    )
    ox = (DIAGRAM_WIDTH - x_span * scale) / 2 - min(xs) * scale
    oy = margin_bottom - min(ys) * scale

    def to_px(p: tuple) -> tuple:
        return (p[0] * scale + ox, p[1] * scale + oy)

    pA, pB, pC = to_px(A), to_px(B), to_px(C)
    centroid = ((pA[0] + pB[0] + pC[0]) / 3, (pA[1] + pB[1] + pC[1]) / 3)

    def outward(p: tuple, q: tuple, dist: float) -> tuple:
        """Midpoint of p-q, offset perpendicular and away from the
        triangle's centroid, with a text anchor chosen from the offset's own
        sign - a middle anchor would let a wide label swing back over the
        line itself (found via this diagram kind's visual spike: a
        near-vertical leg, whose north arrow/arc/"N" label sit right along
        that same line, kept colliding with its own centered leg-length
        label). Mirrors the anchor-by-offset-sign fix already used in
        draw_parallel_lines/draw_triangle_angles."""
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        vx, vy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(vx, vy) or 1.0
        perp = (-vy / length, vx / length)
        to_c = (centroid[0] - mx, centroid[1] - my)
        if perp[0] * to_c[0] + perp[1] * to_c[1] > 0:
            perp = (-perp[0], -perp[1])
        anchor = "start" if perp[0] >= 0 else "end"
        return (mx + perp[0] * dist, my + perp[1] * dist, anchor)

    d.add(Line(pA[0], pA[1], pB[0], pB[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(pB[0], pB[1], pC[0], pC[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(pA[0], pA[1], pC[0], pC[1], strokeColor=MUTED, strokeWidth=1.0, strokeDashArray=[3, 2]))

    lx, ly, anchor = outward(pA, pB, 16)
    d.add(_label(lx, ly, params["leg1_label"], anchor=anchor, size=8))
    lx, ly, anchor = outward(pB, pC, 16)
    d.add(_label(lx, ly, params["leg2_label"], anchor=anchor, size=8))
    lx, ly, anchor = outward(pA, pC, 16)
    d.add(_label(lx, ly, params["unknown_label"], anchor=anchor, color=ACCENT, size=8))

    def vertex_label_pos(p: tuple, has_arrow: bool) -> tuple:
        vx, vy = p[0] - centroid[0], p[1] - centroid[1]
        vdist = math.hypot(vx, vy) or 1.0
        ux, uy = vx / vdist, vy / vdist
        if has_arrow and uy > 0.6:
            # The outward-from-centroid direction points near-straight up,
            # right where that point's own north arrow/arc/"N" label already
            # are - push sideways instead (found via this diagram kind's
            # visual spike: A/B labels routinely collided with their own
            # arrow when the third point sat below them).
            ux, uy = (1.0 if ux >= 0 else -1.0), 0.2
            norm = math.hypot(ux, uy)
            ux, uy = ux / norm, uy / norm
        offset = 15 if has_arrow else 12
        return (p[0] + ux * offset, p[1] + uy * offset)

    for p, label, has_arrow in ((pA, label_A, True), (pB, label_B, True), (pC, label_C, False)):
        d.add(Circle(p[0], p[1], 1.8, strokeColor=INK, fillColor=INK))
        lx, ly = vertex_label_pos(p, has_arrow)
        d.add(_label(lx, ly, label, size=8))

    d.add(_north_arrow(pA[0], pA[1]))
    d.add(_bearing_arc(pA[0], pA[1], bearing_at_A))
    d.add(_north_arrow(pB[0], pB[1]))
    d.add(_bearing_arc(pB[0], pB[1], bearing_at_B))

    _not_to_scale(d)
    return d


def _tick_marks(p: tuple, q: tuple, count: int, length: float = 5, gap: float = 3) -> list:
    """`count` short dashes perpendicular to segment p-q, centred at its
    midpoint - the standard "equal sides" exam-diagram convention (1 tick for
    one equal pair, 2 ticks for a second, distinct, equal pair)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    px, py = -uy, ux
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    marks = []
    offsets = [(i - (count - 1) / 2) * gap for i in range(count)]
    for off in offsets:
        cx, cy = mx + ux * off, my + uy * off
        marks.append(
            Line(cx - px * length / 2, cy - py * length / 2, cx + px * length / 2, cy + py * length / 2,
                 strokeColor=INK, strokeWidth=1.1)
        )
    return marks


def draw_two_triangle_congruence(params: dict) -> Drawing:
    """Two separate, non-overlapping triangles (not to scale) for a
    congruent-triangle-proof question. Sides declared equal get tick marks
    (_tick_marks) and angles declared equal get nested arcs
    (_vertex_angle_arc at increasing radii) - the marks show which parts are
    equal, not the real proportions. Each triangle is 3 fixed points, indexed
    0=bottom-left, 1=bottom-right, 2=apex (matching draw_general_triangle's
    A/B/C convention).

    params: labels_1/labels_2 (3-tuples of vertex label strings), ticks_1/
    ticks_2 (list of (i, j, count) - tick-mark the side between local points
    i and j), arcs_1/arcs_2 (list of (vertex_index, count) - count nested
    arcs at that vertex), note (optional caption, e.g. a shared-side remark;
    replaces the usual "not accurately drawn" caption when present)."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    T1 = [(12, 34), (82, 34), (47, 102)]
    T2 = [(118, 34), (188, 34), (153, 102)]

    for tri in (T1, T2):
        d.add(Polygon([coord for pt in tri for coord in pt], strokeColor=INK, fillColor=None, strokeWidth=1.2))

    for tri, labels in ((T1, params.get("labels_1")), (T2, params.get("labels_2"))):
        if not labels:
            continue
        for idx, (pt, label) in enumerate(zip(tri, labels)):
            x, y = pt
            y_off = -13 if idx < 2 else 10
            anchor = "end" if idx == 0 else ("start" if idx == 1 else "middle")
            d.add(_label(x, y + y_off, label, anchor=anchor, size=8))

    for tri, ticks_key in ((T1, "ticks_1"), (T2, "ticks_2")):
        for i, j, count in params.get(ticks_key, []):
            for mark in _tick_marks(tri[i], tri[j], count):
                d.add(mark)

    for tri, arcs_key in ((T1, "arcs_1"), (T2, "arcs_2")):
        for vertex_idx, count in params.get(arcs_key, []):
            others = [tri[k] for k in range(3) if k != vertex_idx]
            for n in range(count):
                d.add(_vertex_angle_arc(tri[vertex_idx], others[0], others[1], radius=9 + n * 4))

    if params.get("note"):
        d.add(_label(DIAGRAM_WIDTH / 2, 8, params["note"], size=7, color=MUTED))
    else:
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

    # A vector is a directed quantity - mark the direction of travel (O->A,
    # O->B) with a small arrowhead partway along each line, matching real
    # exam-diagram convention (previously these were plain undirected
    # strokes, indistinguishable from an ordinary triangle's sides).
    for start, end in ((O, A), (O, B)):
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy) or 1.0
        d.add(_arrowhead((mx, my), (dx / length, dy / length)))

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
    # Taller than the usual DIAGRAM_HEIGHT: the external point T sits well
    # above the circle (cy + r + 38 = 132), and its label further still - on
    # the standard 130-tall canvas this silently overflowed the Drawing's own
    # bounds, bleeding the label up into the prompt text above it (ReportLab
    # doesn't clip a Drawing's overflowing content) - found via rendering an
    # actual worksheet and looking closely, not a unit test.
    d = Drawing(DIAGRAM_WIDTH, 160)
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


def draw_circle_same_segment(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 74, 42
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    A, B = _circle_point(cx, cy, r, 200), _circle_point(cx, cy, r, 340)
    C, Dp = _circle_point(cx, cy, r, 70), _circle_point(cx, cy, r, 110)
    d.add(Line(A[0], A[1], B[0], B[1], strokeColor=INK, strokeWidth=0.8))
    for P in (C, Dp):
        d.add(Line(P[0], P[1], A[0], A[1], strokeColor=INK, strokeWidth=1))
        d.add(Line(P[0], P[1], B[0], B[1], strokeColor=INK, strokeWidth=1))
    d.add(_vertex_angle_arc(C, A, B, radius=10))
    d.add(_vertex_angle_arc(Dp, A, B, radius=10))
    d.add(_label(C[0], C[1] + 10, params["angle_c_label"], size=7))
    d.add(_label(Dp[0], Dp[1] + 10, params["angle_d_label"], size=7))
    _not_to_scale(d)
    return d


def draw_circle_alternate_segment(params: dict) -> Drawing:
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    cx, cy, r = 100, 76, 40
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    P = _circle_point(cx, cy, r, 270)
    Q = _circle_point(cx, cy, r, 190)
    R = _circle_point(cx, cy, r, 30)
    tangent_left = (P[0] - 46, P[1])
    tangent_right = (P[0] + 46, P[1])
    d.add(Line(tangent_left[0], tangent_left[1], tangent_right[0], tangent_right[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(P[0], P[1], Q[0], Q[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(Q[0], Q[1], R[0], R[1], strokeColor=INK, strokeWidth=1))
    d.add(Line(R[0], R[1], P[0], P[1], strokeColor=INK, strokeWidth=1))
    d.add(_vertex_angle_arc(P, tangent_left, Q, radius=14))
    d.add(_vertex_angle_arc(R, Q, P, radius=10))
    d.add(_label(P[0] - 14, P[1] - 12, params["tangent_angle_label"], size=7, anchor="end"))
    d.add(_label(R[0], R[1] - 12, params["segment_angle_label"], size=7))
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
    """Two schematic straight lines (not to scale) crossing on the axes -
    no point/label marks the crossing itself, since for a 'solve
    simultaneously' question that intersection IS the answer the student
    must find by reading the graph."""
    d = Drawing(DIAGRAM_WIDTH, DIAGRAM_HEIGHT)
    ox, oy = 25, 20
    axis_len_x, axis_len_y = DIAGRAM_WIDTH - 45, DIAGRAM_HEIGHT - 35
    _draw_axes(d, ox, oy, axis_len_x, axis_len_y)

    p1_start = (ox + 5, oy + axis_len_y * 0.15)
    p1_end = (ox + axis_len_x - 5, oy + axis_len_y * 0.75)
    p2_start = (ox + 5, oy + axis_len_y * 0.85)
    p2_end = (ox + axis_len_x - 15, oy + 5)
    d.add(Line(p1_start[0], p1_start[1], p1_end[0], p1_end[1], strokeColor=INK, strokeWidth=1.2))
    d.add(Line(p2_start[0], p2_start[1], p2_end[0], p2_end[1], strokeColor=INK, strokeWidth=1.2))

    def _label_along(p_from: tuple, p_to: tuple, t: float, text: str, anchor: str) -> None:
        # Label anchored a fraction t along the line (never right at an
        # endpoint, which sits close to a diagram corner already carrying
        # the "x"/"y" axis-name label), raised above it. `anchor` is chosen
        # per line so the text grows in the direction the line is moving
        # AWAY from the label (down-slope for an ascending line read
        # right-to-left, down-slope for a descending line read left-to-
        # right) - so the gap to the line only widens along the text's
        # length, never narrows back into it.
        x = p_from[0] + (p_to[0] - p_from[0]) * t
        y = p_from[1] + (p_to[1] - p_from[1]) * t
        d.add(_label(x, y + 10, text, anchor=anchor, size=8))

    _label_along(p1_start, p1_end, 0.85, params["label1"], anchor="end")
    _label_along(p2_start, p2_end, 0.10, params["label2"], anchor="start")
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
    if span <= 100:
        return 10
    if span <= 200:
        return 20
    if span <= 500:
        return 50
    # No existing caller reached a span this large before trig_graph (0-360
    # degrees) - found by rendering an actual worksheet and seeing every
    # integer from 1 to 360 crammed into the tick labels, since the old
    # flat "step=10 for any span>50" never scaled further. These extra
    # tiers are purely additive for spans no prior topic ever used.
    return 100


_MIN_SQUARE_UNIT_PX = 8.0


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
    x_span = (x_max - x_min) or 1
    y_span = (y_max - y_min) or 1
    px_per_unit_x = plot_w / x_span
    px_per_unit_y = plot_h / y_span

    # Prefer a true square grid (equal px-per-unit on both axes, matching
    # real squared exercise-book paper) whenever the tighter of the two
    # per-axis scales still gives a legible unit-square size. Fall back to
    # the old independently-scaled (rectangular) axes only when the data's
    # x/y ranges are too lopsided for that to work (e.g. a 360-degree trig
    # sweep against a y range of +-1.4, or a distance-time graph running to
    # 65 minutes against 12 km) - forcing square there would shrink the
    # constrained axis's unit squares to sub-pixel slivers.
    square_px = min(px_per_unit_x, px_per_unit_y)
    if square_px >= _MIN_SQUARE_UNIT_PX:
        used_w, used_h = x_span * square_px, y_span * square_px
        origin_x = _GRAPH_MARGIN_L + (plot_w - used_w) / 2
        origin_y = _GRAPH_MARGIN_B + (plot_h - used_h) / 2

        def to_px(x: float, y: float) -> tuple[float, float]:
            return origin_x + (x - x_min) * square_px, origin_y + (y - y_min) * square_px
    else:
        def to_px(x: float, y: float) -> tuple[float, float]:
            px = _GRAPH_MARGIN_L + (x - x_min) / x_span * plot_w
            py = _GRAPH_MARGIN_B + (y - y_min) / y_span * plot_h
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
    if kind == "exponential":
        return params["a"] * params["base"] ** x
    if kind == "trigonometric":
        # sin/cos are continuous everywhere. tan has vertical asymptotes at
        # 90 + 180k degrees and would need the same branch-splitting
        # draw_function_graph's reciprocal kind uses if plotted across one -
        # callers using "tan" are expected to only ever pass an x_min/x_max
        # window that stays strictly within one continuous branch (never
        # spanning an asymptote), so a plain lookup is safe here.
        fn = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[params["fn"]]
        return params.get("sign", 1) * fn(math.radians(x))
    raise ValueError(f"unknown function graph kind: {kind!r}")


def _cross_marker(d: Drawing, x: float, y: float, size: float = 2.2, color=INK, width: float = 1.1) -> None:
    """A small X/cross marking one plotted data point - the standard exam-
    graph convention, used everywhere a single value is plotted on any
    graph (never a filled dot)."""
    d.add(Line(x - size, y - size, x + size, y + size, strokeColor=color, strokeWidth=width))
    d.add(Line(x - size, y + size, x + size, y - size, strokeColor=color, strokeWidth=width))


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
            _cross_marker(d, px, py)

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
            _cross_marker(d, px, py)

    return d


def _arrowhead(tip: tuple, direction: tuple, color=INK, length: float = 6, half_width: float = 3) -> Polygon:
    """A small filled triangular arrowhead at `tip`, pointing along the unit
    vector `direction` (dx, dy)."""
    dx, dy = direction
    back = (tip[0] - dx * length, tip[1] - dy * length)
    perp_x, perp_y = -dy, dx
    left = (back[0] + perp_x * half_width, back[1] + perp_y * half_width)
    right = (back[0] - perp_x * half_width, back[1] - perp_y * half_width)
    return Polygon([tip[0], tip[1], left[0], left[1], right[0], right[1]], fillColor=color, strokeColor=color)


def draw_grid_transformation(params: dict) -> Drawing:
    """A real-scale, gridded diagram showing an 'original' polygon and,
    unless params['image_vertices'] is omitted, its transformed 'image' -
    for reflection/rotation/translation/enlargement questions on a
    coordinate grid. params['mirror_line']/'centre'/'translation_vector' are
    given information the student needs to perform the transform (not the
    answer), so they are drawn whenever present, independent of whether the
    image is shown - this lets one diagram kind serve both the blank
    question-page version (no image_vertices) and the completed
    solution-page version (image_vertices present) of a 'complete the
    transformation' question, as well as a 'describe the transformation'
    question (both shapes present, no mirror_line/centre/vector - that's
    exactly what the student must determine)."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_min, x_max = params["x_min"], params["x_max"]
    y_min, y_max = params["y_min"], params["y_max"]
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max)

    def draw_shape(vertices, labels, color) -> None:
        px_vertices = [to_px(x, y) for x, y in vertices]
        pts = [coord for vertex in px_vertices for coord in vertex]
        d.add(Polygon(pts, strokeColor=color, fillColor=None, strokeWidth=1.3))
        cx = sum(p[0] for p in px_vertices) / len(px_vertices)
        cy = sum(p[1] for p in px_vertices) / len(px_vertices)
        for (px, py), label in zip(px_vertices, labels):
            d.add(Circle(px, py, 1.8, strokeColor=color, fillColor=color))
            dx, dy = px - cx, py - cy
            dist = math.hypot(dx, dy) or 1.0
            d.add(_label(px + dx / dist * 9, py + dy / dist * 9, label, color=color, size=7.5))

    mirror = params.get("mirror_line")
    if mirror:
        kind = mirror["type"]
        if kind == "vertical":
            x0, y0 = to_px(mirror["x"], y_min)
            x1, y1 = to_px(mirror["x"], y_max)
        elif kind == "horizontal":
            x0, y0 = to_px(x_min, mirror["y"])
            x1, y1 = to_px(x_max, mirror["y"])
        else:
            sign = mirror["sign"]
            if sign == 1:
                lo, hi = max(x_min, y_min), min(x_max, y_max)
            else:
                lo, hi = max(x_min, -y_max), min(x_max, -y_min)
            x0, y0 = to_px(lo, sign * lo)
            x1, y1 = to_px(hi, sign * hi)
        d.add(Line(x0, y0, x1, y1, strokeColor=MUTED, strokeWidth=1.0, strokeDashArray=[3, 2]))
        if mirror.get("label"):
            d.add(_label(x1 - 4, y1 + 5, mirror["label"], anchor="end", color=MUTED, size=7.5))

    centre = params.get("centre")
    if centre is not None:
        # No text label here (only a dot) - "centre of rotation/enlargement"
        # is long enough that it reliably collides with nearby vertex labels
        # whenever the centre sits close to (or exactly on) a shape vertex, a
        # common and pedagogically normal configuration (e.g. "enlarge from
        # vertex A") - found via this diagram kind's visual spike. The
        # coordinate is stated in the prompt/solution text instead; the dot
        # is enough to show *where* it is against the numbered grid.
        cxp, cyp = to_px(*centre)
        d.add(Circle(cxp, cyp, 2.3, fillColor=INK, strokeColor=INK))

    vector = params.get("translation_vector")
    if vector:
        dx, dy = vector
        anchor = params["original_vertices"][0]
        ax, ay = to_px(*anchor)
        bx, by = to_px(anchor[0] + dx, anchor[1] + dy)
        d.add(Line(ax, ay, bx, by, strokeColor=ACCENT, strokeWidth=1.2, strokeDashArray=[3, 2]))
        length = math.hypot(bx - ax, by - ay)
        if length > 1e-6:
            d.add(_arrowhead((bx, by), ((bx - ax) / length, (by - ay) / length), color=ACCENT))
        if params.get("vector_label"):
            d.add(_label((ax + bx) / 2 + 8, (ay + by) / 2, params["vector_label"], anchor="start", color=ACCENT, size=7.5))

    draw_shape(params["original_vertices"], params["original_labels"], INK)
    if params.get("image_vertices"):
        draw_shape(params["image_vertices"], params["image_labels"], ACCENT)

    return d


def _scaled_circle(to_px: Callable, centre: tuple, r: float, x_span: float, y_span: float, plot_w: float, plot_h: float, **kw) -> Ellipse:
    """A circle of true radius r, drawn correctly on a _draw_scaled_axes
    grid. ALWAYS uses Ellipse with separately-computed rx/ry, never plain
    Circle, since to_px's x/y pixel scaling is never exactly uniform even
    with a square data window (plot_w != plot_h, from GRAPH_WIDTH/HEIGHT
    minus fixed margins) - confirmed by reading _draw_scaled_axes directly."""
    cx, cy = to_px(*centre)
    rx, ry = r * plot_w / x_span, r * plot_h / y_span
    return Ellipse(cx, cy, rx, ry, **kw)


def _loci_reference_points(d: Drawing, to_px: Callable, points: list) -> None:
    for point in points:
        px, py = to_px(*point["xy"])
        d.add(Circle(px, py, 1.8, strokeColor=INK, fillColor=INK))
        if point.get("label"):
            d.add(_label(px + 8, py + 8, point["label"], anchor="start", size=8))


def draw_loci_construction(params: dict) -> Drawing:
    """A real-scale, gridded diagram for a loci question: the fixed
    reference point(s) are always shown; the constructed locus itself - a
    circle (locus of points a fixed distance from a point) or a line segment
    (a perpendicular/angle bisector) - is added only once known, via the
    same blank-question/completed-solution split already used by
    draw_grid_transformation (params['circle']/'segment' omitted for the
    blank question-page diagram, present for the solution-page one).
    params['given_lines'] (e.g. the two rays forming an angle to bisect, or
    the segment between two points to bisect) are drawn on *both* pages,
    same as draw_grid_transformation's mirror_line/centre/vector - they are
    information the student is given, not the answer."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_min, x_max = params["x_min"], params["x_max"]
    y_min, y_max = params["y_min"], params["y_max"]
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max)

    for line in params.get("given_lines", []):
        x0, y0 = to_px(*line["p1"])
        x1, y1 = to_px(*line["p2"])
        d.add(Line(x0, y0, x1, y1, strokeColor=INK, strokeWidth=1.2))

    _loci_reference_points(d, to_px, params.get("points", []))

    circle = params.get("circle")
    if circle is not None:
        x_span = max(x_max, 0) - min(x_min, 0)
        y_span = max(y_max, 0) - min(y_min, 0)
        plot_w = d.width - _GRAPH_MARGIN_L - _GRAPH_MARGIN_R
        plot_h = d.height - _GRAPH_MARGIN_T - _GRAPH_MARGIN_B
        d.add(_scaled_circle(
            to_px, circle["centre"], circle["radius"], x_span, y_span, plot_w, plot_h,
            strokeColor=ACCENT, fillColor=None, strokeWidth=1.2,
        ))

    segment = params.get("segment")
    if segment is not None:
        x0, y0 = to_px(*segment["p1"])
        x1, y1 = to_px(*segment["p2"])
        d.add(Line(
            x0, y0, x1, y1, strokeColor=ACCENT, strokeWidth=1.2,
            strokeDashArray=[3, 2] if segment.get("dashed") else None,
        ))

    return d


def _satisfies_loci_constraints(x: float, y: float, constraints: list) -> bool:
    for c in constraints:
        if c["type"] == "disk":
            cx, cy = c["centre"]
            inside = (x - cx) ** 2 + (y - cy) ** 2 <= c["radius"] ** 2
            if inside != c.get("inside", True):
                return False
        elif c["type"] == "half_plane":
            ax, ay = c["closer_to"]
            bx, by = c["than"]
            if (x - ax) ** 2 + (y - ay) ** 2 > (x - bx) ** 2 + (y - by) ** 2:
                return False
    return True


def draw_loci_region(params: dict) -> Drawing:
    """Same grid base as draw_loci_construction, plus each constraint's own
    boundary (a dashed circle or segment, in params['boundaries'] - always
    drawn on both the question and solution page, since it's given
    information) and, once known, a shaded region satisfying every
    constraint in params['shade_constraints'] - rendered as a rasterized dot
    mesh (sample a fine grid, evaluate each constraint directly at each
    sample point, paint a small translucent dot wherever all of them hold)
    rather than hand-built boolean region geometry (the draw_venn_diagram
    technique), so this generalises to any future constraint combination for
    free."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_min, x_max = params["x_min"], params["x_max"]
    y_min, y_max = params["y_min"], params["y_max"]
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max)

    x_span = max(x_max, 0) - min(x_min, 0)
    y_span = max(y_max, 0) - min(y_min, 0)
    plot_w = d.width - _GRAPH_MARGIN_L - _GRAPH_MARGIN_R
    plot_h = d.height - _GRAPH_MARGIN_T - _GRAPH_MARGIN_B
    for boundary in params.get("boundaries", []):
        if boundary["type"] == "circle":
            d.add(_scaled_circle(
                to_px, boundary["centre"], boundary["radius"], x_span, y_span, plot_w, plot_h,
                strokeColor=INK, fillColor=None, strokeWidth=1.0, strokeDashArray=[3, 2],
            ))
        elif boundary["type"] == "segment":
            x0, y0 = to_px(*boundary["p1"])
            x1, y1 = to_px(*boundary["p2"])
            d.add(Line(x0, y0, x1, y1, strokeColor=INK, strokeWidth=1.0, strokeDashArray=[3, 2]))

    _loci_reference_points(d, to_px, params.get("points", []))

    constraints = params.get("shade_constraints")
    if constraints:
        step = 0.3
        x_lo, x_hi = min(x_min, 0), max(x_max, 0)
        y_lo, y_hi = min(y_min, 0), max(y_max, 0)
        x = x_lo
        while x <= x_hi + 1e-9:
            y = y_lo
            while y <= y_hi + 1e-9:
                if _satisfies_loci_constraints(x, y, constraints):
                    px, py = to_px(x, y)
                    d.add(Circle(px, py, 1.3, fillColor=ACCENT, strokeColor=None, fillOpacity=0.35))
                y += step
            x += step

    return d


def _clip_line_to_window(
    m: float, c: float, x_min: float, x_max: float, y_min: float, y_max: float
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """The segment of the line y = m*x + c that lies within the rectangle
    [x_min, x_max] x [y_min, y_max], as two endpoint (x, y) tuples - or None
    if the line never crosses the rectangle at all. Finds every point where
    the line crosses one of the rectangle's four edges, keeps only the ones
    that actually land on that edge (not off the end of it), and returns the
    two extreme candidates. Needed because a steep line's y-value at x_min or
    x_max routinely lands far outside the window - drawing between those raw
    endpoints (rather than this clipped segment) sends the line's pixel
    coordinates far outside the Drawing's own canvas, which ReportLab does
    not clip, so it bleeds into whatever page content sits above/below the
    diagram - found via rendering an actual worksheet and looking closely,
    not a unit test."""
    candidates: list[tuple[float, float]] = []
    for x in (x_min, x_max):
        y = m * x + c
        if y_min - 1e-9 <= y <= y_max + 1e-9:
            candidates.append((x, y))
    if m != 0:
        for y in (y_min, y_max):
            x = (y - c) / m
            if x_min - 1e-9 <= x <= x_max + 1e-9:
                candidates.append((x, y))
    if len(candidates) < 2:
        return None
    candidates.sort(key=lambda p: p[0])
    return candidates[0], candidates[-1]


def _satisfies_inequality_lines(x: float, y: float, lines: list) -> bool:
    for line in lines:
        rhs = line["m"] * x + line["c"]
        op = line["op"]
        if op == "<" and not (y < rhs):
            return False
        if op == "<=" and not (y <= rhs):
            return False
        if op == ">" and not (y > rhs):
            return False
        if op == ">=" and not (y >= rhs):
            return False
    return True


def draw_inequality_region(params: dict) -> Drawing:
    """Shades the region on gridded axes satisfying every inequality in
    params['lines'] (1-2 entries, each of the form y <op> m*x + c - never a
    general ax+by=c or a vertical line, which covers the realistic GCSE
    question shape). Each boundary is drawn full-width across the window,
    dashed for a strict inequality (<, >) and solid for a non-strict one
    (<=, >=), matching real exam convention. params['blank'] gives bare axes
    only (the question page, matching inequalities_number_line.py's
    blank-question/marked-solution split) - otherwise the boundary lines and
    a rasterized-dot-mesh shaded region are both drawn, reusing the exact
    sample-a-fine-grid-and-test-every-point technique draw_loci_region
    already uses, generalised here to a linear-inequality predicate instead
    of a circle/half-plane one."""
    d = Drawing(GRAPH_WIDTH, GRAPH_HEIGHT)
    x_min, x_max = params["x_min"], params["x_max"]
    y_min, y_max = params["y_min"], params["y_max"]
    to_px = _draw_scaled_axes(d, x_min, x_max, y_min, y_max)

    if params.get("blank", False):
        return d

    lines = params.get("lines", [])
    for line in lines:
        clipped = _clip_line_to_window(line["m"], line["c"], x_min, x_max, y_min, y_max)
        if clipped is None:
            continue
        (x0, y0), (x1, y1) = clipped
        px0, py0 = to_px(x0, y0)
        px1, py1 = to_px(x1, y1)
        dashed = line["op"] in ("<", ">")
        d.add(Line(px0, py0, px1, py1, strokeColor=INK, strokeWidth=1.2, strokeDashArray=[3, 2] if dashed else None))

    step = 0.25
    x_lo, x_hi = min(x_min, 0), max(x_max, 0)
    y_lo, y_hi = min(y_min, 0), max(y_max, 0)
    x = x_lo
    while x <= x_hi + 1e-9:
        y = y_lo
        while y <= y_hi + 1e-9:
            if _satisfies_inequality_lines(x, y, lines):
                px, py = to_px(x, y)
                d.add(Circle(px, py, 1.3, fillColor=ACCENT, strokeColor=None, fillOpacity=0.35))
            y += step
        x += step

    return d


def _transform_base_fn(x: float) -> float:
    # A smooth symmetric bowl-shaped curve (exactly y = 0.5x^2 - 1.5) used
    # as the generic "y = f(x)" schematic - sampled densely below rather
    # than drawn as a coarse hand-picked-point polyline.
    return 0.5 * x**2 - 1.5


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

    n = 40
    base_pts = [(-3 + 6 * i / n, _transform_base_fn(-3 + 6 * i / n)) for i in range(n + 1)]

    orig_pts: list[float] = []
    for pt in base_pts:
        px, py = to_px(*clamp(pt))
        orig_pts.extend([px, py])
    d.add(PolyLine(orig_pts, strokeColor=MUTED, strokeWidth=1.1, strokeDashArray=[3, 2]))

    trans_pts: list[float] = []
    for pt in base_pts:
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
    probability strings shown at each leaf. A branch's prob_str may be ""
    (or omitted/falsy) to draw a short blank placeholder line instead of a
    value, for a tree the student is meant to complete themselves.
    params['stage1_header']/['stage2_header'] (optional) caption the two
    columns of branches (e.g. the name of each stage's random event), drawn
    above the diagram - matching real exam-style labelled trees."""
    stage1: list[tuple[str, str]] = params["stage1"]
    stage2: list[list[tuple[str, str]]] = params["stage2"]
    leaf_probs: list[list[str]] | None = params.get("leaf_probs")
    stage1_header = params.get("stage1_header")
    stage2_header = params.get("stage2_header")

    branch_counts = [len(b) for b in stage2]
    total_leaves = sum(branch_counts)

    leaf_spacing, group_spacing = 46.0, 20.0
    header_h = 26.0 if (stage1_header or stage2_header) else 0.0
    top_pad, bottom_pad = 14.0 + header_h, 14.0
    height = max(
        150.0,
        top_pad + bottom_pad + total_leaves * leaf_spacing + max(0, len(branch_counts) - 1) * group_spacing,
    )
    width = 460.0 if leaf_probs is not None else 400.0
    d = Drawing(width, height)

    x1, x2, x3 = width * 0.30, width * 0.58, width * 0.85
    root_x = 16.0

    leaf_ys: list[list[float]] = []
    cursor = bottom_pad + leaf_spacing / 2
    for count in branch_counts:
        ys = [cursor + i * leaf_spacing for i in range(count)]
        leaf_ys.append(ys)
        cursor += count * leaf_spacing + group_spacing

    node1_ys = [sum(ys) / len(ys) for ys in leaf_ys]
    root_y = sum(node1_ys) / len(node1_ys)

    if stage1_header:
        d.add(String(x1, height - 16, str(stage1_header), textAnchor="middle", fontSize=10, fillColor=INK, fontName=_LABEL_FONT_BOLD))
    if stage2_header:
        d.add(String(x2, height - 16, str(stage2_header), textAnchor="middle", fontSize=10, fillColor=INK, fontName=_LABEL_FONT_BOLD))

    def _branch_prob(x_from: float, y_from: float, x_to: float, y_to: float, prob: str, size: float) -> None:
        # Offset the probability label perpendicular to the branch line
        # (rather than a fixed vertical amount) so it clears the line itself
        # regardless of the branch's slope - dx is always positive here
        # (every branch runs left to right), so this normal always points
        # "up" on the page, matching how real tree diagrams caption branches.
        dx, dy = x_to - x_from, y_to - y_from
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        lx, ly = (x_from + x_to) / 2 + nx * 12, (y_from + y_to) / 2 + ny * 12
        if prob:
            d.add(_label(lx, ly, prob, size=size))
        else:
            d.add(Line(lx - 9, ly - 2, lx + 9, ly - 2, strokeColor=INK, strokeWidth=0.9))

    def _node_label(x: float, y: float, text: str, size: float) -> None:
        # Every line/dash leaving this node starts exactly at (x, y) and
        # only ever extends to the right (greater x) - so a label centred
        # directly ABOVE the node (same x, y offset only) never touches any
        # of them, unlike a label offset to the right, which sat inside the
        # narrow wedge those lines fan out into and collided with one of
        # them as soon as the branches spread more than a few points apart.
        d.add(_label(x, y + 10, text, size=size))

    for i, ((label1, prob1), y1) in enumerate(zip(stage1, node1_ys)):
        d.add(Line(root_x, root_y, x1, y1, strokeColor=INK, strokeWidth=1.2))
        _branch_prob(root_x, root_y, x1, y1, prob1, 9)
        _node_label(x1, y1, label1, 9.5)

        for j, ((label2, prob2), y2) in enumerate(zip(stage2[i], leaf_ys[i])):
            d.add(Line(x1, y1, x2, y2, strokeColor=INK, strokeWidth=1.2))
            _branch_prob(x1, y1, x2, y2, prob2, 9)
            if leaf_probs is not None:
                d.add(Line(x2, y2, x3, y2, strokeColor=MUTED, strokeWidth=0.5, strokeDashArray=[2, 2]))
                _node_label(x2, y2, label2, 9.5)
                d.add(_label(x3 + 6, y2 + 3, leaf_probs[i][j], anchor="start", color=ACCENT, size=8.5))
            else:
                d.add(_label(x2 + 6, y2 + 3, label2, anchor="start", size=9.5))

    d.add(Circle(root_x, root_y, 2.2, strokeColor=INK, fillColor=INK))
    return d


def draw_two_way_table(params: dict) -> Drawing:
    """A grid table with row_labels down the side and col_labels across the
    top (typically including a trailing 'Total' row/column), filled with
    params['cells'] (a row_labels x col_labels 2D list of strings; blank
    entries render as empty cells for a 'complete the table' question)."""
    row_labels: list[str] = params["row_labels"]
    col_labels: list[str] = params["col_labels"]
    cells: list[list[str]] = params["cells"]

    cell_w, cell_h = 44, 22
    # Wide enough for the longest row label (e.g. "Weekly sales (£1000s)"),
    # not just the original fixed 66 - a label longer than that was
    # overflowing straight through the header/first cell border.
    header_w = max(66.0, max((stringWidth(str(rl), _LABEL_FONT, 7.5) for rl in row_labels), default=0) + 10)
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
    d.add(_label(_VENN_CX_A, _VENN_CY + _VENN_R + 10, str(labels[0]), size=9))
    d.add(_label(_VENN_CX_B, _VENN_CY + _VENN_R + 10, str(labels[1]), size=9))

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


def _grid_minor_step(major_step: float) -> float:
    """Half the major tick step, when that lands on a clean whole number
    (e.g. a major step of 10 gives minor squares worth 5) - otherwise one
    square per major tick, rather than an arbitrary/always-1 subdivision
    regardless of the axis's real scale."""
    half = major_step / 2
    return half if abs(half - round(half)) < 1e-9 else major_step


def _draw_square_grid(
    d: Drawing, to_px: Callable, x0: float, y0: float, plot_w: float, plot_h: float,
    x_min: float, x_max: float, y_min: float, y_max: float, show_y_axis: bool,
) -> None:
    """A light squared-paper background, drawn underneath the real axes/
    ticks - square size is derived from each axis's own 'nice' tick step
    (never a flat 1-unit square regardless of scale, e.g. a y-axis running
    in 10s gets squares worth 5). When the y-axis has no real numeric
    meaning (show_y_axis=False, e.g. a box plot), the horizontal lines
    instead mirror the x minor step's own pixel size, so the grid still
    reads as genuine squares rather than an invented numeric scale."""
    x_major = _nice_tick_step(x_min, x_max)
    x_minor = _grid_minor_step(x_major)
    xv = math.ceil(x_min / x_minor) * x_minor
    while xv <= x_max + 1e-9:
        px, _ = to_px(xv, y_min)
        d.add(Line(px, y0, px, y0 + plot_h, strokeColor=GRID, strokeWidth=0.3))
        xv += x_minor

    if show_y_axis:
        y_major = _nice_tick_step(y_min, y_max)
        y_minor = _grid_minor_step(y_major)
        yv = math.ceil(y_min / y_minor) * y_minor
        while yv <= y_max + 1e-9:
            _, py = to_px(x_min, yv)
            d.add(Line(x0, py, x0 + plot_w, py, strokeColor=GRID, strokeWidth=0.3))
            yv += y_minor
    else:
        x_square_px = x_minor * plot_w / (x_max - x_min)
        py = y0
        while py <= y0 + plot_h + 1e-6:
            d.add(Line(x0, py, x0 + plot_w, py, strokeColor=GRID, strokeWidth=0.3))
            py += x_square_px


def _draw_stats_axes(
    d: Drawing, x0: float, y0: float, plot_w: float, plot_h: float,
    x_min: float, x_max: float, y_min: float, y_max: float,
    x_label: str = "", y_label: str = "",
    x_ticks: "list[float] | None" = None, y_ticks: "list[float] | None" = None,
    y_step: "float | None" = None, show_y_axis: bool = True, square_grid: bool = False,
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
    meaningful y-scale, e.g. a box plot). `square_grid=True` adds a light
    squared-paper background (see `_draw_square_grid`) for charts the
    student draws onto or reads values off precisely."""

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = x0 + (x - x_min) / (x_max - x_min) * plot_w
        py = y0 + (y - y_min) / (y_max - y_min) * plot_h
        return px, py

    if square_grid:
        _draw_square_grid(d, to_px, x0, y0, plot_w, plot_h, x_min, x_max, y_min, y_max, show_y_axis)

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
    gap = bar_slot - bar_w  # the same gap sits before every bar, including the first (see bx below)

    to_px = _draw_stats_axes(
        d, margin_l, y0, plot_w, plot_h, 0, n, 0, y_max, y_label=y_label,
        x_ticks=[], square_grid=True,
    )

    if not blank:
        for i in range(n):
            # The gap is placed BEFORE each bar (not split/centred either
            # side of it), so the axis-to-first-bar gap and every
            # between-bar gap all come out equal to `gap` - a centred bar
            # only gets half that gap on its left, since the other half
            # sits after it instead.
            bx = margin_l + i * bar_slot + gap
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
        cx = margin_l + i * bar_slot + gap + bar_w / 2
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
    """A pie chart. params['categories']: list of slice names. params
    ['values']: list of numbers (proportional to slice angle). Every wedge
    is unfilled (no colour) and labelled with its own category name and
    angle out of 360 (e.g. "Football (72°)") - real GCSE convention reads a
    pie chart's angles directly, not a colour key, so no legend is drawn.
    A label sits inside its wedge when there's room, otherwise just outside
    the circle (mirroring draw_spinner's narrow-sector handling)."""
    categories: list = params["categories"]
    values: list = params["values"]

    total = sum(values)
    cx, cy, r = 100, 82, 62
    d = Drawing(230, 164)

    cumulative = 0.0
    for i, v in enumerate(values):
        start = 90 + cumulative / total * 360
        cumulative += v
        end = 90 + cumulative / total * 360
        d.add(Wedge(cx, cy, r, start, end, fillColor=PAPER, strokeColor=INK, strokeWidth=0.8))

        mid = math.radians((start + end) / 2)
        angle_span = end - start
        angle_deg = round(v / total * 360)
        label_text = f"{categories[i]} ({angle_deg}°)"

        if angle_span >= 35:
            lx, ly = cx + r * 0.62 * math.cos(mid), cy + r * 0.62 * math.sin(mid) - 3
            d.add(_label(lx, ly, label_text, size=7))
        else:
            lx, ly = cx + (r + 14) * math.cos(mid), cy + (r + 14) * math.sin(mid) - 3
            anchor = "start" if math.cos(mid) >= 0 else "end"
            d.add(_label(lx, ly, label_text, size=7, anchor=anchor))

    return d


def draw_pie_chart_with_table(params: dict) -> Drawing:
    """The solution-page diagram for pie_chart_construct: the completed
    Category/Frequency/Angle table stacked above the completed pie chart -
    composed as one Drawing (via a nested, translated child Drawing, since
    a Question only carries one diagram slot per page) mirroring
    draw_plans_and_elevations_question's precedent."""
    categories: list = params["categories"]
    values: list = params["values"]
    angle_degrees: list = params["angle_degrees"]

    table = draw_two_way_table({
        "row_labels": [str(c) for c in categories],
        "col_labels": ["Frequency", "Angle"],
        "cells": [[str(v), f"{a}°"] for v, a in zip(values, angle_degrees)],
    })
    pie = draw_pie_chart({"categories": categories, "values": values})

    gap = 10
    width = max(table.width, pie.width)
    height = table.height + gap + pie.height
    d = Drawing(width, height)
    pie.transform = (1, 0, 0, 1, 0, 0)
    d.add(pie)
    table.transform = (1, 0, 0, 1, 0, pie.height + gap)
    d.add(table)
    return d


def draw_box_plot(params: dict) -> Drawing:
    """One or more box plots sharing a numeric axis. params['box_plots'] is a
    list of {"label": str (optional), "min", "q1", "median", "q3", "max"}.
    params['blank'] draws the axis (and square grid) only, no boxes - for
    the question page of a 'draw this yourself' question."""
    box_plots: list = params["box_plots"]
    x_label = params.get("x_label", "")
    blank = params.get("blank", False)

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
        d, margin_l, axis_y, plot_w, height - axis_y, x_min, x_max, 0, 1, x_label=x_label,
        show_y_axis=False, square_grid=True,
    )

    if blank:
        return d

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
        x_label=x_label, y_label=y_label, square_grid=True,
    )

    if not blank:
        for i in range(len(boundaries) - 1):
            x0, y0 = to_px(boundaries[i], 0)
            x1, y1 = to_px(boundaries[i + 1], densities[i])
            d.add(Rect(x0, y0, x1 - x0, y1 - y0, fillColor=HIGHLIGHT, strokeColor=INK, strokeWidth=0.7))

    return d


def _smooth_curve(points: list, **kwargs) -> PolyLine:
    """A smooth curve through `points` (pixel coordinates), built from a
    Catmull-Rom spline sampled densely and joined as one PolyLine - real
    exam convention draws a cumulative frequency curve smoothly, not as
    straight line segments. Each segment's interpolated x/y is clamped
    between its own two endpoints' values, so the curve never overshoots
    past a neighbouring point - kept safe for a graph the student reads
    real values off."""
    if len(points) < 3:
        return PolyLine([c for pt in points for c in pt], **kwargs)

    def catmull_rom(p0, p1, p2, p3, t):
        t2, t3 = t * t, t * t * t
        x = 0.5 * (
            2 * p1[0] + (-p0[0] + p2[0]) * t
            + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
            + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
        )
        y = 0.5 * (
            2 * p1[1] + (-p0[1] + p2[1]) * t
            + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
            + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
        )
        return x, y

    samples = 14
    n = len(points)
    out: list[float] = []
    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[i + 1]
        x_lo, x_hi = min(p1[0], p2[0]), max(p1[0], p2[0])
        y_lo, y_hi = min(p1[1], p2[1]), max(p1[1], p2[1])
        steps = samples if i < n - 2 else samples + 1
        for s in range(steps):
            t = s / samples
            x, y = catmull_rom(p0, p1, p2, p3, t)
            out.extend([min(max(x, x_lo), x_hi), min(max(y, y_lo), y_hi)])
    return PolyLine(out, **kwargs)


def draw_histogram_question(params: dict) -> Drawing:
    """The question-page diagram for histogram_plot: the class/frequency
    data table stacked above the blank (squared-paper) axes the student
    draws their bars onto - composed as one Drawing, mirroring
    draw_cumulative_frequency_question's precedent."""
    boundaries: list = params["boundaries"]
    frequencies: list = params["frequencies"]

    table = draw_two_way_table({
        "row_labels": [f"{boundaries[i]}-{boundaries[i + 1]}" for i in range(len(frequencies))],
        "col_labels": ["Frequency"],
        "cells": [[str(f)] for f in frequencies],
    })
    axes = draw_histogram({
        "boundaries": boundaries, "frequency_densities": params["frequency_densities"],
        "x_label": params.get("x_label", ""), "blank": True,
    })

    gap = 10
    width = max(table.width, axes.width)
    height = table.height + gap + axes.height
    d = Drawing(width, height)
    axes.transform = (1, 0, 0, 1, 0, 0)
    d.add(axes)
    table.transform = (1, 0, 0, 1, 0, axes.height + gap)
    d.add(table)
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
        x_label=x_label, y_label=y_label, x_ticks=xs, square_grid=True,
    )

    if not blank:
        px_points = [to_px(x, y) for x, y in points]
        d.add(_smooth_curve(px_points, strokeColor=ACCENT, strokeWidth=1.3))
        for px, py in px_points:
            _cross_marker(d, px, py, color=ACCENT)

    return d


def draw_cumulative_frequency_question(params: dict) -> Drawing:
    """The question-page diagram for cumulative_frequency_plot: the class/
    frequency data table stacked above the blank (squared-paper) axes the
    student draws their curve onto - composed as one Drawing since a
    Question only carries one diagram slot per page, mirroring
    draw_plans_and_elevations_question's precedent."""
    boundaries: list = params["boundaries"]
    frequencies: list = params["frequencies"]

    table = draw_two_way_table({
        "row_labels": [f"{boundaries[i]}-{boundaries[i + 1]}" for i in range(len(frequencies))],
        "col_labels": ["Frequency"],
        "cells": [[str(f)] for f in frequencies],
    })
    axes = draw_cumulative_frequency({"points": params["points"], "x_label": params.get("x_label", ""), "blank": True})

    gap = 10
    width = max(table.width, axes.width)
    height = table.height + gap + axes.height
    d = Drawing(width, height)
    axes.transform = (1, 0, 0, 1, 0, 0)
    d.add(axes)
    table.transform = (1, 0, 0, 1, 0, axes.height + gap)
    d.add(table)
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
            _cross_marker(d, px, py, color=ACCENT)

    return d


def draw_scatter_graph(params: dict) -> Drawing:
    """A scatter graph through params['points'] (a list of (x, y) pairs) -
    unlike draw_time_series/draw_cumulative_frequency, points are plotted as
    unconnected markers only (no PolyLine), since a scatter graph's x-values
    have no implied order/sequence to join. params['blank'] draws axes only.
    params['best_fit'] (optional {"m", "c"}) draws a single straight line of
    best fit spanning the full x-range - a genuinely new element with no
    precedent in draw_time_series/draw_cumulative_frequency, since neither
    of those diagram kinds ever draws a second, independent line alongside
    the data."""
    points: list = params["points"]
    blank = params.get("blank", False)
    best_fit = params.get("best_fit")
    x_label = params.get("x_label", "x")
    y_label = params.get("y_label", "y")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_span_raw = (max(xs) - min(xs)) or 1
    y_span_raw = (max(ys) - min(ys)) or 1
    x_min, x_max = min(xs) - x_span_raw * 0.1, max(xs) + x_span_raw * 0.1
    y_min_raw, y_max_raw = min(ys) - y_span_raw * 0.15, max(ys) + y_span_raw * 0.15
    y_min = max(0, y_min_raw) if min(ys) >= 0 else y_min_raw
    y_max = y_max_raw

    width, height = 230, 150
    margin_l, margin_r, margin_t, margin_b = 30, 12, 10, 24
    plot_w, plot_h = width - margin_l - margin_r, height - margin_t - margin_b
    d = Drawing(width, height)

    to_px = _draw_stats_axes(
        d, margin_l, margin_b, plot_w, plot_h, x_min, x_max, y_min, y_max,
        x_label=x_label, y_label=y_label, square_grid=True,
    )

    if not blank:
        for x, y in points:
            px, py = to_px(x, y)
            _cross_marker(d, px, py)

        if best_fit is not None:
            m, c = best_fit["m"], best_fit["c"]
            x0, x1 = x_min, x_max
            y0, y1 = m * x0 + c, m * x1 + c
            px0, py0 = to_px(x0, y0)
            px1, py1 = to_px(x1, y1)
            d.add(Line(px0, py0, px1, py1, strokeColor=ACCENT, strokeWidth=1.3))

    return d


def draw_fraction_shapes(params: dict) -> Drawing:
    """One or more shapes (bar or circle), each divided into `parts` equal
    segments with `shaded` of them filled - illustrates a fraction shaded/parts.
    params['shapes']: list of {"kind": "bar"|"circle", "parts": int,
    "shaded": int, "label": Optional[str]} dicts, laid out left to right."""
    shapes: list[dict] = params["shapes"]
    cell_w = 70
    d = Drawing(cell_w * len(shapes) + 20, 110)

    for i, shape in enumerate(shapes):
        cx = 20 + cell_w * i + cell_w / 2
        parts, shaded = shape["parts"], shape["shaded"]

        if shape["kind"] == "circle":
            cy, r = 60, 32
            for seg in range(parts):
                start = 90 + seg * 360 / parts
                end = 90 + (seg + 1) * 360 / parts
                fill = HIGHLIGHT if seg < shaded else PAPER
                d.add(Wedge(cx, cy, r, start, end, fillColor=fill, strokeColor=INK, strokeWidth=0.8))
        else:
            bw, bh = 54, 34
            bx, by = cx - bw / 2, 60 - bh / 2
            seg_w = bw / parts
            for seg in range(shaded):
                d.add(Rect(bx + seg * seg_w, by, seg_w, bh, fillColor=HIGHLIGHT, strokeColor=None))
            for seg in range(1, parts):
                d.add(Line(bx + seg * seg_w, by, bx + seg * seg_w, by + bh, strokeColor=GRID, strokeWidth=0.6))
            d.add(Rect(bx, by, bw, bh, fillColor=None, strokeColor=INK, strokeWidth=1))

        if shape.get("label"):
            d.add(_label(cx, 12, str(shape["label"]), anchor="middle", size=10))

    return d


_PIP_LAYOUTS = {
    1: [(0, 0)],
    2: [(-1, -1), (1, 1)],
    3: [(-1, -1), (0, 0), (1, 1)],
    4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
    5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
    6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)],
}


def draw_dice(params: dict) -> Drawing:
    """One or two die faces with standard pip layouts. params['values']:
    list of 1-2 ints in 1..6. params['highlight']: optional list of indices
    (into values) whose face gets an accent-coloured border."""
    values: list[int] = params["values"]
    highlight = set(params.get("highlight", []))
    face, gap = 60, 20
    d = Drawing(face * len(values) + gap * (len(values) + 1), face + 2 * gap)

    for i, val in enumerate(values):
        x, y = gap + i * (face + gap), gap
        border_color = ACCENT if i in highlight else INK
        border_width = 1.8 if i in highlight else 1
        d.add(Rect(x, y, face, face, rx=8, ry=8, fillColor=PAPER, strokeColor=border_color, strokeWidth=border_width))
        cx, cy = x + face / 2, y + face / 2
        offset, pip_r = face * 0.24, face * 0.07
        for dx, dy in _PIP_LAYOUTS[val]:
            d.add(Circle(cx + dx * offset, cy - dy * offset, pip_r, fillColor=INK, strokeColor=None))

    return d


def _draw_spinner_at(d: Drawing, cx: float, cy: float, r: float, sectors: list, highlight: set) -> None:
    n = len(sectors)
    for i, label in enumerate(sectors):
        start = 90 + i * 360 / n
        end = 90 + (i + 1) * 360 / n
        fill = HIGHLIGHT if i in highlight else PAPER
        d.add(Wedge(cx, cy, r, start, end, fillColor=fill, strokeColor=INK, strokeWidth=0.8))
        mid = math.radians((start + end) / 2)
        d.add(_label(cx + r * 0.62 * math.cos(mid), cy + r * 0.62 * math.sin(mid) - 3, str(label), size=8))

    d.add(Polygon(points=[cx - 5, cy, cx + 5, cy, cx, cy + r * 0.55], fillColor=ACCENT, strokeColor=None))
    d.add(Circle(cx, cy, 4, fillColor=INK, strokeColor=None))


def draw_spinner(params: dict) -> Drawing:
    """A spinner divided into equal sectors, each labelled. params['sectors']:
    list of label strings (one per equal sector). params['highlight']:
    optional list of sector indices filled to mark the target outcome(s)."""
    sectors: list[str] = params["sectors"]
    highlight = set(params.get("highlight", []))
    d = Drawing(150, 130)
    _draw_spinner_at(d, 75, 65, 50, sectors, highlight)
    return d


def draw_spinner_pair(params: dict) -> Drawing:
    """Two independent spinners side by side, for questions combining two
    spinners (e.g. listing outcomes) where neither spinner has a marked
    target outcome - so unlike draw_spinner, there is no highlight param."""
    d = Drawing(320, 130)
    _draw_spinner_at(d, 75, 65, 50, params["sectors_a"], set())
    _draw_spinner_at(d, 245, 65, 50, params["sectors_b"], set())
    return d


def draw_coin(params: dict) -> Drawing:
    """One or two coin faces, each shown split into its two possible
    outcomes (H on the top half, T on the bottom half) - matching how
    draw_spinner shows every sector at once, since this is meant to
    illustrate the object, not one specific flip result. params['count']:
    how many coins to draw side by side (default 1)."""
    count = params.get("count", 1)
    r, gap = 32.0, 22.0
    width = count * (2 * r) + (count + 1) * gap
    height = 2 * r + 2 * gap
    d = Drawing(width, height)
    cy = height / 2
    for i in range(count):
        cx = gap + r + i * (2 * r + gap)
        d.add(Circle(cx, cy, r, fillColor=PAPER, strokeColor=INK, strokeWidth=1.2))
        d.add(Line(cx - r, cy, cx + r, cy, strokeColor=INK, strokeWidth=0.7))
        d.add(_label(cx, cy + r * 0.32, "H", size=12))
        d.add(_label(cx, cy - r * 0.62, "T", size=12))
    return d


def draw_event_pair(params: dict) -> Drawing:
    """Two independent single-object illustrations (a coin, a die, and/or a
    spinner) side by side, for questions combining two different random
    objects (e.g. 'a coin is flipped and a die is rolled'). params
    ['event_a']/['event_b']: each a dict {"kind": "coin"|"dice"|"spinner",
    **kind-specific params, matching draw_coin/draw_dice/draw_spinner's own
    params contract} - composed via the same nested-translated-Drawing
    technique already used by draw_plans_and_elevations_question."""

    def _build(event: dict) -> Drawing:
        kind = event["kind"]
        if kind == "coin":
            return draw_coin({"count": event.get("count", 1)})
        if kind == "dice":
            return draw_dice({"values": event["values"], "highlight": event.get("highlight", [])})
        return draw_spinner({"sectors": event["sectors"], "highlight": event.get("highlight", [])})

    a = _build(params["event_a"])
    b = _build(params["event_b"])
    gap = 20.0
    width = a.width + gap + b.width
    height = max(a.height, b.height)
    d = Drawing(width, height)
    a.transform = (1, 0, 0, 1, 0, (height - a.height) / 2)
    d.add(a)
    b.transform = (1, 0, 0, 1, a.width + gap, (height - b.height) / 2)
    d.add(b)
    return d


_COUNTER_COLOURS = {
    "red": colors.HexColor("#c0555f"),
    "blue": colors.HexColor("#4a72b0"),
    "green": colors.HexColor("#2f6f4f"),
    "yellow": colors.HexColor("#d9a521"),
    "purple": colors.HexColor("#9b6bb0"),
}


def draw_bag(params: dict) -> Drawing:
    """A rectangular bag outline packed with small filled counters. params
    ['counts']: dict of colour name -> count. The counters are interleaved
    round-robin across colours (not grouped into colour blocks) so they read
    as a freely-mixed handful, and the counter size/grid is sized from the
    total count so they fill the rectangle as fully as possible regardless
    of how many there are."""
    counts: dict[str, int] = params["counts"]
    width, height = 160, 120
    d = Drawing(width, height)

    body_x, body_y, body_w, body_h = 12, 12, width - 24, height - 24
    d.add(Rect(body_x, body_y, body_w, body_h, fillColor=PAPER, strokeColor=INK, strokeWidth=1.3))

    order = list(counts.keys())
    remaining = dict(counts)
    tokens: list[str] = []
    while any(remaining[c] > 0 for c in order):
        for c in order:
            if remaining[c] > 0:
                tokens.append(c)
                remaining[c] -= 1

    total = max(1, len(tokens))
    cols = max(1, math.ceil(math.sqrt(total * body_w / body_h)))
    rows = max(1, math.ceil(total / cols))
    cell_w, cell_h = body_w / cols, body_h / rows
    r = max(3.2, min(cell_w, cell_h) / 2 * 0.85)
    r = min(r, 7.0)

    for i, colour in enumerate(tokens):
        row, col = divmod(i, cols)
        cx = body_x + cell_w * (col + 0.5)
        cy = body_y + body_h - cell_h * (row + 0.5)
        fill = _COUNTER_COLOURS.get(colour, MUTED)
        d.add(Circle(cx, cy, r, fillColor=fill, strokeColor=INK, strokeWidth=0.4))

    return d


SOLID_WIDTH = 200
SOLID_HEIGHT = 150

# Fixed oblique "depth" offset applied to a straight-edged solid's front-face
# coordinates to get its back-face coordinates - gives every 3D sketch below a
# consistent look. These are schematic ("Diagram NOT accurately drawn")
# sketches at fixed on-canvas proportions, like draw_general_triangle/
# draw_right_triangle above, not scaled to the question's real numbers -
# a scale-accurate oblique projection isn't how real exam papers draw these
# either.
_SOLID_DX, _SOLID_DY = 26, 16


def _offset(pt: tuple[float, float], dx: float = _SOLID_DX, dy: float = _SOLID_DY) -> tuple[float, float]:
    return (pt[0] + dx, pt[1] + dy)


def draw_cuboid(params: dict) -> Drawing:
    """A cuboid in oblique projection (front face + visible top/right faces
    solid; the three edges meeting at the hidden back-bottom-left vertex
    dashed). A cube is just this same diagram with all three edge labels
    equal - no separate function needed, UNLESS params['is_cube'] is set, in
    which case the front face is drawn genuinely square (rather than always
    the same fixed 80x60 rectangle regardless of input) so it actually reads
    as a cube on screen, not a generic cuboid."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    if params.get("is_cube"):
        x0, y0, fw, fh = 60, 24, 66, 66
    else:
        x0, y0, fw, fh = 55, 30, 80, 60
    FBL, FBR, FTR, FTL = (x0, y0), (x0 + fw, y0), (x0 + fw, y0 + fh), (x0, y0 + fh)
    BBL, BBR, BTR, BTL = _offset(FBL), _offset(FBR), _offset(FTR), _offset(FTL)

    d.add(Rect(x0, y0, fw, fh, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Polygon([*FTL, *FTR, *BTR, *BTL], strokeColor=INK, fillColor=None, strokeWidth=1.1))
    d.add(Polygon([*FBR, *FTR, *BTR, *BBR], strokeColor=INK, fillColor=None, strokeWidth=1.1))
    d.add(Line(*FBL, *BBL, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(Line(*BBL, *BBR, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(Line(*BBL, *BTL, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))

    d.add(_label(x0 + fw / 2, y0 - 14, params["width_label"]))
    d.add(_label(x0 - 10, y0 + fh / 2, params["height_label"], anchor="end"))
    d.add(_label((FBR[0] + BBR[0]) / 2 + 6, (FBR[1] + BBR[1]) / 2 - 4, params["length_label"], anchor="start", size=8))
    if params.get("diagonal_label"):
        d.add(Line(*FBL, *BTR, strokeColor=INK, strokeWidth=0.9, strokeDashArray=[3, 2]))
        # Placed 60% of the way along the diagonal (toward G/BTR) rather than
        # at the exact midpoint - the midpoint sits right in the cluster of
        # hidden dashed edges near the back-bottom-left vertex (D), which
        # collided with D's own vertex label once vertex_labels was added.
        mx = FBL[0] + (BTR[0] - FBL[0]) * 0.6
        my = FBL[1] + (BTR[1] - FBL[1]) * 0.6
        d.add(_label(mx + 6, my + 4, params["diagonal_label"], anchor="start", size=8))

    vertex_labels = params.get("vertex_labels")
    if vertex_labels:
        # Standard ABCD/EFGH cuboid-vertex naming: base face A-B-C-D going
        # front-left, front-right, back-right, back-left; top face E-F-G-H
        # directly above. This makes AG (FBL<->BTR) the true space diagonal
        # already drawn above when diagonal_label is set.
        points_order = [FBL, FBR, BBR, BBL, FTL, FTR, BTR, BTL]
        cx_all = sum(p[0] for p in points_order) / len(points_order)
        cy_all = sum(p[1] for p in points_order) / len(points_order)
        for pt, lbl in zip(points_order, vertex_labels):
            dx_l, dy_l = pt[0] - cx_all, pt[1] - cy_all
            dist = math.hypot(dx_l, dy_l) or 1.0
            lx, ly = pt[0] + dx_l / dist * 13, pt[1] + dy_l / dist * 13
            d.add(_label(lx, ly, lbl, size=7.5))

    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_triangular_prism(params: dict) -> Drawing:
    """A right-angled-triangle cross-section prism in oblique projection.
    Every edge is visible/solid except the far back-bottom edge of the
    hidden underside face, which is dashed."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    A, B, C = (55, 30), (135, 30), (55, 90)  # right angle at A
    A2, B2, C2 = _offset(A), _offset(B), _offset(C)

    d.add(Polygon([*A, *B, *C], strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(*A, *A2, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*B, *B2, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*C, *C2, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*B2, *C2, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*C2, *A2, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*A2, *B2, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))

    s = 7
    d.add(Rect(A[0], A[1], s, s, strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(_label((A[0] + B[0]) / 2, A[1] - 14, params["base_label"]))
    d.add(_label(A[0] - 10, (A[1] + C[1]) / 2, params["triangle_height_label"], anchor="end"))
    d.add(_label((B[0] + B2[0]) / 2 + 6, (B[1] + B2[1]) / 2 - 4, params["length_label"], anchor="start", size=8))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_plans_and_elevations(params: dict) -> Drawing:
    """Three flat orthographic views (front elevation, side elevation, plan)
    of a solid, laid out in the standard first-angle arrangement - plan
    directly below the front view (sharing its width), side view directly
    to the right of the front view (sharing its height). Genuinely
    different in style from every other 3D diagram in this file
    (draw_cuboid, draw_triangular_prism, etc.), which all use oblique/
    cavalier projection via _offset() - no existing helper produces true
    orthographic projections, so this is built from scratch with plain flat
    Rect/Polygon shapes, each sized proportionally to the solid's real
    dimensions from a single shared scale (not just topologically laid out,
    unlike draw_net's unfolded-face diagrams).

    Every solid here reduces to the same three shapes by the same
    reasoning: the plan view and side view are always plain rectangles
    (the silhouette swept along the length is constant), and only the
    front view varies with the solid's actual cross-section (a rectangle
    for a cuboid, a right-angled triangle for a triangular prism)."""
    shape = params["shape"]
    if shape == "cuboid":
        dim_x, dim_y, dim_z = params["length"], params["height"], params["width"]
        x_label, y_label, z_label = params["length_label"], params["height_label"], params["width_label"]
        front_kind = "rect"
    elif shape == "triangular_prism":
        dim_x, dim_y, dim_z = params["base"], params["tri_height"], params["length"]
        x_label, y_label, z_label = params["base_label"], params["tri_height_label"], params["length_label"]
        front_kind = "triangle"
    else:
        raise ValueError(f"unknown plans/elevations shape: {shape!r}")

    cell = 60
    scale = cell / max(dim_x, dim_y, dim_z)
    sx, sy, sz = dim_x * scale, dim_y * scale, dim_z * scale

    # The "Front elevation"/"Side elevation" captions are centred over their
    # own box, but a small solid shrinks both boxes (and the gap between
    # them) while the caption text itself stays a fixed width - a real bug
    # found via rendering an actual modelled-example page and looking
    # closely (not a unit test): a small solid's captions ran together with
    # no gap at all ("Front elevationSide elevation"). Widen the gap
    # whenever the two captions' own widths would otherwise overlap.
    front_caption_w = stringWidth("Front elevation", "Helvetica", 7.5)
    side_caption_w = stringWidth("Side elevation", "Helvetica", 7.5)
    min_gap = front_caption_w / 2 + side_caption_w / 2 + 6 - sx / 2 - sz / 2
    gap = max(16, min_gap)
    margin_l, margin_bottom = 50, 26
    fx0 = margin_l
    fy0 = margin_bottom + sz + gap

    d_width = fx0 + sx + gap + sz + 20
    d_height = fy0 + sy + 22
    d = Drawing(d_width, d_height)

    d.add(_label(fx0 + sx / 2, fy0 + sy + 14, "Front elevation", size=7.5))
    d.add(_label(fx0 + sx + gap + sz / 2, fy0 + sy + 14, "Side elevation", size=7.5))
    d.add(_label(fx0 + sx / 2, margin_bottom - 12, "Plan view", size=7.5))

    if front_kind == "rect":
        d.add(Rect(fx0, fy0, sx, sy, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    else:
        d.add(Polygon(
            [fx0, fy0, fx0 + sx, fy0, fx0, fy0 + sy],
            strokeColor=INK, fillColor=None, strokeWidth=1.2,
        ))
        s = 7
        d.add(Rect(fx0, fy0, s, s, strokeColor=INK, fillColor=None, strokeWidth=1))

    d.add(Rect(fx0, margin_bottom, sx, sz, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Rect(fx0 + sx + gap, fy0, sz, sy, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    d.add(_label(fx0 + sx / 2, fy0 - 10, x_label, size=8))
    d.add(_label(fx0 - 8, fy0 + sy / 2, y_label, anchor="end", size=8))
    d.add(_label(fx0 + sx + gap + sz / 2, fy0 - 10, z_label, size=8))
    d.add(_label(fx0 - 8, margin_bottom + sz / 2, z_label, anchor="end", size=8))

    return d


def draw_plans_and_elevations_blank(params: dict) -> Drawing:
    """Three empty ruled/squared boxes in the same front/side/plan layout as
    draw_plans_and_elevations' real answer, for the student to sketch their
    own views into on the question page. Deliberately fixed equal-sized
    boxes, NOT scaled to the solid's real proportions (unlike the answer
    version) - the blank grid must never hint at the solid's actual shape or
    dimensions before the student has worked it out."""
    box = 60
    grid_step = 12
    gap = 16
    margin_l, margin_bottom = 50, 26
    fx0 = margin_l
    fy0 = margin_bottom + box + gap

    d_width = fx0 + box + gap + box + 20
    d_height = fy0 + box + 22
    d = Drawing(d_width, d_height)

    d.add(_label(fx0 + box / 2, fy0 + box + 14, "Front elevation", size=7.5))
    d.add(_label(fx0 + box + gap + box / 2, fy0 + box + 14, "Side elevation", size=7.5))
    d.add(_label(fx0 + box / 2, margin_bottom - 12, "Plan view", size=7.5))

    def squared_box(x0: float, y0: float) -> None:
        n = round(box / grid_step)
        for i in range(1, n):
            d.add(Line(x0 + i * grid_step, y0, x0 + i * grid_step, y0 + box, strokeColor=GRID, strokeWidth=0.4))
            d.add(Line(x0, y0 + i * grid_step, x0 + box, y0 + i * grid_step, strokeColor=GRID, strokeWidth=0.4))
        d.add(Rect(x0, y0, box, box, strokeColor=INK, fillColor=None, strokeWidth=1.2))

    squared_box(fx0, fy0)
    squared_box(fx0, margin_bottom)
    squared_box(fx0 + box + gap, fy0)

    return d


def draw_plans_and_elevations_question(params: dict) -> Drawing:
    """The question-page diagram for plans_and_elevations: the existing
    oblique 3D sketch (reusing draw_cuboid/draw_triangular_prism unchanged)
    stacked above a blank squared grid (draw_plans_and_elevations_blank) for
    the student to sketch their answer into - composed as one Drawing (via
    a nested, translated child Drawing) since a Question only carries one
    diagram slot for its question page."""
    shape = params["shape"]
    if shape == "cuboid":
        solid = draw_cuboid({
            "length_label": params["length_label"],
            "width_label": params["width_label"],
            "height_label": params["height_label"],
        })
    elif shape == "triangular_prism":
        solid = draw_triangular_prism({
            "base_label": params["base_label"],
            "triangle_height_label": params["triangle_height_label"],
            "length_label": params["length_label"],
        })
    else:
        raise ValueError(f"unknown plans/elevations shape: {shape!r}")

    blank = draw_plans_and_elevations_blank({"shape": shape})

    gap = 10
    d_width = max(solid.width, blank.width)
    d_height = solid.height + gap + blank.height
    d = Drawing(d_width, d_height)

    blank.transform = (1, 0, 0, 1, 0, 0)
    d.add(blank)
    solid.transform = (1, 0, 0, 1, 0, blank.height + gap)
    d.add(solid)

    return d


def _cylinder_edges(cx: float, top_y: float, bottom_y: float, rx: float, ry: float) -> list:
    """The Drawing primitives for a cylinder body between two ellipse
    centres - shared by draw_cylinder and the cylinder+hemisphere compound
    'capsule' variant of draw_compound_3d."""
    return [
        Line(cx - rx, top_y, cx - rx, bottom_y, strokeColor=INK, strokeWidth=1.1),
        Line(cx + rx, top_y, cx + rx, bottom_y, strokeColor=INK, strokeWidth=1.1),
        Ellipse(cx, bottom_y, rx, ry, strokeColor=INK, fillColor=None, strokeWidth=1.2),
        Ellipse(cx, top_y, rx, ry, strokeColor=INK, fillColor=None, strokeWidth=1.2),
    ]


def draw_cylinder(params: dict) -> Drawing:
    """A cylinder: two ellipses (rounded solids draw both end-boundaries
    fully solid rather than splitting hidden/visible arcs - a deliberate,
    lower-risk simplification vs. straight-edged solids' dashed hidden
    edges) plus two vertical tangent side lines."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    cx, top_y, bottom_y, rx, ry = 100, 108, 32, 40, 13
    for shape in _cylinder_edges(cx, top_y, bottom_y, rx, ry):
        d.add(shape)
    d.add(Line(cx, top_y, cx + rx, top_y, strokeColor=INK, strokeWidth=0.9))
    d.add(_label(cx + rx / 2, top_y + 8, params["radius_label"], size=8))
    d.add(_label(cx + rx + 10, (top_y + bottom_y) / 2, params["height_label"], anchor="start"))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_cone(params: dict) -> Drawing:
    """A cone: apex point, base ellipse, two slant tangent lines. When
    params['show_height_triangle'] is set, a dashed vertical height + a
    dashed horizontal radius are added (the right-angled Pythagoras helper
    triangle used when a question requires deriving the slant height)."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    cx, apex_y, base_y, rx, ry = 100, 122, 32, 42, 13
    d.add(Ellipse(cx, base_y, rx, ry, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(cx - rx, base_y, cx, apex_y, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(cx + rx, base_y, cx, apex_y, strokeColor=INK, strokeWidth=1.2))
    if params.get("show_height_triangle"):
        d.add(Line(cx, apex_y, cx, base_y, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        d.add(Line(cx, base_y, cx + rx, base_y, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        d.add(_label(cx + 6, (apex_y + base_y) / 2, params["height_label"], anchor="start", size=8))
    if params.get("slant_label"):
        slant_x, slant_y = cx + rx * 0.62, apex_y + (base_y - apex_y) * 0.62
        d.add(_label(slant_x + 6, slant_y, params["slant_label"], anchor="start", size=8))
    d.add(_label(cx - rx / 2, base_y - 10, params["radius_label"], size=8))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_sphere(params: dict) -> Drawing:
    """A sphere (circle outline + a flattened equator ellipse as the 3D
    cue), or - when params['hemisphere'] is set - a dome: a flat base
    ellipse with a semicircular arc rising from its tangent points."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    cx, cy, r = 100, 78, 46
    if params.get("hemisphere"):
        base_y = cy - r * 0.15
        d.add(Ellipse(cx, base_y, r, r * 0.3, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        arc = ArcPath(strokeColor=INK, fillColor=None, strokeWidth=1.2)
        arc.addArc(cx, base_y, r, 0, 180, moveTo=True)
        d.add(arc)
        d.add(Line(cx, base_y, cx + r, base_y, strokeColor=INK, strokeWidth=0.9))
        d.add(_label(cx + r / 2, base_y + 16, params["radius_label"], size=8))
    else:
        d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        d.add(Ellipse(cx, cy, r, r * 0.3, strokeColor=INK, fillColor=None, strokeWidth=0.9))
        d.add(Line(cx, cy, cx + r, cy, strokeColor=INK, strokeWidth=0.9))
        d.add(_label(cx + r / 2, cy + 16, params["radius_label"], size=8))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_pyramid(params: dict) -> Drawing:
    """A square-based right pyramid: the base drawn as a perspective
    'diamond', apex above the centre connected to all 4 corners. The two
    base edges further from the viewer (the diamond's back edges) are
    dashed; the two nearer edges and all four apex edges are solid."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    cx, base_y = 100, 40
    N, E, S, W = (cx, base_y + 22), (cx + 55, base_y), (cx, base_y - 22), (cx - 55, base_y)
    apex = (cx, base_y + 85)

    d.add(Line(*S, *E, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(*S, *W, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(*N, *E, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(Line(*N, *W, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
    d.add(Line(*apex, *N, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*apex, *E, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*apex, *S, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(*apex, *W, strokeColor=INK, strokeWidth=1.1))
    d.add(Line(cx, base_y, *apex, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))

    d.add(_label((S[0] + E[0]) / 2 + 8, (S[1] + E[1]) / 2 - 2, params["base_label"], anchor="start", size=8))
    # Placed just above N (the diamond's back vertex) so the label clears
    # both the dashed N-E back base edge below it and the converging slant
    # edge to its right - a label at the true midpoint crosses one or the
    # other (found via high-DPI visual inspection).
    height_label_y = base_y + (apex[1] - base_y) * 0.28
    d.add(_label(cx + 6, height_label_y, params["height_label"], anchor="start", size=8))
    if params.get("slant_label"):
        slant_x = apex[0] + (E[0] - apex[0]) * 0.65
        slant_y = apex[1] + (E[1] - apex[1]) * 0.65
        d.add(_label(slant_x + 6, slant_y, params["slant_label"], anchor="start", size=8))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


def draw_frustum(params: dict) -> Drawing:
    """A cone frustum: like draw_cone but with a smaller top ellipse instead
    of an apex point, connected by two slant tangent lines."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    cx, bottom_y, top_y = 100, 32, 100
    R, r_ry, r_top, r_top_ry = 46, 14, 24, 8

    d.add(Ellipse(cx, bottom_y, R, r_ry, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Ellipse(cx, top_y, r_top, r_top_ry, strokeColor=INK, fillColor=None, strokeWidth=1.2))
    d.add(Line(cx - R, bottom_y, cx - r_top, top_y, strokeColor=INK, strokeWidth=1.2))
    d.add(Line(cx + R, bottom_y, cx + r_top, top_y, strokeColor=INK, strokeWidth=1.2))

    d.add(_label(cx - R / 2, bottom_y - 10, params["radius_bottom_label"], size=8))
    d.add(_label(cx + r_top / 2, top_y + 8, params["radius_top_label"], size=8))
    d.add(_label(cx + R + 6, (bottom_y + top_y) / 2, params["height_label"], anchor="start"))
    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


NET_WIDTH = 220
NET_HEIGHT = 170

_NET_CELL = 30  # uniform face-cell size for the net layouts below - purely
# topological (correct face count/arrangement), not scaled to real question
# values, since a "which net folds into this solid" / "how many rectangles"
# question only depends on the layout, not exact proportions.


def _draw_net_cuboid(params: dict) -> Drawing:
    d = Drawing(NET_WIDTH, NET_HEIGHT)
    c = _NET_CELL
    x0, y0 = 20, 70
    for i in range(4):
        d.add(Rect(x0 + i * c, y0, c, c, strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Rect(x0, y0 + c, c, c, strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Rect(x0, y0 - c, c, c, strokeColor=INK, fillColor=None, strokeWidth=1))
    return d


def _draw_net_cylinder(params: dict) -> Drawing:
    d = Drawing(NET_WIDTH, NET_HEIGHT)
    rw, rh = 90, 40
    x0, y0 = (NET_WIDTH - rw) / 2, (NET_HEIGHT - rh) / 2
    r = 16
    d.add(Rect(x0, y0, rw, rh, strokeColor=INK, fillColor=None, strokeWidth=1.1))
    d.add(Circle(x0 + rw / 2, y0 + rh + r, r, strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Circle(x0 + rw / 2, y0 - r, r, strokeColor=INK, fillColor=None, strokeWidth=1))
    return d


def _draw_net_cone(params: dict) -> Drawing:
    d = Drawing(NET_WIDTH, NET_HEIGHT)
    cx, cy, r = 70, 85, 30
    d.add(Circle(cx, cy, r, strokeColor=INK, fillColor=None, strokeWidth=1.1))
    sector_cx, sector_r = 158, 60
    d.add(Wedge(sector_cx, cy, sector_r, -125, 125, strokeColor=INK, fillColor=None, strokeWidth=1.1))
    return d


def _draw_net_triangular_prism(params: dict) -> Drawing:
    d = Drawing(NET_WIDTH, NET_HEIGHT)
    c = _NET_CELL
    x0, y0 = 20, 70
    for i in range(3):
        d.add(Rect(x0 + i * c, y0, c, c + 10, strokeColor=INK, fillColor=None, strokeWidth=1))
    tri_top = y0 + c + 10
    d.add(Polygon([x0, tri_top, x0 + c, tri_top, x0 + c / 2, tri_top + 22], strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Polygon([x0, y0, x0 + c, y0, x0 + c / 2, y0 - 22], strokeColor=INK, fillColor=None, strokeWidth=1))
    return d


def _draw_net_pyramid(params: dict) -> Drawing:
    d = Drawing(NET_WIDTH, NET_HEIGHT)
    c = _NET_CELL * 1.4
    x0, y0 = (NET_WIDTH - c) / 2, (NET_HEIGHT - c) / 2
    d.add(Rect(x0, y0, c, c, strokeColor=INK, fillColor=None, strokeWidth=1.1))
    tri_h = c * 0.6
    d.add(Polygon([x0, y0 + c, x0 + c, y0 + c, x0 + c / 2, y0 + c + tri_h], strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Polygon([x0, y0, x0 + c, y0, x0 + c / 2, y0 - tri_h], strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Polygon([x0, y0, x0, y0 + c, x0 - tri_h, y0 + c / 2], strokeColor=INK, fillColor=None, strokeWidth=1))
    d.add(Polygon([x0 + c, y0, x0 + c, y0 + c, x0 + c + tri_h, y0 + c / 2], strokeColor=INK, fillColor=None, strokeWidth=1))
    return d


def draw_net(params: dict) -> Drawing:
    """Dispatches on params['shape'] to lay out that solid's net (cuboid/
    cube -> 6-rectangle cross, cylinder -> rectangle + 2 circles, cone ->
    circle + sector, triangular_prism -> 3 rectangles + 2 triangles,
    pyramid -> square + 4 triangles). Purely topological layouts (see
    _NET_CELL above), not scaled to real dimensions."""
    shape = params["shape"]
    if shape in ("cuboid", "cube"):
        return _draw_net_cuboid(params)
    if shape == "cylinder":
        return _draw_net_cylinder(params)
    if shape == "cone":
        return _draw_net_cone(params)
    if shape == "triangular_prism":
        return _draw_net_triangular_prism(params)
    if shape == "pyramid":
        return _draw_net_pyramid(params)
    raise ValueError(f"unknown net shape: {shape!r}")


def draw_compound_3d(params: dict) -> Drawing:
    """A compound solid made of two joined parts, selected by
    params['variant']: 'cylinder_hemisphere' (a capsule), 'cone_hemisphere'
    (an ice-cream shape), or 'cuboid_pyramid' (a silo roof). Each variant
    reuses the same coordinate helpers/primitives as the standalone
    draw_cylinder/draw_sphere/draw_cuboid/draw_pyramid functions above
    rather than duplicating projection math."""
    d = Drawing(SOLID_WIDTH, SOLID_HEIGHT)
    variant = params["variant"]

    if variant == "cylinder_hemisphere":
        cx, bottom_y, mid_y, rx, ry = 100, 25, 85, 38, 12
        for shape in _cylinder_edges(cx, mid_y, bottom_y, rx, ry):
            d.add(shape)
        arc = ArcPath(strokeColor=INK, fillColor=None, strokeWidth=1.2)
        arc.addArc(cx, mid_y, rx, 0, 180, moveTo=True)
        d.add(arc)
        d.add(Line(cx, mid_y, cx + rx, mid_y, strokeColor=INK, strokeWidth=0.9))
        d.add(_label(cx + rx / 2, mid_y + 16, params["radius_label"], size=8))
        d.add(_label(cx + rx + 10, (bottom_y + mid_y) / 2, params["height_label"], anchor="start"))

    elif variant == "cone_hemisphere":
        cx, apex_y, base_y, rx, ry = 100, 100, 55, 38, 12
        d.add(Ellipse(cx, base_y, rx, ry, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        d.add(Line(cx - rx, base_y, cx, apex_y, strokeColor=INK, strokeWidth=1.2))
        d.add(Line(cx + rx, base_y, cx, apex_y, strokeColor=INK, strokeWidth=1.2))
        arc = ArcPath(strokeColor=INK, fillColor=None, strokeWidth=1.2)
        arc.addArc(cx, base_y, rx, 180, 360, moveTo=True)
        d.add(arc)
        d.add(_label(cx - rx / 2, base_y + 14, params["radius_label"], size=8))
        d.add(_label(cx + rx / 2 + 8, (apex_y + base_y) / 2, params["cone_height_label"], anchor="start", size=8))

    elif variant == "cuboid_pyramid":
        x0, y0, fw, fh = 55, 30, 80, 40
        FBL, FBR, FTR, FTL = (x0, y0), (x0 + fw, y0), (x0 + fw, y0 + fh), (x0, y0 + fh)
        BBL, BBR, BTR, BTL = _offset(FBL), _offset(FBR), _offset(FTR), _offset(FTL)
        d.add(Rect(x0, y0, fw, fh, strokeColor=INK, fillColor=None, strokeWidth=1.2))
        d.add(Polygon([*FTL, *FTR, *BTR, *BTL], strokeColor=INK, fillColor=None, strokeWidth=1.1))
        d.add(Polygon([*FBR, *FTR, *BTR, *BBR], strokeColor=INK, fillColor=None, strokeWidth=1.1))
        d.add(Line(*FBL, *BBL, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        d.add(Line(*BBL, *BBR, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        d.add(Line(*BBL, *BTL, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        roof_apex = ((FTL[0] + BTR[0]) / 2, FTL[1] + 34)
        for corner in (FTL, FTR, BTR, BTL):
            d.add(Line(*corner, *roof_apex, strokeColor=INK, strokeWidth=1.1))
        roof_base_centre = (roof_apex[0], (FTL[1] + BTR[1]) / 2)
        d.add(Line(*roof_base_centre, *roof_apex, strokeColor=INK, strokeWidth=0.75, strokeDashArray=[3, 2]))
        d.add(_label(x0 + fw / 2, y0 - 14, params["base_label"]))
        d.add(_label(roof_apex[0] + 6, (roof_base_centre[1] + roof_apex[1]) / 2, params["roof_height_label"], anchor="start", size=8))

    else:
        raise ValueError(f"unknown compound_3d variant: {variant!r}")

    _not_to_scale(d, x=SOLID_WIDTH / 2, y=8)
    return d


_RENDERERS: dict[str, Callable[[dict], Drawing]] = {
    "rectangle": draw_rectangle,
    "two_similar_rectangles": draw_two_similar_rectangles,
    "triangle_area": draw_triangle_area,
    "l_shape": draw_l_shape,
    "circle": draw_circle,
    "rectangle_semicircle": draw_rectangle_semicircle,
    "angle_line": draw_angle_line,
    "triangle_angles": draw_triangle_angles,
    "polygon_angles": draw_polygon_angles,
    "parallel_lines": draw_parallel_lines,
    "exterior_triangle": draw_exterior_triangle,
    "polygon": draw_polygon,
    "symmetry_shape": draw_symmetry_shape,
    "right_triangle": draw_right_triangle,
    "trig_triangle": draw_trig_triangle,
    "general_triangle": draw_general_triangle,
    "bearings": draw_bearings,
    "two_triangle_congruence": draw_two_triangle_congruence,
    "vector_triangle": draw_vector_triangle,
    "circle_angle_centre": draw_circle_angle_centre,
    "circle_semicircle": draw_circle_semicircle,
    "circle_cyclic_quad": draw_circle_cyclic_quad,
    "circle_two_tangents": draw_circle_two_tangents,
    "circle_same_segment": draw_circle_same_segment,
    "circle_alternate_segment": draw_circle_alternate_segment,
    "parabola": draw_parabola,
    "linear_graph_pair": draw_linear_graph_pair,
    "function_graph": draw_function_graph,
    "piecewise_graph": draw_piecewise_graph,
    "graph_transformation": draw_graph_transformation,
    "grid_transformation": draw_grid_transformation,
    "loci_construction": draw_loci_construction,
    "loci_region": draw_loci_region,
    "inequality_region": draw_inequality_region,
    "tree_diagram": draw_tree_diagram,
    "two_way_table": draw_two_way_table,
    "sample_space_diagram": draw_sample_space_diagram,
    "cumulative_frequency_question": draw_cumulative_frequency_question,
    "histogram_question": draw_histogram_question,
    "venn_diagram": draw_venn_diagram,
    "bar_chart": draw_bar_chart,
    "pie_chart": draw_pie_chart,
    "pie_chart_with_table": draw_pie_chart_with_table,
    "box_plot": draw_box_plot,
    "histogram": draw_histogram,
    "cumulative_frequency": draw_cumulative_frequency,
    "time_series": draw_time_series,
    "scatter_graph": draw_scatter_graph,
    "plans_and_elevations": draw_plans_and_elevations,
    "plans_and_elevations_question": draw_plans_and_elevations_question,
    "number_line": draw_number_line,
    "fraction_shapes": draw_fraction_shapes,
    "dice": draw_dice,
    "spinner": draw_spinner,
    "spinner_pair": draw_spinner_pair,
    "coin": draw_coin,
    "event_pair": draw_event_pair,
    "bag_of_counters": draw_bag,
    "parallelogram": draw_parallelogram,
    "trapezium": draw_trapezium,
    "sector": draw_sector,
    "mixed_compound": draw_mixed_compound,
    "cuboid": draw_cuboid,
    "triangular_prism": draw_triangular_prism,
    "cylinder": draw_cylinder,
    "cone": draw_cone,
    "sphere": draw_sphere,
    "pyramid": draw_pyramid,
    "frustum": draw_frustum,
    "net": draw_net,
    "compound_3d": draw_compound_3d,
}


def render_diagram(spec: DiagramSpec) -> Drawing:
    try:
        renderer = _RENDERERS[spec.kind]
    except KeyError:
        raise ValueError(f"Unknown diagram kind: {spec.kind!r}") from None
    return renderer(spec.params)
