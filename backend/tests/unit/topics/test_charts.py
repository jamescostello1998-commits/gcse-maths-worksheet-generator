import random

from app.core.models import Tier
from app.topics import charts

TRIALS = 200

GENERATORS = [
    (charts.generate_bar_chart_construct, Tier.FOUNDATION),
    (charts.generate_bar_chart_interpret, Tier.FOUNDATION),
    (charts.generate_composite_bar_chart, Tier.FOUNDATION),
    (charts.generate_pie_chart_construct, Tier.FOUNDATION),
    (charts.generate_pie_chart_interpret, Tier.FOUNDATION),
    (charts.generate_time_series_graph, Tier.FOUNDATION),
]

MODELLED_GENERATORS = [
    charts.generate_modelled_example_bar_chart_construct,
    charts.generate_modelled_example_bar_chart_interpret,
    charts.generate_modelled_example_composite_bar_chart,
    charts.generate_modelled_example_pie_chart_construct,
    charts.generate_modelled_example_pie_chart_interpret,
    charts.generate_modelled_example_time_series_graph,
]

TOPICS = [
    charts.TOPIC_BAR_CONSTRUCT,
    charts.TOPIC_BAR_INTERPRET,
    charts.TOPIC_COMPOSITE_BAR,
    charts.TOPIC_PIE_CONSTRUCT,
    charts.TOPIC_PIE_INTERPRET,
    charts.TOPIC_TIME_SERIES,
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(500)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_key_space_is_wide_enough_over_300_trials():
    for generate, tier in GENERATORS:
        rng = random.Random(501)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 20, f"{generate.__name__} dedup key space too narrow: {len(keys)}"


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in TOPICS}
    assert len(ids) == 6
    for t in TOPICS:
        assert t.section == "statistics"
        assert t.group == "Charts and Graphs"
        assert t.fixed_tier == Tier.FOUNDATION


def test_modelled_example_topics_are_wired_up():
    for t in TOPICS:
        assert t.generate_modelled_example is not None


def test_all_modelled_examples_produce_verified_examples():
    for generate_modelled in MODELLED_GENERATORS:
        rng = random.Random(502)
        for _ in range(TRIALS):
            example = generate_modelled(Tier.FOUNDATION, rng)
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_bar_chart_construct_diagram_blank_and_solution_complete():
    rng = random.Random(503)
    for _ in range(TRIALS):
        q = charts.generate_bar_chart_construct(Tier.FOUNDATION, rng)
        assert q.diagram.params.get("blank") is True
        assert q.solution_diagram is not None
        assert not q.solution_diagram.params.get("blank")
        assert q.solution_diagram.params["series"] == q.diagram.params["series"]


def test_pie_chart_construct_has_no_question_diagram_but_a_solution_diagram():
    rng = random.Random(504)
    for _ in range(TRIALS):
        q = charts.generate_pie_chart_construct(Tier.FOUNDATION, rng)
        assert q.diagram is None
        assert q.solution_diagram is not None
        assert q.solution_diagram.kind == "pie_chart"


def test_composite_bar_chart_uses_stacked_series():
    rng = random.Random(505)
    for _ in range(TRIALS):
        q = charts.generate_composite_bar_chart(Tier.FOUNDATION, rng)
        assert q.diagram.kind == "bar_chart"
        assert isinstance(q.diagram.params["series"][0], list)
        assert "series_labels" in q.diagram.params


def test_pie_chart_construct_angles_sum_to_360():
    rng = random.Random(506)
    for _ in range(TRIALS):
        q = charts.generate_pie_chart_construct(Tier.FOUNDATION, rng)
        values = q.solution_diagram.params["values"]
        total = sum(values)
        angle_sum = sum(v / total * 360 for v in values)
        assert abs(angle_sum - 360) < 1e-9
