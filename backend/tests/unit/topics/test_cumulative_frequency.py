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
        assert q.diagram.kind == "cumulative_frequency_question"
        assert q.diagram.params["boundaries"] and q.diagram.params["frequencies"]
        assert q.solution_diagram is not None
        assert not q.solution_diagram.params.get("blank")
        assert q.solution_diagram.params["points"] == q.diagram.params["points"]


def test_box_plot_construct_has_a_blank_question_diagram_and_a_solved_solution():
    rng = random.Random(604)
    for _ in range(TRIALS):
        q = cf.generate_box_plot_construct(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "box_plot"
        assert q.diagram.params.get("blank") is True
        assert q.solution_diagram is not None
        assert q.solution_diagram.kind == "box_plot"
        assert not q.solution_diagram.params.get("blank")
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


def test_grouped_table_always_starts_at_zero_with_a_bell_shaped_distribution():
    # Real GCSE cumulative frequency curves are smooth S-shaped ogives
    # starting at the origin: the first class boundary must be 0, and the
    # underlying frequencies must be unimodal (peak in the interior, never
    # at either end) so the cumulative curve rises steeply in the middle
    # rather than zigzagging.
    rng = random.Random(900)
    for _ in range(300):
        _, _, boundaries, frequencies = cf._random_grouped_table(rng)
        assert boundaries[0] == 0
        peak = max(frequencies)
        assert frequencies[0] < peak
        assert frequencies[-1] < peak
