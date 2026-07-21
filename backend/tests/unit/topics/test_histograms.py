import random

from app.core.models import Tier
from app.topics import histograms as h

TRIALS = 200

GENERATORS = [
    (h.generate_histogram_plot, Tier.HIGHER),
    (h.generate_histogram_interpret, Tier.HIGHER),
]

MODELLED_GENERATORS = [
    h.generate_modelled_example_histogram_plot,
    h.generate_modelled_example_histogram_interpret,
]

TOPICS = [h.TOPIC_HISTOGRAM_PLOT, h.TOPIC_HISTOGRAM_INTERPRET]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(700)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_key_space_is_wide_enough_over_300_trials():
    for generate, tier in GENERATORS:
        rng = random.Random(701)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 20, f"{generate.__name__} dedup key space too narrow: {len(keys)}"


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in TOPICS}
    assert len(ids) == 2
    for t in TOPICS:
        assert t.section == "statistics"
        assert t.group == "Histograms"
        assert t.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_are_wired_up():
    for t in TOPICS:
        assert t.generate_modelled_example is not None


def test_all_modelled_examples_produce_verified_examples():
    for generate_modelled in MODELLED_GENERATORS:
        rng = random.Random(702)
        for _ in range(TRIALS):
            example = generate_modelled(Tier.HIGHER, rng)
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_histogram_plot_diagram_blank_and_solution_complete():
    rng = random.Random(703)
    for _ in range(TRIALS):
        q = h.generate_histogram_plot(Tier.HIGHER, rng)
        assert q.diagram.params.get("blank") is True
        assert q.solution_diagram is not None
        assert not q.solution_diagram.params.get("blank")
        assert q.solution_diagram.params["boundaries"] == q.diagram.params["boundaries"]


def test_class_widths_are_genuinely_unequal_across_generated_histograms():
    rng = random.Random(704)
    unequal_count = 0
    for _ in range(100):
        q = h.generate_histogram_plot(Tier.HIGHER, rng)
        boundaries = q.diagram.params["boundaries"]
        widths = {boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1)}
        if len(widths) > 1:
            unequal_count += 1
    assert unequal_count > 50


def test_histogram_interpret_frequency_equals_density_times_width():
    rng = random.Random(705)
    for _ in range(TRIALS):
        q = h.generate_histogram_interpret(Tier.HIGHER, rng)
        boundaries = q.diagram.params["boundaries"]
        densities = q.diagram.params["frequency_densities"]
        widths = [boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1)]
        for d, w in zip(densities, widths):
            freq = d * w
            assert abs(freq - round(freq)) < 1e-6
