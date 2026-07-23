import random

from app.core.models import Tier
from app.topics import fractions

TRIALS = 200

GENERATORS = [
    (fractions.generate_simplify_fraction, Tier.FOUNDATION),
    (fractions.generate_add_subtract_fractions, Tier.FOUNDATION),
    (fractions.generate_multiply_fractions, Tier.FOUNDATION),
    (fractions.generate_divide_fractions, Tier.HIGHER),
    (fractions.generate_divide_fractions_foundation, Tier.FOUNDATION),
    (fractions.generate_mixed_number_arithmetic, Tier.HIGHER),
    (fractions.generate_fraction_of_amount, Tier.FOUNDATION),
    (fractions.generate_fractions_equivalent, Tier.FOUNDATION),
    (fractions.generate_fractions_equivalent_diagram, Tier.FOUNDATION),
    (fractions.generate_fractions_ordering, Tier.FOUNDATION),
    (fractions.generate_fractions_improper_mixed, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(90)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(92)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        fractions.TOPIC_SIMPLIFY,
        fractions.TOPIC_ADD_SUBTRACT,
        fractions.TOPIC_MULTIPLY,
        fractions.TOPIC_DIVIDE,
        fractions.TOPIC_DIVIDE_FOUNDATION,
        fractions.TOPIC_MIXED_NUMBER_ARITHMETIC,
        fractions.TOPIC_OF_AMOUNT,
        fractions.TOPIC_EQUIVALENT,
        fractions.TOPIC_EQUIVALENT_DIAGRAM,
        fractions.TOPIC_ORDERING,
        fractions.TOPIC_IMPROPER_MIXED,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 11
    for t in topics:
        assert t.section == "number"
        assert t.group == "Fractions"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert fractions.TOPIC_DIVIDE_FOUNDATION.fixed_tier == Tier.FOUNDATION


def test_all_fraction_topics_have_modelled_examples():
    topics = [
        fractions.TOPIC_SIMPLIFY,
        fractions.TOPIC_ADD_SUBTRACT,
        fractions.TOPIC_MULTIPLY,
        fractions.TOPIC_DIVIDE,
        fractions.TOPIC_DIVIDE_FOUNDATION,
        fractions.TOPIC_MIXED_NUMBER_ARITHMETIC,
        fractions.TOPIC_OF_AMOUNT,
        fractions.TOPIC_EQUIVALENT,
        fractions.TOPIC_EQUIVALENT_DIAGRAM,
        fractions.TOPIC_ORDERING,
        fractions.TOPIC_IMPROPER_MIXED,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (fractions.generate_modelled_example_simplify_fraction, Tier.FOUNDATION, "fractions_simplify"),
    (fractions.generate_modelled_example_add_subtract, Tier.FOUNDATION, "fractions_add_subtract"),
    (fractions.generate_modelled_example_multiply_fractions, Tier.FOUNDATION, "fractions_multiply"),
    (fractions.generate_modelled_example_divide_fractions, Tier.HIGHER, "fractions_divide"),
    (
        fractions.generate_modelled_example_divide_fractions_foundation,
        Tier.FOUNDATION,
        "fractions_divide_foundation",
    ),
    (fractions.generate_modelled_example_mixed_number_arithmetic, Tier.HIGHER, "fractions_mixed_number_arithmetic"),
    (fractions.generate_modelled_example_fraction_of_amount, Tier.FOUNDATION, "fractions_of_amount"),
    (fractions.generate_modelled_example_fractions_equivalent, Tier.FOUNDATION, "fractions_equivalent"),
    (
        fractions.generate_modelled_example_fractions_equivalent_diagram,
        Tier.FOUNDATION,
        "fractions_equivalent_diagram",
    ),
    (fractions.generate_modelled_example_fractions_ordering, Tier.FOUNDATION, "fractions_ordering"),
    (fractions.generate_modelled_example_fractions_improper_mixed, Tier.FOUNDATION, "fractions_improper_mixed"),
]


def test_modelled_examples_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(200)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_equivalent_diagram_attaches_a_matching_fraction_shapes_diagram():
    rng = random.Random(300)
    for _ in range(TRIALS):
        q = fractions.generate_fractions_equivalent_diagram(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "fraction_shapes"
        shapes = q.diagram.params["shapes"]
        assert all(s["kind"] in ("bar", "circle") for s in shapes)
        assert all(0 <= s["shaded"] <= s["parts"] for s in shapes)


def test_equivalent_diagram_fill_missing_shape_blanks_shape_b_until_solution():
    rng = random.Random(301)
    found_fill_missing = False
    for _ in range(TRIALS):
        q = fractions.generate_fractions_equivalent_diagram(Tier.FOUNDATION, rng)
        if q.dedup_key.startswith("diagram_fill:"):
            found_fill_missing = True
            a, b, d, kind = q.dedup_key.split(":")[1:5]
            shapes = q.diagram.params["shapes"]
            assert len(shapes) == 2
            assert shapes[0] == {"kind": kind, "parts": int(b), "shaded": int(a), "label": f"{a}/{b}"}
            assert shapes[1]["parts"] == int(d)
            assert shapes[1]["shaded"] == 0
            assert q.solution_diagram is not None
            sol_shapes = q.solution_diagram.params["shapes"]
            assert sol_shapes[1]["shaded"] == int(q.final_answer)
            assert sol_shapes[1]["parts"] == int(d)
    assert found_fill_missing


def test_equivalent_diagram_identify_shape_shows_reference_plus_three_candidates():
    rng = random.Random(302)
    found_identify = False
    for _ in range(TRIALS):
        q = fractions.generate_fractions_equivalent_diagram(Tier.FOUNDATION, rng)
        if q.dedup_key.startswith("diagram_id:"):
            found_identify = True
            shapes = q.diagram.params["shapes"]
            assert len(shapes) == 4
            assert shapes[0]["label"] and "/" in shapes[0]["label"] and ")" not in shapes[0]["label"]
            for letter, shape in zip("ABC", shapes[1:]):
                assert shape["label"].startswith(f"{letter})")
            assert q.solution_diagram is None
    assert found_identify
