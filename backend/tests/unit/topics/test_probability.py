import random

from app.core.models import Tier
from app.topics import probability

TRIALS = 200

GENERATORS = [
    (probability.generate_single_event, Tier.FOUNDATION),
    (probability.generate_complement, Tier.FOUNDATION),
    (probability.generate_combined_dice, Tier.HIGHER),
    (probability.generate_conditional_without_replacement, Tier.HIGHER),
    (probability.generate_listing_outcomes, Tier.FOUNDATION),
    (probability.generate_and_or_rule, Tier.FOUNDATION),
    (probability.generate_expectation, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(70)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(72)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 20


def test_topic_definitions_have_expected_metadata():
    topics = [
        probability.TOPIC_SINGLE_EVENT,
        probability.TOPIC_COMPLEMENT,
        probability.TOPIC_COMBINED_DICE,
        probability.TOPIC_CONDITIONAL,
        probability.TOPIC_LISTING_OUTCOMES,
        probability.TOPIC_AND_OR_RULE,
        probability.TOPIC_EXPECTATION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 7
    for t in topics:
        assert t.section == "probability"
        assert t.group == "Probability"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_modelled_example_topics_are_wired_up():
    for t in (
        probability.TOPIC_SINGLE_EVENT,
        probability.TOPIC_COMPLEMENT,
        probability.TOPIC_COMBINED_DICE,
        probability.TOPIC_CONDITIONAL,
        probability.TOPIC_LISTING_OUTCOMES,
        probability.TOPIC_AND_OR_RULE,
        probability.TOPIC_EXPECTATION,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_single_event_produces_verified_examples():
    rng = random.Random(204)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_single_event(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_single_event"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_complement_produces_verified_examples():
    rng = random.Random(205)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_complement(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_complement"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_combined_dice_produces_verified_examples():
    rng = random.Random(206)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_combined_dice(Tier.HIGHER, rng)
        assert example.topic_id == "probability_combined_dice"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_conditional_produces_verified_examples():
    rng = random.Random(207)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_conditional_without_replacement(Tier.HIGHER, rng)
        assert example.topic_id == "probability_conditional"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_listing_outcomes_produces_verified_examples():
    rng = random.Random(208)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_listing_outcomes(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_listing_outcomes"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_and_or_rule_produces_verified_examples():
    rng = random.Random(209)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_and_or_rule(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_and_or_rule"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_expectation_produces_verified_examples():
    rng = random.Random(210)
    for _ in range(TRIALS):
        example = probability.generate_modelled_example_expectation(Tier.FOUNDATION, rng)
        assert example.topic_id == "probability_expectation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_bag_topics_always_attach_a_bag_diagram_matching_the_prompt():
    for generate, tier in [
        (probability.generate_single_event, Tier.FOUNDATION),
        (probability.generate_complement, Tier.FOUNDATION),
        (probability.generate_conditional_without_replacement, Tier.HIGHER),
    ]:
        rng = random.Random(211)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.diagram is not None
            assert q.diagram.kind == "bag_of_counters"
            for colour, count in q.diagram.params["counts"].items():
                assert f"{count} {colour}" in q.prompt


def test_combined_dice_always_attaches_a_two_die_diagram():
    rng = random.Random(212)
    for _ in range(TRIALS):
        q = probability.generate_combined_dice(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "dice"
        assert len(q.diagram.params["values"]) == 2
        assert all(1 <= v <= 6 for v in q.diagram.params["values"])


def test_and_or_rule_always_attaches_a_diagram_of_the_right_kind():
    rng = random.Random(213)
    seen_kinds = set()
    for _ in range(TRIALS):
        q = probability.generate_and_or_rule(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind in ("bag_of_counters", "dice", "spinner")
        seen_kinds.add(q.diagram.kind)
    assert seen_kinds == {"bag_of_counters", "dice", "spinner"}


def test_expectation_attaches_a_dice_diagram_only_for_the_die_context():
    rng = random.Random(214)
    saw_dice_diagram = False
    saw_no_diagram = False
    for _ in range(TRIALS):
        q = probability.generate_expectation(Tier.FOUNDATION, rng)
        if "A biased die has" in q.prompt:
            assert q.diagram is not None
            assert q.diagram.kind == "dice"
            saw_dice_diagram = True
        else:
            assert q.diagram is None
            saw_no_diagram = True
    assert saw_dice_diagram
    assert saw_no_diagram


def test_listing_outcomes_attaches_a_spinner_diagram_only_for_single_spinner_scenarios():
    rng = random.Random(215)
    saw_spinner_diagram = False
    saw_no_diagram = False
    for _ in range(TRIALS):
        q = probability.generate_listing_outcomes(Tier.FOUNDATION, rng)
        if q.dedup_key.startswith("listing:coin_spinner"):
            assert q.diagram is not None
            assert q.diagram.kind == "spinner"
            saw_spinner_diagram = True
        else:
            assert q.diagram is None
            saw_no_diagram = True
    assert saw_spinner_diagram
    assert saw_no_diagram
