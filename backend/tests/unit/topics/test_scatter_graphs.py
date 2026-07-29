import random

from app.core.models import Tier
from app.topics import scatter_graphs

TRIALS = 300

GENERATORS = [
    (scatter_graphs.generate_scatter_graph_construct, Tier.FOUNDATION),
    (scatter_graphs.generate_scatter_graph_interpret, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(1000)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_construct_has_no_diagram_on_the_question_page_but_one_on_the_solution():
    # Same "student draws it" pattern as tree_diagram_drawing.
    rng = random.Random(1001)
    for _ in range(TRIALS):
        q = scatter_graphs.generate_scatter_graph_construct(Tier.FOUNDATION, rng)
        assert q.diagram is None
        assert q.solution_diagram is not None
        assert q.solution_diagram.kind == "scatter_graph"
        assert "best_fit" not in q.solution_diagram.params


def test_interpret_diagram_always_includes_a_line_of_best_fit():
    rng = random.Random(1002)
    for _ in range(TRIALS):
        q = scatter_graphs.generate_scatter_graph_interpret(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "scatter_graph"
        assert "best_fit" in q.diagram.params


def test_correlation_sign_matches_the_actual_plotted_points():
    # Independent re-check of the Pearson correlation sign directly from the
    # points actually returned, not just trusting the generator's own label.
    rng = random.Random(1003)
    for _ in range(TRIALS):
        q = scatter_graphs.generate_scatter_graph_construct(Tier.FOUNDATION, rng)
        points = q.solution_diagram.params["points"]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        sign = scatter_graphs._pearson_sign(xs, ys)
        if "Positive" in q.final_answer:
            assert sign == 1
        else:
            assert sign == -1


def test_dedup_keys_vary_widely():
    for generate, tier in GENERATORS:
        rng = random.Random(1004)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 90


def test_topic_definitions_have_expected_metadata():
    topics = [scatter_graphs.TOPIC_SCATTER_GRAPH_CONSTRUCT, scatter_graphs.TOPIC_SCATTER_GRAPH_INTERPRET]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "statistics"
        assert t.group == "Charts and Graphs"
        assert t.fixed_tier == Tier.FOUNDATION
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (scatter_graphs.generate_modelled_example_scatter_graph_construct, Tier.FOUNDATION, "scatter_graph_construct"),
    (scatter_graphs.generate_modelled_example_scatter_graph_interpret, Tier.FOUNDATION, "scatter_graph_interpret"),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(1005)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            assert example.diagram is not None
            assert example.diagram.kind == "scatter_graph"
