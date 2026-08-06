"""Congruent triangle proof: classic GCSE "prove that these two triangles are
congruent" questions (SSS/SAS/ASA/RHS). Like algebraic_proof.py, these are
fixed narrative arguments rather than something to re-randomise per instance -
a proof's claim can't be meaningfully varied like arithmetic can - so this
uses the same curated-template-bank pattern: `TopicDefinition.question_count`
is set to the template bank size, not the usual default of 20.

Higher gets the full written proof; Foundation gets a shorter "state which
criterion applies" version of the same template bank (not a separate bank),
since the underlying geometric fact is the same either way - only how much of
the justification the student has to write out differs.
"""

import math
import random
from typing import Callable, NamedTuple

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Congruence Proof"

_CRITERION_FULL_NAME = {
    "SSS": "Side-Side-Side (SSS)",
    "SAS": "Side-Angle-Side (SAS)",
    "ASA": "Angle-Side-Angle (ASA)",
    "RHS": "Right angle-Hypotenuse-Side (RHS)",
}


def _dist(P: tuple, Q: tuple) -> float:
    return math.hypot(Q[0] - P[0], Q[1] - P[1])


def _verify_congruent_triangles(tri1: tuple, tri2: tuple, tol: float = 1e-6) -> None:
    """tri1/tri2 each a 3-tuple of 2D points, in corresponding vertex order.
    Confirms all 3 corresponding side lengths match - the actual geometric
    consequence of any of SSS/SAS/ASA/RHS - computed from concrete
    coordinates built to satisfy the template's stated givens, rather than
    re-trusting the criterion label."""
    pairs1 = [(tri1[0], tri1[1]), (tri1[1], tri1[2]), (tri1[2], tri1[0])]
    pairs2 = [(tri2[0], tri2[1]), (tri2[1], tri2[2]), (tri2[2], tri2[0])]
    for (a1, b1), (a2, b2) in zip(pairs1, pairs2):
        if abs(_dist(a1, b1) - _dist(a2, b2)) > tol:
            raise ValueError("congruent_triangle_proof: side lengths do not match")


def _point_from_two_distances(A: tuple, C: tuple, dA: float, dC: float, side: float = 1.0) -> tuple:
    """The point P with |PA| = dA, |PC| = dC, on the given side of line AC."""
    ax, ay = A
    cx, cy = C
    d = math.hypot(cx - ax, cy - ay)
    a = (d * d + dA * dA - dC * dC) / (2 * d)
    h = math.sqrt(max(dA * dA - a * a, 0.0))
    px, py = ax + a * (cx - ax) / d, ay + a * (cy - ay) / d
    perp = (-(cy - ay) / d, (cx - ax) / d)
    return (px + side * h * perp[0], py + side * h * perp[1])


def _third_vertex_asa(P: tuple, Q: tuple, angle_at_p_deg: float, angle_at_q_deg: float, side: float = 1.0) -> tuple:
    """The point R such that in triangle PQR, angle QPR = angle_at_p_deg and
    angle PQR = angle_at_q_deg, with R on the given side of line PQ - placed
    via the law of sines rather than a separate ray-intersection solver."""
    px, py = P
    qx, qy = Q
    pq = math.hypot(qx - px, qy - py)
    angle_r = 180 - angle_at_p_deg - angle_at_q_deg
    pr = pq * math.sin(math.radians(angle_at_q_deg)) / math.sin(math.radians(angle_r))
    base_angle = math.degrees(math.atan2(qy - py, qx - px))
    theta = math.radians(base_angle + side * angle_at_p_deg)
    return (px + pr * math.cos(theta), py + pr * math.sin(theta))


class _CongruenceTemplate(NamedTuple):
    id: str
    scenario: str
    given_facts: tuple[str, ...]
    criterion: str
    proof_conclusion: str
    diagram_params: dict
    verify: Callable[[], None]


def _t(id, scenario, given_facts, criterion, proof_conclusion, diagram_params, verify):
    return _CongruenceTemplate(id, scenario, tuple(given_facts), criterion, proof_conclusion, diagram_params, verify)


# ---------------------------------------------------------------------------
# Per-template verification: build one concrete coordinate instance
# satisfying the template's stated givens, then confirm all 3 corresponding
# sides match - an authoring-error trap (these are fixed narrative proofs, no
# per-instance random numbers), mirroring algebraic_proof.py's verify().
# ---------------------------------------------------------------------------


def _verify_shared_side_sss() -> None:
    A, C = (0.0, 0.0), (6.0, 0.0)
    B = _point_from_two_distances(A, C, 5, 4, 1)
    D = _point_from_two_distances(A, C, 5, 4, -1)
    _verify_congruent_triangles((A, B, C), (A, D, C))


def _verify_kite_diagonal_sss() -> None:
    A, C = (0.0, 0.0), (8.0, 0.0)
    B = _point_from_two_distances(A, C, 5, 7, 1)
    D = _point_from_two_distances(A, C, 5, 7, -1)
    _verify_congruent_triangles((A, B, C), (A, D, C))


def _verify_rhombus_diagonal_sss() -> None:
    A, C = (0.0, 0.0), (7.0, 0.0)
    B = _point_from_two_distances(A, C, 6, 6, 1)
    D = _point_from_two_distances(A, C, 6, 6, -1)
    _verify_congruent_triangles((A, B, C), (A, D, C))


def _verify_isosceles_median_sss() -> None:
    B, M, C = (-4.0, 0.0), (0.0, 0.0), (4.0, 0.0)
    A = (0.0, math.sqrt(6**2 - 4**2))
    _verify_congruent_triangles((A, B, M), (A, C, M))


def _verify_equal_chords_sss() -> None:
    O = (0.0, 0.0)
    A, B = (-3.0, 4.0), (3.0, 4.0)
    C, D = (-3.0, -4.0), (3.0, -4.0)
    _verify_congruent_triangles((O, A, B), (O, C, D))


def _verify_parallelogram_diagonal_sss() -> None:
    A, C = (0.0, 0.0), (9.0, 0.0)
    B = _point_from_two_distances(A, C, 5, 7, 1)
    D = _point_from_two_distances(A, C, 7, 5, -1)
    _verify_congruent_triangles((A, B, C), (C, D, A))


def _verify_parallelogram_diagonal_asa() -> None:
    A, C = (0.0, 0.0), (8.0, 0.0)
    B = _third_vertex_asa(A, C, 50, 70, 1)
    D = _third_vertex_asa(C, A, 50, 70, 1)
    _verify_congruent_triangles((A, B, C), (C, D, A))


def _verify_parallelogram_diagonals_bisect_asa() -> None:
    A, B, C, D = (0.0, 0.0), (6.0, 0.0), (8.0, 4.0), (2.0, 4.0)
    t = 0.5  # intersection of AC and BD, both parametrised from their first endpoint
    O = (A[0] + t * (C[0] - A[0]), A[1] + t * (C[1] - A[1]))
    _verify_congruent_triangles((O, A, B), (O, C, D))


def _verify_rectangle_diagonals_sas() -> None:
    A, B, C, D = (0.0, 0.0), (6.0, 0.0), (6.0, 4.0), (0.0, 4.0)
    O = (3.0, 2.0)
    _verify_congruent_triangles((A, O, B), (C, O, D))


def _verify_vertically_opposite_sas() -> None:
    O = (0.0, 0.0)
    A, C = (-4.0, 0.0), (4.0, 0.0)
    direction = (math.cos(math.radians(70)), math.sin(math.radians(70)))
    B = (5 * direction[0], 5 * direction[1])
    D = (-5 * direction[0], -5 * direction[1])
    _verify_congruent_triangles((A, O, B), (C, O, D))


def _verify_isosceles_bisector_sas() -> None:
    B, D, C = (-4.0, 0.0), (0.0, 0.0), (4.0, 0.0)
    A = (0.0, 5.0)
    _verify_congruent_triangles((A, B, D), (A, C, D))


def _verify_isosceles_trapezium_diagonal_sas() -> None:
    A, B = (0.0, 0.0), (6.0, 0.0)
    D = (A[0] + 5 * math.cos(math.radians(60)), A[1] + 5 * math.sin(math.radians(60)))
    C = (B[0] + 5 * math.cos(math.radians(120)), B[1] + 5 * math.sin(math.radians(120)))
    _verify_congruent_triangles((A, B, D), (B, A, C))


def _verify_square_diagonal_sas() -> None:
    A, B, C, D = (0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0)
    _verify_congruent_triangles((A, B, C), (A, D, C))


def _verify_perpendicular_bisector_point_sas() -> None:
    A, M, B = (-3.0, 0.0), (0.0, 0.0), (3.0, 0.0)
    P = (0.0, 7.0)
    _verify_congruent_triangles((A, M, P), (B, M, P))


def _verify_isosceles_perpendicular_bisector_rhs() -> None:
    B, D, C = (-4.0, 0.0), (0.0, 0.0), (4.0, 0.0)
    A = (0.0, 5.0)
    _verify_congruent_triangles((A, B, D), (A, C, D))


def _verify_right_triangles_shared_hypotenuse_rhs() -> None:
    A, B = (0.0, 0.0), (10.0, 0.0)
    C = _point_from_two_distances(A, B, 6, 8, 1)
    D = _point_from_two_distances(A, B, 6, 8, -1)
    _verify_congruent_triangles((A, C, B), (A, D, B))


def _verify_ladder_wall_rhs() -> None:
    T, W = (0.0, 8.0), (0.0, 0.0)
    F1, F2 = (6.0, 0.0), (-6.0, 0.0)
    _verify_congruent_triangles((T, W, F1), (T, W, F2))


def _verify_right_angle_shared_leg_asa() -> None:
    A, B = (0.0, 0.0), (0.0, -5.0)
    C = _third_vertex_asa(A, B, 40, 90, 1)
    D = _third_vertex_asa(A, B, 40, 90, -1)
    _verify_congruent_triangles((A, B, C), (A, B, D))


# ---------------------------------------------------------------------------
# Template bank
# ---------------------------------------------------------------------------

TEMPLATES: list[_CongruenceTemplate] = [
    _t(
        "shared_side_sss",
        "Triangles ABC and ADC share side AC, with AB = AD and BC = DC.",
        ("AB = AD (given)", "BC = DC (given)", "AC is common to both triangles"),
        "SSS",
        "Since all three corresponding sides are equal, triangles ABC and ADC are congruent.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("A", "D", "C"),
            "ticks_1": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "ticks_2": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "arcs_1": [], "arcs_2": [],
            "note": "AC is common to both triangles.",
        },
        _verify_shared_side_sss,
    ),
    _t(
        "kite_diagonal_sss",
        "ABCD is a kite with AB = AD and CB = CD. AC is a diagonal of the kite.",
        ("AB = AD (given, adjacent sides of the kite)", "CB = CD (given, adjacent sides of the kite)", "AC is common to both triangles"),
        "SSS",
        "Since all three corresponding sides are equal, triangles ABC and ADC are congruent - this is why a kite's diagonal AC is a line of symmetry.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("A", "D", "C"),
            "ticks_1": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "ticks_2": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "arcs_1": [], "arcs_2": [],
            "note": "AC is common to both triangles.",
        },
        _verify_kite_diagonal_sss,
    ),
    _t(
        "rhombus_diagonal_sss",
        "ABCD is a rhombus (all four sides equal length), and AC is one of its diagonals.",
        ("AB = AD (sides of the rhombus)", "CB = CD (sides of the rhombus)", "AC is common to both triangles"),
        "SSS",
        "Since all three corresponding sides are equal, triangles ABC and ADC are congruent.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("A", "D", "C"),
            "ticks_1": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "ticks_2": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "arcs_1": [], "arcs_2": [],
            "note": "AC is common to both triangles.",
        },
        _verify_rhombus_diagonal_sss,
    ),
    _t(
        "isosceles_median_sss",
        "Triangle ABC is isosceles with AB = AC. M is the midpoint of BC, and AM is drawn.",
        ("AB = AC (given)", "BM = CM (M is the midpoint of BC)", "AM is common to both triangles"),
        "SSS",
        "Since all three corresponding sides are equal, triangles ABM and ACM are congruent - this is why the median AM from the apex of an isosceles triangle is also its line of symmetry.",
        {
            "labels_1": ("A", "B", "M"), "labels_2": ("A", "C", "M"),
            "ticks_1": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "ticks_2": [(0, 1, 2), (1, 2, 3), (0, 2, 1)],
            "arcs_1": [], "arcs_2": [],
            "note": "AM is common to both triangles.",
        },
        _verify_isosceles_median_sss,
    ),
    _t(
        "equal_chords_sss",
        "O is the centre of a circle. AB and CD are two chords of the circle, with AB = CD.",
        ("OA = OC (radii of the circle)", "AB = CD (given, equal chords)", "OB = OD (radii of the circle)"),
        "SSS",
        "Since all three corresponding sides are equal, triangles OAB and OCD are congruent.",
        {
            "labels_1": ("O", "A", "B"), "labels_2": ("O", "C", "D"),
            "ticks_1": [(0, 1, 1), (1, 2, 2), (2, 0, 3)],
            "ticks_2": [(0, 1, 1), (1, 2, 2), (2, 0, 3)],
            "arcs_1": [], "arcs_2": [],
        },
        _verify_equal_chords_sss,
    ),
    _t(
        "parallelogram_diagonal_sss",
        "ABCD is a parallelogram, and AC is one of its diagonals.",
        ("AB = CD (opposite sides of a parallelogram)", "BC = DA (opposite sides of a parallelogram)", "AC is common to both triangles"),
        "SSS",
        "Since all three corresponding sides are equal, triangles ABC and CDA are congruent.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("C", "D", "A"),
            "ticks_1": [(0, 1, 2), (1, 2, 3), (2, 0, 1)],
            "ticks_2": [(0, 1, 2), (1, 2, 3), (2, 0, 1)],
            "arcs_1": [], "arcs_2": [],
            "note": "AC is common to both triangles.",
        },
        _verify_parallelogram_diagonal_sss,
    ),
    _t(
        "parallelogram_diagonal_asa",
        "ABCD is a parallelogram with AB parallel to DC, and AC is one of its diagonals.",
        ("angle BAC = angle DCA (alternate angles, AB parallel to DC)", "AC is common to both triangles", "angle BCA = angle DAC (alternate angles, BC parallel to AD)"),
        "ASA",
        "Since two angles and the included side match, triangles ABC and CDA are congruent.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("C", "D", "A"),
            "ticks_1": [(2, 0, 1)], "ticks_2": [(2, 0, 1)],
            "arcs_1": [(0, 1), (2, 2)], "arcs_2": [(0, 1), (2, 2)],
            "note": "AC is common to both triangles.",
        },
        _verify_parallelogram_diagonal_asa,
    ),
    _t(
        "parallelogram_diagonals_bisect_asa",
        "ABCD is a parallelogram with AB parallel to DC. Its diagonals AC and BD cross at O.",
        ("angle OAB = angle OCD (alternate angles, AB parallel to DC)", "AB = CD (opposite sides of a parallelogram)", "angle OBA = angle ODC (alternate angles, AB parallel to DC)"),
        "ASA",
        "Since triangles OAB and OCD are congruent, OA = OC and OB = OD - the diagonals of a parallelogram bisect each other.",
        {
            "labels_1": ("A", "B", "O"), "labels_2": ("C", "D", "O"),
            "ticks_1": [(0, 1, 1)], "ticks_2": [(0, 1, 1)],
            "arcs_1": [(0, 1), (1, 2)], "arcs_2": [(0, 1), (1, 2)],
        },
        _verify_parallelogram_diagonals_bisect_asa,
    ),
    _t(
        "rectangle_diagonals_sas",
        "ABCD is a rectangle. Its diagonals AC and BD cross at O.",
        ("AO = CO (diagonals of a rectangle bisect each other and are equal)", "angle AOB = angle COD (vertically opposite angles)", "BO = DO (diagonals of a rectangle bisect each other and are equal)"),
        "SAS",
        "Since two sides and the included angle match, triangles AOB and COD are congruent.",
        {
            "labels_1": ("A", "O", "B"), "labels_2": ("C", "O", "D"),
            "ticks_1": [(0, 1, 1), (1, 2, 2)], "ticks_2": [(0, 1, 1), (1, 2, 2)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
        },
        _verify_rectangle_diagonals_sas,
    ),
    _t(
        "vertically_opposite_sas",
        "Lines AC and BD cross at point O, with OA = OC and OB = OD.",
        ("OA = OC (given)", "angle AOB = angle COD (vertically opposite angles)", "OB = OD (given)"),
        "SAS",
        "Since two sides and the included angle match, triangles AOB and COD are congruent.",
        {
            "labels_1": ("A", "O", "B"), "labels_2": ("C", "O", "D"),
            "ticks_1": [(0, 1, 1), (1, 2, 2)], "ticks_2": [(0, 1, 1), (1, 2, 2)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
        },
        _verify_vertically_opposite_sas,
    ),
    _t(
        "isosceles_bisector_sas",
        "Triangle ABC is isosceles with AB = AC. AD bisects angle BAC, meeting BC at D.",
        ("AB = AC (given)", "angle BAD = angle CAD (AD bisects angle BAC)", "AD is common to both triangles"),
        "SAS",
        "Since two sides and the included angle match, triangles ABD and ACD are congruent.",
        {
            "labels_1": ("A", "B", "D"), "labels_2": ("A", "C", "D"),
            "ticks_1": [(0, 1, 2), (0, 2, 1)], "ticks_2": [(0, 1, 2), (0, 2, 1)],
            "arcs_1": [(0, 1)], "arcs_2": [(0, 1)],
            "note": "AD is common to both triangles.",
        },
        _verify_isosceles_bisector_sas,
    ),
    _t(
        "isosceles_trapezium_diagonal_sas",
        "ABCD is an isosceles trapezium with AB parallel to DC and AD = BC. AC and BD are its diagonals.",
        ("AB is common to both triangles", "angle DAB = angle CBA (base angles of an isosceles trapezium are equal)", "AD = BC (given, the equal sides of the trapezium)"),
        "SAS",
        "Since two sides and the included angle match, triangles ABD and BAC are congruent - so AC = BD, the diagonals of an isosceles trapezium are equal.",
        {
            "labels_1": ("A", "B", "D"), "labels_2": ("B", "A", "C"),
            "ticks_1": [(0, 1, 1), (0, 2, 2)], "ticks_2": [(0, 1, 1), (0, 2, 2)],
            "arcs_1": [(0, 1)], "arcs_2": [(0, 1)],
            "note": "AB is common to both triangles.",
        },
        _verify_isosceles_trapezium_diagonal_sas,
    ),
    _t(
        "square_diagonal_sas",
        "ABCD is a square, and AC is one of its diagonals.",
        ("AB = AD (sides of the square)", "angle ABC = angle ADC = 90° (angles of the square)", "BC = DC (sides of the square)"),
        "SAS",
        "Since two sides and the included angle match, triangles ABC and ADC are congruent.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("A", "D", "C"),
            "ticks_1": [(0, 1, 2), (1, 2, 3)], "ticks_2": [(0, 1, 2), (1, 2, 3)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
            "note": "AC is the shared diagonal of the square.",
        },
        _verify_square_diagonal_sas,
    ),
    _t(
        "perpendicular_bisector_point_sas",
        "M is the midpoint of AB. P is a point such that PM is perpendicular to AB.",
        ("AM = BM (M is the midpoint of AB)", "angle AMP = angle BMP = 90° (PM is perpendicular to AB)", "PM is common to both triangles"),
        "SAS",
        "Since two sides and the included angle match, triangles AMP and BMP are congruent - so PA = PB, meaning P is equidistant from A and B.",
        {
            "labels_1": ("A", "M", "P"), "labels_2": ("B", "M", "P"),
            "ticks_1": [(0, 1, 2), (1, 2, 1)], "ticks_2": [(0, 1, 2), (1, 2, 1)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
            "note": "MP is common to both triangles.",
        },
        _verify_perpendicular_bisector_point_sas,
    ),
    _t(
        "isosceles_perpendicular_bisector_rhs",
        "Triangle ABC is isosceles with AB = AC. D is the foot of the perpendicular from A to BC.",
        ("angle ADB = angle ADC = 90° (AD is perpendicular to BC)", "AB = AC (given, the hypotenuse of each right triangle)", "AD is common to both triangles"),
        "RHS",
        "Since the hypotenuse and a common side match, with the right angle at D, triangles ABD and ACD are congruent - so BD = CD, meaning D is the midpoint of BC.",
        {
            "labels_1": ("A", "B", "D"), "labels_2": ("A", "C", "D"),
            "ticks_1": [(0, 1, 1), (0, 2, 2)], "ticks_2": [(0, 1, 1), (0, 2, 2)],
            "arcs_1": [(2, 1)], "arcs_2": [(2, 1)],
            "note": "AD is common to both triangles.",
        },
        _verify_isosceles_perpendicular_bisector_rhs,
    ),
    _t(
        "right_triangles_shared_hypotenuse_rhs",
        "Triangles ABC and ABD are both right-angled (at C and at D respectively) and share hypotenuse AB, with AC = AD.",
        ("angle ACB = angle ADB = 90° (given)", "AB is the common hypotenuse", "AC = AD (given)"),
        "RHS",
        "Since the hypotenuse and a given side match, with the right angle at C and D, triangles ABC and ABD are congruent.",
        {
            "labels_1": ("A", "C", "B"), "labels_2": ("A", "D", "B"),
            "ticks_1": [(0, 2, 1), (0, 1, 2)], "ticks_2": [(0, 2, 1), (0, 1, 2)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
            "note": "AB is the common hypotenuse.",
        },
        _verify_right_triangles_shared_hypotenuse_rhs,
    ),
    _t(
        "ladder_wall_rhs",
        "Two ladders of equal length lean against a vertical wall, both touching it at the same point T. "
        "Their feet, F1 and F2, rest on the (horizontal) ground on either side of the foot of the wall, W.",
        ("angle TWF1 = angle TWF2 = 90° (both ladders meet the ground at right angles to the wall)", "TW is common to both triangles (the height on the wall)", "TF1 = TF2 (given, both ladders have the same length)"),
        "RHS",
        "Since the hypotenuse and a common side match, with the right angle at W, triangles TWF1 and TWF2 are congruent - so WF1 = WF2, meaning the two ladders' feet are equally far from the wall.",
        {
            "labels_1": ("T", "W", "F1"), "labels_2": ("T", "W", "F2"),
            "ticks_1": [(0, 1, 1), (2, 0, 2)], "ticks_2": [(0, 1, 1), (2, 0, 2)],
            "arcs_1": [(1, 1)], "arcs_2": [(1, 1)],
            "note": "TW is common to both triangles (the height on the wall).",
        },
        _verify_ladder_wall_rhs,
    ),
    _t(
        "right_angle_shared_leg_asa",
        "Triangles ABC and ABD both have a right angle at B, and share side AB, with angle BAC = angle BAD.",
        ("angle BAC = angle BAD (given)", "AB is common to both triangles", "angle ABC = angle ABD = 90° (given)"),
        "ASA",
        "Since two angles and the included side match, triangles ABC and ABD are congruent - so BC = BD.",
        {
            "labels_1": ("A", "B", "C"), "labels_2": ("A", "B", "D"),
            "ticks_1": [(0, 1, 1)], "ticks_2": [(0, 1, 1)],
            "arcs_1": [(0, 1), (1, 2)], "arcs_2": [(0, 1), (1, 2)],
            "note": "AB is common to both triangles.",
        },
        _verify_right_angle_shared_leg_asa,
    ),
]

_ids = [t.id for t in TEMPLATES]
if len(_ids) != len(set(_ids)):
    raise ValueError("congruent_triangle_proof: duplicate template id found in TEMPLATES")

_MC_CRITERIA = ["SSS", "SAS", "ASA", "RHS"]
_MC_LETTERS = ["A", "B", "C", "D"]


def _shuffled_mc_options(rng: random.Random, correct: str) -> tuple[str, str]:
    """A lettered multiple-choice line ("A) SSS  B) ASA  C) SAS  D) RHS"),
    shuffled per question, plus the matching answer string ("C) SAS")."""
    order = _MC_CRITERIA[:]
    rng.shuffle(order)
    options_line = "  ".join(f"{letter}) {crit}" for letter, crit in zip(_MC_LETTERS, order))
    answer_letter = _MC_LETTERS[order.index(correct)]
    return options_line, f"{answer_letter}) {correct}"


def generate_congruent_triangle_proof_higher(tier: Tier, rng: random.Random) -> Question:
    template = rng.choice(TEMPLATES)
    template.verify()

    steps = list(template.given_facts) + [
        f"By {_CRITERION_FULL_NAME[template.criterion]}, the triangles are congruent.",
        template.proof_conclusion,
    ]
    return Question(
        topic_id="congruent_triangle_proof",
        tier=Tier.HIGHER,
        prompt=f"{template.scenario} Prove that the two triangles are congruent.",
        solution_steps=tuple(steps),
        final_answer=f"Triangles are congruent ({template.criterion}).",
        dedup_key=f"congruence:{template.id}",
        diagram=DiagramSpec(kind="two_triangle_congruence", params=template.diagram_params),
    )


def generate_modelled_example_congruent_triangle_proof_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    template = rng.choice(TEMPLATES)
    template.verify()

    teaching_steps = [
        "To prove two triangles are congruent, you need to show one of four fixed combinations of "
        "matching sides/angles holds: SSS (all three sides), SAS (two sides and the angle between "
        "them), ASA (two angles and the side between them), or RHS (right angle, hypotenuse, and "
        "one other side) - matching any other combination (like two sides and a non-included "
        "angle) does NOT guarantee congruence.",
        f"Here, the given facts are: {'; '.join(template.given_facts)}.",
        f"This matches the {_CRITERION_FULL_NAME[template.criterion]} criterion exactly, so the "
        "two triangles must be congruent.",
        template.proof_conclusion,
    ]
    worked_calculation = list(template.given_facts) + [
        f"{_CRITERION_FULL_NAME[template.criterion]} -> triangles congruent",
    ]
    return ModelledExample(
        topic_id="congruent_triangle_proof",
        tier=Tier.HIGHER,
        prompt=f"{template.scenario} Prove that the two triangles are congruent.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Triangles are congruent ({template.criterion}).",
        diagram=DiagramSpec(kind="two_triangle_congruence", params=template.diagram_params),
    )


def generate_congruent_triangle_proof_foundation(tier: Tier, rng: random.Random) -> Question:
    template = rng.choice(TEMPLATES)
    template.verify()
    options_line, answer = _shuffled_mc_options(rng, template.criterion)

    steps = list(template.given_facts) + [
        f"These facts match the {_CRITERION_FULL_NAME[template.criterion]} congruence criterion.",
    ]
    return Question(
        topic_id="congruent_triangle_proof_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"{template.scenario} Which congruence criterion proves that the two triangles are "
            f"congruent? {options_line}"
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"congruence_f:{template.id}",
        diagram=DiagramSpec(kind="two_triangle_congruence", params=template.diagram_params),
    )


def generate_modelled_example_congruent_triangle_proof_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    template = rng.choice(TEMPLATES)
    template.verify()
    options_line, answer = _shuffled_mc_options(rng, template.criterion)

    teaching_steps = [
        "There are four combinations of matching sides/angles that guarantee two triangles are "
        "congruent: SSS (all three sides), SAS (two sides and the angle between them), ASA (two "
        "angles and the side between them), and RHS (right angle, hypotenuse, one other side).",
        f"Here, the given facts are: {'; '.join(template.given_facts)}.",
        f"Checking which combination this matches: it's exactly {_CRITERION_FULL_NAME[template.criterion]}.",
    ]
    worked_calculation = list(template.given_facts) + [
        f"Criterion: {template.criterion}",
    ]
    return ModelledExample(
        topic_id="congruent_triangle_proof_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"{template.scenario} Which congruence criterion proves that the two triangles are "
            f"congruent? {options_line}"
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(kind="two_triangle_congruence", params=template.diagram_params),
    )


TOPIC_CONGRUENT_TRIANGLE_PROOF = TopicDefinition(
    id="congruent_triangle_proof",
    display_name="Congruent Triangle Proof",
    description="Prove that two triangles are congruent, citing SSS, SAS, ASA or RHS.",
    generate=generate_congruent_triangle_proof_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    question_count=len(TEMPLATES),
    generate_modelled_example=generate_modelled_example_congruent_triangle_proof_higher,
)

TOPIC_CONGRUENT_TRIANGLE_PROOF_FOUNDATION = TopicDefinition(
    id="congruent_triangle_proof_foundation",
    display_name="Congruent Triangle Proof (Foundation)",
    description="State which congruence criterion (SSS, SAS, ASA or RHS) proves two triangles are congruent.",
    generate=generate_congruent_triangle_proof_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=len(TEMPLATES),
    generate_modelled_example=generate_modelled_example_congruent_triangle_proof_foundation,
)
