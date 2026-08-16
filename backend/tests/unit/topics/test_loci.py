import random

from app.core.models import Tier
from app.topics import loci

TRIALS = 300

GENERATORS = [
    (loci.generate_loci_constructions, Tier.FOUNDATION, "loci_construction"),
    (loci.generate_loci_regions, Tier.HIGHER, "loci_region"),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier, kind in GENERATORS:
        rng = random.Random(1000)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.solution_diagram is not None
            assert q.diagram.kind == kind
            assert q.solution_diagram.kind == kind


def test_question_diagram_never_leaks_the_answer_geometry():
    """The blank question-page diagram must never carry the constructed
    locus/region - only the solution-page one may. loci_constructions uses
    either 'circle' or 'segment' depending on which branch was picked (the
    other stays None); loci_regions uses 'shade_constraints'."""
    rng = random.Random(1001)
    for _ in range(TRIALS):
        q = loci.generate_loci_constructions(Tier.FOUNDATION, rng)
        assert "circle" not in q.diagram.params
        assert "segment" not in q.diagram.params
        assert q.solution_diagram.params.get("circle") or q.solution_diagram.params.get("segment")

    rng = random.Random(1005)
    for _ in range(TRIALS):
        q = loci.generate_loci_regions(Tier.HIGHER, rng)
        assert "shade_constraints" not in q.diagram.params
        # The boundaries (the circle and the perpendicular/angle bisector)
        # are themselves part of what the student must construct - only the
        # fixed reference points/given lines may appear on the question page.
        assert "boundaries" not in q.diagram.params
        assert q.solution_diagram.params.get("shade_constraints")
        assert q.solution_diagram.params.get("boundaries")


def test_loci_regions_covers_both_perpendicular_and_angle_bisector_variants():
    rng = random.Random(1006)
    branches = {q.dedup_key.split(":")[0] for q in (
        loci.generate_loci_regions(Tier.HIGHER, rng) for _ in range(TRIALS)
    )}
    assert branches == {"loci_region_perp", "loci_region_angle"}


def test_dedup_keys_vary_widely():
    for generate, tier, _kind in GENERATORS:
        rng = random.Random(1002)
        keys = {generate(tier, rng).dedup_key for _ in range(TRIALS)}
        assert len(keys) > TRIALS * 0.9


def test_loci_constructions_covers_all_three_branches():
    rng = random.Random(1003)
    branches = {q.dedup_key.split(":")[0] for q in (
        loci.generate_loci_constructions(Tier.FOUNDATION, rng) for _ in range(TRIALS)
    )}
    assert branches == {"loci_point", "loci_two_points", "loci_two_lines"}


def test_topic_definitions_have_expected_metadata():
    topics = [loci.TOPIC_LOCI_CONSTRUCTIONS, loci.TOPIC_LOCI_REGIONS]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Loci"
        assert t.generate_modelled_example is not None
    assert loci.TOPIC_LOCI_CONSTRUCTIONS.fixed_tier == Tier.FOUNDATION
    assert loci.TOPIC_LOCI_REGIONS.fixed_tier == Tier.HIGHER


MODELLED_GENERATORS = [
    (loci.generate_modelled_example_loci_constructions, Tier.FOUNDATION, "loci_constructions_F"),
    (loci.generate_modelled_example_loci_regions, Tier.HIGHER, "loci_regions_H"),
]


def test_modelled_examples_are_valid():
    for generate, tier, topic_id in MODELLED_GENERATORS:
        rng = random.Random(1004)
        for _ in range(TRIALS):
            ex = generate(tier, rng)
            assert ex.topic_id == topic_id
            assert ex.tier == tier
            assert ex.prompt
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3
            assert ex.final_answer
            assert ex.diagram is not None


# ---------------------------------------------------------------------------
# Direct tests of loci_regions's constraint-evaluation helpers, with known
# points, rather than only exercising them indirectly via generate().
# ---------------------------------------------------------------------------

def test_in_disk_boundary_cases():
    centre = (0, 0)
    assert loci._in_disk(0, 0, centre, 5)
    assert loci._in_disk(5, 0, centre, 5)
    assert loci._in_disk(3, 4, centre, 5)
    assert not loci._in_disk(5.1, 0, centre, 5)
    assert not loci._in_disk(4, 4, centre, 5)


def test_closer_to_known_points():
    A, B = (-2, 0), (2, 0)
    assert loci._closer_to(-1, 0, A, B)
    assert not loci._closer_to(1, 0, A, B)
    assert loci._closer_to(0, 0, A, B)  # equidistant -> boundary counts as satisfying
    assert loci._closer_to(A[0], A[1], A, B)
    assert not loci._closer_to(B[0], B[1], A, B)
