import random

from app.core.models import Tier
from app.topics import tree_diagrams

TRIALS = 200

GENERATORS = [
    (tree_diagrams.generate_tree_diagram_independent, Tier.FOUNDATION),
    (tree_diagrams.generate_tree_diagram_dependent, Tier.HIGHER),
    (tree_diagrams.generate_tree_diagram_drawing, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(330)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_interpreting_generators_show_a_tree_diagram_on_the_question():
    rng = random.Random(331)
    for _ in range(TRIALS):
        q_indep = tree_diagrams.generate_tree_diagram_independent(Tier.FOUNDATION, rng)
        q_dep = tree_diagrams.generate_tree_diagram_dependent(Tier.HIGHER, rng)
        assert q_indep.diagram is not None and q_indep.diagram.kind == "tree_diagram"
        assert q_dep.diagram is not None and q_dep.diagram.kind == "tree_diagram"
        assert "leaf_probs" in q_dep.diagram.params


def test_drawing_generator_has_no_question_diagram_but_a_solution_diagram():
    rng = random.Random(332)
    for _ in range(TRIALS):
        q = tree_diagrams.generate_tree_diagram_drawing(Tier.FOUNDATION, rng)
        assert q.diagram is None
        assert q.solution_diagram is not None
        assert q.solution_diagram.kind == "tree_diagram"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(333)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        tree_diagrams.TOPIC_TREE_INDEPENDENT,
        tree_diagrams.TOPIC_TREE_DEPENDENT,
        tree_diagrams.TOPIC_TREE_DRAWING,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "probability"
        assert t.group == "Tree Diagrams"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert tree_diagrams.TOPIC_TREE_DRAWING.question_count == 5
    assert tree_diagrams.TOPIC_TREE_INDEPENDENT.question_count is None
    assert tree_diagrams.TOPIC_TREE_DEPENDENT.question_count is None
