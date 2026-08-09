import random

from app.core.models import Tier
from app.topics import solids_prisms

TRIALS = 300

GENERATORS = [
    (solids_prisms.generate_volume_surface_area_cuboid, Tier.FOUNDATION),
    (solids_prisms.generate_volume_surface_area_cube, Tier.FOUNDATION),
    (solids_prisms.generate_volume_surface_area_triangular_prism, Tier.FOUNDATION),
]


EXPECTED_DIAGRAM_KINDS = {
    solids_prisms.generate_volume_surface_area_cuboid: "cuboid",
    solids_prisms.generate_volume_surface_area_cube: "cuboid",
    solids_prisms.generate_volume_surface_area_triangular_prism: "triangular_prism",
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
            assert q.final_answer.endswith("cm³") or q.final_answer.endswith("cm²")


def test_all_generators_attach_a_matching_diagram():
    for generate, tier in GENERATORS:
        rng = random.Random(41)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == EXPECTED_DIAGRAM_KINDS[generate]


def test_cuboid_diagram_params_match_generated_values():
    rng = random.Random(43)
    q = solids_prisms.generate_volume_surface_area_cuboid(Tier.FOUNDATION, rng)
    length, width, height = (int(part) for part in q.dedup_key.split(":")[1:4])
    assert q.diagram.params["length_label"] == f"{length} cm"
    assert q.diagram.params["width_label"] == f"{width} cm"
    assert q.diagram.params["height_label"] == f"{height} cm"


def test_cube_diagram_uses_the_same_side_for_every_label():
    rng = random.Random(44)
    for _ in range(50):
        q = solids_prisms.generate_volume_surface_area_cube(Tier.FOUNDATION, rng)
        labels = {
            q.diagram.params["width_label"],
            q.diagram.params["height_label"],
            q.diagram.params["length_label"],
        }
        assert len(labels) == 1


def test_triangular_prism_diagram_params_match_generated_values():
    rng = random.Random(45)
    q = solids_prisms.generate_volume_surface_area_triangular_prism(Tier.FOUNDATION, rng)
    p, q_leg = (int(part) for part in q.dedup_key.split(":")[1:3])
    assert q.diagram.params["base_label"] == f"{p} cm"
    assert q.diagram.params["triangle_height_label"] == f"{q_leg} cm"


def test_triangular_prism_cross_section_is_always_right_angled():
    rng = random.Random(46)
    for _ in range(TRIALS):
        q = solids_prisms.generate_volume_surface_area_triangular_prism(Tier.FOUNDATION, rng)
        _, p, q_leg, hyp, _length, _measure = q.dedup_key.split(":")
        p, q_leg, hyp = int(p), int(q_leg), int(hyp)
        assert hyp ** 2 == p ** 2 + q_leg ** 2


def test_cuboid_and_triangular_prism_dedup_keys_vary_widely():
    for generate in (
        solids_prisms.generate_volume_surface_area_cuboid,
        solids_prisms.generate_volume_surface_area_triangular_prism,
    ):
        rng = random.Random(42)
        keys = {generate(Tier.FOUNDATION, rng).dedup_key for _ in range(300)}
        assert len(keys) > 100


def test_cube_dedup_keys_vary():
    # The cube's parameter space is small (19 side lengths x 2 measures = 38
    # max distinct keys) - comfortably above the default 20-question worksheet.
    rng = random.Random(42)
    keys = {
        solids_prisms.generate_volume_surface_area_cube(Tier.FOUNDATION, rng).dedup_key
        for _ in range(200)
    }
    assert len(keys) > 15


ALL_TOPICS = [
    solids_prisms.TOPIC_CUBOID,
    solids_prisms.TOPIC_CUBE,
    solids_prisms.TOPIC_TRIANGULAR_PRISM,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert len(ids) == 3
    for t in ALL_TOPICS:
        assert t.section == "geometry"
        assert t.group == "3D Shapes"
        assert t.fixed_tier == Tier.FOUNDATION
    assert solids_prisms.TOPIC_CUBOID.id == "volume_surface_area_cuboid_F"
    assert solids_prisms.TOPIC_CUBE.id == "volume_surface_area_cube_F"
    assert solids_prisms.TOPIC_TRIANGULAR_PRISM.id == "volume_surface_area_triangular_prism_F"


def test_topic_definitions_have_modelled_examples_wired_up():
    for t in ALL_TOPICS:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (
        solids_prisms.generate_modelled_example_volume_surface_area_cuboid,
        Tier.FOUNDATION,
        "volume_surface_area_cuboid_F",
        "cuboid",
    ),
    (
        solids_prisms.generate_modelled_example_volume_surface_area_cube,
        Tier.FOUNDATION,
        "volume_surface_area_cube_F",
        "cuboid",
    ),
    (
        solids_prisms.generate_modelled_example_volume_surface_area_triangular_prism,
        Tier.FOUNDATION,
        "volume_surface_area_triangular_prism_F",
        "triangular_prism",
    ),
]


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
