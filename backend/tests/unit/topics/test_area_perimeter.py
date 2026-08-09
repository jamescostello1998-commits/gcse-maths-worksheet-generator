import random

from app.core.models import Tier
from app.topics import area_perimeter

TRIALS = 200

GENERATORS = [
    (area_perimeter.generate_rectangle, Tier.FOUNDATION),
    (area_perimeter.generate_triangle, Tier.FOUNDATION),
    (area_perimeter.generate_composite_rectangles, Tier.FOUNDATION),
    (area_perimeter.generate_circle_foundation, Tier.FOUNDATION),
    (area_perimeter.generate_circle, Tier.HIGHER),
    (area_perimeter.generate_semicircle_compound, Tier.FOUNDATION),
    (area_perimeter.generate_semicircle_compound_higher, Tier.HIGHER),
    (area_perimeter.generate_subtract_compound, Tier.HIGHER),
    (area_perimeter.generate_subtract_compound_foundation, Tier.FOUNDATION),
    (area_perimeter.generate_area_parallelogram, Tier.FOUNDATION),
    (area_perimeter.generate_area_trapezium, Tier.FOUNDATION),
    (area_perimeter.generate_area_mixed_compound, Tier.HIGHER),
    (area_perimeter.generate_arc_length_foundation, Tier.FOUNDATION),
    (area_perimeter.generate_arc_length, Tier.HIGHER),
    (area_perimeter.generate_area_sector_foundation, Tier.FOUNDATION),
    (area_perimeter.generate_area_sector, Tier.HIGHER),
]


EXPECTED_DIAGRAM_KINDS = {
    area_perimeter.generate_rectangle: "rectangle",
    area_perimeter.generate_triangle: "triangle_area",
    # 4 distinct compound-shape branches (2 L orientations + a T-shape + a
    # "find x" reverse branch, both L variants and the reverse branch use
    # kind="l_shape") - either diagram kind is valid for a single draw.
    area_perimeter.generate_composite_rectangles: {"l_shape", "t_shape"},
    area_perimeter.generate_circle_foundation: "circle",
    area_perimeter.generate_circle: "circle",
    area_perimeter.generate_semicircle_compound: "rectangle_semicircle",
    area_perimeter.generate_semicircle_compound_higher: "rectangle_semicircle",
    area_perimeter.generate_subtract_compound: "l_shape",
    area_perimeter.generate_subtract_compound_foundation: "l_shape",
    area_perimeter.generate_area_parallelogram: "parallelogram",
    area_perimeter.generate_area_trapezium: "trapezium",
    area_perimeter.generate_area_mixed_compound: "mixed_compound",
    area_perimeter.generate_arc_length_foundation: "sector",
    area_perimeter.generate_arc_length: "sector",
    area_perimeter.generate_area_sector_foundation: "sector",
    area_perimeter.generate_area_sector: "sector",
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
        expected = EXPECTED_DIAGRAM_KINDS[generate]
        expected_kinds = expected if isinstance(expected, (set, frozenset)) else {expected}
        assert q.diagram.kind in expected_kinds


def test_rectangle_diagram_params_match_generated_values():
    rng = random.Random(43)
    q = area_perimeter.generate_rectangle(Tier.FOUNDATION, rng)
    length, width = q.dedup_key.split(":")[1:3]
    assert q.diagram.params["width"] == int(length)
    assert q.diagram.params["height"] == int(width)


def test_semicircle_compound_higher_gives_an_exact_pi_answer():
    rng = random.Random(44)
    for _ in range(TRIALS):
        q = area_perimeter.generate_semicircle_compound_higher(Tier.HIGHER, rng)
        assert "π" in q.final_answer
        assert "≈" not in q.final_answer


def test_arc_length_and_area_sector_higher_give_exact_pi_answers():
    for generate in (area_perimeter.generate_arc_length, area_perimeter.generate_area_sector):
        rng = random.Random(45)
        for _ in range(TRIALS):
            q = generate(Tier.HIGHER, rng)
            assert "π" in q.final_answer
            assert "≈" not in q.final_answer


def test_arc_length_and_area_sector_foundation_give_decimal_answers():
    for generate in (area_perimeter.generate_arc_length_foundation, area_perimeter.generate_area_sector_foundation):
        rng = random.Random(46)
        for _ in range(TRIALS):
            q = generate(Tier.FOUNDATION, rng)
            assert "π" not in q.final_answer


def test_decimal_topics_reach_all_three_rounding_phrasings():
    generators = [
        area_perimeter.generate_circle_foundation,
        area_perimeter.generate_arc_length_foundation,
        area_perimeter.generate_area_sector_foundation,
    ]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate in generators:
        rng = random.Random(48)
        seen = set()
        for _ in range(200):
            q = generate(Tier.FOUNDATION, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings


def test_mixed_compound_gives_a_decimal_answer():
    rng = random.Random(47)
    for _ in range(TRIALS):
        q = area_perimeter.generate_area_mixed_compound(Tier.HIGHER, rng)
        assert "π" not in q.final_answer
        assert "cm²" in q.final_answer


def test_mixed_compound_reaches_all_three_rounding_phrasings():
    rng = random.Random(49)
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    seen = set()
    for _ in range(200):
        q = area_perimeter.generate_area_mixed_compound(Tier.HIGHER, rng)
        seen |= {p for p in phrasings if p in q.prompt}
    assert seen == phrasings


def test_mixed_compound_reaches_every_top_and_cut_kind_combination():
    rng = random.Random(50)
    seen = set()
    for _ in range(200):
        q = area_perimeter.generate_area_mixed_compound(Tier.HIGHER, rng)
        seen.add((q.diagram.params["top_kind"], q.diagram.params["cut_kind"]))
    assert seen == {
        ("triangle", "quarter_circle"), ("triangle", "semicircle_notch"),
        ("semicircle", "quarter_circle"), ("semicircle", "semicircle_notch"),
    }


def test_dedup_keys_vary_per_generator():
    # generate_circle's parameter space is small (13 radii x 2 measures = 26 max
    # distinct keys), so this uses a lower bar than other topic files' equivalent test.
    for generate, tier in GENERATORS:
        rng = random.Random(42)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 15


ALL_TOPICS = [
    area_perimeter.TOPIC_RECTANGLE,
    area_perimeter.TOPIC_TRIANGLE,
    area_perimeter.TOPIC_COMPOSITE_RECTANGLES,
    area_perimeter.TOPIC_CIRCLE_FOUNDATION,
    area_perimeter.TOPIC_CIRCLE,
    area_perimeter.TOPIC_SEMICIRCLE_COMPOUND,
    area_perimeter.TOPIC_SEMICIRCLE_COMPOUND_HIGHER,
    area_perimeter.TOPIC_SUBTRACT_COMPOUND,
    area_perimeter.TOPIC_SUBTRACT_COMPOUND_FOUNDATION,
    area_perimeter.TOPIC_PARALLELOGRAM,
    area_perimeter.TOPIC_TRAPEZIUM,
    area_perimeter.TOPIC_MIXED_COMPOUND,
    area_perimeter.TOPIC_ARC_LENGTH_FOUNDATION,
    area_perimeter.TOPIC_ARC_LENGTH,
    area_perimeter.TOPIC_AREA_SECTOR_FOUNDATION,
    area_perimeter.TOPIC_AREA_SECTOR,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert len(ids) == 16
    for t in ALL_TOPICS:
        assert t.section == "geometry"
        assert t.group == "Area & Perimeter"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert area_perimeter.TOPIC_SEMICIRCLE_COMPOUND.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_SEMICIRCLE_COMPOUND_HIGHER.fixed_tier == Tier.HIGHER
    assert area_perimeter.TOPIC_SUBTRACT_COMPOUND_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_PARALLELOGRAM.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_TRAPEZIUM.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_MIXED_COMPOUND.fixed_tier == Tier.HIGHER
    assert area_perimeter.TOPIC_ARC_LENGTH_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_ARC_LENGTH.fixed_tier == Tier.HIGHER
    assert area_perimeter.TOPIC_AREA_SECTOR_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert area_perimeter.TOPIC_AREA_SECTOR.fixed_tier == Tier.HIGHER


MODELLED_EXAMPLE_GENERATORS = [
    (area_perimeter.generate_modelled_example_rectangle, Tier.FOUNDATION, "area_rectangle_F", "rectangle"),
    (area_perimeter.generate_modelled_example_triangle, Tier.FOUNDATION, "area_triangle_F", "triangle_area"),
    (
        area_perimeter.generate_modelled_example_composite_rectangles,
        Tier.FOUNDATION,
        "area_composite_rectangles_F",
        {"l_shape", "t_shape"},
    ),
    (
        area_perimeter.generate_modelled_example_circle_foundation,
        Tier.FOUNDATION,
        "area_circle_F",
        "circle",
    ),
    (area_perimeter.generate_modelled_example_circle, Tier.HIGHER, "area_circle_H", "circle"),
    (
        area_perimeter.generate_modelled_example_semicircle_compound,
        Tier.FOUNDATION,
        "area_semicircle_compound_F",
        "rectangle_semicircle",
    ),
    (
        area_perimeter.generate_modelled_example_semicircle_compound_higher,
        Tier.HIGHER,
        "area_semicircle_compound_H",
        "rectangle_semicircle",
    ),
    (
        area_perimeter.generate_modelled_example_subtract_compound,
        Tier.HIGHER,
        "area_subtract_compound_H",
        "l_shape",
    ),
    (
        area_perimeter.generate_modelled_example_subtract_compound_foundation,
        Tier.FOUNDATION,
        "area_subtract_compound_F",
        "l_shape",
    ),
    (area_perimeter.generate_modelled_example_area_parallelogram, Tier.FOUNDATION, "area_parallelogram_F", "parallelogram"),
    (area_perimeter.generate_modelled_example_area_trapezium, Tier.FOUNDATION, "area_trapezium_F", "trapezium"),
    (
        area_perimeter.generate_modelled_example_area_mixed_compound,
        Tier.HIGHER,
        "area_mixed_compound_H",
        "mixed_compound",
    ),
    (
        area_perimeter.generate_modelled_example_arc_length_foundation,
        Tier.FOUNDATION,
        "arc_length_F",
        "sector",
    ),
    (area_perimeter.generate_modelled_example_arc_length, Tier.HIGHER, "arc_length_H", "sector"),
    (
        area_perimeter.generate_modelled_example_area_sector_foundation,
        Tier.FOUNDATION,
        "area_sector_F",
        "sector",
    ),
    (area_perimeter.generate_modelled_example_area_sector, Tier.HIGHER, "area_sector_H", "sector"),
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
            expected_kinds = diagram_kind if isinstance(diagram_kind, (set, frozenset)) else {diagram_kind}
            assert example.diagram.kind in expected_kinds
