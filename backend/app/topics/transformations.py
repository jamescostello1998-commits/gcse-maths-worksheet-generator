"""Geometry Phase 4a: Symmetry and Transformations (reflections, rotations,
translations, enlargements) on a coordinate grid. Both a "Symmetry" group
(line symmetry, rotational symmetry, curated small shape bank) and a
"Transformations" group (4 transform types, each with a "complete the
transformation" and a "describe the transformation" topic) live in this one
file, since all of it shares the same vertex/polygon plumbing.
"""

import math
import random
from fractions import Fraction
from typing import NamedTuple

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_SYMMETRY = "Symmetry"
GROUP_TRANSFORMATIONS = "Transformations"

Point = tuple[int, int]

_GRID_MIN, _GRID_MAX = -8, 8  # the diagram's drawn axis range
# Vertices must fit within one grid unit of the drawn edge, not right up to
# it (some headroom for vertex *labels*, which are pushed further out still,
# outward from the shape's own centroid).
_FIT_MIN, _FIT_MAX = _GRID_MIN + 1, _GRID_MAX - 1
_VERTEX_LABELS = ("A", "B", "C", "D", "E", "F")

# For enlargement specifically, the image must also span at least this many
# grid units itself (as well as being clear of the original - see
# _well_separated below), or the reroll below tries again. Without this, a
# small scale factor can shrink the image so much that its own vertex labels
# collide with each other, independent of the original shape entirely -
# found via this diagram kind's visual spike, not a unit test (see
# CLAUDE.md's established pattern of catching diagram-overlap bugs only by
# rendering and looking).
_MIN_IMAGE_SPAN = 1.8


# ---------------------------------------------------------------------------
# Shape templates for the grid-transform topics
# ---------------------------------------------------------------------------
# Deliberately asymmetric (0 lines of symmetry, rotational order 1) so a
# "describe the transformation" question has a uniquely identifiable answer -
# a symmetric shape could make two different transforms produce the same
# image. Every edge is at least 2 grid units long so a shrinking enlargement
# (scale factor 1/2) still leaves legible spacing between vertex labels.

_SHAPE_TEMPLATES: tuple[tuple[Point, ...], ...] = (
    ((0, 0), (4, 0), (4, 2), (2, 2), (2, 5), (0, 5)),   # tall flag/L-shape
    ((0, 0), (5, 0), (5, 2), (3, 2), (3, 4), (0, 4)),   # step shape
    ((0, 0), (4, 0), (3, 4), (-1, 3)),                  # irregular quadrilateral
    ((0, 0), (5, 0), (1, 4)),                            # scalene triangle
)


def _random_shape(rng: random.Random) -> list[Point]:
    template = rng.choice(_SHAPE_TEMPLATES)
    ox, oy = rng.randint(-3, 3), rng.randint(-3, 3)
    return [(x + ox, y + oy) for x, y in template]


# ---------------------------------------------------------------------------
# Transform primitives (exact integer/Fraction arithmetic throughout)
# ---------------------------------------------------------------------------


def _reflect_point(p: Point, mirror: dict) -> Point:
    x, y = p
    kind = mirror["type"]
    if kind == "vertical":
        return (2 * mirror["x"] - x, y)
    if kind == "horizontal":
        return (x, 2 * mirror["y"] - y)
    sign = mirror["sign"]
    return (y, x) if sign == 1 else (-y, -x)


_ROTATIONS: tuple[int, ...] = (90, 180, 270)


def _rotation_wording(angle: int) -> str:
    return {90: "90° anticlockwise", 180: "180°", 270: "90° clockwise"}[angle]


def _rotate_point(p: Point, centre: Point, angle: int) -> Point:
    """`angle` is the counterclockwise angle in {90, 180, 270} (standard
    maths convention) - see _rotation_wording for how this is phrased to the
    student (270 CCW is always worded as "90° clockwise", never "270°
    anticlockwise", matching real GCSE convention)."""
    x, y = p[0] - centre[0], p[1] - centre[1]
    if angle == 90:
        x, y = -y, x
    elif angle == 180:
        x, y = -x, -y
    elif angle == 270:
        x, y = y, -x
    else:
        raise ValueError(f"transformations: unsupported rotation angle {angle}")
    return (x + centre[0], y + centre[1])


def _mirror_direction(mirror: dict) -> tuple[int, int]:
    kind = mirror["type"]
    if kind == "vertical":
        return (0, 1)
    if kind == "horizontal":
        return (1, 0)
    return (1, mirror["sign"])


def _point_on_mirror(pt: tuple, mirror: dict) -> bool:
    x, y = pt
    kind = mirror["type"]
    if kind == "vertical":
        return x == mirror["x"]
    if kind == "horizontal":
        return y == mirror["y"]
    return y == mirror["sign"] * x


# ---------------------------------------------------------------------------
# Independent verification - each check uses a genuinely different method
# than the primitive above, per this project's established convention.
# ---------------------------------------------------------------------------


def _verify_reflection(original: list, mirror: dict, image: list) -> None:
    """The geometric definition of a reflection: the mirror line is the
    perpendicular bisector of every point-image pair."""
    dir_x, dir_y = _mirror_direction(mirror)
    for p, q in zip(original, image):
        midpoint = (Fraction(p[0] + q[0], 2), Fraction(p[1] + q[1], 2))
        if not _point_on_mirror(midpoint, mirror):
            raise ValueError("transformations: reflection verification failed (midpoint not on mirror line)")
        dx, dy = q[0] - p[0], q[1] - p[1]
        if dx * dir_x + dy * dir_y != 0:
            raise ValueError("transformations: reflection verification failed (not perpendicular to mirror)")


def _verify_rotation(original: list, centre: Point, angle: int, image: list) -> None:
    """Complex-number rotation (multiply by i / -1 / -i) - a different
    representation than the coordinate swap/negate used to build the image."""
    rotator = {90: 1j, 180: -1, 270: -1j}[angle]
    for p, q in zip(original, image):
        z = complex(p[0] - centre[0], p[1] - centre[1]) * rotator
        expected = (centre[0] + z.real, centre[1] + z.imag)
        if abs(expected[0] - q[0]) > 1e-9 or abs(expected[1] - q[1]) > 1e-9:
            raise ValueError("transformations: rotation verification failed")


def _verify_translation(original: list, vector: Point, image: list) -> None:
    """Invariant-displacement check: image[i] - original[i] must be
    identical (and equal to the stated vector) for every vertex - catches an
    indexing bug the addition itself wouldn't."""
    displacements = {(q[0] - p[0], q[1] - p[1]) for p, q in zip(original, image)}
    if displacements != {vector}:
        raise ValueError("transformations: translation verification failed")


def _verify_enlargement(original: list, centre: Point, k: Fraction, image: list) -> None:
    """Squared-distance ratio (magnitude) + collinearity (direction) + a
    dot-product sign check (same/opposite side of the centre) - together
    these pin down q = centre + k*(p - centre) without ever recomputing that
    formula directly."""
    for p, q in zip(original, image):
        px, py = Fraction(p[0] - centre[0]), Fraction(p[1] - centre[1])
        qx, qy = Fraction(q[0] - centre[0]), Fraction(q[1] - centre[1])
        if qx * qx + qy * qy != k * k * (px * px + py * py):
            raise ValueError("transformations: enlargement verification failed (distance ratio)")
        if px * qy - py * qx != 0:
            raise ValueError("transformations: enlargement verification failed (not collinear)")
        if (px, py) != (0, 0):
            dot = px * qx + py * qy
            if k > 0 and dot <= 0:
                raise ValueError("transformations: enlargement verification failed (wrong side of centre)")
            if k < 0 and dot >= 0:
                raise ValueError("transformations: enlargement verification failed (wrong side of centre)")


# ---------------------------------------------------------------------------
# Grid-fit + separation checks used by every reroll loop below
# ---------------------------------------------------------------------------


def _polygon_centroid(vertices: list) -> tuple[float, float]:
    n = len(vertices)
    return (sum(v[0] for v in vertices) / n, sum(v[1] for v in vertices) / n)


def _fits_grid(vertices: list) -> bool:
    return all(_FIT_MIN <= x <= _FIT_MAX and _FIT_MIN <= y <= _FIT_MAX for x, y in vertices)


def _clear_of_axis_name_labels(vertices: list) -> bool:
    """True if no vertex sits near (0, _GRID_MAX) or (_GRID_MAX, 0) - the two
    spots where the axis's own permanent "y" and "x" name labels are drawn.
    A vertex there is fine on its own (_fits_grid already keeps it inside the
    grid), but its *label* is pushed further out still, outward from the
    shape's own centroid, and can then land on top of the axis name label -
    found via this diagram kind's visual spike, not a unit test. Deliberately
    narrower than a blanket margin shrink (which made valid instances too
    rare) - only these two specific spots are ever a problem."""
    return all(not (abs(x) < 2 and y > _GRID_MAX - 2) and not (x > _GRID_MAX - 2 and abs(y) < 2) for x, y in vertices)


def _clear_of_axis_tick_labels(vertices: list) -> bool:
    """True if no vertex's *predicted label position* (see
    _predicted_label_positions below) lands close enough to either axis line
    to risk sitting on top of one of that axis's own numbered tick labels,
    which are printed at regular intervals along the whole visible axis, not
    just at the two "axis name" spots _clear_of_axis_name_labels already
    guards. Only needed for combined_transformations - its wider double-prime
    labels (e.g. "A''") made this collision visible where the narrower
    single-prime labels on every other _describe topic hadn't - found via
    this topic's own visual spike, not a unit test."""
    positions = _predicted_label_positions(vertices)
    return all(abs(x) > 1.3 and abs(y) > 1.3 for x, y in positions)


def _bounding_box(vertices: list) -> tuple[float, float, float, float]:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    return min(xs), max(xs), min(ys), max(ys)


_LABEL_PUSH = 0.85  # grid units - approximates diagrams.py draw_shape's 9px
# outward push, converted to grid units at this diagram's ~10.9 px/unit scale
# (GRAPH_WIDTH=210, minus margins, over the widest supported range of 16
# units). Used only to *predict* where a label will land, in the same grid
# units the reroll logic already works in - not an exact pixel match, just
# close enough to catch the same collisions the real renderer would produce.


def _predicted_label_positions(vertices: list) -> list[tuple[float, float]]:
    """Where diagrams.py's draw_shape will place each vertex's label -
    pushed outward from the *shape's own* centroid, normalised, by
    _LABEL_PUSH grid units (mirrors that function's pixel-space formula)."""
    cx, cy = _polygon_centroid(vertices)
    positions = []
    for x, y in vertices:
        dx, dy = x - cx, y - cy
        dist = math.hypot(dx, dy) or 1.0
        positions.append((x + dx / dist * _LABEL_PUSH, y + dy / dist * _LABEL_PUSH))
    return positions


def _well_separated(original: list, image: list, min_gap: float = 1.1) -> bool:
    """True if no *predicted label position* (original or image, pushed
    outward from its own shape's centroid, exactly as diagrams.py will draw
    it) comes within min_gap grid units of any other. A centroid-distance
    check alone let one shape's bounding box swallow the other's whenever
    either was elongated or a vertex sat close to a rotation/enlargement
    centre (which keeps its image close too, since those transforms
    preserve distance from the centre); a stricter bounding-box-disjoint
    check was tried next but turned out to be geometrically near-impossible
    for a plain positive-scale-factor enlargement on a bounded grid (the
    required gap from the centre grows with span/(k-1), easily exceeding the
    grid's own size). Checking predicted label positions directly targets
    the actual problem (two labels landing on top of each other) without
    over-constraining shapes that merely overlap or cross without their
    labels colliding - found via a programmatic label-position scan across a
    large random sample, not just eyeballing individual renders, after
    several rounds of visual spot-checks still showed occasional collisions."""
    positions = _predicted_label_positions(original) + _predicted_label_positions(image)
    for i in range(len(positions)):
        ax, ay = positions[i]
        for bx, by in positions[i + 1:]:
            if math.hypot(ax - bx, ay - by) < min_gap:
                return False
    return True


def _image_not_too_small(image: list) -> bool:
    xs = [v[0] for v in image]
    ys = [v[1] for v in image]
    return (max(xs) - min(xs)) >= _MIN_IMAGE_SPAN and (max(ys) - min(ys)) >= _MIN_IMAGE_SPAN


# ---------------------------------------------------------------------------
# Reroll instance generators - mirrors this project's established
# reroll-away-from-illegible-combinations pattern (e.g. solids_3d_trig.py's
# _cuboid_dims). Degenerate parameter values (0° rotation, zero vector, scale
# factor 1) are excluded from the random-choice pools themselves.
# ---------------------------------------------------------------------------


_MIRROR_OFFSETS = (-4, -3, -2, -1, 1, 2, 3, 4)  # excludes 0 - see below


def _random_mirror_line(rng: random.Random) -> dict:
    kind = rng.choice(("vertical", "horizontal", "diagonal_pos", "diagonal_neg"))
    if kind == "vertical":
        # x = 0 is excluded: it coincides exactly with the y-axis, so the
        # dashed mirror line draws directly on top of the solid axis line and
        # the "x = 0" label collides with the axis's own "y" name label -
        # found via this diagram kind's visual spike, not a unit test.
        x = rng.choice(_MIRROR_OFFSETS)
        return {"type": "vertical", "x": x, "label": f"x = {x}"}
    if kind == "horizontal":
        y = rng.choice(_MIRROR_OFFSETS)  # y = 0 excluded for the same reason (coincides with the x-axis)
        return {"type": "horizontal", "y": y, "label": f"y = {y}"}
    if kind == "diagonal_pos":
        return {"type": "diagonal", "sign": 1, "label": "y = x"}
    return {"type": "diagonal", "sign": -1, "label": "y = -x"}


def _signed_distance_from_mirror(pt: tuple, mirror: dict) -> float:
    """True perpendicular distance from `pt` to the mirror line (signed) -
    for the diagonal case this means dividing by sqrt(2), since y - sign*x
    is sqrt(2) times the true perpendicular distance to y = sign*x. Skipping
    that normalisation let diagonal-mirror vertices sit visibly closer to
    the line than vertical/horizontal ones at the same _shape_clear_of_mirror
    threshold - found via this diagram kind's visual spike."""
    x, y = pt
    kind = mirror["type"]
    if kind == "vertical":
        return x - mirror["x"]
    if kind == "horizontal":
        return y - mirror["y"]
    return (y - mirror["sign"] * x) / math.sqrt(2)


def _shape_clear_of_mirror(shape: list, mirror: dict, min_gap: float = 1.5) -> bool:
    """True if every vertex of `shape` is strictly on the same side of the
    mirror line, with at least `min_gap` clearance - i.e. the shape never
    straddles the line. Without this, a shape with a vertex close to the
    mirror produces an image vertex just as close on the other side, and
    since each vertex's label is pushed outward from its *own* shape's
    centroid (which can point straight at the mirror for a vertex near it),
    the two labels converge on each other right at the line - a real
    collision found via this diagram kind's visual spike, not a unit test."""
    distances = [_signed_distance_from_mirror(p, mirror) for p in shape]
    same_sign = all(d > 0 for d in distances) or all(d < 0 for d in distances)
    return same_sign and min(abs(d) for d in distances) >= min_gap


_REROLL_ATTEMPTS = 4000  # generous - each attempt is cheap, and the combined
# grid-fit / separation / axis-label-clearance / mirror-clearance checks
# reject enough combinations that a couple hundred attempts wasn't always
# enough - Higher-tier enlargement (the strictest combination: divisibility
# for a fractional scale factor, plus every other check) needed as many as
# ~1600 tries in a 3000-trial empirical check.


def _random_reflect_instance(rng: random.Random) -> tuple[list, dict, list]:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        mirror = _random_mirror_line(rng)
        image = [_reflect_point(p, mirror) for p in shape]
        if (_fits_grid(shape) and _fits_grid(image) and _well_separated(shape, image)
                and _shape_clear_of_mirror(shape, mirror)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(image)):
            return shape, mirror, image
    raise ValueError("transformations: could not fit a reflection instance on the grid")


def _random_rotate_instance(rng: random.Random) -> tuple[list, Point, int, list]:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        centre = (rng.randint(-4, 4), rng.randint(-4, 4))
        angle = rng.choice(_ROTATIONS)
        image = [_rotate_point(p, centre, angle) for p in shape]
        if (_fits_grid(shape) and _fits_grid(image) and _well_separated(shape, image)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(image)):
            return shape, centre, angle, image
    raise ValueError("transformations: could not fit a rotation instance on the grid")


def _random_translate_instance(rng: random.Random) -> tuple[list, Point, list]:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        dx, dy = rng.randint(-6, 6), rng.randint(-6, 6)
        if dx == 0 and dy == 0:
            continue
        vector = (dx, dy)
        image = [(p[0] + dx, p[1] + dy) for p in shape]
        if (_fits_grid(shape) and _fits_grid(image) and _well_separated(shape, image)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(image)):
            return shape, vector, image
    raise ValueError("transformations: could not fit a translation instance on the grid")


_ENLARGE_K_FOUNDATION: tuple[Fraction, ...] = (Fraction(2), Fraction(3))
_ENLARGE_K_HIGHER: tuple[Fraction, ...] = (
    Fraction(-1), Fraction(-2), Fraction(-3), Fraction(1, 2), Fraction(-1, 2),
)


def _random_enlarge_centre(rng: random.Random, shape: list) -> Point:
    """A centre placed just outside the shape's own bounding box, offset in
    a random cardinal direction. A uniformly-random centre anywhere on the
    grid was tried first, but for a positive scale factor (Foundation's
    k in {2, 3}, never flipping to the other side) a centre inside or near
    the shape almost always produces an image whose bounding box swallows
    the original - growing from an interior point pushes every direction
    the shape already extends even further, so the two never end up
    disjoint. Constructing the centre outside the shape by design (rather
    than hoping reroll finds one by chance - empirically it essentially
    never did) fixes this while still leaving k, direction and gap free to
    vary. Found via a programmatic scan for label collisions across a large
    random sample, not just individual visual spot-checks."""
    x0, x1, y0, y1 = _bounding_box(shape)
    gap = rng.randint(2, 4)
    direction = rng.choice(("left", "right", "up", "down"))
    if direction == "left":
        return (int(x0) - gap, rng.randint(int(y0), int(y1)))
    if direction == "right":
        return (int(x1) + gap, rng.randint(int(y0), int(y1)))
    if direction == "up":
        return (rng.randint(int(x0), int(x1)), int(y1) + gap)
    return (rng.randint(int(x0), int(x1)), int(y0) - gap)


def _random_enlarge_instance(rng: random.Random, k_pool: tuple) -> tuple[list, Point, Fraction, list]:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        centre = _random_enlarge_centre(rng, shape)
        k = Fraction(rng.choice(k_pool))
        offsets = [(p[0] - centre[0], p[1] - centre[1]) for p in shape]
        if k.denominator != 1 and any(ox % k.denominator or oy % k.denominator for ox, oy in offsets):
            continue  # image wouldn't land on integer grid points - reroll
        image = [(int(centre[0] + k * ox), int(centre[1] + k * oy)) for ox, oy in offsets]
        if (_fits_grid(shape) and _fits_grid(image) and _well_separated(shape, image)
                and _image_not_too_small(image)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(image)):
            return shape, centre, k, image
    raise ValueError("transformations: could not fit an enlargement instance on the grid")


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt_point(p: tuple) -> str:
    return f"({p[0]}, {p[1]})"


def _fmt_vector(v: tuple) -> str:
    return f"({v[0]}, {v[1]})"


def _fmt_scale_factor(k: Fraction) -> str:
    return str(k.numerator) if k.denominator == 1 else f"{k.numerator}/{k.denominator}"


def _shape_name(labels: tuple) -> str:
    return "".join(labels)


def _article(name: str) -> str:
    return "an" if name[0].lower() in "aeiou" else "a"


def _vertex_mapping_text(labels: tuple, points: list, image_labels: tuple, image: list) -> str:
    return ", ".join(
        f"{l}{_fmt_point(p)} -> {il}{_fmt_point(q)}"
        for l, p, il, q in zip(labels, points, image_labels, image)
    )


# ---------------------------------------------------------------------------
# Symmetry shape bank (Symmetry group)
# ---------------------------------------------------------------------------


class _SymmetryShape(NamedTuple):
    id: str
    name: str
    vertices: tuple[Point, ...]
    lines_of_symmetry: tuple[dict, ...]
    rotational_order: int
    rotational_centre: tuple[float, float]


def _symmetry_shape(id_: str, name: str, vertices: list, lines_of_symmetry: list, rotational_order: int) -> _SymmetryShape:
    n = len(vertices)
    centre = (sum(v[0] for v in vertices) / n, sum(v[1] for v in vertices) / n)
    return _SymmetryShape(id_, name, tuple(vertices), tuple(lines_of_symmetry), rotational_order, centre)


def _regular_polygon_vertices(n: int, radius: float, centre: tuple = (0, 0), start_angle: float = 90) -> list:
    vertices = []
    for i in range(n):
        angle = math.radians(start_angle + i * 360 / n)
        vertices.append((centre[0] + radius * math.cos(angle), centre[1] + radius * math.sin(angle)))
    return vertices


def _regular_polygon_symmetry_lines(n: int, radius: float, centre: tuple = (0, 0), start_angle: float = 90) -> list:
    """The n evenly-spaced (180/n degrees apart) symmetry axes of a regular
    n-gon, each through the centre at angle start_angle + i*180/n - this
    single formula correctly covers both "vertex to opposite vertex" axes
    (even n) and "vertex to opposite edge-midpoint" axes (odd n)."""
    lines = []
    for i in range(n):
        angle = math.radians(start_angle + i * 180 / n)
        far = (centre[0] + radius * 1.3 * math.cos(angle), centre[1] + radius * 1.3 * math.sin(angle))
        near = (centre[0] - radius * 1.3 * math.cos(angle), centre[1] - radius * 1.3 * math.sin(angle))
        lines.append({"p1": near, "p2": far})
    return lines


_TRIANGLE_V = _regular_polygon_vertices(3, 4)
_SQUARE_V = _regular_polygon_vertices(4, 4, start_angle=45)
_PENTAGON_V = _regular_polygon_vertices(5, 4)
_HEXAGON_V = _regular_polygon_vertices(6, 4)

_SYMMETRY_SHAPES: tuple[_SymmetryShape, ...] = (
    _symmetry_shape(
        "rectangle", "rectangle", [(0, 0), (6, 0), (6, 4), (0, 4)],
        [{"p1": (3, -1), "p2": (3, 5)}, {"p1": (-1, 2), "p2": (7, 2)}], 2,
    ),
    _symmetry_shape(
        "square", "square", _SQUARE_V,
        _regular_polygon_symmetry_lines(4, 4, start_angle=45), 4,
    ),
    _symmetry_shape(
        "equilateral_triangle", "equilateral triangle", _TRIANGLE_V,
        _regular_polygon_symmetry_lines(3, 4), 3,
    ),
    _symmetry_shape(
        "isosceles_triangle", "isosceles triangle", [(0, 0), (6, 0), (3, 4)],
        [{"p1": (3, -1), "p2": (3, 5)}], 1,
    ),
    _symmetry_shape(
        "isosceles_trapezium", "isosceles trapezium", [(0, 0), (6, 0), (4, 3), (2, 3)],
        [{"p1": (3, -1), "p2": (3, 4)}], 1,
    ),
    _symmetry_shape(
        "regular_pentagon", "regular pentagon", _PENTAGON_V,
        _regular_polygon_symmetry_lines(5, 4), 5,
    ),
    _symmetry_shape(
        "regular_hexagon", "regular hexagon", _HEXAGON_V,
        _regular_polygon_symmetry_lines(6, 4), 6,
    ),
    _symmetry_shape(
        "parallelogram", "parallelogram", [(0, 0), (5, 0), (7, 3), (2, 3)],
        [], 2,
    ),
    _symmetry_shape(
        "kite", "kite", [(0, -2), (3, 1), (0, 5), (-3, 1)],
        [{"p1": (0, -3), "p2": (0, 6)}], 1,
    ),
    _symmetry_shape(
        "rhombus", "rhombus", [(0, -3), (4, 0), (0, 3), (-4, 0)],
        [{"p1": (-5, 0), "p2": (5, 0)}, {"p1": (0, -4), "p2": (0, 4)}], 2,
    ),
    _symmetry_shape(
        "irregular_pentagon", "irregular pentagon", [(0, 0), (5, 0), (6, 3), (2, 5), (-2, 2)],
        [], 1,
    ),
)


def _reflect_across_line(pt: tuple, p1: tuple, p2: tuple) -> tuple:
    """Reflect `pt` across the infinite line through p1 and p2 - a general
    line reflection (not restricted to the axis-aligned/diagonal special
    cases in _reflect_point above), used to independently verify every
    _SYMMETRY_SHAPES entry's hand-authored symmetry claims, including
    diagonal axes at arbitrary angles (e.g. an equilateral triangle's)."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    a = dx * dx - dy * dy
    b = 2 * dx * dy
    d2 = dx * dx + dy * dy
    x, y = pt[0] - x1, pt[1] - y1
    rx = (a * x + b * y) / d2
    ry = (b * x - a * y) / d2
    return (rx + x1, ry + y1)


def _vertex_sets_match(a: list, b: list, tol: float = 1e-6) -> bool:
    if len(a) != len(b):
        return False
    remaining = list(b)
    for pa in a:
        match_idx = None
        for i, pb in enumerate(remaining):
            if abs(pa[0] - pb[0]) < tol and abs(pa[1] - pb[1]) < tol:
                match_idx = i
                break
        if match_idx is None:
            return False
        remaining.pop(match_idx)
    return True


def _count_symmetries(vertices: tuple) -> tuple[int, int]:
    """Independently (re-)derive the number of lines of symmetry and the
    order of rotational symmetry directly from the vertex coordinates, by
    trying every geometrically possible axis (through the centroid and each
    vertex, or the centroid and each edge midpoint) and every rotation order
    from 2 to 6 - used only to validate _SYMMETRY_SHAPES' hand-authored
    claims below, not at question-generation time."""
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n

    candidates = list(vertices)
    for i in range(n):
        p1, p2 = vertices[i], vertices[(i + 1) % n]
        candidates.append(((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2))

    def _same_axis(a: float, b: float, tol: float = 1e-6) -> bool:
        # A line's direction is periodic with period pi (angle 0 and angle
        # pi describe the same line) - plain "% math.pi" reduction puts an
        # angle just below 0 near pi instead of near 0 (Python's modulo
        # always returns a non-negative result for a positive divisor), so a
        # naive abs-difference comparison misses that wraparound and can
        # double-count the same axis as two "different" ones.
        diff = abs(a - b) % math.pi
        return diff < tol or diff > math.pi - tol

    seen_angles: list = []
    line_count = 0
    for c in candidates:
        angle = math.atan2(c[1] - cy, c[0] - cx) % math.pi
        if any(_same_axis(angle, a) for a in seen_angles):
            continue
        far = (cx + math.cos(angle) * 100, cy + math.sin(angle) * 100)
        reflected = [_reflect_across_line(v, (cx, cy), far) for v in vertices]
        if _vertex_sets_match(list(vertices), reflected):
            line_count += 1
            seen_angles.append(angle)

    order = 1
    for k in range(2, 7):
        angle = 2 * math.pi / k
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rotated = []
        for x, y in vertices:
            dx, dy = x - cx, y - cy
            rotated.append((cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a))
        if _vertex_sets_match(list(vertices), rotated):
            order = k
    return line_count, order


for _shape in _SYMMETRY_SHAPES:
    _computed_lines, _computed_order = _count_symmetries(_shape.vertices)
    if _computed_lines != len(_shape.lines_of_symmetry):
        raise ValueError(
            f"transformations: {_shape.id} claims {len(_shape.lines_of_symmetry)} lines of symmetry "
            f"but {_computed_lines} were independently found"
        )
    if _computed_order != _shape.rotational_order:
        raise ValueError(
            f"transformations: {_shape.id} claims rotational order {_shape.rotational_order} "
            f"but {_computed_order} was independently found"
        )
    for _line in _shape.lines_of_symmetry:
        _reflected = [_reflect_across_line(v, _line["p1"], _line["p2"]) for v in _shape.vertices]
        if not _vertex_sets_match(list(_shape.vertices), _reflected):
            raise ValueError(f"transformations: {_shape.id}'s drawn symmetry line does not reflect it onto itself")


# ---------------------------------------------------------------------------
# Symmetry topics
# ---------------------------------------------------------------------------


def generate_symmetry_lines(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_SYMMETRY_SHAPES)
    n = len(shape.lines_of_symmetry)
    word = "line" if n == 1 else "lines"
    prompt = f"The diagram shows {_article(shape.name)} {shape.name}. How many lines of symmetry does it have?"
    if n:
        steps = [
            f"{_article(shape.name).capitalize()} {shape.name} has {n} {word} of symmetry.",
            "Each line of symmetry divides the shape into two mirror-image halves - shown dashed on the diagram.",
        ]
    else:
        steps = [
            f"{_article(shape.name).capitalize()} {shape.name} (of this kind) has no lines of symmetry - "
            "no mirror line maps it back onto itself."
        ]
    return Question(
        topic_id="symmetry_lines",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{n} {word} of symmetry",
        dedup_key=f"sym_lines:{shape.id}",
        diagram=DiagramSpec(kind="symmetry_shape", params={"vertices": shape.vertices, "blank": True}),
        solution_diagram=DiagramSpec(
            kind="symmetry_shape",
            params={
                "vertices": shape.vertices,
                "symmetry_lines": [{"p1": l["p1"], "p2": l["p2"]} for l in shape.lines_of_symmetry],
            },
        ),
    )


def generate_modelled_example_symmetry_lines(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_SYMMETRY_SHAPES)
    n = len(shape.lines_of_symmetry)
    word = "line" if n == 1 else "lines"
    teaching_steps = [
        "A line of symmetry is a line you could fold the shape along so the two halves match up exactly.",
        "Try every candidate fold line in turn - through opposite vertices, or through the midpoints of "
        "opposite sides - and check whether folding along it really does make the two halves match.",
        f"Checking every possible fold line for this {shape.name} shows it has {n} {word} of symmetry."
        if n else f"Trying every possible fold line for this {shape.name} shows none of them makes the two "
        "halves match - so it has no lines of symmetry.",
    ]
    if n:
        teaching_steps.append("Each valid fold line is shown dashed on the diagram.")
    return ModelledExample(
        topic_id="symmetry_lines",
        tier=Tier.FOUNDATION,
        prompt=f"The diagram shows {_article(shape.name)} {shape.name}. How many lines of symmetry does it have?",
        worked_calculation=(f"{shape.name} -> {n} {word} of symmetry", "checked against every possible fold line"),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{n} {word} of symmetry",
        diagram=DiagramSpec(
            kind="symmetry_shape",
            params={
                "vertices": shape.vertices,
                "symmetry_lines": [{"p1": l["p1"], "p2": l["p2"]} for l in shape.lines_of_symmetry],
            },
        ),
    )


def generate_symmetry_rotational(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_SYMMETRY_SHAPES)
    order = shape.rotational_order
    prompt = f"The diagram shows {_article(shape.name)} {shape.name}. State the order of rotational symmetry."
    if order > 1:
        steps = [
            f"Rotating the {shape.name} about its centre, it looks exactly the same {order} times during a "
            "full 360° turn.",
            f"So the order of rotational symmetry is {order}.",
        ]
    else:
        steps = [
            f"Rotating the {shape.name} about its centre, it only looks the same once during a full 360° turn "
            "(back at the start).",
            "So the order of rotational symmetry is 1.",
        ]
    return Question(
        topic_id="symmetry_rotational",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"order {order}",
        dedup_key=f"sym_rot:{shape.id}",
        diagram=DiagramSpec(kind="symmetry_shape", params={"vertices": shape.vertices, "blank": True}),
        solution_diagram=DiagramSpec(
            kind="symmetry_shape",
            params={"vertices": shape.vertices, "rotation_centre": shape.rotational_centre, "rotation_order": order},
        ),
    )


def generate_modelled_example_symmetry_rotational(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_SYMMETRY_SHAPES)
    order = shape.rotational_order
    teaching_steps = [
        "The order of rotational symmetry is how many times a shape looks exactly the same during one full "
        "360° turn about its centre (always at least 1, since it looks the same after a full turn back to start).",
        "Tracing paper makes this easy to check: trace the shape, then turn the tracing about the centre and "
        "count how many times it lines up exactly with the original before you're back at the start.",
        f"Turning this {shape.name} through 360° about its centre, it lines back up with itself {order} "
        f"time{'s' if order != 1 else ''}.",
    ]
    return ModelledExample(
        topic_id="symmetry_rotational",
        tier=Tier.FOUNDATION,
        prompt=f"The diagram shows {_article(shape.name)} {shape.name}. State the order of rotational symmetry.",
        worked_calculation=(f"{shape.name} -> order {order}", "checked by rotating through the full 360° turn"),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"order {order}",
        diagram=DiagramSpec(
            kind="symmetry_shape",
            params={"vertices": shape.vertices, "rotation_centre": shape.rotational_centre, "rotation_order": order},
        ),
    )


# ---------------------------------------------------------------------------
# Reflection
# ---------------------------------------------------------------------------


def generate_transform_reflect_complete(tier: Tier, rng: random.Random) -> Question:
    shape, mirror, image = _random_reflect_instance(rng)
    _verify_reflection(shape, mirror, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = [
        f"Reflect each vertex in the line {mirror['label']}: the mirror line is the perpendicular bisector "
        "of every point and its image, so each point stays the same distance from the line, on the other side.",
        _vertex_mapping_text(labels, shape, image_labels, image),
    ]
    return Question(
        topic_id="transform_reflect_complete",
        tier=Tier.FOUNDATION,
        prompt=f"Reflect shape {name} in the line {mirror['label']}. Draw and label the image {image_name}.",
        solution_steps=tuple(steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        dedup_key=f"reflect:{shape}:{mirror['label']}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "mirror_line": mirror,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "mirror_line": mirror,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_reflect_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, mirror, image = _random_reflect_instance(rng)
    _verify_reflection(shape, mirror, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    teaching_steps = [
        f"To reflect a shape in the line {mirror['label']}, imagine folding the grid along that line - each "
        "point of the shape lands exactly on top of its image.",
        "That means the mirror line is always the perpendicular bisector of the line joining a point to its "
        "image: same distance from the line, directly opposite it.",
        "Work through the vertices one at a time, counting squares from each point to the mirror line, then "
        "the same number of squares again on the other side.",
    ]
    return ModelledExample(
        topic_id="transform_reflect_complete",
        tier=Tier.FOUNDATION,
        prompt=f"Reflect shape {name} in the line {mirror['label']}. Draw and label the image {image_name}.",
        worked_calculation=(
            _vertex_mapping_text(labels, shape, image_labels, image),
            f"mirror line: {mirror['label']}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "mirror_line": mirror,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_transform_reflect_describe(tier: Tier, rng: random.Random) -> Question:
    shape, mirror, image = _random_reflect_instance(rng)
    _verify_reflection(shape, mirror, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = [
        f"Every vertex and its image are the same distance from a single line, on opposite sides of it - "
        "that line is the mirror line.",
        f"Comparing corresponding vertices shows the mirror line is {mirror['label']}.",
    ]
    return Question(
        topic_id="transform_reflect_describe",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Shape {name} is reflected to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Reflection in the line {mirror['label']}",
        dedup_key=f"reflect_describe:{shape}:{mirror['label']}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_reflect_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, mirror, image = _random_reflect_instance(rng)
    _verify_reflection(shape, mirror, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    teaching_steps = [
        f"'Describe fully' a reflection means naming the mirror line, not just saying 'reflection'.",
        f"Pick one vertex and its image, e.g. {labels[0]}{_fmt_point(shape[0])} and "
        f"{image_labels[0]}{_fmt_point(image[0])} - the mirror line passes exactly halfway between them, "
        "at right angles to the line joining them.",
        f"Checking every other vertex pair the same way confirms the mirror line is {mirror['label']}.",
    ]
    return ModelledExample(
        topic_id="transform_reflect_describe",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Shape {name} is reflected to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        worked_calculation=(
            f"{labels[0]}{_fmt_point(shape[0])} -> {image_labels[0]}{_fmt_point(image[0])}",
            f"mirror line: {mirror['label']}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Reflection in the line {mirror['label']}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------


def generate_transform_rotate_complete(tier: Tier, rng: random.Random) -> Question:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)
    wording = _rotation_wording(angle)

    steps = [
        f"Rotate each vertex {wording} about the centre {_fmt_point(centre)}: every point stays the same "
        "distance from the centre and turns through the same angle.",
        _vertex_mapping_text(labels, shape, image_labels, image),
    ]
    return Question(
        topic_id="transform_rotate_complete",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Rotate shape {name} {wording} about the centre {_fmt_point(centre)}. Draw and label the image "
            f"{image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        dedup_key=f"rotate:{shape}:{centre}:{angle}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_rotate_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)
    wording = _rotation_wording(angle)

    teaching_steps = [
        f"A rotation turns every point of the shape through the same angle ({wording}) about a fixed centre, "
        f"here {_fmt_point(centre)} - every point stays the same distance from the centre.",
        "Tracing paper (or counting squares round the centre) makes this easier: for a 90° turn, swap and "
        "flip the coordinates relative to the centre; for 180°, both coordinates flip sign relative to it.",
        "Work through the vertices one at a time, using the centre as the pivot.",
    ]
    return ModelledExample(
        topic_id="transform_rotate_complete",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Rotate shape {name} {wording} about the centre {_fmt_point(centre)}. Draw and label the image "
            f"{image_name}."
        ),
        worked_calculation=(
            _vertex_mapping_text(labels, shape, image_labels, image),
            f"centre: {_fmt_point(centre)}, rotation: {wording}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_transform_rotate_describe(tier: Tier, rng: random.Random) -> Question:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)
    wording = _rotation_wording(angle)

    steps = [
        "The centre of rotation is the one point that is the same distance from a vertex and its image, for "
        "every vertex - it can be found where the perpendicular bisectors of two such pairs cross.",
        f"Measuring the turn from a vertex to its image about that point gives {wording} about {_fmt_point(centre)}.",
    ]
    return Question(
        topic_id="transform_rotate_describe",
        tier=Tier.HIGHER,
        prompt=(
            f"Shape {name} is rotated to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Rotation {wording} about {_fmt_point(centre)}",
        dedup_key=f"rotate_describe:{shape}:{centre}:{angle}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_rotate_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)
    wording = _rotation_wording(angle)

    teaching_steps = [
        "A full description of a rotation needs three things: the word 'rotation', the angle and direction "
        "(or just the angle for 180°), and the centre.",
        f"To find the centre without guessing, join a vertex to its image (e.g. {labels[0]} to {image_labels[0]}) "
        "and construct its perpendicular bisector; do the same for a second vertex pair - the two bisectors "
        f"cross exactly at the centre, {_fmt_point(centre)}.",
        f"Finally check the angle by measuring the turn from a vertex to its image about that centre: {wording}.",
    ]
    return ModelledExample(
        topic_id="transform_rotate_describe",
        tier=Tier.HIGHER,
        prompt=(
            f"Shape {name} is rotated to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        worked_calculation=(
            f"perpendicular bisectors of {labels[0]}{image_labels[0]} and {labels[1]}{image_labels[1]} meet at "
            f"{_fmt_point(centre)}",
            f"rotation: {wording} about {_fmt_point(centre)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Rotation {wording} about {_fmt_point(centre)}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------


def generate_transform_translate_complete(tier: Tier, rng: random.Random) -> Question:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = [
        f"Translate every vertex by the vector {_fmt_vector(vector)}: move each point {abs(vector[0])} "
        f"square{'s' if abs(vector[0]) != 1 else ''} {'right' if vector[0] >= 0 else 'left'} and "
        f"{abs(vector[1])} square{'s' if abs(vector[1]) != 1 else ''} {'up' if vector[1] >= 0 else 'down'}.",
        _vertex_mapping_text(labels, shape, image_labels, image),
    ]
    return Question(
        topic_id="transform_translate_complete",
        tier=Tier.FOUNDATION,
        prompt=f"Translate shape {name} by the vector {_fmt_vector(vector)}. Draw and label the image {image_name}.",
        solution_steps=tuple(steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        dedup_key=f"translate:{shape}:{vector}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "translation_vector": vector, "vector_label": _fmt_vector(vector),
            },
        ),
        solution_diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "translation_vector": vector, "vector_label": _fmt_vector(vector),
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_translate_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    teaching_steps = [
        f"A translation slides every point of the shape by the same vector, {_fmt_vector(vector)} - the shape "
        "doesn't turn or flip, it just moves.",
        f"The top number of the vector is how far to move left/right ({vector[0]}), and the bottom number is "
        f"how far to move up/down ({vector[1]}).",
        "Apply the same move to every vertex in turn, keeping the shape's size and orientation unchanged.",
    ]
    return ModelledExample(
        topic_id="transform_translate_complete",
        tier=Tier.FOUNDATION,
        prompt=f"Translate shape {name} by the vector {_fmt_vector(vector)}. Draw and label the image {image_name}.",
        worked_calculation=(
            _vertex_mapping_text(labels, shape, image_labels, image),
            f"vector: {_fmt_vector(vector)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "translation_vector": vector, "vector_label": _fmt_vector(vector),
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_transform_translate_describe(tier: Tier, rng: random.Random) -> Question:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = [
        f"Every vertex moves by exactly the same amount: comparing {labels[0]}{_fmt_point(shape[0])} with "
        f"{image_labels[0]}{_fmt_point(image[0])} gives the vector {_fmt_vector(vector)}.",
        "Checking the other vertices confirms the same vector applies throughout, so this is a translation.",
    ]
    return Question(
        topic_id="transform_translate_describe",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Shape {name} is translated to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Translation by the vector {_fmt_vector(vector)}",
        dedup_key=f"translate_describe:{shape}:{vector}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_translate_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    teaching_steps = [
        "If the image is the same size and orientation as the original, just slid to a new position, it's a "
        "translation - described fully by a single column vector.",
        f"Pick any vertex and its image, e.g. {labels[0]}{_fmt_point(shape[0])} to "
        f"{image_labels[0]}{_fmt_point(image[0])}: subtract to get the vector {_fmt_vector(vector)}.",
        "Check a second vertex pair gives the same vector, to confirm it isn't a rotation or reflection that "
        "happens to move that one point the same way.",
    ]
    return ModelledExample(
        topic_id="transform_translate_describe",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Shape {name} is translated to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        worked_calculation=(
            f"{image_labels[0]}{_fmt_point(image[0])} - {labels[0]}{_fmt_point(shape[0])} = {_fmt_vector(vector)}",
            f"vector: {_fmt_vector(vector)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Translation by the vector {_fmt_vector(vector)}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Enlargement
# ---------------------------------------------------------------------------


def _enlarge_steps(labels: tuple, shape: list, centre: Point, k: Fraction, image_labels: tuple, image: list) -> list:
    p0, q0 = shape[0], image[0]
    offset0 = (p0[0] - centre[0], p0[1] - centre[1])
    return [
        f"The centre of enlargement is {_fmt_point(centre)} and the scale factor is {_fmt_scale_factor(k)}.",
        f"For each vertex, find its displacement from the centre and multiply by the scale factor: "
        f"{labels[0]} is a displacement of ({offset0[0]}, {offset0[1]}) from the centre, so "
        f"{image_labels[0]} = {_fmt_point(centre)} + {_fmt_scale_factor(k)} × ({offset0[0]}, {offset0[1]}) "
        f"= {_fmt_point(q0)}.",
        "Repeat for every vertex: " + _vertex_mapping_text(labels, shape, image_labels, image),
    ]


def generate_transform_enlarge_complete_foundation(tier: Tier, rng: random.Random) -> Question:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_FOUNDATION)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    return Question(
        topic_id="transform_enlarge_complete_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Enlarge shape {name} by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}. "
            f"Draw and label the image {image_name}."
        ),
        solution_steps=tuple(_enlarge_steps(labels, shape, centre, k, image_labels, image)),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        dedup_key=f"enlarge_f:{shape}:{centre}:{k}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_enlarge_complete_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_FOUNDATION)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    teaching_steps = [
        f"An enlargement scales every distance from the centre of enlargement by the scale factor - here, "
        f"scale factor {_fmt_scale_factor(k)} means every point ends up {_fmt_scale_factor(k)} times as far "
        f"from {_fmt_point(centre)} as it started.",
        "Count the squares across and up from the centre to each vertex, multiply both by the scale factor, "
        "then count that new distance from the centre in the same direction to plot the image.",
        "The shape gets bigger but keeps exactly the same proportions, since every vertex is scaled by the "
        "same factor.",
    ]
    return ModelledExample(
        topic_id="transform_enlarge_complete_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Enlarge shape {name} by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}. "
            f"Draw and label the image {image_name}."
        ),
        worked_calculation=(
            _vertex_mapping_text(labels, shape, image_labels, image),
            f"centre: {_fmt_point(centre)}, scale factor: {_fmt_scale_factor(k)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_transform_enlarge_complete_higher(tier: Tier, rng: random.Random) -> Question:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = _enlarge_steps(labels, shape, centre, k, image_labels, image)
    if k < 0:
        steps.append(
            "A negative scale factor puts the image on the opposite side of the centre from the original shape."
        )
    else:
        steps.append(
            f"A scale factor between 0 and 1 (here {_fmt_scale_factor(k)}) makes the image smaller than the "
            "original, but on the same side of the centre."
        )
    return Question(
        topic_id="transform_enlarge_complete_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"Enlarge shape {name} by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}. "
            f"Draw and label the image {image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        dedup_key=f"enlarge_h:{shape}:{centre}:{k}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_enlarge_complete_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    if k < 0:
        extra = (
            f"Because the scale factor {_fmt_scale_factor(k)} is negative, each image point goes on the "
            "opposite side of the centre from the original point, at |scale factor| times the distance."
        )
    else:
        extra = (
            f"Because the scale factor {_fmt_scale_factor(k)} is between 0 and 1, the image is smaller than "
            "the original but stays on the same side of the centre."
        )
    teaching_steps = [
        "The same rule works for negative or fractional scale factors as for positive ones: displacement "
        "from the centre, times the scale factor, gives the image's displacement from the centre.",
        extra,
        "Work through the vertices one at a time, keeping careful track of direction (sign) as well as size.",
    ]
    return ModelledExample(
        topic_id="transform_enlarge_complete_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"Enlarge shape {name} by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}. "
            f"Draw and label the image {image_name}."
        ),
        worked_calculation=(
            _vertex_mapping_text(labels, shape, image_labels, image),
            f"centre: {_fmt_point(centre)}, scale factor: {_fmt_scale_factor(k)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(f"{il}{_fmt_point(p)}" for il, p in zip(image_labels, image)),
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels, "centre": centre,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_transform_enlarge_describe(tier: Tier, rng: random.Random) -> Question:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    steps = [
        "The centre of enlargement is where lines joining each vertex to its image all meet (extended if "
        "needed) - the scale factor is the ratio of a side length in the image to the matching side in the "
        "original.",
        f"For this pair, the lines meet at {_fmt_point(centre)} and the ratio works out as "
        f"{_fmt_scale_factor(k)}.",
    ]
    return Question(
        topic_id="transform_enlarge_describe",
        tier=Tier.HIGHER,
        prompt=(
            f"Shape {name} is enlarged to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Enlargement, scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}",
        dedup_key=f"enlarge_describe:{shape}:{centre}:{k}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_transform_enlarge_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}'" for l in labels)
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    p0, q0 = shape[0], image[0]
    offset0 = (p0[0] - centre[0], p0[1] - centre[1])
    image_offset0 = (q0[0] - centre[0], q0[1] - centre[1])
    teaching_steps = [
        "A full description of an enlargement needs the word 'enlargement', the scale factor, and the centre.",
        f"Find the centre by drawing a line through a vertex and its image and extending it, e.g. through "
        f"{labels[0]}{_fmt_point(shape[0])} and {image_labels[0]}{_fmt_point(image[0])}; do the same for a "
        f"second vertex pair - where the lines cross is the centre, {_fmt_point(centre)}.",
        f"Find the scale factor by comparing displacement from the centre: {labels[0]} is "
        f"({offset0[0]}, {offset0[1]}) from the centre, and {image_labels[0]} is "
        f"({image_offset0[0]}, {image_offset0[1]}) from it - a scale factor of {_fmt_scale_factor(k)}.",
    ]
    return ModelledExample(
        topic_id="transform_enlarge_describe",
        tier=Tier.HIGHER,
        prompt=(
            f"Shape {name} is enlarged to give shape {image_name}, shown on the grid. Describe fully the "
            f"single transformation that maps {name} onto {image_name}."
        ),
        worked_calculation=(
            f"lines through vertex/image pairs meet at {_fmt_point(centre)}",
            f"scale factor: {_fmt_scale_factor(k)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Enlargement, scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}",
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": image, "image_labels": image_labels,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Topic registration
# ---------------------------------------------------------------------------


TOPIC_SYMMETRY_LINES = TopicDefinition(
    id="symmetry_lines",
    display_name="Line Symmetry",
    description="State the number of lines of symmetry of a shape.",
    generate=generate_symmetry_lines,
    section=SECTION,
    group=GROUP_SYMMETRY,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(_SYMMETRY_SHAPES),
    generate_modelled_example=generate_modelled_example_symmetry_lines,
)

TOPIC_SYMMETRY_ROTATIONAL = TopicDefinition(
    id="symmetry_rotational",
    display_name="Rotational Symmetry",
    description="State the order of rotational symmetry of a shape.",
    generate=generate_symmetry_rotational,
    section=SECTION,
    group=GROUP_SYMMETRY,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(_SYMMETRY_SHAPES),
    generate_modelled_example=generate_modelled_example_symmetry_rotational,
)

TOPIC_TRANSFORM_REFLECT_COMPLETE = TopicDefinition(
    id="transform_reflect_complete",
    display_name="Reflection",
    description="Reflect a shape in a given line on a coordinate grid.",
    generate=generate_transform_reflect_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_reflect_complete,
)

TOPIC_TRANSFORM_REFLECT_DESCRIBE = TopicDefinition(
    id="transform_reflect_describe",
    display_name="Describe a Reflection",
    description="Describe fully the reflection that maps one shape onto another.",
    generate=generate_transform_reflect_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_reflect_describe,
)

TOPIC_TRANSFORM_ROTATE_COMPLETE = TopicDefinition(
    id="transform_rotate_complete",
    display_name="Rotation",
    description="Rotate a shape about a given centre on a coordinate grid.",
    generate=generate_transform_rotate_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_rotate_complete,
)

TOPIC_TRANSFORM_ROTATE_DESCRIBE = TopicDefinition(
    id="transform_rotate_describe",
    display_name="Describe a Rotation",
    description="Describe fully the rotation that maps one shape onto another, including finding the centre.",
    generate=generate_transform_rotate_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_rotate_describe,
)

TOPIC_TRANSFORM_TRANSLATE_COMPLETE = TopicDefinition(
    id="transform_translate_complete",
    display_name="Translation",
    description="Translate a shape by a given vector on a coordinate grid.",
    generate=generate_transform_translate_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_translate_complete,
)

TOPIC_TRANSFORM_TRANSLATE_DESCRIBE = TopicDefinition(
    id="transform_translate_describe",
    display_name="Describe a Translation",
    description="Describe fully the translation that maps one shape onto another.",
    generate=generate_transform_translate_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_translate_describe,
)

TOPIC_TRANSFORM_ENLARGE_COMPLETE_FOUNDATION = TopicDefinition(
    id="transform_enlarge_complete_foundation",
    display_name="Enlargement",
    description="Enlarge a shape by a positive integer scale factor from a given centre.",
    generate=generate_transform_enlarge_complete_foundation,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_enlarge_complete_foundation,
)

TOPIC_TRANSFORM_ENLARGE_COMPLETE_HIGHER = TopicDefinition(
    id="transform_enlarge_complete_higher",
    display_name="Enlargement",
    description="Enlarge a shape by a negative or fractional scale factor from a given centre.",
    generate=generate_transform_enlarge_complete_higher,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_enlarge_complete_higher,
)

TOPIC_TRANSFORM_ENLARGE_DESCRIBE = TopicDefinition(
    id="transform_enlarge_describe",
    display_name="Describe an Enlargement",
    description="Describe fully the enlargement that maps one shape onto another, including finding the centre.",
    generate=generate_transform_enlarge_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_enlarge_describe,
)


# ---------------------------------------------------------------------------
# Combined transformations (Higher) - two transformations applied in
# sequence, described as the single equivalent transformation. Scoped to 4
# combination types, each with a known closed-form composition rule:
#   1. two translations -> a single translation (vector sum)
#   2. two reflections in parallel mirrors (both vertical or both
#      horizontal) -> a single translation, perpendicular to the mirrors,
#      of twice the distance between them
#   3. two rotations about the SAME centre -> a single rotation about that
#      centre, by the sum of the two angles
#   4. reflection in the x-axis then the y-axis (either order - both give
#      the same result) -> a single 180 deg rotation about the origin
# Unlike the four _describe topics above (which show only the final image
# and ask the student to work out what happened), this topic states both
# given transformations explicitly in the prompt text - matching the real
# GCSE phrasing for this question type ("...is reflected in x = 1 to give
# A'B'C'. A'B'C' is then reflected in x = 4 to give A''B''C''. Describe
# fully the single transformation that maps ABC onto A''B''C''.") - so the
# diagram only ever needs to show the original and the final image (no
# intermediate shape), reusing draw_grid_transformation exactly as the
# _describe topics already do.
#
# Rotation angles are drawn from the same _ROTATIONS pool (90/180/270) used
# throughout this file, so every non-degenerate pair's angle sum reduces
# (mod 360) to another value in {90, 180, 270} automatically - see
# _ROTATE_COMBO_PAIRS below - which is exactly the "keep it a nice
# describable rotation" requirement without any extra reflex-angle handling.
# ---------------------------------------------------------------------------


class _ComboInstance(NamedTuple):
    shape: list
    step1_text: str          # e.g. "translated by the vector (2, 3)"
    step2_text: str          # e.g. "translated by the vector (1, -1)"
    reasoning_steps: tuple    # solution_steps content specific to this combo
    final_answer: str
    dedup_key: str
    final: list


_COMBO_TYPES = ("translate_translate", "reflect_parallel", "rotate_same_centre", "reflect_axes")


def _random_combo_translate_translate(rng: random.Random) -> tuple:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        v1 = (rng.randint(-5, 5), rng.randint(-5, 5))
        v2 = (rng.randint(-5, 5), rng.randint(-5, 5))
        if v1 == (0, 0) or v2 == (0, 0):
            continue
        combined = (v1[0] + v2[0], v1[1] + v2[1])
        if combined == (0, 0):
            continue  # the two translations would cancel out - not describable as "a" transformation
        intermediate = [(x + v1[0], y + v1[1]) for x, y in shape]
        final = [(x + v2[0], y + v2[1]) for x, y in intermediate]
        if (_fits_grid(shape) and _fits_grid(final) and _well_separated(shape, final)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(final)
                and _clear_of_axis_tick_labels(shape) and _clear_of_axis_tick_labels(final)):
            return shape, v1, v2, combined, final
    raise ValueError("transformations: could not fit a translate+translate combined instance on the grid")


def _verify_combo_translate_translate(shape: list, combined: Point, final: list) -> None:
    """Independent check: apply the *claimed* single translation (the vector
    sum) directly to the original vertices, and confirm it reproduces the
    same final image as actually simulating the two given translations in
    sequence - this re-derives the answer by simulation rather than trusting
    the composition rule itself."""
    direct = [(x + combined[0], y + combined[1]) for x, y in shape]
    if direct != final:
        raise ValueError("transformations: combined translate+translate verification failed")


_PARALLEL_MIRROR_OFFSETS = tuple(range(-3, 4))  # -3..3; these mirror lines are
# never drawn (the diagram shows only the original and final image, matching
# every other _describe topic), so - unlike _random_mirror_line's drawn
# mirrors - there's no axis-name-label collision risk in including 0 here.


def _random_combo_reflect_parallel(rng: random.Random) -> tuple:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        orientation = rng.choice(("vertical", "horizontal"))
        a, b = rng.sample(_PARALLEL_MIRROR_OFFSETS, 2)
        key = "x" if orientation == "vertical" else "y"
        mirror1 = {"type": orientation, key: a}
        mirror2 = {"type": orientation, key: b}
        intermediate = [_reflect_point(p, mirror1) for p in shape]
        final = [_reflect_point(p, mirror2) for p in intermediate]
        combined_vector = (2 * (b - a), 0) if orientation == "vertical" else (0, 2 * (b - a))
        if (_fits_grid(shape) and _fits_grid(final) and _well_separated(shape, final)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(final)
                and _clear_of_axis_tick_labels(shape) and _clear_of_axis_tick_labels(final)):
            return shape, orientation, a, b, combined_vector, final
    raise ValueError("transformations: could not fit a reflect-parallel combined instance on the grid")


def _verify_combo_reflect_parallel(shape: list, combined_vector: Point, final: list) -> None:
    """Independent check: apply the *claimed* single translation (twice the
    gap between the mirrors, perpendicular to them) directly to the original
    vertices, and confirm it reproduces the same final image as actually
    reflecting in both mirror lines in sequence."""
    direct = [(x + combined_vector[0], y + combined_vector[1]) for x, y in shape]
    if direct != final:
        raise ValueError("transformations: combined reflect-parallel verification failed")


# Only pairs whose angle sum is NOT a multiple of 360 (i.e. doesn't compose
# to the identity, which can't meaningfully be "described" as a rotation) -
# every remaining pair's sum reduces mod 360 to another value already in
# _ROTATIONS (90/180/270), confirmed by direct enumeration of all 9 pairs.
_ROTATE_COMBO_PAIRS: tuple = tuple(
    (a1, a2) for a1 in _ROTATIONS for a2 in _ROTATIONS if (a1 + a2) % 360 != 0
)


def _random_combo_rotate_same_centre(rng: random.Random) -> tuple:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        centre = (rng.randint(-4, 4), rng.randint(-4, 4))
        angle1, angle2 = rng.choice(_ROTATE_COMBO_PAIRS)
        combined_angle = (angle1 + angle2) % 360
        intermediate = [_rotate_point(p, centre, angle1) for p in shape]
        final = [_rotate_point(p, centre, angle2) for p in intermediate]
        if (_fits_grid(shape) and _fits_grid(final) and _well_separated(shape, final)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(final)
                and _clear_of_axis_tick_labels(shape) and _clear_of_axis_tick_labels(final)):
            return shape, centre, angle1, angle2, combined_angle, final
    raise ValueError("transformations: could not fit a rotate-same-centre combined instance on the grid")


def _verify_combo_rotate_same_centre(shape: list, centre: Point, combined_angle: int, final: list) -> None:
    """Independent check: apply the *claimed* single rotation (the angle
    sum) directly to the original vertices, and confirm it reproduces the
    same final image as actually rotating twice about the same centre in
    sequence."""
    direct = [_rotate_point(p, centre, combined_angle) for p in shape]
    if direct != final:
        raise ValueError("transformations: combined rotate-same-centre verification failed")


_MIRROR_X_AXIS = {"type": "horizontal", "y": 0}  # the line y = 0 IS the x-axis
_MIRROR_Y_AXIS = {"type": "vertical", "x": 0}     # the line x = 0 IS the y-axis


def _random_combo_reflect_axes(rng: random.Random) -> tuple:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        order = rng.choice(("x_then_y", "y_then_x"))
        first, second = (_MIRROR_X_AXIS, _MIRROR_Y_AXIS) if order == "x_then_y" else (_MIRROR_Y_AXIS, _MIRROR_X_AXIS)
        intermediate = [_reflect_point(p, first) for p in shape]
        final = [_reflect_point(p, second) for p in intermediate]
        if (_fits_grid(shape) and _fits_grid(final) and _well_separated(shape, final)
                and _clear_of_axis_name_labels(shape) and _clear_of_axis_name_labels(final)
                and _clear_of_axis_tick_labels(shape) and _clear_of_axis_tick_labels(final)):
            return shape, order, final
    raise ValueError("transformations: could not fit a reflect-axes combined instance on the grid")


def _verify_combo_reflect_axes(shape: list, final: list) -> None:
    """Independent check: apply the *claimed* single 180 deg rotation about
    the origin directly to the original vertices, and confirm it reproduces
    the same final image as actually reflecting in the x-axis then the
    y-axis (or vice versa) in sequence."""
    direct = [_rotate_point(p, (0, 0), 180) for p in shape]
    if direct != final:
        raise ValueError("transformations: combined reflect-axes verification failed")


def _build_combo_instance(rng: random.Random, combo_type: str) -> _ComboInstance:
    if combo_type == "translate_translate":
        shape, v1, v2, combined, final = _random_combo_translate_translate(rng)
        _verify_combo_translate_translate(shape, combined, final)
        reasoning_steps = (
            "Two translations in a row combine into a single translation - just add the two vectors together.",
            f"{_fmt_vector(v1)} + {_fmt_vector(v2)} = {_fmt_vector(combined)}.",
        )
        return _ComboInstance(
            shape=shape,
            step1_text=f"translated by the vector {_fmt_vector(v1)}",
            step2_text=f"translated by the vector {_fmt_vector(v2)}",
            reasoning_steps=reasoning_steps,
            final_answer=f"Translation by the vector {_fmt_vector(combined)}",
            dedup_key=f"combo_tt:{shape}:{v1}:{v2}",
            final=final,
        )

    if combo_type == "reflect_parallel":
        shape, orientation, a, b, combined_vector, final = _random_combo_reflect_parallel(rng)
        _verify_combo_reflect_parallel(shape, combined_vector, final)
        line = "x" if orientation == "vertical" else "y"
        reasoning_steps = (
            "Two reflections in parallel mirror lines combine into a single translation, perpendicular to "
            "the mirrors, of twice the distance between them.",
            f"The mirror lines are a distance {abs(b - a)} apart, so the combined translation is "
            f"{_fmt_vector(combined_vector)}.",
        )
        return _ComboInstance(
            shape=shape,
            step1_text=f"reflected in the line {line} = {a}",
            step2_text=f"reflected in the line {line} = {b}",
            reasoning_steps=reasoning_steps,
            final_answer=f"Translation by the vector {_fmt_vector(combined_vector)}",
            dedup_key=f"combo_rp:{shape}:{orientation}:{a}:{b}",
            final=final,
        )

    if combo_type == "rotate_same_centre":
        shape, centre, angle1, angle2, combined_angle, final = _random_combo_rotate_same_centre(rng)
        _verify_combo_rotate_same_centre(shape, centre, combined_angle, final)
        reasoning_steps = (
            "Two rotations about the same centre combine into a single rotation about that centre, by the "
            "sum of the two angles.",
            f"Measuring both turns anticlockwise: {angle1}° + {angle2}° = {angle1 + angle2}°, "
            f"which is the same as {_rotation_wording(combined_angle)}.",
        )
        return _ComboInstance(
            shape=shape,
            step1_text=f"rotated {_rotation_wording(angle1)} about the centre {_fmt_point(centre)}",
            step2_text=f"rotated {_rotation_wording(angle2)} about the same centre",
            reasoning_steps=reasoning_steps,
            final_answer=f"Rotation {_rotation_wording(combined_angle)} about {_fmt_point(centre)}",
            dedup_key=f"combo_rc:{shape}:{centre}:{angle1}:{angle2}",
            final=final,
        )

    # reflect_axes
    shape, order, final = _random_combo_reflect_axes(rng)
    _verify_combo_reflect_axes(shape, final)
    if order == "x_then_y":
        step1_text, step2_text = "reflected in the x-axis", "reflected in the y-axis"
    else:
        step1_text, step2_text = "reflected in the y-axis", "reflected in the x-axis"
    reasoning_steps = (
        "Reflecting in the x-axis then the y-axis (or the other way round - the order doesn't matter here) "
        "sends every point (x, y) to (-x, -y).",
        "That is exactly the same effect as a single 180° rotation about the origin.",
    )
    return _ComboInstance(
        shape=shape,
        step1_text=step1_text,
        step2_text=step2_text,
        reasoning_steps=reasoning_steps,
        final_answer="Rotation 180° about (0, 0)",
        dedup_key=f"combo_ra:{shape}:{order}",
        final=final,
    )


def generate_combined_transformations(tier: Tier, rng: random.Random) -> Question:
    instance = _build_combo_instance(rng, rng.choice(_COMBO_TYPES))
    shape, final = instance.shape, instance.final
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}''" for l in labels)
    intermediate_name = _shape_name(tuple(f"{l}'" for l in labels))
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    prompt = (
        f"Shape {name} is {instance.step1_text} to give shape {intermediate_name}. "
        f"Shape {intermediate_name} is then {instance.step2_text} to give shape {image_name}. "
        f"Describe fully the single transformation that maps {name} directly onto {image_name}."
    )
    return Question(
        topic_id="combined_transformations",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=instance.reasoning_steps,
        final_answer=instance.final_answer,
        dedup_key=instance.dedup_key,
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": final, "image_labels": image_labels,
            },
        ),
    )


def generate_modelled_example_combined_transformations(tier: Tier, rng: random.Random) -> ModelledExample:
    instance = _build_combo_instance(rng, rng.choice(_COMBO_TYPES))
    shape, final = instance.shape, instance.final
    labels = _VERTEX_LABELS[: len(shape)]
    image_labels = tuple(f"{l}''" for l in labels)
    intermediate_name = _shape_name(tuple(f"{l}'" for l in labels))
    name, image_name = _shape_name(labels), _shape_name(image_labels)

    prompt = (
        f"Shape {name} is {instance.step1_text} to give shape {intermediate_name}. "
        f"Shape {intermediate_name} is then {instance.step2_text} to give shape {image_name}. "
        f"Describe fully the single transformation that maps {name} directly onto {image_name}."
    )
    teaching_steps = [
        "Two transformations applied one after another can often be combined into a single equivalent "
        "transformation - the key is knowing the combination rule for that particular pair of transformation "
        "types.",
        instance.reasoning_steps[0],
        instance.reasoning_steps[1],
        f"So the single transformation that maps {name} directly onto {image_name} is: {instance.final_answer}.",
    ]
    return ModelledExample(
        topic_id="combined_transformations",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=(
            f"{labels[0]}{_fmt_point(shape[0])} -> {image_labels[0]}{_fmt_point(final[0])}",
            f"combined: {instance.final_answer}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=instance.final_answer,
        diagram=DiagramSpec(
            kind="grid_transformation",
            params={
                "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
                "original_vertices": shape, "original_labels": labels,
                "image_vertices": final, "image_labels": image_labels,
            },
        ),
    )


TOPIC_COMBINED_TRANSFORMATIONS = TopicDefinition(
    id="combined_transformations",
    display_name="Combined Transformations",
    description="Describe the single transformation equivalent to two transformations applied in sequence.",
    generate=generate_combined_transformations,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_combined_transformations,
)
