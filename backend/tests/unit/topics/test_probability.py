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
    ]:
        rng = random.Random(211)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.diagram is not None
            assert q.diagram.kind == "bag_of_counters"
            for colour, count in q.diagram.params["counts"].items():
                assert f"{count} {colour}" in q.prompt


def test_conditional_attaches_a_blank_question_and_solved_solution_tree():
    rng = random.Random(2110)
    for _ in range(TRIALS):
        q = probability.generate_conditional_without_replacement(Tier.HIGHER, rng)
        assert q.diagram is not None and q.diagram.kind == "tree_diagram"
        assert all(prob == "" for _label, prob in q.diagram.params["stage1"])
        assert all(
            prob == "" for branch in q.diagram.params["stage2"] for _label, prob in branch
        )
        assert q.solution_diagram is not None and q.solution_diagram.kind == "tree_diagram"
        assert all(prob != "" for _label, prob in q.solution_diagram.params["stage1"])
        assert all(
            prob != "" for branch in q.solution_diagram.params["stage2"] for _label, prob in branch
        )


def test_combined_dice_never_attaches_a_diagram():
    rng = random.Random(212)
    for _ in range(TRIALS):
        q = probability.generate_combined_dice(Tier.HIGHER, rng)
        assert q.diagram is None


def test_and_or_rule_always_attaches_a_diagram_of_the_right_kind():
    rng = random.Random(213)
    seen_kinds = set()
    for _ in range(TRIALS):
        q = probability.generate_and_or_rule(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind in ("bag_of_counters", "event_pair")
        if q.diagram.kind == "event_pair":
            for event in (q.diagram.params["event_a"], q.diagram.params["event_b"]):
                assert event["kind"] in ("coin", "dice", "spinner")
        seen_kinds.add(q.diagram.kind)
    assert seen_kinds == {"bag_of_counters", "event_pair"}


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
        elif "A spinner has" not in q.prompt:
            assert q.diagram is None
            saw_no_diagram = True
    assert saw_dice_diagram
    assert saw_no_diagram


def test_expectation_spinner_diagram_matches_the_stated_probability():
    # dedup_key = f"expectation:spinner:{colour}:{numerator}:{denominator}:{trials}"
    rng = random.Random(2140)
    saw_diagram = False
    saw_no_diagram_large_denominator = False
    for _ in range(TRIALS):
        q = probability.generate_expectation(Tier.FOUNDATION, rng)
        if "A spinner has" not in q.prompt:
            continue
        parts = q.dedup_key.split(":")
        numerator, denominator = int(parts[3]), int(parts[4])
        if denominator <= 12:
            assert q.diagram is not None
            assert q.diagram.kind == "spinner"
            assert len(q.diagram.params["sectors"]) == denominator
            assert q.diagram.params["highlight"] == list(range(numerator))
            saw_diagram = True
        else:
            assert q.diagram is None
            saw_no_diagram_large_denominator = True
    assert saw_diagram
    assert saw_no_diagram_large_denominator


def test_listing_outcomes_attaches_a_diagram_matching_every_scenario():
    rng = random.Random(215)
    saw_spinner_diagram = False
    saw_pair_diagram = False
    saw_coin_die_diagram = False
    saw_two_coins_diagram = False
    for _ in range(TRIALS):
        q = probability.generate_listing_outcomes(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        if q.dedup_key.startswith("listing:coin_spinner"):
            assert q.diagram.kind == "spinner"
            saw_spinner_diagram = True
        elif q.dedup_key.startswith("listing:two_spinner3") or q.dedup_key.startswith("listing:spinner3_spinner4"):
            assert q.diagram.kind == "spinner_pair"
            assert "sectors_a" in q.diagram.params
            assert "sectors_b" in q.diagram.params
            saw_pair_diagram = True
        elif q.dedup_key.startswith("listing:coin_die"):
            assert q.diagram.kind == "event_pair"
            assert q.diagram.params["event_a"]["kind"] == "coin"
            assert q.diagram.params["event_b"]["kind"] == "dice"
            saw_coin_die_diagram = True
        else:  # listing:two_coins
            assert q.diagram.kind == "coin"
            assert q.diagram.params["count"] == 2
            saw_two_coins_diagram = True
    assert saw_spinner_diagram
    assert saw_pair_diagram
    assert saw_coin_die_diagram
    assert saw_two_coins_diagram
