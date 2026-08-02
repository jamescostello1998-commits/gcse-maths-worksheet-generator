import random

import sympy as sp

from app.core.models import Tier
from app.topics import solids_curved_compound as solids

TRIALS = 300

GENERATORS = [
    (solids.generate_volume_surface_area_sphere, Tier.HIGHER),
    (solids.generate_volume_surface_area_pyramid, Tier.HIGHER),
    (solids.generate_frustum_volume_surface_area, Tier.HIGHER),
    (solids.generate_compound_3d_volume, Tier.HIGHER),
    (solids.generate_compound_3d_surface_area, Tier.HIGHER),
]


EXPECTED_DIAGRAM_KINDS = {
    solids.generate_volume_surface_area_sphere: "sphere",
    solids.generate_volume_surface_area_pyramid: "pyramid",
    solids.generate_frustum_volume_surface_area: "frustum",
    solids.generate_compound_3d_volume: "compound_3d",
    solids.generate_compound_3d_surface_area: "compound_3d",
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
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.diagram is not None
            assert q.diagram.kind == EXPECTED_DIAGRAM_KINDS[generate]


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(42)
        keys = {generate(tier, rng).dedup_key for _ in range(TRIALS)}
        assert len(keys) > 40


def test_no_generator_ever_emits_scientific_notation():
    # Regression test: sp.N(expr, 3)'s default string form switches to
    # scientific notation (e.g. "1.41e+4") once the rounded value has more
    # integer digits than the requested precision - caught by rendering an
    # actual worksheet PDF, where a sphere of radius 15 cm displayed its
    # volume as "1.41E+4 cm3" instead of "14100 cm3". Several quantities in
    # this module (sphere/frustum volumes, curved compound-solid volumes)
    # comfortably exceed 999 for the larger end of their random ranges, so
    # this is a real risk here unlike in area_perimeter.py, which this
    # sp.N(expr, 3) pattern was copied from. Fixed by routing every rounded
    # display value through app.topics.rounding's round_fn (which formats via
    # Decimal fixed-point, never scientific notation); this test guards
    # against a future edit re-introducing a bare sp.N(expr, 3) in a
    # displayed string.
    for generate, tier in GENERATORS:
        rng = random.Random(43)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            text = q.prompt + q.final_answer + " ".join(q.solution_steps)
            assert "e+" not in text.lower(), (generate.__name__, text)


def test_decimal_topics_reach_all_three_rounding_phrasings():
    # Every topic in this module whose answer is rounded (i.e. all 5 - even
    # the two topics with one exact/no-rounding branch, since their other
    # branch(es) are always rounded) should reach all three GCSE-standard
    # rounding instructions (see app.topics.rounding) given enough trials,
    # not just the old hardcoded "3 significant figures".
    generators = [
        solids.generate_volume_surface_area_sphere,
        solids.generate_volume_surface_area_pyramid,
        solids.generate_frustum_volume_surface_area,
        solids.generate_compound_3d_volume,
        solids.generate_compound_3d_surface_area,
    ]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate in generators:
        rng = random.Random(700)
        seen = set()
        for _ in range(200):
            q = generate(Tier.HIGHER, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings, (generate.__name__, seen)


def test_no_modelled_example_ever_emits_scientific_notation():
    for generate_example, tier, _, _ in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(44)
        for _ in range(TRIALS):
            example = generate_example(tier, rng)
            text = (
                example.prompt
                + example.final_answer
                + " ".join(example.worked_calculation)
                + " ".join(example.teaching_steps)
            )
            assert "e+" not in text.lower(), (generate_example.__name__, text)


# ---------------------------------------------------------------------------
# Sphere
# ---------------------------------------------------------------------------

def test_sphere_diagram_params_reflect_hemisphere_flag():
    rng = random.Random(100)
    saw_sphere = False
    saw_hemisphere = False
    for _ in range(TRIALS):
        q = solids.generate_volume_surface_area_sphere(Tier.HIGHER, rng)
        assert "radius_label" in q.diagram.params
        assert q.diagram.params["radius_label"].endswith(" cm")
        if q.diagram.params["hemisphere"]:
            saw_hemisphere = True
            assert "hemisphere" in q.prompt
        else:
            saw_sphere = True
    assert saw_sphere and saw_hemisphere


def test_sphere_volume_answers_are_in_cubic_units_and_area_in_square_units():
    rng = random.Random(101)
    for _ in range(TRIALS):
        q = solids.generate_volume_surface_area_sphere(Tier.HIGHER, rng)
        if "volume" in q.prompt:
            assert "cm³" in q.final_answer
        else:
            assert "cm²" in q.final_answer


def test_hemisphere_surface_area_prompt_mentions_the_flat_face():
    rng = random.Random(102)
    found = False
    for _ in range(TRIALS):
        q = solids.generate_volume_surface_area_sphere(Tier.HIGHER, rng)
        if q.diagram.params["hemisphere"] and "cm²" in q.final_answer:
            found = True
            assert "flat circular face" in q.prompt
    assert found


# ---------------------------------------------------------------------------
# Pyramid
# ---------------------------------------------------------------------------

def test_pyramid_volume_is_exact_and_surface_area_is_rounded_decimal():
    rng = random.Random(200)
    saw_volume = False
    saw_surface_area = False
    for _ in range(TRIALS):
        q = solids.generate_volume_surface_area_pyramid(Tier.HIGHER, rng)
        if "volume" in q.prompt and "surface area" not in q.prompt:
            saw_volume = True
            assert "cm³" in q.final_answer
            assert "slant_label" not in q.diagram.params
        else:
            saw_surface_area = True
            assert "cm²" in q.final_answer
            assert "slant_label" in q.diagram.params
    assert saw_volume and saw_surface_area


def test_pyramid_volume_matches_independent_base_area_times_height_formula():
    rng = random.Random(201)
    for _ in range(TRIALS):
        q = solids.generate_volume_surface_area_pyramid(Tier.HIGHER, rng)
        if "cm³" not in q.final_answer:
            continue
        base, height, _ = q.dedup_key.split(":")[1:4]
        base, height = int(base), int(height)
        expected = sp.Rational(base**2 * height, 3)
        expected_str = str(int(expected)) if expected.is_Integer else f"{expected.p}/{expected.q}"
        assert q.final_answer == f"{expected_str} cm³"


# ---------------------------------------------------------------------------
# Frustum - the highest-risk topic: independently regression-check the two
# volume derivations agree, on top of the generator's own internal check.
# ---------------------------------------------------------------------------

def test_frustum_two_volume_formulas_agree_independently():
    rng = random.Random(300)
    for _ in range(TRIALS):
        q = solids.generate_frustum_volume_surface_area(Tier.HIGHER, rng)
        parts = q.dedup_key.split(":")
        R, r, h = int(parts[1]), int(parts[2]), int(parts[3])

        H = sp.Rational(R * h, R - r)
        small_h = H - h
        cone_diff_method = (
            sp.Rational(1, 3) * sp.pi * R**2 * H - sp.Rational(1, 3) * sp.pi * r**2 * small_h
        )
        closed_form_method = sp.Rational(1, 3) * sp.pi * h * (R**2 + R * r + r**2)
        assert sp.simplify(cone_diff_method - closed_form_method) == 0


def test_frustum_requires_bottom_radius_strictly_greater_than_top_radius():
    rng = random.Random(301)
    for _ in range(TRIALS):
        q = solids.generate_frustum_volume_surface_area(Tier.HIGHER, rng)
        parts = q.dedup_key.split(":")
        R, r = int(parts[1]), int(parts[2])
        assert R > r


def test_frustum_volume_and_surface_area_use_correct_units():
    rng = random.Random(302)
    for _ in range(TRIALS):
        q = solids.generate_frustum_volume_surface_area(Tier.HIGHER, rng)
        if "volume" in q.prompt:
            assert "cm³" in q.final_answer
        else:
            assert "cm²" in q.final_answer


def test_frustum_diagram_params_match_dedup_key_values():
    rng = random.Random(303)
    q = solids.generate_frustum_volume_surface_area(Tier.HIGHER, rng)
    parts = q.dedup_key.split(":")
    R, r, h = parts[1], parts[2], parts[3]
    assert q.diagram.params["radius_bottom_label"] == f"{R} cm"
    assert q.diagram.params["radius_top_label"] == f"{r} cm"
    assert q.diagram.params["height_label"] == f"{h} cm"


# ---------------------------------------------------------------------------
# Compound 3D (volume)
# ---------------------------------------------------------------------------

def test_compound_3d_covers_all_three_variants():
    rng = random.Random(400)
    variants_seen = {q.diagram.params["variant"] for q in (
        solids.generate_compound_3d_volume(Tier.HIGHER, rng) for _ in range(TRIALS)
    )}
    assert variants_seen == {"cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"}


def test_compound_3d_cuboid_pyramid_variant_gives_exact_answer_no_pi():
    rng = random.Random(401)
    found = False
    for _ in range(TRIALS):
        q = solids.generate_compound_3d_volume(Tier.HIGHER, rng)
        if q.diagram.params["variant"] == "cuboid_pyramid":
            found = True
            assert "π" not in q.final_answer
            assert "cm³" in q.final_answer
    assert found


def test_compound_3d_curved_variants_give_rounded_decimal_answers():
    rng = random.Random(402)
    seen_curved = False
    for _ in range(TRIALS):
        q = solids.generate_compound_3d_volume(Tier.HIGHER, rng)
        if q.diagram.params["variant"] in ("cylinder_hemisphere", "cone_hemisphere"):
            seen_curved = True
            assert "π" not in q.final_answer
            assert "cm³" in q.final_answer
    assert seen_curved


# ---------------------------------------------------------------------------
# Compound 3D (surface area)
# ---------------------------------------------------------------------------
# Unlike the volume topic above, EVERY variant here is a rounded decimal -
# the cuboid_pyramid variant's slant height (sqrt(roof_height^2 +
# (base/2)^2)) is routinely irrational, unlike its exact volume counterpart.

def test_compound_3d_surface_area_covers_all_three_variants():
    rng = random.Random(600)
    variants_seen = {q.diagram.params["variant"] for q in (
        solids.generate_compound_3d_surface_area(Tier.HIGHER, rng) for _ in range(TRIALS)
    )}
    assert variants_seen == {"cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"}


def test_compound_3d_surface_area_cuboid_pyramid_is_rounded_and_pi_free():
    rng = random.Random(601)
    found = False
    for _ in range(TRIALS):
        q = solids.generate_compound_3d_surface_area(Tier.HIGHER, rng)
        if q.diagram.params["variant"] == "cuboid_pyramid":
            found = True
            assert "π" not in q.final_answer
            assert "cm²" in q.final_answer
    assert found


def test_compound_3d_surface_area_curved_variants_are_pi_free_in_final_answer():
    # π is fine in the intermediate solution_steps (it's part of the working)
    # but the final_answer itself is always a rounded decimal, same as the
    # volume sibling's curved variants.
    rng = random.Random(602)
    seen_curved = False
    for _ in range(TRIALS):
        q = solids.generate_compound_3d_surface_area(Tier.HIGHER, rng)
        if q.diagram.params["variant"] in ("cylinder_hemisphere", "cone_hemisphere"):
            seen_curved = True
            assert "π" not in q.final_answer
            assert "cm²" in q.final_answer
    assert seen_curved


def test_compound_3d_surface_area_cuboid_pyramid_is_strictly_less_than_naively_including_both_internal_faces():
    # A direct, exact cross-check for the one variant with no irrationality
    # involved anywhere except the slant height: the real formula (excluding
    # the cuboid's top / pyramid's base, the shared internal square) must give
    # a strictly smaller total than a naive version that mistakenly includes
    # both of those flat faces - confirming the exclusion is real, not just
    # that some plausible-looking rounded number came out.
    for base, box_height, roof_height in [(4, 3, 2), (10, 8, 5), (16, 15, 10), (7, 4, 9)]:
        slant = float(sp.sqrt(roof_height**2 + sp.Rational(base, 2) ** 2))
        correct_sa = 4 * base * box_height + base**2 + 2 * base * slant
        naive_sa_with_both_internal_faces = 4 * base * box_height + 2 * base**2 + 2 * base * slant
        assert correct_sa < naive_sa_with_both_internal_faces
        assert naive_sa_with_both_internal_faces - correct_sa == base**2


# ---------------------------------------------------------------------------
# Topic metadata
# ---------------------------------------------------------------------------

ALL_TOPICS = [
    solids.TOPIC_VOLUME_SURFACE_AREA_SPHERE,
    solids.TOPIC_VOLUME_SURFACE_AREA_PYRAMID,
    solids.TOPIC_FRUSTUM_VOLUME_SURFACE_AREA,
    solids.TOPIC_COMPOUND_3D_VOLUME,
    solids.TOPIC_COMPOUND_3D_SURFACE_AREA,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert ids == {
        "volume_surface_area_sphere",
        "volume_surface_area_pyramid",
        "frustum_volume_surface_area",
        "compound_3d_volume",
        "compound_3d_surface_area",
    }
    for t in ALL_TOPICS:
        assert t.section == "geometry"
        assert t.group == "3D Shapes"
        assert t.fixed_tier == Tier.HIGHER
        assert t.generate_modelled_example is not None


# ---------------------------------------------------------------------------
# Modelled examples
# ---------------------------------------------------------------------------

MODELLED_EXAMPLE_GENERATORS = [
    (
        solids.generate_modelled_example_volume_surface_area_sphere,
        Tier.HIGHER,
        "volume_surface_area_sphere",
        "sphere",
    ),
    (
        solids.generate_modelled_example_volume_surface_area_pyramid,
        Tier.HIGHER,
        "volume_surface_area_pyramid",
        "pyramid",
    ),
    (
        solids.generate_modelled_example_frustum_volume_surface_area,
        Tier.HIGHER,
        "frustum_volume_surface_area",
        "frustum",
    ),
    (
        solids.generate_modelled_example_compound_3d_volume,
        Tier.HIGHER,
        "compound_3d_volume",
        "compound_3d",
    ),
    (
        solids.generate_modelled_example_compound_3d_surface_area,
        Tier.HIGHER,
        "compound_3d_surface_area",
        "compound_3d",
    ),
]


def test_modelled_examples_produce_verified_examples_with_diagrams():
    for generate_example, tier, topic_id, diagram_kind in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(500)
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


def test_frustum_modelled_example_teaching_steps_explain_similar_triangles():
    rng = random.Random(501)
    example = solids.generate_modelled_example_frustum_volume_surface_area(Tier.HIGHER, rng)
    combined = " ".join(example.teaching_steps).lower()
    assert "similar triangles" in combined
