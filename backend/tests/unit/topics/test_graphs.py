import random

from app.core.models import Tier
from app.topics import graphs

TRIALS = 200

GENERATORS = [
    (graphs.generate_plot_straight_line, Tier.FOUNDATION),
    (graphs.generate_plot_quadratic, Tier.FOUNDATION),
    (graphs.generate_plot_cubic, Tier.HIGHER),
    (graphs.generate_plot_reciprocal, Tier.HIGHER),
    (graphs.generate_plot_distance_time, Tier.FOUNDATION),
    (graphs.generate_line_equation_from_graph, Tier.FOUNDATION),
    (graphs.generate_parallel_lines_equation, Tier.FOUNDATION),
    (graphs.generate_perpendicular_lines_equation, Tier.HIGHER),
    (graphs.generate_distance_time_interpret, Tier.FOUNDATION),
    (graphs.generate_velocity_time_interpret, Tier.HIGHER),
    (graphs.generate_graph_transformations, Tier.HIGHER),
]

PLOTTING_GENERATORS = [
    (graphs.generate_plot_straight_line, Tier.FOUNDATION),
    (graphs.generate_plot_quadratic, Tier.FOUNDATION),
    (graphs.generate_plot_cubic, Tier.HIGHER),
    (graphs.generate_plot_reciprocal, Tier.HIGHER),
    (graphs.generate_plot_distance_time, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(230)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_plotting_generators_provide_blank_axes_on_the_question_and_a_completed_graph_on_the_solution():
    for generate, tier in PLOTTING_GENERATORS:
        rng = random.Random(231)
        for _ in range(20):
            q = generate(tier, rng)
            assert q.diagram is not None
            assert q.diagram.params.get("blank") is True
            assert q.solution_diagram is not None
            assert not q.solution_diagram.params.get("blank", False)


def test_line_equation_from_graph_diagram_shows_the_two_marked_points():
    rng = random.Random(232)
    for _ in range(TRIALS):
        q = graphs.generate_line_equation_from_graph(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "function_graph"
        assert len(q.diagram.params["table_points"]) == 2


def test_graph_transformations_diagram_matches_notation():
    rng = random.Random(233)
    for _ in range(TRIALS):
        q = graphs.generate_graph_transformations(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "graph_transformation"
        assert q.diagram.params["transformed_label"] in (q.prompt + q.final_answer)


def test_real_life_graph_diagrams_use_piecewise_graph_kind():
    rng = random.Random(234)
    for _ in range(TRIALS):
        q_dt = graphs.generate_distance_time_interpret(Tier.FOUNDATION, rng)
        q_vt = graphs.generate_velocity_time_interpret(Tier.HIGHER, rng)
        assert q_dt.diagram.kind == "piecewise_graph"
        assert q_vt.diagram.kind == "piecewise_graph"


_20_QUESTION_GENERATORS = [
    (generate, tier) for generate, tier in GENERATORS
    if generate not in dict(PLOTTING_GENERATORS)
]


def test_dedup_keys_vary_per_generator():
    for generate, tier in _20_QUESTION_GENERATORS:
        rng = random.Random(235)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_dedup_keys_vary_per_plotting_generator():
    # These topics only ever generate 5 questions per worksheet, so their
    # dedup-key pool just needs to comfortably clear 5, not 20.
    for generate, tier in PLOTTING_GENERATORS:
        rng = random.Random(236)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) >= 8


def test_topic_definitions_have_expected_metadata():
    topics = [
        graphs.TOPIC_PLOT_STRAIGHT_LINE,
        graphs.TOPIC_PLOT_QUADRATIC,
        graphs.TOPIC_PLOT_CUBIC,
        graphs.TOPIC_PLOT_RECIPROCAL,
        graphs.TOPIC_PLOT_DISTANCE_TIME,
        graphs.TOPIC_LINE_EQUATION_FROM_GRAPH,
        graphs.TOPIC_PARALLEL_LINES_EQUATION,
        graphs.TOPIC_PERPENDICULAR_LINES_EQUATION,
        graphs.TOPIC_DISTANCE_TIME_INTERPRET,
        graphs.TOPIC_VELOCITY_TIME_INTERPRET,
        graphs.TOPIC_GRAPH_TRANSFORMATIONS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 11
    for t in topics:
        assert t.section == "algebra"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)

    plotting_topics = [
        graphs.TOPIC_PLOT_STRAIGHT_LINE,
        graphs.TOPIC_PLOT_QUADRATIC,
        graphs.TOPIC_PLOT_CUBIC,
        graphs.TOPIC_PLOT_RECIPROCAL,
        graphs.TOPIC_PLOT_DISTANCE_TIME,
    ]
    for t in plotting_topics:
        assert t.group == "Plotting Graphs"
        assert t.question_count == 5

    non_plotting_topics = [t for t in topics if t not in plotting_topics]
    for t in non_plotting_topics:
        assert t.question_count is None


MODELLED_EXAMPLE_GENERATORS = [
    (graphs.generate_modelled_example_plot_straight_line, Tier.FOUNDATION, "plot_straight_line"),
    (graphs.generate_modelled_example_plot_quadratic, Tier.FOUNDATION, "plot_quadratic"),
    (graphs.generate_modelled_example_plot_cubic, Tier.HIGHER, "plot_cubic"),
    (graphs.generate_modelled_example_plot_reciprocal, Tier.HIGHER, "plot_reciprocal"),
    (graphs.generate_modelled_example_plot_distance_time, Tier.FOUNDATION, "plot_distance_time"),
    (graphs.generate_modelled_example_line_equation_from_graph, Tier.FOUNDATION, "line_equation_from_graph"),
    (graphs.generate_modelled_example_parallel_lines_equation, Tier.FOUNDATION, "parallel_lines_equation"),
    (graphs.generate_modelled_example_perpendicular_lines_equation, Tier.HIGHER, "perpendicular_lines_equation"),
    (graphs.generate_modelled_example_distance_time_interpret, Tier.FOUNDATION, "distance_time_interpret"),
    (graphs.generate_modelled_example_velocity_time_interpret, Tier.HIGHER, "velocity_time_interpret"),
    (graphs.generate_modelled_example_graph_transformations, Tier.HIGHER, "graph_transformations"),
]


def test_all_topics_have_modelled_example_wired():
    topics = [
        graphs.TOPIC_PLOT_STRAIGHT_LINE,
        graphs.TOPIC_PLOT_QUADRATIC,
        graphs.TOPIC_PLOT_CUBIC,
        graphs.TOPIC_PLOT_RECIPROCAL,
        graphs.TOPIC_PLOT_DISTANCE_TIME,
        graphs.TOPIC_LINE_EQUATION_FROM_GRAPH,
        graphs.TOPIC_PARALLEL_LINES_EQUATION,
        graphs.TOPIC_PERPENDICULAR_LINES_EQUATION,
        graphs.TOPIC_DISTANCE_TIME_INTERPRET,
        graphs.TOPIC_VELOCITY_TIME_INTERPRET,
        graphs.TOPIC_GRAPH_TRANSFORMATIONS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


_NO_DIAGRAM_TOPIC_IDS = {"parallel_lines_equation", "perpendicular_lines_equation"}


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(330)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            if topic_id not in _NO_DIAGRAM_TOPIC_IDS:
                assert example.diagram is not None


def test_modelled_example_plotting_diagrams_are_never_blank():
    plotting_generators = MODELLED_EXAMPLE_GENERATORS[:5]
    for generate, tier, _ in plotting_generators:
        rng = random.Random(331)
        for _ in range(20):
            example = generate(tier, rng)
            assert not example.diagram.params.get("blank", False)
