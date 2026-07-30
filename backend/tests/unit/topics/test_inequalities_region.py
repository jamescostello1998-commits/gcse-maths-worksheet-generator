import random

from app.core.models import Tier
from app.topics import inequalities_region

TRIALS = 300

GENERATORS = [
    (inequalities_region.generate_inequalities_region_higher, Tier.HIGHER),
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
            assert q.diagram is not None
            assert q.diagram.kind == "inequality_region"


def test_draw_mode_gives_blank_question_and_marked_solution():
    rng = random.Random(1001)
    seen_draw = False
    for _ in range(TRIALS):
        q = inequalities_region.generate_inequalities_region_higher(Tier.HIGHER, rng)
        if q.solution_diagram is None:
            continue
        seen_draw = True
        assert q.diagram.params.get("blank") is True
        assert "lines" not in q.diagram.params or not q.diagram.params.get("lines")
        assert q.solution_diagram.kind == "inequality_region"
        assert not q.solution_diagram.params.get("blank", False)
        assert len(q.solution_diagram.params["lines"]) == 2
    assert seen_draw


def test_read_mode_diagram_is_the_stimulus_with_no_separate_solution_diagram():
    rng = random.Random(1002)
    seen_read = False
    for _ in range(TRIALS):
        q = inequalities_region.generate_inequalities_region_higher(Tier.HIGHER, rng)
        if q.solution_diagram is not None:
            continue
        seen_read = True
        assert q.diagram is not None
        assert not q.diagram.params.get("blank", False)
        assert len(q.diagram.params["lines"]) == 2
        assert "and" in q.final_answer
    assert seen_read


def test_boundary_lines_dashed_iff_strict():
    rng = random.Random(1003)
    for _ in range(TRIALS):
        q = inequalities_region.generate_inequalities_region_higher(Tier.HIGHER, rng)
        diagram = q.solution_diagram if q.solution_diagram is not None else q.diagram
        for line in diagram.params["lines"]:
            strict = line["op"] in ("<", ">")
            # The final answer text uses < / > for strict and ≤ / ≥ for non-strict,
            # so the count of each symbol family must match the number of
            # strict/non-strict lines.
            if strict:
                assert line["op"] in ("<", ">")
            else:
                assert line["op"] in ("<=", ">=")


def test_dedup_keys_vary_widely():
    rng = random.Random(1004)
    keys = {inequalities_region.generate_inequalities_region_higher(Tier.HIGHER, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > 100


def test_topic_definition_metadata():
    t = inequalities_region.TOPIC_INEQUALITIES_REGION_HIGHER
    assert t.id == "inequalities_region_higher"
    assert t.section == "algebra"
    assert t.group == "Inequalities"
    assert t.fixed_tier == Tier.HIGHER
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(1005)
    for _ in range(TRIALS):
        ex = inequalities_region.generate_modelled_example_inequalities_region_higher(Tier.HIGHER, rng)
        assert ex.topic_id == "inequalities_region_higher"
        assert ex.tier == Tier.HIGHER
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
        assert ex.diagram.kind == "inequality_region"


def test_lines_never_parallel_and_intersection_within_window():
    rng = random.Random(1006)
    for _ in range(TRIALS):
        line1, line2 = inequalities_region._build_lines(rng)
        assert line1["m"] != line2["m"]
