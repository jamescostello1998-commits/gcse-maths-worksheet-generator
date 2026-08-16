import random

from app.core.models import Tier
from app.topics import forming_equations

TRIALS = 200

GENERATORS = [
    (forming_equations.generate_forming_equations_foundation, Tier.FOUNDATION),
    (forming_equations.generate_forming_equations_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(120)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_people_and_consecutive_contexts_appear_and_read_correctly():
    # Regression test for two real wording bugs caught by rendering real
    # output: "20 years old older than" (double unit - the difference
    # clause needs "years", not the self-description's "years old") and
    # "amount of moneys" (naive "+s" pluralization of a multi-word noun).
    checks = [
        (forming_equations.generate_forming_equations_foundation, Tier.FOUNDATION, "form_people", "form_consecutive"),
        (forming_equations.generate_forming_equations_higher, Tier.HIGHER, "form_people_h", "form_consecutive_h"),
    ]
    for generate, tier, people_prefix, consecutive_prefix in checks:
        rng = random.Random(41)
        people_seen = consecutive_seen = False
        for _ in range(3000):
            q = generate(tier, rng)
            if q.dedup_key.startswith(people_prefix + ":"):
                people_seen = True
                assert "years old older" not in q.prompt
                assert "years old younger" not in q.prompt
                assert "amount of moneys" not in q.prompt
            elif q.dedup_key.startswith(consecutive_prefix + ":"):
                consecutive_seen = True
                assert "consecutive" in q.prompt
                assert len(q.final_answer.split(",")) in (3, 5)
            if people_seen and consecutive_seen:
                break
        assert people_seen, f"{generate.__name__} never produced a 'people' question"
        assert consecutive_seen, f"{generate.__name__} never produced a 'consecutive' question"


_PERIMETER_SHAPE_DIAGRAM_KINDS = {
    "l_shape": "l_shape",
    "rectangle": "rectangle",
    "isosceles": "general_triangle",
    "parallelogram": "parallelogram_perimeter",
    "right_triangle": "right_triangle",
    "polygon": "regular_polygon_side",
}


def test_perimeter_higher_covers_all_six_shapes_with_matching_diagrams():
    rng = random.Random(37)
    seen = set()
    for _ in range(600):
        shape, _desc, _eq, _expand, _coeff, _const, _total, _steps, _sol, _key, diagram = (
            forming_equations._build_perimeter_higher(rng)
        )
        seen.add(shape)
        assert diagram.kind == _PERIMETER_SHAPE_DIAGRAM_KINDS[shape]
    assert seen == set(_PERIMETER_SHAPE_DIAGRAM_KINDS)


def test_topic_definitions_have_expected_metadata():
    topics = [
        forming_equations.TOPIC_FORMING_EQUATIONS_FOUNDATION,
        forming_equations.TOPIC_FORMING_EQUATIONS_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Forming and Solving Equations"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (
        forming_equations.generate_modelled_example_forming_equations_foundation,
        Tier.FOUNDATION,
        "forming_equations_F",
    ),
    (
        forming_equations.generate_modelled_example_forming_equations_higher,
        Tier.HIGHER,
        "forming_equations_H",
    ),
]


def test_all_topics_have_modelled_example_wired():
    for t in (
        forming_equations.TOPIC_FORMING_EQUATIONS_FOUNDATION,
        forming_equations.TOPIC_FORMING_EQUATIONS_HIGHER,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(220)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
