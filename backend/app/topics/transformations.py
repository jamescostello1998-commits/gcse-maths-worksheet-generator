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

# A small compact right-angled triangle, used ONLY for reflection (see
# _random_reflect_shape below) - not added to the shared _SHAPE_TEMPLATES
# pool, so rotate/translate/enlarge are completely unaffected. Every one of
# the 4 shapes above spans 7-9 units diagonally (in the y - x direction) -
# reflecting any of them in "y = x" would need the image to land roughly
# twice that span away to keep the required clearance from the mirror line,
# which can never fit inside this diagram's +/-7 grid no matter how the
# shape is positioned (confirmed empirically: 0 successes in 200,000
# simulated attempts) - a genuine pre-existing dead branch, since this has
# been true since the diagram kind was first built, not something this
# session's reweighting introduced. This much smaller, more compact triangle
# (diagonal span of ~5, instead of 7-9) is the targeted fix: just large
# enough to still give clearly separated/legible vertex labels, small enough
# that a "y = x" reflection can actually be found within the grid at a
# realistic rate (~1.6% of random draws - well within the existing reroll
# budget) - confirmed via the same kind of direct empirical measurement used
# throughout this app rather than guessed.
_COMPACT_REFLECT_TEMPLATE: tuple[Point, ...] = ((0, 0), (3, 0), (0, 2))


def _random_shape(rng: random.Random) -> list[Point]:
    template = rng.choice(_SHAPE_TEMPLATES)
    ox, oy = rng.randint(-3, 3), rng.randint(-3, 3)
    return [(x + ox, y + oy) for x, y in template]


def _random_reflect_shape(rng: random.Random) -> list[Point]:
    """Like _random_shape, but also offers the small compact triangle - see
    _COMPACT_REFLECT_TEMPLATE - so a "y = x" mirror line has at least one
    template it can actually succeed against."""
    template = rng.choice(_SHAPE_TEMPLATES + (_COMPACT_REFLECT_TEMPLATE,))
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

# Mirror-line kind weights per tier: vertical/horizontal (y = k / x = k)
# dominate at every tier - the easiest lines to reflect in - "y = x" is an
# occasional step up, and "y = -x" (genuinely the hardest of the four, since
# neither coordinate keeps its sign) never appears at Foundation and is only
# occasional even at Higher. There is currently no Higher sibling of
# transform_reflect_complete/_describe (both topics that call this are
# Foundation-only), so in practice only the FOUNDATION weights are ever
# reached - tier is still threaded through here (rather than hardcoding the
# Foundation weights directly) so this degrades correctly if a Higher
# sibling is ever added, matching what this reweighting was actually asked
# to do.
_MIRROR_KIND_WEIGHTS = {
    Tier.FOUNDATION: {"vertical": 40, "horizontal": 40, "diagonal_pos": 20, "diagonal_neg": 0},
    Tier.HIGHER: {"vertical": 35, "horizontal": 35, "diagonal_pos": 20, "diagonal_neg": 10},
}


def _random_mirror_line(rng: random.Random, tier: Tier) -> dict:
    weights = _MIRROR_KIND_WEIGHTS[tier]
    kinds = list(weights)
    kind = rng.choices(kinds, weights=[weights[k] for k in kinds])[0]
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


def _random_reflect_instance(rng: random.Random, tier: Tier = Tier.FOUNDATION) -> tuple[list, dict, list]:
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_reflect_shape(rng)
        mirror = _random_mirror_line(rng, tier)
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
# Foundation "describe the enlargement": positive only - the enlargements
# 1.5, 2.5, and the shrinks 1/2, 1/3, 1/4 (per review feedback).
_ENLARGE_DESCRIBE_K_FOUNDATION: tuple[Fraction, ...] = (
    Fraction(3, 2), Fraction(5, 2), Fraction(1, 2), Fraction(1, 3), Fraction(1, 4),
)
# A small asymmetric base (span ~2) for constructing describe-enlargement
# instances with a scale factor p/q: the original is q x base and the image
# is p x base (both from the centre), so every vertex is an exact integer grid
# point for ANY of the fractional factors above - the general
# _random_enlarge_instance can't reliably do this, since it would need every
# vertex's offset from the centre to be divisible by q, which almost never
# happens by chance when no integer scale factor is available to fall back on.
_ENLARGE_DESCRIBE_F_BASE: tuple[Point, ...] = ((0, 0), (2, 0), (2, 1), (0, 2))


def _enlarge_describe_foundation_raw(rng: random.Random) -> tuple[list, Point, Fraction, list]:
    for _ in range(_REROLL_ATTEMPTS):
        k = Fraction(rng.choice(_ENLARGE_DESCRIBE_K_FOUNDATION))
        p, q = k.numerator, k.denominator
        orig_rel = [(q * x, q * y) for x, y in _ENLARGE_DESCRIBE_F_BASE]
        img_rel = [(p * x, p * y) for x, y in _ENLARGE_DESCRIBE_F_BASE]
        xs = [x for x, _ in orig_rel + img_rel]
        ys = [y for _, y in orig_rel + img_rel]
        cx_lo, cx_hi = _GRID_MIN - min(xs), _GRID_MAX - max(xs)
        cy_lo, cy_hi = _GRID_MIN - min(ys), _GRID_MAX - max(ys)
        if cx_lo > cx_hi or cy_lo > cy_hi:
            continue
        centre = (rng.randint(cx_lo, cx_hi), rng.randint(cy_lo, cy_hi))
        shape = [(centre[0] + x, centre[1] + y) for x, y in orig_rel]
        image = [(centre[0] + x, centre[1] + y) for x, y in img_rel]
        if _fits_grid(shape) and _fits_grid(image):
            _verify_enlargement(shape, centre, k, image)
            return shape, centre, k, image
    raise ValueError("transformations: could not fit a foundation describe-enlargement instance")


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
    # A real stacked column vector (via the \colvec mathtext marker), the
    # correct GCSE notation for a translation vector - not a coordinate pair.
    return f"\\colvec{{{v[0]}}}{{{v[1]}}}"


def _segments_cross(p1, p2, p3, p4) -> bool:
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = ccw(p3, p4, p1), ccw(p3, p4, p2)
    d3, d4 = ccw(p1, p2, p3), ccw(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _point_in_poly(pt, poly) -> bool:
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xint = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xint:
                inside = not inside
    return inside


def _polygons_intersect(a: list, b: list) -> bool:
    """True if two polygons overlap (an edge crosses, or one contains a
    vertex of the other). Used to keep the two shapes in a 'describe a
    rotation' question from sitting on top of each other."""
    na, nb = len(a), len(b)
    for i in range(na):
        for j in range(nb):
            if _segments_cross(a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]):
                return True
    if any(_point_in_poly(p, b) for p in a):
        return True
    if any(_point_in_poly(p, a) for p in b):
        return True
    return False


def _fmt_scale_factor(k: Fraction) -> str:
    return str(k.numerator) if k.denominator == 1 else f"{k.numerator}/{k.denominator}"


def _shape_name(labels: tuple) -> str:
    return "".join(labels)


def _image_coords(image: list) -> str:
    """The image's vertices as a plain coordinate list (no per-vertex letters,
    since vertices are no longer labelled)."""
    return ", ".join(_fmt_point(p) for p in image)


def _transform_diagram(original: list, image=None, *, mirror=None, image_same_color: bool = False) -> DiagramSpec:
    """Build a grid_transformation spec with the current conventions: vertices
    unlabelled, each shape identified by a whole-shape letter (A original,
    B image). No centre dot or translation arrow is ever drawn (the student
    reads/plots those from the text). The mirror line, when given, is still
    shown. image=None gives the blank question-page version."""
    params: dict = {
        "x_min": _GRID_MIN, "x_max": _GRID_MAX, "y_min": _GRID_MIN, "y_max": _GRID_MAX,
        "original_vertices": original, "original_labels": tuple("" for _ in original),
        "original_shape_label": "A",
    }
    if mirror is not None:
        params["mirror_line"] = mirror
    if image is not None:
        params["image_vertices"] = image
        params["image_labels"] = tuple("" for _ in image)
        params["image_shape_label"] = "B"
        if image_same_color:
            params["image_same_color"] = True
    return DiagramSpec(kind="grid_transformation", params=params)


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
        topic_id="symmetry_lines_F",
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
        topic_id="symmetry_lines_F",
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
        topic_id="symmetry_rotational_F",
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
        topic_id="symmetry_rotational_F",
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
    shape, mirror, image = _random_reflect_instance(rng, tier)
    _verify_reflection(shape, mirror, image)

    steps = [
        f"Reflect each vertex of shape A in the line {mirror['label']}: the mirror line is the perpendicular "
        "bisector of every point and its image, so each point stays the same distance from the line, on the "
        "other side.",
        f"The image, shape B, has vertices {_image_coords(image)}.",
    ]
    return Question(
        topic_id="transform_reflect_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Reflect shape A in the line {mirror['label']}.",
        solution_steps=tuple(steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        dedup_key=f"reflect:{shape}:{mirror['label']}",
        diagram=_transform_diagram(shape, mirror=mirror),
        solution_diagram=_transform_diagram(shape, image, mirror=mirror),
    )


def generate_modelled_example_transform_reflect_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, mirror, image = _random_reflect_instance(rng, tier)
    _verify_reflection(shape, mirror, image)

    teaching_steps = [
        f"To reflect shape A in the line {mirror['label']}, imagine folding the grid along that line - each "
        "point of the shape lands exactly on top of its image.",
        "That means the mirror line is always the perpendicular bisector of the line joining a point to its "
        "image: same distance from the line, directly opposite it.",
        "Work through the vertices one at a time, counting squares from each point to the mirror line, then "
        "the same number of squares again on the other side.",
    ]
    return ModelledExample(
        topic_id="transform_reflect_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Reflect shape A in the line {mirror['label']}.",
        worked_calculation=(
            f"mirror line: {mirror['label']}",
            f"image (shape B): {_image_coords(image)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        diagram=_transform_diagram(shape, image, mirror=mirror),
    )


def generate_transform_reflect_describe(tier: Tier, rng: random.Random) -> Question:
    shape, mirror, image = _random_reflect_instance(rng, tier)
    _verify_reflection(shape, mirror, image)

    steps = [
        f"Every vertex and its image are the same distance from a single line, on opposite sides of it - "
        "that line is the mirror line.",
        f"Comparing corresponding vertices shows the mirror line is {mirror['label']}.",
    ]
    return Question(
        topic_id="transform_reflect_describe_F",
        tier=Tier.FOUNDATION,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        solution_steps=tuple(steps),
        final_answer=f"Reflection in the line {mirror['label']}",
        dedup_key=f"reflect_describe:{shape}:{mirror['label']}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


def generate_modelled_example_transform_reflect_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, mirror, image = _random_reflect_instance(rng, tier)
    _verify_reflection(shape, mirror, image)

    teaching_steps = [
        f"'Describe fully' a reflection means naming the mirror line, not just saying 'reflection'.",
        f"Pick a vertex of shape A and its image on shape B, e.g. {_fmt_point(shape[0])} and "
        f"{_fmt_point(image[0])} - the mirror line passes exactly halfway between them, "
        "at right angles to the line joining them.",
        f"Checking every other vertex pair the same way confirms the mirror line is {mirror['label']}.",
    ]
    return ModelledExample(
        topic_id="transform_reflect_describe_F",
        tier=Tier.FOUNDATION,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        worked_calculation=(
            f"{_fmt_point(shape[0])} -> {_fmt_point(image[0])}",
            f"mirror line: {mirror['label']}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Reflection in the line {mirror['label']}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------


def generate_transform_rotate_complete(tier: Tier, rng: random.Random) -> Question:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    wording = _rotation_wording(angle)

    steps = [
        f"Rotate each vertex of shape A {wording} about the centre {_fmt_point(centre)}: every point stays "
        "the same distance from the centre and turns through the same angle.",
        f"The image, shape B, has vertices {_image_coords(image)}.",
    ]
    return Question(
        topic_id="transform_rotate_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Rotate shape A {wording} about the centre {_fmt_point(centre)}.",
        solution_steps=tuple(steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        dedup_key=f"rotate:{shape}:{centre}:{angle}",
        diagram=_transform_diagram(shape),
        solution_diagram=_transform_diagram(shape, image),
    )


def generate_modelled_example_transform_rotate_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, angle, image = _random_rotate_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    wording = _rotation_wording(angle)

    teaching_steps = [
        f"A rotation turns every point of shape A through the same angle ({wording}) about a fixed centre, "
        f"here {_fmt_point(centre)} - every point stays the same distance from the centre.",
        "Tracing paper (or counting squares round the centre) makes this easier: for a 90° turn, swap and "
        "flip the coordinates relative to the centre; for 180°, both coordinates flip sign relative to it.",
        "Work through the vertices one at a time, using the centre as the pivot.",
    ]
    return ModelledExample(
        topic_id="transform_rotate_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Rotate shape A {wording} about the centre {_fmt_point(centre)}.",
        worked_calculation=(
            f"centre: {_fmt_point(centre)}, rotation: {wording}",
            f"image (shape B): {_image_coords(image)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        diagram=_transform_diagram(shape, image),
    )


def _random_rotate_describe_instance(rng: random.Random):
    """A rotation instance whose original and image do not overlap - so the
    two shapes on a 'describe the rotation' diagram sit clearly apart. Falls
    back to whatever it last generated if a non-intersecting pair isn't found
    within the budget (which keeps the intersecting rate well under 5%)."""
    result = _random_rotate_instance(rng)
    for _ in range(80):
        shape, _centre, _angle, image = result
        if not _polygons_intersect(shape, image):
            return result
        result = _random_rotate_instance(rng)
    return result


def generate_transform_rotate_describe(tier: Tier, rng: random.Random) -> Question:
    shape, centre, angle, image = _random_rotate_describe_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    wording = _rotation_wording(angle)

    steps = [
        "The centre of rotation is the one point that is the same distance from a vertex and its image, for "
        "every vertex - it can be found where the perpendicular bisectors of two such pairs cross.",
        f"Measuring the turn from a vertex to its image about that point gives {wording} about {_fmt_point(centre)}.",
    ]
    return Question(
        topic_id="transform_rotate_describe_H",
        tier=Tier.HIGHER,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        solution_steps=tuple(steps),
        final_answer=f"Rotation {wording} about {_fmt_point(centre)}",
        dedup_key=f"rotate_describe:{shape}:{centre}:{angle}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


def generate_modelled_example_transform_rotate_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, angle, image = _random_rotate_describe_instance(rng)
    _verify_rotation(shape, centre, angle, image)
    wording = _rotation_wording(angle)

    teaching_steps = [
        "A full description of a rotation needs three things: the word 'rotation', the angle and direction "
        "(or just the angle for 180°), and the centre.",
        f"To find the centre without guessing, join a vertex to its image "
        "and construct its perpendicular bisector; do the same for a second vertex pair - the two bisectors "
        f"cross exactly at the centre, {_fmt_point(centre)}.",
        f"Finally check the angle by measuring the turn from a vertex to its image about that centre: {wording}.",
    ]
    return ModelledExample(
        topic_id="transform_rotate_describe_H",
        tier=Tier.HIGHER,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        worked_calculation=(
            f"perpendicular bisectors of two vertex-and-image pairs meet at "
            f"{_fmt_point(centre)}",
            f"rotation: {wording} about {_fmt_point(centre)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Rotation {wording} about {_fmt_point(centre)}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------


def generate_transform_translate_complete(tier: Tier, rng: random.Random) -> Question:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)

    steps = [
        f"Translate every vertex of shape A by the vector {_fmt_vector(vector)}: move each point "
        f"{abs(vector[0])} square{'s' if abs(vector[0]) != 1 else ''} "
        f"{'right' if vector[0] >= 0 else 'left'} and {abs(vector[1])} "
        f"square{'s' if abs(vector[1]) != 1 else ''} {'up' if vector[1] >= 0 else 'down'}.",
        f"The image, shape B, has vertices {_image_coords(image)}.",
    ]
    return Question(
        topic_id="transform_translate_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Translate shape A by the vector {_fmt_vector(vector)}.",
        solution_steps=tuple(steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        dedup_key=f"translate:{shape}:{vector}",
        # No direction arrow on the diagram - the vector is given in the text.
        diagram=_transform_diagram(shape),
        solution_diagram=_transform_diagram(shape, image),
    )


def generate_modelled_example_transform_translate_complete(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)

    teaching_steps = [
        f"A translation slides every point of shape A by the same vector, {_fmt_vector(vector)} - the shape "
        "doesn't turn or flip, it just moves.",
        f"The top number of the vector is how far to move left/right ({vector[0]}), and the bottom number is "
        f"how far to move up/down ({vector[1]}).",
        "Apply the same move to every vertex in turn, keeping the shape's size and orientation unchanged.",
    ]
    return ModelledExample(
        topic_id="transform_translate_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Translate shape A by the vector {_fmt_vector(vector)}.",
        worked_calculation=(
            f"vector: {_fmt_vector(vector)}",
            f"image (shape B): {_image_coords(image)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        diagram=_transform_diagram(shape, image),
    )


def generate_transform_translate_describe(tier: Tier, rng: random.Random) -> Question:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)

    steps = [
        f"Every vertex moves by exactly the same amount: comparing a vertex of shape A, {_fmt_point(shape[0])}, "
        f"with the matching vertex of shape B, {_fmt_point(image[0])}, gives the vector {_fmt_vector(vector)}.",
        "Checking the other vertices confirms the same vector applies throughout, so this is a translation.",
    ]
    return Question(
        topic_id="transform_translate_describe_F",
        tier=Tier.FOUNDATION,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        solution_steps=tuple(steps),
        final_answer=f"Translation by the vector {_fmt_vector(vector)}",
        dedup_key=f"translate_describe:{shape}:{vector}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


def generate_modelled_example_transform_translate_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, vector, image = _random_translate_instance(rng)
    _verify_translation(shape, vector, image)

    teaching_steps = [
        "If the image is the same size and orientation as the original, just slid to a new position, it's a "
        "translation - described fully by a single column vector.",
        f"Pick any vertex of shape A and the matching vertex of shape B, e.g. {_fmt_point(shape[0])} to "
        f"{_fmt_point(image[0])}: subtract to get the vector {_fmt_vector(vector)}.",
        "Check a second vertex pair gives the same vector, to confirm it isn't a rotation or reflection that "
        "happens to move that one point the same way.",
    ]
    return ModelledExample(
        topic_id="transform_translate_describe_F",
        tier=Tier.FOUNDATION,
        prompt="Describe fully the single transformation that maps shape A onto shape B.",
        worked_calculation=(
            f"{_fmt_point(image[0])} - {_fmt_point(shape[0])} = {_fmt_vector(vector)}",
            f"vector: {_fmt_vector(vector)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Translation by the vector {_fmt_vector(vector)}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


# ---------------------------------------------------------------------------
# Enlargement
# ---------------------------------------------------------------------------


def _enlarge_steps(shape: list, centre: Point, k: Fraction, image: list) -> list:
    p0, q0 = shape[0], image[0]
    offset0 = (p0[0] - centre[0], p0[1] - centre[1])
    return [
        f"The centre of enlargement is {_fmt_point(centre)} and the scale factor is {_fmt_scale_factor(k)}.",
        f"For each vertex, find its displacement from the centre and multiply by the scale factor: e.g. "
        f"{_fmt_point(p0)} is a displacement of ({offset0[0]}, {offset0[1]}) from the centre, so it maps to "
        f"{_fmt_point(centre)} + {_fmt_scale_factor(k)} × ({offset0[0]}, {offset0[1]}) = {_fmt_point(q0)}.",
        f"Repeat for every vertex. The image, shape B, has vertices {_image_coords(image)}.",
    ]


def generate_transform_enlarge_complete_foundation(tier: Tier, rng: random.Random) -> Question:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_FOUNDATION)
    _verify_enlargement(shape, centre, k, image)

    return Question(
        topic_id="transform_enlarge_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Enlarge shape A by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}.",
        solution_steps=tuple(_enlarge_steps(shape, centre, k, image)),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        dedup_key=f"enlarge_f:{shape}:{centre}:{k}",
        diagram=_transform_diagram(shape),
        solution_diagram=_transform_diagram(shape, image),
    )


def generate_modelled_example_transform_enlarge_complete_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_FOUNDATION)
    _verify_enlargement(shape, centre, k, image)

    teaching_steps = [
        f"An enlargement scales every distance from the centre of enlargement by the scale factor - here, "
        f"scale factor {_fmt_scale_factor(k)} means every point of shape A ends up {_fmt_scale_factor(k)} "
        f"times as far from {_fmt_point(centre)} as it started.",
        "Count the squares across and up from the centre to each vertex, multiply both by the scale factor, "
        "then count that new distance from the centre in the same direction to plot the image.",
        "The shape gets bigger but keeps exactly the same proportions, since every vertex is scaled by the "
        "same factor.",
    ]
    return ModelledExample(
        topic_id="transform_enlarge_complete_F",
        tier=Tier.FOUNDATION,
        prompt=f"Enlarge shape A by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}.",
        worked_calculation=(
            f"centre: {_fmt_point(centre)}, scale factor: {_fmt_scale_factor(k)}",
            f"image (shape B): {_image_coords(image)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        diagram=_transform_diagram(shape, image),
    )


def generate_transform_enlarge_complete_higher(tier: Tier, rng: random.Random) -> Question:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)

    steps = _enlarge_steps(shape, centre, k, image)
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
        topic_id="transform_enlarge_complete_H",
        tier=Tier.HIGHER,
        prompt=f"Enlarge shape A by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}.",
        solution_steps=tuple(steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        dedup_key=f"enlarge_h:{shape}:{centre}:{k}",
        diagram=_transform_diagram(shape),
        solution_diagram=_transform_diagram(shape, image),
    )


def generate_modelled_example_transform_enlarge_complete_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, centre, k, image = _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)
    _verify_enlargement(shape, centre, k, image)

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
        topic_id="transform_enlarge_complete_H",
        tier=Tier.HIGHER,
        prompt=f"Enlarge shape A by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}.",
        worked_calculation=(
            f"centre: {_fmt_point(centre)}, scale factor: {_fmt_scale_factor(k)}",
            f"image (shape B): {_image_coords(image)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Image (shape B): {_image_coords(image)}",
        diagram=_transform_diagram(shape, image),
    )


def _enlarge_describe_instance(rng: random.Random, instance_fn, allow_reverse: bool):
    """Set up a 'describe the enlargement' question. Shape A is the original,
    shape B its image under scale factor k about `centre` (built by
    instance_fn). When allow_reverse (Foundation), 10% of the time the question
    instead asks what maps B onto A - the same centre with the reciprocal scale
    factor 1/k."""
    shape, centre, k, image = instance_fn(rng)
    _verify_enlargement(shape, centre, k, image)
    reverse = allow_reverse and rng.random() < 0.10
    if reverse:
        src, dst, answer_k = "B", "A", Fraction(1) / k
    else:
        src, dst, answer_k = "A", "B", k
    return shape, centre, k, image, src, dst, answer_k, reverse


def _enlarge_describe_question(topic_id: str, tier: Tier, instance_fn, allow_reverse: bool, rng: random.Random) -> Question:
    shape, centre, k, image, src, dst, answer_k, reverse = _enlarge_describe_instance(rng, instance_fn, allow_reverse)
    steps = [
        "The centre of enlargement is where lines joining each vertex to its image all meet (extended if "
        "needed) - the scale factor is the ratio of a side length in the image to the matching side in the "
        "original.",
        f"For mapping shape {src} onto shape {dst}, the lines meet at {_fmt_point(centre)} and the scale "
        f"factor works out as {_fmt_scale_factor(answer_k)}.",
    ]
    return Question(
        topic_id=topic_id,
        tier=tier,
        prompt=f"Describe fully the single transformation that maps shape {src} onto shape {dst}.",
        solution_steps=tuple(steps),
        final_answer=f"Enlargement, scale factor {_fmt_scale_factor(answer_k)}, centre {_fmt_point(centre)}",
        dedup_key=f"enlarge_describe:{topic_id}:{shape}:{centre}:{k}:{reverse}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


def _enlarge_describe_modelled(topic_id: str, tier: Tier, instance_fn, allow_reverse: bool, rng: random.Random) -> ModelledExample:
    shape, centre, k, image, src, dst, answer_k, reverse = _enlarge_describe_instance(rng, instance_fn, allow_reverse)
    teaching_steps = [
        "A full description of an enlargement needs the word 'enlargement', the scale factor, and the centre.",
        f"Find the centre by drawing a line through a vertex and its image and extending it, then doing the "
        f"same for a second vertex pair - where the lines cross is the centre, {_fmt_point(centre)}.",
        f"Find the scale factor by comparing distances from the centre for the direction asked "
        f"(shape {src} onto shape {dst}): it works out as {_fmt_scale_factor(answer_k)}.",
    ]
    return ModelledExample(
        topic_id=topic_id,
        tier=tier,
        prompt=f"Describe fully the single transformation that maps shape {src} onto shape {dst}.",
        worked_calculation=(
            f"lines through vertex/image pairs meet at {_fmt_point(centre)}",
            f"scale factor ({src} -> {dst}): {_fmt_scale_factor(answer_k)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Enlargement, scale factor {_fmt_scale_factor(answer_k)}, centre {_fmt_point(centre)}",
        diagram=_transform_diagram(shape, image, image_same_color=True),
    )


def _enlarge_describe_higher_raw(rng: random.Random):
    return _random_enlarge_instance(rng, _ENLARGE_K_HIGHER)


def generate_transform_enlarge_describe(tier: Tier, rng: random.Random) -> Question:
    return _enlarge_describe_question("transform_enlarge_describe_H", Tier.HIGHER, _enlarge_describe_higher_raw, False, rng)


def generate_modelled_example_transform_enlarge_describe(tier: Tier, rng: random.Random) -> ModelledExample:
    return _enlarge_describe_modelled("transform_enlarge_describe_H", Tier.HIGHER, _enlarge_describe_higher_raw, False, rng)


def generate_transform_enlarge_describe_foundation(tier: Tier, rng: random.Random) -> Question:
    return _enlarge_describe_question(
        "transform_enlarge_describe_F", Tier.FOUNDATION, _enlarge_describe_foundation_raw, True, rng
    )


def generate_modelled_example_transform_enlarge_describe_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    return _enlarge_describe_modelled(
        "transform_enlarge_describe_F", Tier.FOUNDATION, _enlarge_describe_foundation_raw, True, rng
    )


# ---------------------------------------------------------------------------
# Topic registration
# ---------------------------------------------------------------------------


TOPIC_SYMMETRY_LINES = TopicDefinition(
    id="symmetry_lines_F",
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
    id="symmetry_rotational_F",
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
    id="transform_reflect_complete_F",
    display_name="Reflection",
    description="Reflect a shape in a given line on a coordinate grid.",
    generate=generate_transform_reflect_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_reflect_complete,
)

TOPIC_TRANSFORM_REFLECT_DESCRIBE = TopicDefinition(
    id="transform_reflect_describe_F",
    display_name="Describe a Reflection",
    description="Describe fully the reflection that maps one shape onto another.",
    generate=generate_transform_reflect_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_reflect_describe,
)

TOPIC_TRANSFORM_ROTATE_COMPLETE = TopicDefinition(
    id="transform_rotate_complete_F",
    display_name="Rotation",
    description="Rotate a shape about a given centre on a coordinate grid.",
    generate=generate_transform_rotate_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_rotate_complete,
)

TOPIC_TRANSFORM_ROTATE_DESCRIBE = TopicDefinition(
    id="transform_rotate_describe_H",
    display_name="Describe a Rotation",
    description="Describe fully the rotation that maps one shape onto another, including finding the centre.",
    generate=generate_transform_rotate_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_rotate_describe,
)

TOPIC_TRANSFORM_TRANSLATE_COMPLETE = TopicDefinition(
    id="transform_translate_complete_F",
    display_name="Translation",
    description="Translate a shape by a given vector on a coordinate grid.",
    generate=generate_transform_translate_complete,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_translate_complete,
)

TOPIC_TRANSFORM_TRANSLATE_DESCRIBE = TopicDefinition(
    id="transform_translate_describe_F",
    display_name="Describe a Translation",
    description="Describe fully the translation that maps one shape onto another.",
    generate=generate_transform_translate_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_translate_describe,
)

TOPIC_TRANSFORM_ENLARGE_COMPLETE_FOUNDATION = TopicDefinition(
    id="transform_enlarge_complete_F",
    display_name="Enlargement",
    description="Enlarge a shape by a positive integer scale factor from a given centre.",
    generate=generate_transform_enlarge_complete_foundation,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_enlarge_complete_foundation,
)

TOPIC_TRANSFORM_ENLARGE_COMPLETE_HIGHER = TopicDefinition(
    id="transform_enlarge_complete_H",
    display_name="Enlargement",
    description="Enlarge a shape by a negative or fractional scale factor from a given centre.",
    generate=generate_transform_enlarge_complete_higher,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_enlarge_complete_higher,
)

TOPIC_TRANSFORM_ENLARGE_DESCRIBE = TopicDefinition(
    id="transform_enlarge_describe_H",
    display_name="Describe an Enlargement",
    description="Describe fully the enlargement that maps one shape onto another, including finding the centre.",
    generate=generate_transform_enlarge_describe,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_transform_enlarge_describe,
)

TOPIC_TRANSFORM_ENLARGE_DESCRIBE_FOUNDATION = TopicDefinition(
    id="transform_enlarge_describe_F",
    display_name="Describe an Enlargement",
    description="Describe fully a positive enlargement (including fractional scale factors) that maps one shape onto another.",
    generate=generate_transform_enlarge_describe_foundation,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_transform_enlarge_describe_foundation,
)


# ---------------------------------------------------------------------------
# Combined transformations (Higher) - the student applies a sequence of 2 or 3
# transformations to shape A themselves and draws the final image B (rather
# than describing a single equivalent transformation). Each step is a genuine
# reflection / rotation / translation / enlargement; every intermediate and
# the final image is checked to fit the grid, and each step is independently
# verified via the same _verify_* helpers the single-transform topics use.
# ---------------------------------------------------------------------------


def _combo_apply_reflect(shape: list, rng: random.Random):
    mirror = _random_mirror_line(rng, Tier.HIGHER)
    image = [_reflect_point(p, mirror) for p in shape]
    _verify_reflection(shape, mirror, image)
    return image, f"reflected in the line {mirror['label']}"


def _combo_apply_rotate(shape: list, rng: random.Random):
    centre = (rng.randint(-3, 3), rng.randint(-3, 3))
    angle = rng.choice(_ROTATIONS)
    image = [_rotate_point(p, centre, angle) for p in shape]
    _verify_rotation(shape, centre, angle, image)
    return image, f"rotated {_rotation_wording(angle)} about {_fmt_point(centre)}"


def _combo_apply_translate(shape: list, rng: random.Random):
    vector = (0, 0)
    while vector == (0, 0):
        vector = (rng.randint(-6, 6), rng.randint(-6, 6))
    image = [(p[0] + vector[0], p[1] + vector[1]) for p in shape]
    _verify_translation(shape, vector, image)
    return image, f"translated by the vector {_fmt_vector(vector)}"


def _combo_apply_enlarge(shape: list, rng: random.Random):
    k = Fraction(rng.choice((2, Fraction(1, 2))))
    centre = (rng.randint(-3, 3), rng.randint(-3, 3))
    offsets = [(p[0] - centre[0], p[1] - centre[1]) for p in shape]
    if k.denominator != 1 and any(ox % k.denominator or oy % k.denominator for ox, oy in offsets):
        return None  # image wouldn't land on integer grid points
    image = [(int(centre[0] + k * ox), int(centre[1] + k * oy)) for ox, oy in offsets]
    _verify_enlargement(shape, centre, k, image)
    return image, f"enlarged by scale factor {_fmt_scale_factor(k)}, centre {_fmt_point(centre)}"


_COMBO_APPLIERS = (_combo_apply_reflect, _combo_apply_rotate, _combo_apply_translate, _combo_apply_enlarge)


def _random_combined_sequence(rng: random.Random):
    """Shape A plus a sequence of 2-3 transformations (of any type), returning
    (shape, step_texts, final_image). Every intermediate and the final image is
    kept on the grid; each step is independently verified as it is built."""
    for _ in range(_REROLL_ATTEMPTS):
        shape = _random_shape(rng)
        if not _fits_grid(shape):
            continue
        n_steps = rng.choice((2, 2, 3))
        current = shape
        texts: list[str] = []
        ok = True
        for _ in range(n_steps):
            applier = rng.choice(_COMBO_APPLIERS)
            result = applier(current, rng)
            if result is None:
                ok = False
                break
            image, text = result
            if not _fits_grid(image):
                ok = False
                break
            current = image
            texts.append(text)
        if ok and len(texts) == n_steps and current != shape:
            return shape, texts, current
    raise ValueError("transformations: could not build a combined sequence on the grid")


def generate_combined_transformations(tier: Tier, rng: random.Random) -> Question:
    shape, texts, final = _random_combined_sequence(rng)
    prompt = "Shape A is " + ", then ".join(texts) + ". Draw and label the final image B."
    steps = ["Apply each transformation in order, carrying the image of one step into the next as the shape to transform for the next step."]
    steps += [f"Step {i + 1}: {text}." for i, text in enumerate(texts)]
    steps.append(f"The final image, shape B, has vertices {_image_coords(final)}.")
    return Question(
        topic_id="combined_transformations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"Final image (shape B): {_image_coords(final)}",
        dedup_key=f"combined:{shape}:{final}",
        diagram=_transform_diagram(shape),
        solution_diagram=_transform_diagram(shape, final),
    )


def generate_modelled_example_combined_transformations(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, texts, final = _random_combined_sequence(rng)
    prompt = "Shape A is " + ", then ".join(texts) + ". Draw and label the final image B."
    teaching_steps = [
        "When several transformations are applied one after another, do them strictly in order: the image "
        "from each step becomes the shape you transform in the next step - never transform the original each "
        "time.",
        "Transform one vertex at a time through the whole sequence, or transform the whole shape at each step "
        "and redraw it before moving on - both work as long as you keep the order.",
        "The order of the steps here is: " + "; ".join(f"({i + 1}) {text}" for i, text in enumerate(texts)) + ".",
        f"After the last step, the final image (shape B) has vertices {_image_coords(final)}.",
    ]
    return ModelledExample(
        topic_id="combined_transformations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=(
            "apply the transformations in order",
            f"final image (shape B): {_image_coords(final)}",
        ),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Final image (shape B): {_image_coords(final)}",
        diagram=_transform_diagram(shape, final),
    )


TOPIC_COMBINED_TRANSFORMATIONS = TopicDefinition(
    id="combined_transformations_H",
    display_name="Combined Transformations",
    description="Describe the single transformation equivalent to two transformations applied in sequence.",
    generate=generate_combined_transformations,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_combined_transformations,
)
