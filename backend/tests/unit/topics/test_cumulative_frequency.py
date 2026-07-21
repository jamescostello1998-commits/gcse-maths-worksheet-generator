import random

from app.core.models import Tier
from app.topics import cumulative_frequency as cf

TRIALS = 200

GENERATORS = [
    (cf.generate_cumulative_frequency_plot, Tier.HIGHER),
    (cf.generate_cumulative_frequency_interpret, Tier.HIGHER),
    (cf.generate_box_plot_construct, Tier.HIGHER),
    (cf.generate_box_plot_interpret, Tier.HIGHER),
]

MODELLED_GENERATORS = [
    cf.generate_modelled_example_cumulative_frequency_plot,
    cf.generate_modelled_example_cumulative_frequency_interpret,
    cf.generate_modelled_example_box_plot_construct,
    cf.generate_modelled_example_box_plot_interpret,
]

TOPICS = [
    cf.TOPIC_CUMULATIVE_FREQUENCY_PLOT,
    cf.TOPIC_CUMULATIVE_FREQUENCY_INTERPRET,
    cf.TOPIC_BOX_PLOT_CONSTRUCT,
    cf.TOPIC_BOX_PLOT_INTERPRET,
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(600)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_key_space_is_wide_enough_over_300_trials():
    for generate, tier in GENERATORS:
        rng = random.Random(601)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 20, f"{generate.__name__} dedup key space too narrow: {len(keys)}"


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in TOPICS}
    assert len(ids) == 4
    for t in TOPICS:
        assert t.section == "statistics"
        assert t.group == "Cumulative Frequency & Box Plots"
        assert t.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_are_wired_up():
    for t in TOPICS:
        assert t.generate_modelled_example is not None


def test_all_modelled_examples_produce_verified_examples():
    for generate_modelled in MODELLED_GENERATORS:
        rng = random.Random(602)
        for _ in range(TRIALS):
            example = generate_modelled(Tier.HIGHER, rng)
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_cumulative_frequency_plot_diagram_blank_and_solution_complete():
    rng = random.Random(603)
    for _ in range(TRIALS):
        q = cf.generate_cumulative_frequency_plot(Tier.HIGHER, rng)
        assert q.diagram.params.get("blank") is True
        assert q.solution_diagram is not None
        assert not q.solution_diagram.params.get("blank")
        assert q.solution_diagram.params["points"] == q.diagram.params["points"]


def test_box_plot_construct_has_no_question_diagram_but_a_solution_diagram():
    rng = random.Random(604)
    for _ in range(TRIALS):
        q = cf.generate_box_plot_construct(Tier.HIGHER, rng)
        assert q.diagram is None
        assert q.solution_diagram is not None
        assert q.solution_diagram.kind == "box_plot"
        assert len(q.solution_diagram.params["box_plots"]) == 1


def test_box_plot_interpret_sometimes_compares_two_box_plots():
    rng = random.Random(605)
    counts = {"single": 0, "compare": 0}
    for _ in range(TRIALS):
        q = cf.generate_box_plot_interpret(Tier.HIGHER, rng)
        n = len(q.diagram.params["box_plots"])
        counts["single" if n == 1 else "compare"] += 1
    assert counts["single"] > 0
    assert counts["compare"] > 0


def test_box_plot_interpret_comparison_labels_are_present():
    rng = random.Random(606)
    for _ in range(TRIALS):
        q = cf.generate_box_plot_interpret(Tier.HIGHER, rng)
        if len(q.diagram.params["box_plots"]) == 2:
            labels = [bp.get("label") for bp in q.diagram.params["box_plots"]]
            assert all(labels)
            assert len(set(labels)) == 2
