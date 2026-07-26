import random

from app.core.models import Tier
from app.topics import solids_properties

TRIALS = 200

GENERATORS = [
    (solids_properties.generate_properties_3d_shapes, Tier.FOUNDATION),
    (solids_properties.generate_nets_3d_shapes, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(40)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert all(step for step in q.solution_steps)
            assert q.final_answer


def test_properties_dedup_keys_cover_every_shape_and_quantity():
    # 9 shapes x 3 quantities (faces/edges/vertices) = 27 distinct facts -
    # measured directly, not guessed (see solids_properties.py's module
    # docstring for why this exceeds len(TEMPLATES)).
    rng = random.Random(41)
    keys = {solids_properties.generate_properties_3d_shapes(Tier.FOUNDATION, rng).dedup_key for _ in range(2000)}
    assert len(keys) == 9 * 3 == 27


def test_nets_dedup_keys_cover_every_shape_and_angle():
    # 2 "describe" phrasings per shape + 1 "count" question per composition
    # key (1 key for cuboid/cube, 2 keys for the other 4 shapes):
    # 2x(2+1) + 4x(2+2) = 6 + 16 = 22 - measured directly.
    rng = random.Random(42)
    keys = {solids_properties.generate_nets_3d_shapes(Tier.FOUNDATION, rng).dedup_key for _ in range(2000)}
    assert len(keys) == 22


def test_properties_answers_match_the_curated_bank():
    lookup = {t.id: t for t in solids_properties.TEMPLATES}
    rng = random.Random(43)
    for _ in range(TRIALS):
        q = solids_properties.generate_properties_3d_shapes(Tier.FOUNDATION, rng)
        _, shape_id, quantity = q.dedup_key.split(":")
        template = lookup[shape_id]
        expected = {"faces": template.faces, "edges": template.edges, "vertices": template.vertices}[quantity]
        assert q.final_answer == str(expected)


def test_nets_answers_match_the_curated_bank():
    lookup = {t.id: t for t in solids_properties.NET_TEMPLATES}
    rng = random.Random(44)
    for _ in range(TRIALS):
        q = solids_properties.generate_nets_3d_shapes(Tier.FOUNDATION, rng)
        parts = q.dedup_key.split(":")
        shape_id = parts[1]
        angle = ":".join(parts[2:])
        template = lookup[shape_id]
        if angle in ("describe_a", "describe_b"):
            assert q.final_answer == template.description
        else:
            _, key = angle.split(":")
            assert q.final_answer == str(template.composition[key])


def test_properties_diagrams_match_expected_kinds_where_present():
    expected_kinds = {
        "cube": "cuboid",
        "cuboid": "cuboid",
        "triangular_prism": "triangular_prism",
        "square_pyramid": "pyramid",
        "tetrahedron": None,
        "cylinder": "cylinder",
        "cone": "cone",
        "sphere": "sphere",
        "hexagonal_prism": None,
    }
    rng = random.Random(45)
    seen_ids = set()
    for _ in range(400):
        q = solids_properties.generate_properties_3d_shapes(Tier.FOUNDATION, rng)
        shape_id = q.dedup_key.split(":")[1]
        seen_ids.add(shape_id)
        expected = expected_kinds[shape_id]
        if expected is None:
            assert q.diagram is None
        else:
            assert q.diagram is not None
            assert q.diagram.kind == expected
    assert seen_ids == set(expected_kinds)


def test_nets_diagrams_always_present_with_expected_shape_param():
    expected_shapes = {
        "cuboid": "cuboid",
        "cube": "cube",
        "triangular_prism": "triangular_prism",
        "cylinder": "cylinder",
        "cone": "cone",
        "square_pyramid": "pyramid",
    }
    rng = random.Random(46)
    seen_ids = set()
    for _ in range(400):
        q = solids_properties.generate_nets_3d_shapes(Tier.FOUNDATION, rng)
        shape_id = q.dedup_key.split(":")[1]
        seen_ids.add(shape_id)
        assert q.diagram is not None
        assert q.diagram.kind == "net"
        assert q.diagram.params["shape"] == expected_shapes[shape_id]
    assert seen_ids == set(expected_shapes)


ALL_TOPICS = [
    solids_properties.TOPIC_PROPERTIES_3D_SHAPES,
    solids_properties.TOPIC_NETS_3D_SHAPES,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert ids == {"properties_3d_shapes", "nets_3d_shapes"}
    for t in ALL_TOPICS:
        assert t.section == "geometry"
        assert t.group == "3D Shapes"
        assert t.fixed_tier == Tier.FOUNDATION
    assert solids_properties.TOPIC_PROPERTIES_3D_SHAPES.question_count == len(solids_properties.TEMPLATES) == 9
    assert solids_properties.TOPIC_NETS_3D_SHAPES.question_count == len(solids_properties.NET_TEMPLATES) == 6


def test_topic_definitions_have_modelled_examples_wired_up():
    for t in ALL_TOPICS:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (solids_properties.generate_modelled_example_properties_3d_shapes, "properties_3d_shapes"),
    (solids_properties.generate_modelled_example_nets_3d_shapes, "nets_3d_shapes"),
]


def test_modelled_examples_produce_verified_examples():
    for generate_example, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(303)
        for _ in range(TRIALS):
            example = generate_example(Tier.FOUNDATION, rng)
            assert example.topic_id == topic_id
            assert example.tier == Tier.FOUNDATION
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_properties_modelled_example_diagrams_match_generator():
    rng = random.Random(47)
    seen = set()
    for _ in range(400):
        example = solids_properties.generate_modelled_example_properties_3d_shapes(Tier.FOUNDATION, rng)
        # Every template with a diagram in the plain generator should also have
        # one here (they share the same TEMPLATES list), and vice versa.
        prompt_shape = example.prompt.split("does a ")[1].rsplit(" have?", 1)[0]
        seen.add(prompt_shape)
    assert len(seen) > 5


def test_nets_modelled_example_always_has_a_net_diagram():
    rng = random.Random(48)
    for _ in range(TRIALS):
        example = solids_properties.generate_modelled_example_nets_3d_shapes(Tier.FOUNDATION, rng)
        assert example.diagram is not None
        assert example.diagram.kind == "net"
