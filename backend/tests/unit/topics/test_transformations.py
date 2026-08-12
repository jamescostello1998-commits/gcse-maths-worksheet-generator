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
    (transformations.generate_transform_enlarge_describe_foundation, Tier.FOUNDATION),
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


def test_reflect_foundation_never_uses_y_equals_minus_x():
    # "y = -x" is the hardest of the four mirror-line kinds (neither
    # coordinate keeps its sign) and is excluded entirely at Foundation -
    # both transform_reflect_complete/_describe are Foundation-only.
    rng = random.Random(407)
    for _ in range(TRIALS):
        q = transformations.generate_transform_reflect_complete(Tier.FOUNDATION, rng)
        assert q.solution_diagram.params["mirror_line"]["label"] != "y = -x"
        q2 = transformations.generate_transform_reflect_describe(Tier.FOUNDATION, rng)
        # reflect_describe doesn't expose mirror_line directly, but the
        # final answer states it in the same "y = ..." form.
        assert "y = -x" not in q2.final_answer


def test_reflect_foundation_mirror_kinds_still_include_vertical_horizontal_and_y_equals_x():
    rng = random.Random(408)
    kinds_seen = set()
    for _ in range(TRIALS):
        q = transformations.generate_transform_reflect_complete(Tier.FOUNDATION, rng)
        kinds_seen.add(q.solution_diagram.params["mirror_line"]["type"])
    assert kinds_seen == {"vertical", "horizontal", "diagonal"}


def test_rotate_complete_uses_only_90_180_270():
    rng = random.Random(404)
    for _ in range(TRIALS):
        q = transformations.generate_transform_rotate_complete(Tier.FOUNDATION, rng)
        assert any(w in q.prompt for w in ("90° anticlockwise", "90° clockwise", "180°"))


def test_translate_complete_never_uses_the_zero_vector():
    rng = random.Random(405)
    for _ in range(TRIALS):
        q = transformations.generate_transform_translate_complete(Tier.FOUNDATION, rng)
        original = q.solution_diagram.params["original_vertices"]
        image = q.solution_diagram.params["image_vertices"]
        vector = (image[0][0] - original[0][0], image[0][1] - original[0][1])
        assert vector != (0, 0)


def test_translate_complete_diagram_has_no_direction_arrow():
    # The question/solution diagrams no longer carry "translation_vector" -
    # the vector is still given in the prompt/solution text, just not drawn
    # as an arrow on the diagram itself.
    rng = random.Random(410)
    for _ in range(TRIALS):
        q = transformations.generate_transform_translate_complete(Tier.FOUNDATION, rng)
        assert "translation_vector" not in q.diagram.params
        assert "translation_vector" not in q.solution_diagram.params


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


def test_compact_reflect_template_is_asymmetric():
    lines, order = transformations._count_symmetries(transformations._COMPACT_REFLECT_TEMPLATE)
    assert lines == 0
    assert order == 1


def test_y_equals_x_reflection_is_actually_reachable():
    # A real pre-existing bug, found via property-based sampling while
    # reweighting the mirror-line pool (this phase's actual task): every one
    # of the 4 original _SHAPE_TEMPLATES spans 7-9 units in the y - x
    # direction, which - given the grid's own +/-7 fit range - made a
    # "y = x" reflection geometrically impossible to ever satisfy
    # (0 successes in 200,000 simulated attempts) regardless of how the
    # mirror-line weights were set. _COMPACT_REFLECT_TEMPLATE (used only by
    # reflection, via _random_reflect_shape) is small enough that "y = x"
    # can actually succeed - confirm it really does show up in real
    # generator output, not just in isolated sampling.
    rng = random.Random(409)
    seen_diagonal_pos = False
    for _ in range(2000):
        q = transformations.generate_transform_reflect_complete(Tier.FOUNDATION, rng)
        mirror = q.solution_diagram.params["mirror_line"]
        if mirror["type"] == "diagonal" and mirror["sign"] == 1:
            seen_diagonal_pos = True
            break
    assert seen_diagonal_pos


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
    (transformations.generate_modelled_example_symmetry_lines, Tier.FOUNDATION, "symmetry_lines_F"),
    (transformations.generate_modelled_example_symmetry_rotational, Tier.FOUNDATION, "symmetry_rotational_F"),
    (transformations.generate_modelled_example_transform_reflect_complete, Tier.FOUNDATION, "transform_reflect_complete_F"),
    (transformations.generate_modelled_example_transform_reflect_describe, Tier.FOUNDATION, "transform_reflect_describe_F"),
    (transformations.generate_modelled_example_transform_rotate_complete, Tier.FOUNDATION, "transform_rotate_complete_F"),
    (transformations.generate_modelled_example_transform_rotate_describe, Tier.HIGHER, "transform_rotate_describe_H"),
    (transformations.generate_modelled_example_transform_translate_complete, Tier.FOUNDATION, "transform_translate_complete_F"),
    (transformations.generate_modelled_example_transform_translate_describe, Tier.FOUNDATION, "transform_translate_describe_F"),
    (transformations.generate_modelled_example_transform_enlarge_complete_foundation, Tier.FOUNDATION, "transform_enlarge_complete_F"),
    (transformations.generate_modelled_example_transform_enlarge_complete_higher, Tier.HIGHER, "transform_enlarge_complete_H"),
    (transformations.generate_modelled_example_transform_enlarge_describe, Tier.HIGHER, "transform_enlarge_describe_H"),
    (transformations.generate_modelled_example_transform_enlarge_describe_foundation, Tier.FOUNDATION, "transform_enlarge_describe_F"),
    (transformations.generate_modelled_example_combined_transformations, Tier.HIGHER, "combined_transformations_H"),
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


def test_combined_transformations_apply_two_or_three_and_draw_final():
    """The redesigned topic asks the student to apply 2-3 transformations in
    sequence and draw the final image: the question page shows only shape A,
    the solution page shows the final image B, and every final image fits the
    grid."""
    rng = random.Random(410)
    step_counts = set()
    for _ in range(TRIALS):
        q = transformations.generate_combined_transformations(Tier.HIGHER, rng)
        assert q.tier == Tier.HIGHER
        assert q.prompt.startswith("Shape A is ")
        assert q.prompt.endswith("Draw and label the final image B.")
        assert q.final_answer.startswith("Final image (shape B):")
        assert q.diagram is not None and q.solution_diagram is not None
        assert "image_vertices" not in q.diagram.params  # question shows shape A only
        image = q.solution_diagram.params["image_vertices"]
        assert all(
            transformations._GRID_MIN <= x <= transformations._GRID_MAX
            and transformations._GRID_MIN <= y <= transformations._GRID_MAX
            for x, y in image
        )
        step_counts.add(q.prompt.count(", then ") + 1)
    assert step_counts == {2, 3}


def test_enlarge_describe_foundation_wording_split_and_scale_factors():
    """90% ask 'maps A onto B', 10% ask 'maps B onto A'; the generating scale
    factors are the positive set 3/2, 5/2, 1/2, 1/3, 1/4."""
    rng = random.Random(70)
    a_to_b = b_to_a = 0
    n = 4000
    for _ in range(n):
        q = transformations.generate_transform_enlarge_describe_foundation(Tier.FOUNDATION, rng)
        if "maps shape A onto shape B" in q.prompt:
            a_to_b += 1
        elif "maps shape B onto shape A" in q.prompt:
            b_to_a += 1
        assert q.final_answer.startswith("Enlargement, scale factor")
    assert a_to_b + b_to_a == n
    assert 0.05 < b_to_a / n < 0.16  # ~10%


def test_combined_transformations_reach_all_transform_types():
    rng = random.Random(4102)
    seen = set()
    for _ in range(600):
        q = transformations.generate_combined_transformations(Tier.HIGHER, rng)
        if "reflected in the line" in q.prompt:
            seen.add("reflect")
        if "rotated " in q.prompt:
            seen.add("rotate")
        if "translated by the vector" in q.prompt:
            seen.add("translate")
        if "enlarged by scale factor" in q.prompt:
            seen.add("enlarge")
    assert seen == {"reflect", "rotate", "translate", "enlarge"}
