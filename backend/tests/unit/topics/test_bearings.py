import random

from app.core.models import Tier
from app.topics import bearings

TRIALS = 300

GENERATORS = [
    (bearings.generate_bearings, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(700)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "bearings"


def test_bearings_are_always_valid_compass_bearings():
    rng = random.Random(701)
    for _ in range(TRIALS):
        q = bearings.generate_bearings(Tier.HIGHER, rng)
        assert 0 <= q.diagram.params["bearing_at_A"] <= 359
        assert 0 <= q.diagram.params["bearing_at_B"] <= 359
        assert 1 <= q.diagram.params["bearing_at_A"]


def test_dedup_keys_vary_widely():
    rng = random.Random(702)
    keys = {bearings.generate_bearings(Tier.HIGHER, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.95


def test_topic_definitions_have_expected_metadata():
    t = bearings.TOPIC_BEARINGS_COSINE_RULE
    assert t.id == "bearings_cosine_rule_H"
    assert t.section == "geometry"
    assert t.group == "Bearings"
    assert t.fixed_tier == Tier.HIGHER
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(703)
    for _ in range(TRIALS):
        ex = bearings.generate_modelled_example_bearings(Tier.HIGHER, rng)
        assert ex.topic_id == "bearings_cosine_rule_H"
        assert ex.tier == Tier.HIGHER
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
        assert ex.diagram.kind == "bearings"
        # Unlike the plain generator (which shows "x km" - the unknown to be
        # found), the modelled example's diagram states the real answer.
        assert ex.diagram.params["unknown_label"] == ex.final_answer


def test_bearings_foundation_produces_valid_verified_questions():
    rng = random.Random(710)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_foundation(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer
        assert q.diagram is not None
        assert q.diagram.kind == "bearings"
        assert q.diagram.params.get("bearing_at_B") is None  # single-leg diagram mode


def test_bearings_foundation_back_bearing_is_always_180_degrees_different():
    rng = random.Random(711)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_foundation(Tier.FOUNDATION, rng)
        if "Find the bearing of A from B" not in q.prompt:
            continue
        given = q.diagram.params["bearing_at_A"]
        answer_bearing = int(q.final_answer.rstrip("°"))
        assert abs((answer_bearing - given) % 360) in (180,)


def test_bearings_foundation_solution_diagram_reveals_the_back_bearing_arc():
    rng = random.Random(712)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_foundation(Tier.FOUNDATION, rng)
        if q.solution_diagram is None:
            continue
        assert q.solution_diagram.params["answer_bearing_at_B"] == int(q.final_answer.rstrip("°"))


def test_bearings_foundation_dedup_keys_vary_widely():
    rng = random.Random(713)
    keys = {bearings.generate_bearings_foundation(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.6


def test_bearings_foundation_topic_definition_metadata():
    t = bearings.TOPIC_BEARINGS_FOUNDATION
    assert t.id == "bearings_F"
    assert t.section == "geometry"
    assert t.group == "Bearings"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_bearings_cosine_rule_reaches_all_three_rounding_phrasings():
    generators = [bearings.generate_bearings]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate in generators:
        rng = random.Random(750)
        seen = set()
        for _ in range(200):
            q = generate(Tier.HIGHER, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings


def test_bearings_foundation_modelled_examples_are_valid():
    rng = random.Random(714)
    for _ in range(TRIALS):
        ex = bearings.generate_modelled_example_bearings_foundation(Tier.FOUNDATION, rng)
        assert ex.topic_id == "bearings_F"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
        assert ex.diagram.kind == "bearings"


# ---------------------------------------------------------------------------
# bearings_back_bearing_F
# ---------------------------------------------------------------------------

def test_back_bearing_produces_valid_verified_questions_with_no_diagram():
    rng = random.Random(720)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_back_bearing(Tier.FOUNDATION, rng)
        assert q.topic_id == "bearings_back_bearing_F"
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer
        assert q.diagram is None


def test_back_bearing_is_always_exactly_180_degrees_different():
    rng = random.Random(721)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_back_bearing(Tier.FOUNDATION, rng)
        given = int(q.prompt.split(" is ")[1].split("°")[0])
        answer = int(q.final_answer.rstrip("°"))
        assert (answer - given) % 360 in (180,)


def test_back_bearing_direction_varies_both_ways():
    rng = random.Random(722)
    forward_first = 0
    other_first = 0
    for _ in range(TRIALS):
        q = bearings.generate_bearings_back_bearing(Tier.FOUNDATION, rng)
        # "The bearing of X from Y is ..." - which letter comes first (the
        # "given" direction) should vary, confirming genuine bidirectionality.
        first_letter = q.prompt.split(" from ")[1][0]
        second_letter = q.prompt.split("bearing of ")[1][0]
        if first_letter < second_letter:
            forward_first += 1
        else:
            other_first += 1
    assert forward_first > 0
    assert other_first > 0


def test_back_bearing_dedup_keys_vary_widely():
    rng = random.Random(723)
    keys = {bearings.generate_bearings_back_bearing(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.9


def test_back_bearing_topic_definition_metadata():
    t = bearings.TOPIC_BEARINGS_BACK_BEARING
    assert t.id == "bearings_back_bearing_F"
    assert t.section == "geometry"
    assert t.group == "Bearings"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_back_bearing_modelled_examples_are_valid():
    rng = random.Random(724)
    for _ in range(TRIALS):
        ex = bearings.generate_modelled_example_bearings_back_bearing(Tier.FOUNDATION, rng)
        assert ex.topic_id == "bearings_back_bearing_F"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is None


# ---------------------------------------------------------------------------
# bearings_angle_facts_F
# ---------------------------------------------------------------------------

def test_angle_facts_produces_valid_verified_questions_with_a_diagram():
    rng = random.Random(730)
    for _ in range(TRIALS):
        q = bearings.generate_bearings_angle_facts(Tier.FOUNDATION, rng)
        assert q.topic_id == "bearings_angle_facts_F"
        assert q.tier == Tier.FOUNDATION
        assert q.prompt
        assert q.solution_steps
        assert q.final_answer
        assert q.diagram is not None
        assert q.diagram.kind in ("bearings_two_rays", "bearings")


def test_angle_facts_covers_both_branches():
    rng = random.Random(731)
    branches = {q.dedup_key.split(":")[0] for q in (
        bearings.generate_bearings_angle_facts(Tier.FOUNDATION, rng) for _ in range(TRIALS)
    )}
    assert branches == {"angle_facts_around_point", "angle_facts_co_interior"}


def test_angle_facts_around_point_answer_is_a_valid_bearing_and_wraps_360():
    rng = random.Random(732)
    for _ in range(TRIALS):
        c = bearings._around_point_case(rng)
        answer_deg = int(c["answer"].rstrip("°"))
        assert 0 <= answer_deg <= 359
        # The whole point of this branch is that the turn genuinely crosses
        # north (wraps past 0/360) - confirmed structurally by the branch's
        # own construction (it only accepts a wrap-around case), so the
        # raw un-wrapped total must fall outside [0, 360).
        if c["direction"] == "clockwise":
            raw = c["bearing_b"] + c["turn_deg"]
        else:
            raw = c["bearing_b"] - c["turn_deg"]
        assert raw > 360 or raw < 0


def test_angle_facts_co_interior_answer_matches_the_ordinary_back_bearing_rule():
    rng = random.Random(733)
    for _ in range(TRIALS):
        c = bearings._co_interior_case(rng)
        bearing_pq = int(c["prompt"].split(" is ")[1].split("°")[0])
        answer_deg = int(c["answer"].rstrip("°"))
        assert (answer_deg - bearing_pq) % 360 == 180


def test_angle_facts_dedup_keys_vary_widely():
    rng = random.Random(734)
    keys = {bearings.generate_bearings_angle_facts(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > TRIALS * 0.9


def test_angle_facts_topic_definition_metadata():
    t = bearings.TOPIC_BEARINGS_ANGLE_FACTS
    assert t.id == "bearings_angle_facts_F"
    assert t.section == "geometry"
    assert t.group == "Bearings"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_angle_facts_modelled_examples_are_valid():
    rng = random.Random(735)
    for _ in range(TRIALS):
        ex = bearings.generate_modelled_example_bearings_angle_facts(Tier.FOUNDATION, rng)
        assert ex.topic_id == "bearings_angle_facts_F"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
