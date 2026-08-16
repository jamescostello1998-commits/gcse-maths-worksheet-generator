"""Geometry Phase 4b (part 3 of 3): loci - the locus of points satisfying a
distance rule from fixed points/lines (loci_constructions, Foundation), and
a shaded region satisfying two such rules at once (loci_regions, Higher).

Both topics draw on a real-scale numbered grid (app/pdf/diagrams.py's
draw_loci_construction/draw_loci_region), reusing the same blank-question/
completed-solution split as the Phase 4a grid-transformation diagrams -
`diagram` shows only the given points/lines, `solution_diagram` adds the
constructed locus or shaded region.
"""

import math
import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_LOCI = "Loci"

_GRID_RANGE = (-4, 4)


def _unit_vector(angle_deg: float) -> tuple:
    rad = math.radians(angle_deg)
    return (math.cos(rad), math.sin(rad))


def _bbox(xs: list, ys: list, margin: float = 1.0) -> dict:
    return {
        "x_min": min(xs) - margin, "x_max": max(xs) + margin,
        "y_min": min(ys) - margin, "y_max": max(ys) + margin,
    }


# ---------------------------------------------------------------------------
# loci_constructions (Foundation): point / two_points / two_lines
# ---------------------------------------------------------------------------

def _point_locus(rng: random.Random) -> dict:
    P = (rng.randint(*_GRID_RANGE), rng.randint(*_GRID_RANGE))
    r_cm = rng.randint(2, 6)
    prompt = f"P is a fixed point. Describe the locus of points that are exactly {r_cm} cm from P."
    steps = [
        "The locus of points a fixed distance from a single point is a circle centred on that point.",
        f"Every point on the locus must be exactly {r_cm} cm from P, so the locus is a circle with "
        f"centre P and radius {r_cm} cm.",
    ]
    answer = f"A circle, centre P, radius {r_cm} cm."
    bbox = _bbox([P[0] - r_cm, P[0] + r_cm], [P[1] - r_cm, P[1] + r_cm])
    return {
        "prompt": prompt, "steps": steps, "answer": answer, "bbox": bbox,
        "points": [{"xy": P, "label": "P"}], "given_lines": [],
        "circle": {"centre": P, "radius": r_cm}, "segment": None,
        "dedup_key": f"loci_point:{P}:{r_cm}",
    }


def _two_points_locus(rng: random.Random) -> dict:
    while True:
        A = (rng.randint(*_GRID_RANGE), rng.randint(*_GRID_RANGE))
        B = (rng.randint(*_GRID_RANGE), rng.randint(*_GRID_RANGE))
        if A != B:
            break
    mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    dx, dy = B[0] - A[0], B[1] - A[1]
    length = math.hypot(dx, dy)
    ux, uy = -dy / length, dx / length
    extend = max(length, 4) * 0.9
    seg_p1 = (mx + ux * extend, my + uy * extend)
    seg_p2 = (mx - ux * extend, my - uy * extend)

    # Independent verification: the perpendicular-bisector definition
    # directly (equidistant from A and B, and perpendicular to AB) - the
    # same reasoning transformations.py's _verify_reflection uses for a
    # reflection mirror line, which a perpendicular bisector geometrically
    # is.
    for P in (seg_p1, seg_p2):
        dA = math.hypot(P[0] - A[0], P[1] - A[1])
        dB = math.hypot(P[0] - B[0], P[1] - B[1])
        if abs(dA - dB) > 1e-6:
            raise ValueError("loci_constructions verification failed: two_points locus not equidistant from A and B")
    if abs((seg_p2[0] - seg_p1[0]) * dx + (seg_p2[1] - seg_p1[1]) * dy) > 1e-6:
        raise ValueError("loci_constructions verification failed: two_points locus not perpendicular to AB")

    prompt = (
        "A and B are two fixed points (shown). Describe the locus of points that are equidistant from "
        "A and B (the same distance from both)."
    )
    steps = [
        "The locus of points equidistant from two fixed points is the perpendicular bisector of the "
        "line segment joining them.",
        "So the locus is the perpendicular bisector of AB: the line through the midpoint of AB, at a "
        "right angle to AB.",
    ]
    answer = "The perpendicular bisector of AB."
    bbox = _bbox([A[0], B[0], seg_p1[0], seg_p2[0]], [A[1], B[1], seg_p1[1], seg_p2[1]])
    return {
        "prompt": prompt, "steps": steps, "answer": answer, "bbox": bbox,
        "points": [{"xy": A, "label": "A"}, {"xy": B, "label": "B"}],
        "given_lines": [{"p1": A, "p2": B}],
        "circle": None, "segment": {"p1": seg_p1, "p2": seg_p2, "dashed": False},
        "dedup_key": f"loci_two_points:{A}:{B}",
    }


def _dist_to_line(P: tuple, line_a: tuple, line_b: tuple) -> float:
    lx, ly = line_b[0] - line_a[0], line_b[1] - line_a[1]
    line_len = math.hypot(lx, ly)
    cross = abs(lx * (P[1] - line_a[1]) - ly * (P[0] - line_a[0]))
    return cross / line_len


def _two_lines_locus(rng: random.Random) -> dict:
    Y = (0.0, 0.0)
    base_angle = rng.randint(0, 359)
    sep_deg = rng.randint(30, 150)
    ray_len = 5.0
    ux1, uy1 = _unit_vector(base_angle)
    ux2, uy2 = _unit_vector(base_angle + sep_deg)
    X = (Y[0] + ray_len * ux1, Y[1] + ray_len * uy1)
    Z = (Y[0] + ray_len * ux2, Y[1] + ray_len * uy2)
    bux, buy = _unit_vector(base_angle + sep_deg / 2)
    bisector_end = (Y[0] + ray_len * 1.1 * bux, Y[1] + ray_len * 1.1 * buy)

    # Independent verification: sample a point on the constructed bisector
    # ray and confirm it is the same perpendicular distance from each of the
    # two given rays (the point-to-line distance formula, computed
    # separately per ray) - the geometric definition of an angle bisector.
    d1 = _dist_to_line(bisector_end, Y, X)
    d2 = _dist_to_line(bisector_end, Y, Z)
    if abs(d1 - d2) > 1e-6:
        raise ValueError("loci_constructions verification failed: two_lines locus not equidistant from both rays")

    prompt = (
        "Two straight lines meet at Y, passing through X and Z as shown. Describe the locus of points "
        "that are equidistant from line XY and line ZY."
    )
    steps = [
        "The locus of points equidistant from two intersecting lines is the bisector of the angle "
        "between them.",
        "So the locus is the bisector of angle XYZ: the line from Y that splits the angle into two "
        "equal halves.",
    ]
    answer = "The angle bisector of angle XYZ."
    bbox = _bbox([X[0], Y[0], Z[0], bisector_end[0]], [X[1], Y[1], Z[1], bisector_end[1]])
    return {
        "prompt": prompt, "steps": steps, "answer": answer, "bbox": bbox,
        "points": [{"xy": Y, "label": "Y"}, {"xy": X, "label": "X"}, {"xy": Z, "label": "Z"}],
        "given_lines": [{"p1": Y, "p2": X}, {"p1": Y, "p2": Z}],
        "circle": None, "segment": {"p1": Y, "p2": bisector_end, "dashed": False},
        "dedup_key": f"loci_two_lines:{base_angle}:{sep_deg}",
    }


def _build_loci_construction(rng: random.Random) -> dict:
    branch = rng.choice([_point_locus, _two_points_locus, _two_lines_locus])
    return branch(rng)


def _loci_construction_diagrams(c: dict) -> tuple:
    base = {**c["bbox"], "points": c["points"], "given_lines": c["given_lines"], "show_grid": False}
    question = DiagramSpec(kind="loci_construction", params=dict(base))
    solution = DiagramSpec(kind="loci_construction", params={**base, "circle": c["circle"], "segment": c["segment"]})
    return question, solution


def generate_loci_constructions(tier: Tier, rng: random.Random) -> Question:
    c = _build_loci_construction(rng)
    diagram, solution_diagram = _loci_construction_diagrams(c)
    return Question(
        topic_id="loci_constructions_F",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        solution_steps=tuple(c["steps"]),
        final_answer=c["answer"],
        dedup_key=c["dedup_key"],
        diagram=diagram,
        solution_diagram=solution_diagram,
    )


def generate_modelled_example_loci_constructions(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _build_loci_construction(rng)
    diagram, solution_diagram = _loci_construction_diagrams(c)
    teaching_steps = [
        "A 'locus' is just the set of every point that satisfies a given rule - so the first thing to "
        "work out is what kind of shape that rule traces out.",
        *c["steps"],
        "It helps to picture testing a few points by hand: any point that fits the rule is part of the "
        "locus, any point that does not is outside it - the locus is the boundary between the two.",
    ]
    return ModelledExample(
        topic_id="loci_constructions_F",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        worked_calculation=tuple(c["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=c["answer"],
        diagram=solution_diagram,
    )


# ---------------------------------------------------------------------------
# loci_regions (Higher): a genuinely two-constraint shaded region
# ---------------------------------------------------------------------------

def _in_disk(x: float, y: float, centre: tuple, radius: float) -> bool:
    return (x - centre[0]) ** 2 + (y - centre[1]) ** 2 <= radius ** 2


def _closer_to(x: float, y: float, target: tuple, other: tuple) -> bool:
    d_target = (x - target[0]) ** 2 + (y - target[1]) ** 2
    d_other = (x - other[0]) ** 2 + (y - other[1]) ** 2
    return d_target <= d_other


def _perp_bisector_region(rng: random.Random) -> dict:
    """circle + perpendicular-bisector variant: region within r cm of one
    fixed point AND closer to it than to a second fixed point."""
    while True:
        A = (rng.randint(*_GRID_RANGE), rng.randint(*_GRID_RANGE))
        B = (rng.randint(*_GRID_RANGE), rng.randint(*_GRID_RANGE))
        if A != B and math.hypot(A[0] - B[0], A[1] - B[1]) >= 3:
            break
    anchor_is_A = rng.choice([True, False])
    anchor, other = (A, B) if anchor_is_A else (B, A)
    anchor_label, other_label = ("A", "B") if anchor_is_A else ("B", "A")
    r_cm = rng.randint(3, 6)

    # Independent verification: a boundary-consistency check on each
    # constraint separately (the "answer" here is a region, not a scalar,
    # so there is no single value to re-derive).
    if not _in_disk(anchor[0], anchor[1], anchor, r_cm):
        raise ValueError("loci_regions verification failed: anchor should satisfy its own disk constraint")
    if _in_disk(anchor[0] + r_cm + 0.5, anchor[1], anchor, r_cm):
        raise ValueError("loci_regions verification failed: a point beyond the radius satisfied the disk constraint")
    if not _closer_to(anchor[0], anchor[1], anchor, other):
        raise ValueError("loci_regions verification failed: anchor should be closer to itself than to other")
    if _closer_to(other[0], other[1], anchor, other):
        raise ValueError("loci_regions verification failed: other point should not be closer to anchor")

    mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    dx, dy = B[0] - A[0], B[1] - A[1]
    length = math.hypot(dx, dy)
    ux, uy = -dy / length, dx / length

    # Same perpendicular-bisector-definition check as loci_constructions's
    # two_points branch, applied to this region's half-plane boundary too.
    bisector_sample = (mx + ux, my + uy)
    dA = math.hypot(bisector_sample[0] - A[0], bisector_sample[1] - A[1])
    dB = math.hypot(bisector_sample[0] - B[0], bisector_sample[1] - B[1])
    if abs(dA - dB) > 1e-6:
        raise ValueError("loci_regions verification failed: half-plane boundary not equidistant from A and B")

    bbox = _bbox([A[0], B[0], anchor[0] - r_cm, anchor[0] + r_cm], [A[1], B[1], anchor[1] - r_cm, anchor[1] + r_cm])
    extend = max(bbox["x_max"] - bbox["x_min"], bbox["y_max"] - bbox["y_min"])
    seg_p1 = (mx + ux * extend, my + uy * extend)
    seg_p2 = (mx - ux * extend, my - uy * extend)

    prompt = (
        f"Shade the region containing points that are both within {r_cm} cm of {anchor_label} AND closer "
        f"to {anchor_label} than to {other_label}."
    )
    steps = [
        f"The boundary for 'within {r_cm} cm of {anchor_label}' is a circle, centre {anchor_label}, "
        f"radius {r_cm} cm - the region is inside this circle.",
        f"The boundary for 'closer to {anchor_label} than to {other_label}' is the perpendicular "
        f"bisector of {anchor_label}{other_label} - the region is on the {anchor_label} side of it.",
        "The required region is where these two conditions overlap.",
    ]
    answer = (
        f"The region inside the circle of radius {r_cm} cm centred on {anchor_label}, and on the "
        f"{anchor_label} side of the perpendicular bisector of {anchor_label}{other_label}."
    )
    return {
        "prompt": prompt, "steps": steps, "answer": answer, "bbox": bbox,
        "points": [{"xy": A, "label": "A"}, {"xy": B, "label": "B"}],
        "given_lines": [],
        "boundaries": [
            {"type": "circle", "centre": anchor, "radius": r_cm},
            {"type": "segment", "p1": seg_p1, "p2": seg_p2},
        ],
        "shade_constraints": [
            {"type": "disk", "centre": anchor, "radius": r_cm, "inside": True},
            {"type": "half_plane", "closer_to": anchor, "than": other},
        ],
        "dedup_key": f"loci_region_perp:{A}:{B}:{anchor_label}:{r_cm}",
    }


def _angle_bisector_region(rng: random.Random) -> dict:
    """circle + angle-bisector variant: region within r cm of the vertex of
    two given rays AND closer to one ray than the other."""
    Y = (0.0, 0.0)
    base_angle = rng.randint(0, 359)
    sep_deg = rng.randint(40, 140)
    ray_len = 5.0
    ux1, uy1 = _unit_vector(base_angle)
    ux2, uy2 = _unit_vector(base_angle + sep_deg)
    X = (Y[0] + ray_len * ux1, Y[1] + ray_len * uy1)
    Z = (Y[0] + ray_len * ux2, Y[1] + ray_len * uy2)
    r_cm = rng.choice([2, 3, 4])

    bux, buy = _unit_vector(base_angle + sep_deg / 2)
    bisector_end = (Y[0] + ray_len * 1.1 * bux, Y[1] + ray_len * 1.1 * buy)

    # Independent verification: the bisector ray is equidistant from both
    # rays (the geometric definition of an angle bisector - same check
    # _two_lines_locus uses), and a point actually ON ray YX is strictly
    # closer to line YX (distance ~0) than to line YZ, confirming the
    # "closer to line YX" half of the region is on the correct side.
    d1 = _dist_to_line(bisector_end, Y, X)
    d2 = _dist_to_line(bisector_end, Y, Z)
    if abs(d1 - d2) > 1e-6:
        raise ValueError("loci_regions verification failed: bisector ray not equidistant from both rays")
    p_on_x = (Y[0] + 0.5 * ux1, Y[1] + 0.5 * uy1)
    if _dist_to_line(p_on_x, Y, X) > 1e-6:
        raise ValueError("loci_regions verification failed: point on ray YX should have ~0 distance to it")
    if _dist_to_line(p_on_x, Y, X) >= _dist_to_line(p_on_x, Y, Z):
        raise ValueError("loci_regions verification failed: point on ray YX should be closer to YX than YZ")

    bbox = _bbox(
        [X[0], Y[0], Z[0], bisector_end[0], Y[0] - r_cm, Y[0] + r_cm],
        [X[1], Y[1], Z[1], bisector_end[1], Y[1] - r_cm, Y[1] + r_cm],
    )

    prompt = (
        f"Shade the region containing points that are both within {r_cm} cm of Y AND closer to line YX "
        f"than to line YZ."
    )
    steps = [
        f"The boundary for 'within {r_cm} cm of Y' is a circle, centre Y, radius {r_cm} cm - the region "
        "is inside this circle.",
        "The boundary for 'closer to line YX than to line YZ' is the bisector of angle XYZ - the region "
        "is on the X side of it.",
        "The required region is where these two conditions overlap.",
    ]
    answer = (
        f"The region inside the circle of radius {r_cm} cm centred on Y, and on the X side of the "
        "bisector of angle XYZ."
    )
    return {
        "prompt": prompt, "steps": steps, "answer": answer, "bbox": bbox,
        "points": [{"xy": Y, "label": "Y"}, {"xy": X, "label": "X"}, {"xy": Z, "label": "Z"}],
        "given_lines": [{"p1": Y, "p2": X}, {"p1": Y, "p2": Z}],
        "boundaries": [
            {"type": "circle", "centre": Y, "radius": r_cm},
            {"type": "segment", "p1": Y, "p2": bisector_end},
        ],
        "shade_constraints": [
            {"type": "disk", "centre": Y, "radius": r_cm, "inside": True},
            {"type": "closer_to_line", "line_a": (Y, X), "line_b": (Y, Z)},
        ],
        "dedup_key": f"loci_region_angle:{base_angle}:{sep_deg}:{r_cm}",
    }


def _build_loci_region(rng: random.Random) -> dict:
    branch = rng.choice([_perp_bisector_region, _angle_bisector_region])
    return branch(rng)


def _loci_region_diagrams(c: dict) -> tuple:
    # The boundaries (the circle and the perpendicular/angle bisector) are
    # themselves part of what the student must construct, not given
    # information - so only the fixed reference points appear on the
    # question page; the solution page reveals the constructed boundaries
    # and the shaded region together.
    base = {**c["bbox"], "points": c["points"], "given_lines": c["given_lines"]}
    question = DiagramSpec(kind="loci_region", params=dict(base))
    solution = DiagramSpec(
        kind="loci_region",
        params={**base, "boundaries": c["boundaries"], "shade_constraints": c["shade_constraints"]},
    )
    return question, solution


def generate_loci_regions(tier: Tier, rng: random.Random) -> Question:
    c = _build_loci_region(rng)
    diagram, solution_diagram = _loci_region_diagrams(c)
    return Question(
        topic_id="loci_regions_H",
        tier=Tier.HIGHER,
        prompt=c["prompt"],
        solution_steps=tuple(c["steps"]),
        final_answer=c["answer"],
        dedup_key=c["dedup_key"],
        diagram=diagram,
        solution_diagram=solution_diagram,
    )


def generate_modelled_example_loci_regions(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _build_loci_region(rng)
    diagram, solution_diagram = _loci_region_diagrams(c)
    teaching_steps = [
        "A region satisfying two rules at once is just the overlap of the two separate loci - draw each "
        "boundary on its own first, then shade wherever both conditions are true together.",
        *c["steps"],
        "A quick way to check a shaded region: pick any point clearly inside it and confirm it really "
        "does satisfy both original conditions, then pick a point just outside and confirm it fails at "
        "least one.",
    ]
    return ModelledExample(
        topic_id="loci_regions_H",
        tier=Tier.HIGHER,
        prompt=c["prompt"],
        worked_calculation=tuple(c["steps"]),
        teaching_steps=tuple(teaching_steps),
        final_answer=c["answer"],
        diagram=solution_diagram,
    )


TOPIC_LOCI_CONSTRUCTIONS = TopicDefinition(
    id="loci_constructions_F",
    display_name="Loci",
    description="Describe the locus of points satisfying a given distance rule from a point, two points, or two lines.",
    generate=generate_loci_constructions,
    section=SECTION,
    group=GROUP_LOCI,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_loci_constructions,
)

TOPIC_LOCI_REGIONS = TopicDefinition(
    id="loci_regions_H",
    display_name="Loci Regions",
    description="Shade the region of points satisfying two distance rules at once.",
    generate=generate_loci_regions,
    section=SECTION,
    group=GROUP_LOCI,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_loci_regions,
)
