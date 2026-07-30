import random

from app.core.models import Tier
from app.topics import transformations

TRIALS = 200

GENERATORS = [
    (transformations.generate_symmetry_lines, Tier.FOUNDATION),
    (transformations.generate_symmetry_rotational, Tier.FOUNDATION),
    (transformations.generate_transform_reflect_complete, Tier.FOUNDATION),
    (transformations.generate_transform_reflect_describe, Tier.FOUNDATION),
    (transformations.generate_transform_rotate_complete, Tier.FOUNDATION),
    (transformations.generate_transform_rotate_describe, Tier.HIGHER),
    (transformations.generate_transform_translate_complete, Tier.FOUNDATION),
    (transformations.generate_transform_translate_describe, Tier.FOUNDATION),
    (transformations.generate_transform_enlarge_complete_foundation, Tier.FOUNDATION),
    (transformations.generate_transform_enlarge_complete_higher, Tier.HIGHER),
    (transformations.generate_transform_enlarge_describe, Tier.HIGHER),
    (transformations.generate_combined_transformations, Tier.HIGHER),
]

# Only the 4 grid-transform topics (not the 2 curated-bank symmetry topics,
# which have a deliberately small question_count matching their bank size).
GRID_GENERATORS = [g for g in GENERATORS if g[0].__name__ not in ("generate_symmetry_lines", "generate_symmetry_rotational")]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(400)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None


def test_dedup_keys_vary_per_grid_generator():
    for generate, tier in GRID_GENERATORS:
        rng = random.Random(401)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_symmetry_dedup_keys_cover_the_whole_shape_bank():
    for generate, tier in ((transformations.generate_symmetry_lines, Tier.FOUNDATION),
                            (transformations.generate_symmetry_rotational, Tier.FOUNDATION)):
        rng = random.Random(402)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) == len(transformations._SYMMETRY_SHAPES)


def test_reflect_complete_image_is_a_true_reflection_independently_rechecked():
    """Re-derive the perpendicular-bisector property at the test level too,
    not just trusting the generator's own internal _verify_reflection call."""
    rng = random.Random(403)
    for _ in range(TRIALS):
        q = transformations.generate_transform_reflect_complete(Tier.FOUNDATION, rng)
        mirror = q.solution_diagram.params["mirror_line"]
        original = q.solution_diagram.params["original_vertices"]
        image = q.solution_diagram.params["image_vertices"]
        for p, im in zip(original, image):
            mx, my = (p[0] + im[0]) / 2, (p[1] + im[1]) / 2
            if mirror["type"] == "vertical":
                assert mx == mirror["x"]
            elif mirror["type"] == "horizontal":
                assert my == mirror["y"]
            else:
                assert my == mirror["sign"] * mx


def test_rotate_complete_uses_only_90_180_270():
    rng = random.Random(404)
    for _ in range(TRIALS):
        q = transformations.generate_transform_rotate_complete(Tier.FOUNDATION, rng)
        assert any(w in q.prompt for w in ("90° anticlockwise", "90° clockwise", "180°"))


def test_translate_complete_never_uses_the_zero_vector():
    rng = random.Random(405)
    for _ in range(TRIALS):
        q = transformations.generate_transform_translate_complete(Tier.FOUNDATION, rng)
        vector = q.diagram.params["translation_vector"]
        assert vector != (0, 0)


def test_enlarge_foundation_never_uses_negative_or_fractional_scale_factor():
    rng = random.Random(406)
    for _ in range(TRIALS):
        q = transformations.generate_transform_enlarge_complete_foundation(Tier.FOUNDATION, rng)
        assert "/" not in q.prompt.split("scale factor ")[1].split(",")[0]
        assert "-" not in q.prompt.split("scale factor ")[1].split(",")[0]


def test_enlarge_higher_always_uses_negative_or_fractional_scale_factor():
    rng = random.Random(407)
    for _ in range(TRIALS):
        q = transformations.generate_transform_enlarge_complete_higher(Tier.HIGHER, rng)
        factor_text = q.prompt.split("scale factor ")[1].split(",")[0]
        assert factor_text.startswith("-") or "/" in factor_text


def test_describe_topics_final_answer_reproduces_the_shown_image():
    rng = random.Random(408)
    for _ in range(TRIALS):
        q = transformations.generate_transform_reflect_describe(Tier.FOUNDATION, rng)
        assert q.final_answer.startswith("Reflection in the line")

        q = transformations.generate_transform_rotate_describe(Tier.HIGHER, rng)
        assert q.final_answer.startswith("Rotation")

        q = transformations.generate_transform_translate_describe(Tier.FOUNDATION, rng)
        assert q.final_answer.startswith("Translation by the vector")

        q = transformations.generate_transform_enlarge_describe(Tier.HIGHER, rng)
        assert q.final_answer.startswith("Enlargement, scale factor")


def test_all_grid_diagrams_fit_within_the_declared_range():
    rng = random.Random(409)
    for generate, tier in GRID_GENERATORS:
        for _ in range(TRIALS):
            q = generate(tier, rng)
            params = q.diagram.params
            x_min, x_max = params["x_min"], params["x_max"]
            y_min, y_max = params["y_min"], params["y_max"]
            for spec in (q.diagram, q.solution_diagram):
                if spec is None:
                    continue
                for key in ("original_vertices", "image_vertices"):
                    for x, y in spec.params.get(key) or []:
                        assert x_min <= x <= x_max
                        assert y_min <= y <= y_max


def test_shape_templates_are_asymmetric():
    """Sanity check that every _SHAPE_TEMPLATES entry (used by the 4 grid-
    transform topics) has 0 lines of symmetry and rotational order 1 - a
    symmetric shape would make a "describe the transformation" question's
    answer ambiguous (more than one transform could produce the same image)."""
    for template in transformations._SHAPE_TEMPLATES:
        lines, order = transformations._count_symmetries(template)
        assert lines == 0
        assert order == 1


def test_symmetry_shapes_match_their_claimed_counts():
    """Re-derive independently at the test level too (not just trusting the
    module's own import-time validation loop)."""
    for shape in transformations._SYMMETRY_SHAPES:
        lines, order = transformations._count_symmetries(shape.vertices)
        assert lines == len(shape.lines_of_symmetry)
        assert order == shape.rotational_order


def test_topic_definitions_have_expected_metadata():
    topics = [
        transformations.TOPIC_SYMMETRY_LINES,
        transformations.TOPIC_SYMMETRY_ROTATIONAL,
        transformations.TOPIC_TRANSFORM_REFLECT_COMPLETE,
        transformations.TOPIC_TRANSFORM_REFLECT_DESCRIBE,
        transformations.TOPIC_TRANSFORM_ROTATE_COMPLETE,
        transformations.TOPIC_TRANSFORM_ROTATE_DESCRIBE,
        transformations.TOPIC_TRANSFORM_TRANSLATE_COMPLETE,
        transformations.TOPIC_TRANSFORM_TRANSLATE_DESCRIBE,
        transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_FOUNDATION,
        transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_HIGHER,
        transformations.TOPIC_TRANSFORM_ENLARGE_DESCRIBE,
        transformations.TOPIC_COMBINED_TRANSFORMATIONS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 12
    for t in topics:
        assert t.section == "geometry"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
        assert t.group in (transformations.GROUP_SYMMETRY, transformations.GROUP_TRANSFORMATIONS)

    assert transformations.TOPIC_SYMMETRY_LINES.group == transformations.GROUP_SYMMETRY
    assert transformations.TOPIC_SYMMETRY_ROTATIONAL.group == transformations.GROUP_SYMMETRY
    assert transformations.TOPIC_SYMMETRY_LINES.question_count == len(transformations._SYMMETRY_SHAPES)
    assert transformations.TOPIC_SYMMETRY_ROTATIONAL.question_count == len(transformations._SYMMETRY_SHAPES)

    assert transformations.TOPIC_TRANSFORM_ROTATE_COMPLETE.fixed_tier == Tier.FOUNDATION
    assert transformations.TOPIC_TRANSFORM_ROTATE_DESCRIBE.fixed_tier == Tier.HIGHER
    assert transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_HIGHER.fixed_tier == Tier.HIGHER
    assert transformations.TOPIC_TRANSFORM_ENLARGE_DESCRIBE.fixed_tier == Tier.HIGHER
    assert transformations.TOPIC_COMBINED_TRANSFORMATIONS.fixed_tier == Tier.HIGHER
    assert transformations.TOPIC_COMBINED_TRANSFORMATIONS.group == transformations.GROUP_TRANSFORMATIONS


def test_topics_have_a_modelled_example_generator_wired_up():
    topics = [
        transformations.TOPIC_SYMMETRY_LINES,
        transformations.TOPIC_SYMMETRY_ROTATIONAL,
        transformations.TOPIC_TRANSFORM_REFLECT_COMPLETE,
        transformations.TOPIC_TRANSFORM_REFLECT_DESCRIBE,
        transformations.TOPIC_TRANSFORM_ROTATE_COMPLETE,
        transformations.TOPIC_TRANSFORM_ROTATE_DESCRIBE,
        transformations.TOPIC_TRANSFORM_TRANSLATE_COMPLETE,
        transformations.TOPIC_TRANSFORM_TRANSLATE_DESCRIBE,
        transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_FOUNDATION,
        transformations.TOPIC_TRANSFORM_ENLARGE_COMPLETE_HIGHER,
        transformations.TOPIC_TRANSFORM_ENLARGE_DESCRIBE,
        transformations.TOPIC_COMBINED_TRANSFORMATIONS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (transformations.generate_modelled_example_symmetry_lines, Tier.FOUNDATION, "symmetry_lines"),
    (transformations.generate_modelled_example_symmetry_rotational, Tier.FOUNDATION, "symmetry_rotational"),
    (transformations.generate_modelled_example_transform_reflect_complete, Tier.FOUNDATION, "transform_reflect_complete"),
    (transformations.generate_modelled_example_transform_reflect_describe, Tier.FOUNDATION, "transform_reflect_describe"),
    (transformations.generate_modelled_example_transform_rotate_complete, Tier.FOUNDATION, "transform_rotate_complete"),
    (transformations.generate_modelled_example_transform_rotate_describe, Tier.HIGHER, "transform_rotate_describe"),
    (transformations.generate_modelled_example_transform_translate_complete, Tier.FOUNDATION, "transform_translate_complete"),
    (transformations.generate_modelled_example_transform_translate_describe, Tier.FOUNDATION, "transform_translate_describe"),
    (transformations.generate_modelled_example_transform_enlarge_complete_foundation, Tier.FOUNDATION, "transform_enlarge_complete_foundation"),
    (transformations.generate_modelled_example_transform_enlarge_complete_higher, Tier.HIGHER, "transform_enlarge_complete_higher"),
    (transformations.generate_modelled_example_transform_enlarge_describe, Tier.HIGHER, "transform_enlarge_describe"),
    (transformations.generate_modelled_example_combined_transformations, Tier.HIGHER, "combined_transformations"),
]


def test_modelled_examples_are_valid():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(500)
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
# combined_transformations - bespoke coverage. The generic checks above
# (valid-question smoke test, dedup-key variance, grid-fit) already run
# against this generator via GENERATORS/GRID_GENERATORS; these tests add
# combo-type-specific coverage, re-deriving each composition rule
# independently at the test level too (matching this file's own precedent,
# e.g. test_reflect_complete_image_is_a_true_reflection_independently_rechecked
# and test_symmetry_shapes_match_their_claimed_counts).
# ---------------------------------------------------------------------------


def test_combined_transformations_all_four_combo_types_are_reachable():
    rng = random.Random(410)
    seen = set()
    for _ in range(400):
        q = transformations.generate_combined_transformations(Tier.HIGHER, rng)
        if "translated by the vector" in q.prompt:
            seen.add("translate_translate")
        elif "reflected in the line" in q.prompt:
            seen.add("reflect_parallel")
        elif "about the centre" in q.prompt:
            seen.add("rotate_same_centre")
        elif "x-axis" in q.prompt and "y-axis" in q.prompt:
            seen.add("reflect_axes")
    assert seen == {"translate_translate", "reflect_parallel", "rotate_same_centre", "reflect_axes"}


def test_combined_transformations_tier_and_group():
    rng = random.Random(4101)
    for _ in range(TRIALS):
        q = transformations.generate_combined_transformations(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.solution_diagram is None  # only original + final image, no intermediate shape shown


def test_combined_translate_translate_matches_vector_sum():
    """Independently re-derive: the claimed vector (v1 + v2) applied once
    directly to the original must reproduce the same image as simulating
    both translations in sequence."""
    rng = random.Random(411)
    for _ in range(TRIALS):
        shape, v1, v2, combined, final = transformations._random_combo_translate_translate(rng)
        assert combined == (v1[0] + v2[0], v1[1] + v2[1])
        recombined = [(x + combined[0], y + combined[1]) for x, y in shape]
        assert recombined == final


def test_combined_reflect_parallel_matches_translation_formula():
    """Independently re-derive: twice the gap between the two mirror lines,
    perpendicular to them, applied once directly to the original must
    reproduce the same image as reflecting in both mirrors in sequence."""
    rng = random.Random(412)
    for _ in range(TRIALS):
        shape, orientation, a, b, combined_vector, final = transformations._random_combo_reflect_parallel(rng)
        expected = (2 * (b - a), 0) if orientation == "vertical" else (0, 2 * (b - a))
        assert combined_vector == expected
        recombined = [(x + combined_vector[0], y + combined_vector[1]) for x, y in shape]
        assert recombined == final


def test_combined_rotate_same_centre_matches_angle_sum():
    """Independently re-derive: the summed angle (reduced mod 360, always a
    value already in _ROTATIONS) applied once directly about the shared
    centre must reproduce the same image as rotating twice in sequence."""
    rng = random.Random(413)
    for _ in range(TRIALS):
        shape, centre, angle1, angle2, combined_angle, final = transformations._random_combo_rotate_same_centre(rng)
        assert combined_angle == (angle1 + angle2) % 360
        assert combined_angle in transformations._ROTATIONS
        recombined = [transformations._rotate_point(p, centre, combined_angle) for p in shape]
        assert recombined == final


def test_combined_reflect_axes_gives_180_rotation_about_origin():
    """Independently re-derive: a single 180 deg rotation about the origin
    applied directly to the original must reproduce the same image as
    reflecting in the x-axis then the y-axis (or vice versa) in sequence."""
    rng = random.Random(414)
    for _ in range(TRIALS):
        shape, order, final = transformations._random_combo_reflect_axes(rng)
        recombined = [transformations._rotate_point(p, (0, 0), 180) for p in shape]
        assert recombined == final


def test_combined_rotate_combo_pairs_never_compose_to_the_identity():
    for angle1, angle2 in transformations._ROTATE_COMBO_PAIRS:
        assert (angle1 + angle2) % 360 != 0
        assert (angle1 + angle2) % 360 in transformations._ROTATIONS
