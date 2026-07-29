import random

from app.core.models import Tier
from app.topics import plans_elevations

TRIALS = 300

GENERATORS = [
    (plans_elevations.generate_plans_and_elevations, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(1100)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind in ("cuboid", "triangular_prism")
            assert q.solution_diagram is not None
            assert q.solution_diagram.kind == "plans_and_elevations"


def test_both_solid_shapes_are_generated():
    rng = random.Random(1101)
    shapes = {plans_elevations.generate_plans_and_elevations(Tier.FOUNDATION, rng).solution_diagram.params["shape"]
              for _ in range(TRIALS)}
    assert shapes == {"cuboid", "triangular_prism"}


def test_cuboid_views_share_the_correct_dimensions():
    # The front/plan views must share the length; the front/side views must
    # share the height - the defining geometric property of an orthographic
    # plans-and-elevations layout.
    rng = random.Random(1102)
    for _ in range(TRIALS):
        q = plans_elevations.generate_plans_and_elevations(Tier.FOUNDATION, rng)
        p = q.solution_diagram.params
        if p["shape"] != "cuboid":
            continue
        assert f"{p['length']} cm by {p['height']} cm" in q.final_answer
        assert f"{p['width']} cm by {p['height']} cm" in q.final_answer
        assert f"{p['length']} cm by {p['width']} cm" in q.final_answer


def test_triangular_prism_cross_section_is_right_angled():
    rng = random.Random(1103)
    seen = False
    for _ in range(TRIALS):
        q = plans_elevations.generate_plans_and_elevations(Tier.FOUNDATION, rng)
        p = q.solution_diagram.params
        if p["shape"] != "triangular_prism":
            continue
        seen = True
        base, tri_height = p["base"], p["tri_height"]
        # Independent check: recompute the hypotenuse from base/height via
        # Pythagoras and confirm it's a whole number (matching
        # solids_prisms.py's own right-angle guarantee).
        hyp_sq = base**2 + tri_height**2
        hyp = round(hyp_sq**0.5)
        assert hyp * hyp == hyp_sq
    assert seen


def test_dedup_keys_vary_widely():
    rng = random.Random(1104)
    keys = {plans_elevations.generate_plans_and_elevations(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.5


def test_topic_definition_metadata():
    t = plans_elevations.TOPIC_PLANS_AND_ELEVATIONS
    assert t.id == "plans_and_elevations"
    assert t.section == "geometry"
    assert t.group == "3D Shapes"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(1105)
    for _ in range(TRIALS):
        ex = plans_elevations.generate_modelled_example_plans_and_elevations(Tier.FOUNDATION, rng)
        assert ex.topic_id == "plans_and_elevations"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
        assert ex.diagram.kind == "plans_and_elevations"
