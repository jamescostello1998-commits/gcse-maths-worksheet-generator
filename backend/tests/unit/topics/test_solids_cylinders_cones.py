import random

from app.core.models import Tier
from app.topics import solids_cylinders_cones

TRIALS = 200

GENERATORS = [
    (solids_cylinders_cones.generate_volume_surface_area_cylinder_foundation, Tier.FOUNDATION),
    (solids_cylinders_cones.generate_volume_surface_area_cylinder, Tier.HIGHER),
    (solids_cylinders_cones.generate_volume_surface_area_cone, Tier.HIGHER),
]


EXPECTED_DIAGRAM_KINDS = {
    solids_cylinders_cones.generate_volume_surface_area_cylinder_foundation: "cylinder",
    solids_cylinders_cones.generate_volume_surface_area_cylinder: "cylinder",
    solids_cylinders_cones.generate_volume_surface_area_cone: "cone",
}


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(40)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_all_generators_attach_a_matching_diagram():
    for generate, tier in GENERATORS:
        rng = random.Random(41)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == EXPECTED_DIAGRAM_KINDS[generate]


def test_cylinder_diagram_params_match_generated_values():
    rng = random.Random(43)
    for generate, tier in GENERATORS[:2]:
        for _ in range(TRIALS):
            q = generate(tier, rng)
            radius, height = q.dedup_key.split(":")[1:3]
            assert q.diagram.params["radius_label"] == f"{radius} cm"
            assert q.diagram.params["height_label"] == f"{height} cm"


def test_cylinder_foundation_gives_a_decimal_answer():
    rng = random.Random(44)
    for _ in range(TRIALS):
        q = solids_cylinders_cones.generate_volume_surface_area_cylinder_foundation(Tier.FOUNDATION, rng)
        assert "π" not in q.final_answer
        assert q.final_answer.split(" ")[1] in ("cm³", "cm²")


def test_cylinder_foundation_never_prints_scientific_notation():
    # Real bug found and fixed while building this topic (same class of bug as
    # estimation.py's documented _round_to_1sf gotcha): sp.N(expr, 3) switches
    # to scientific notation ("1.02E+3") for values >= 1000, which cylinder
    # volumes/surface areas comfortably reach - _round_to_3sf avoids this.
    rng = random.Random(444)
    for _ in range(500):
        q = solids_cylinders_cones.generate_volume_surface_area_cylinder_foundation(Tier.FOUNDATION, rng)
        assert "E+" not in q.final_answer
        assert "e+" not in q.final_answer


def test_cylinder_higher_gives_an_exact_pi_answer():
    rng = random.Random(45)
    for _ in range(TRIALS):
        q = solids_cylinders_cones.generate_volume_surface_area_cylinder(Tier.HIGHER, rng)
        assert "π" in q.final_answer
        assert "≈" not in q.final_answer


def test_cone_gives_a_decimal_answer_never_scientific_notation():
    rng = random.Random(46)
    for _ in range(500):
        q = solids_cylinders_cones.generate_volume_surface_area_cone(Tier.HIGHER, rng)
        assert "π" not in q.final_answer
        assert "E+" not in q.final_answer
        assert "e+" not in q.final_answer
        assert q.final_answer.endswith("cm³") or q.final_answer.endswith("cm²")


def test_cone_slant_given_branch_diagram_has_no_height_label():
    rng = random.Random(50)
    found_slant_given = False
    for _ in range(TRIALS):
        q = solids_cylinders_cones.generate_volume_surface_area_cone(Tier.HIGHER, rng)
        if q.dedup_key.split(":")[1] == "slant_given":
            found_slant_given = True
            assert "slant_label" in q.diagram.params
            assert "height_label" not in q.diagram.params
            assert "show_height_triangle" not in q.diagram.params
            assert q.solution_diagram is None
    assert found_slant_given


def test_cone_derive_slant_branch_diagram_has_no_slant_label_on_question_page():
    rng = random.Random(51)
    found_derive_slant = False
    for _ in range(TRIALS):
        q = solids_cylinders_cones.generate_volume_surface_area_cone(Tier.HIGHER, rng)
        if q.dedup_key.split(":")[1] == "derive_slant":
            found_derive_slant = True
            assert "slant_label" not in q.diagram.params
            assert "height_label" in q.diagram.params
            assert q.diagram.params["show_height_triangle"] is True
            # The solution page is allowed to reveal the derived slant.
            assert q.solution_diagram is not None
            assert "slant_label" in q.solution_diagram.params
    assert found_derive_slant


def test_cone_both_branches_occur_over_many_trials():
    rng = random.Random(52)
    branches = set()
    for _ in range(TRIALS):
        q = solids_cylinders_cones.generate_volume_surface_area_cone(Tier.HIGHER, rng)
        branches.add(q.dedup_key.split(":")[1])
    assert branches == {"slant_given", "derive_slant"}


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(42)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 100


ALL_TOPICS = [
    solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CYLINDER_FOUNDATION,
    solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CYLINDER,
    solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CONE,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert len(ids) == 3
    for t in ALL_TOPICS:
        assert t.section == "geometry"
        assert t.group == "3D Shapes"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CYLINDER_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CYLINDER.fixed_tier == Tier.HIGHER
    assert solids_cylinders_cones.TOPIC_VOLUME_SURFACE_AREA_CONE.fixed_tier == Tier.HIGHER


MODELLED_EXAMPLE_GENERATORS = [
    (
        solids_cylinders_cones.generate_modelled_example_volume_surface_area_cylinder_foundation,
        Tier.FOUNDATION,
        "volume_surface_area_cylinder_foundation",
        "cylinder",
    ),
    (
        solids_cylinders_cones.generate_modelled_example_volume_surface_area_cylinder,
        Tier.HIGHER,
        "volume_surface_area_cylinder",
        "cylinder",
    ),
    (
        solids_cylinders_cones.generate_modelled_example_volume_surface_area_cone,
        Tier.HIGHER,
        "volume_surface_area_cone",
        "cone",
    ),
]


def test_topic_definitions_have_modelled_examples_wired_up():
    for t in ALL_TOPICS:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_verified_examples_with_diagrams():
    for generate_example, tier, topic_id, diagram_kind in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(303)
        for _ in range(TRIALS):
            example = generate_example(tier, rng)
            assert example.topic_id == topic_id
            assert example.tier == tier
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            assert example.diagram is not None
            assert example.diagram.kind == diagram_kind


def test_modelled_examples_never_print_scientific_notation():
    for generate_example, tier, _topic_id, _diagram_kind in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(304)
        for _ in range(TRIALS):
            example = generate_example(tier, rng)
            assert "E+" not in example.final_answer
            assert "e+" not in example.final_answer


def test_decimal_topics_reach_all_three_rounding_phrasings():
    # The cylinder-foundation and cone topics' answers were converted from a
    # hardcoded "3 significant figures" to a random choice among the 3 real
    # GCSE rounding instructions (see app/topics/rounding.py) - confirm all
    # three genuinely appear over enough trials. The Higher (exact-π-form)
    # cylinder topic is untouched and deliberately excluded here.
    generators = [
        (solids_cylinders_cones.generate_volume_surface_area_cylinder_foundation, Tier.FOUNDATION),
        (solids_cylinders_cones.generate_volume_surface_area_cone, Tier.HIGHER),
    ]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate, tier in generators:
        rng = random.Random(505)
        seen = set()
        for _ in range(200):
            q = generate(tier, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings
