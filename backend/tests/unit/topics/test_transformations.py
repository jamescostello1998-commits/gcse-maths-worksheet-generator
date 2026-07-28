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
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 11
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
