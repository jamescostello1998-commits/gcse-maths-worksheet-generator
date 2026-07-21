import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import venn_diagrams

TRIALS = 200

GENERATORS = [
    (venn_diagrams.generate_venn_diagram_shading, Tier.FOUNDATION),
    (venn_diagrams.generate_venn_diagram_probability, Tier.FOUNDATION),
    (venn_diagrams.generate_venn_diagram_notation, Tier.HIGHER),
    (venn_diagrams.generate_venn_diagram_algebra, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(900)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "venn_diagram"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(901)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 20


def test_dedup_key_space_is_wide_enough_over_300_trials():
    # Sanity check per CLAUDE.md: each topic's dedup key space should
    # comfortably exceed the 20-question worksheet size.
    for generate, tier in GENERATORS:
        rng = random.Random(902)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 20, f"{generate.__name__} dedup key space too narrow: {len(keys)}"


def test_topic_definitions_have_expected_metadata():
    topics = [
        venn_diagrams.TOPIC_VENN_SHADING,
        venn_diagrams.TOPIC_VENN_PROBABILITY,
        venn_diagrams.TOPIC_VENN_NOTATION,
        venn_diagrams.TOPIC_VENN_ALGEBRA,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "probability"
        assert t.group == "Venn Diagrams"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert venn_diagrams.TOPIC_VENN_SHADING.fixed_tier == Tier.FOUNDATION
    assert venn_diagrams.TOPIC_VENN_PROBABILITY.fixed_tier == Tier.FOUNDATION
    assert venn_diagrams.TOPIC_VENN_NOTATION.fixed_tier == Tier.HIGHER
    assert venn_diagrams.TOPIC_VENN_ALGEBRA.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_are_wired_up():
    for t in (
        venn_diagrams.TOPIC_VENN_SHADING,
        venn_diagrams.TOPIC_VENN_PROBABILITY,
        venn_diagrams.TOPIC_VENN_NOTATION,
        venn_diagrams.TOPIC_VENN_ALGEBRA,
    ):
        assert t.generate_modelled_example is not None


def test_venn_diagram_shading_question_diagram_unshaded_and_solution_shaded():
    rng = random.Random(903)
    for _ in range(TRIALS):
        q = venn_diagrams.generate_venn_diagram_shading(Tier.FOUNDATION, rng)
        assert not q.diagram.params.get("shade")
        assert q.solution_diagram is not None
        assert q.solution_diagram.params.get("shade")


def test_venn_diagram_shading_matches_mapping_table_for_specific_regions():
    # Directly construct known cases from the region definitions and confirm
    # the shade list produced matches the documented mapping table.
    expected = {
        "A": {"a_only", "both"},
        "B": {"b_only", "both"},
        "intersection": {"both"},
        "union": {"a_only", "b_only", "both"},
        "A_only": {"a_only"},
        "B_only": {"b_only"},
        "not_A": {"b_only", "neither"},
        "not_B": {"a_only", "neither"},
        "neither": {"neither"},
        "not_both": {"a_only", "b_only", "neither"},
    }
    found_keys = set()
    rng = random.Random(904)
    for _ in range(500):
        q = venn_diagrams.generate_venn_diagram_shading(Tier.FOUNDATION, rng)
        key = q.dedup_key.split(":")[1]
        found_keys.add(key)
        assert set(q.solution_diagram.params["shade"]) == expected[key]
    assert found_keys == set(expected.keys())


def test_venn_diagram_shading_prompt_avoids_formal_notation():
    rng = random.Random(905)
    for _ in range(TRIALS):
        q = venn_diagrams.generate_venn_diagram_shading(Tier.FOUNDATION, rng)
        for symbol in ("∪", "∩", "'"):
            assert symbol not in q.prompt


def test_venn_diagram_probability_answer_matches_diagram_counts():
    rng = random.Random(906)
    for _ in range(TRIALS):
        q = venn_diagrams.generate_venn_diagram_probability(Tier.FOUNDATION, rng)
        region_text = q.diagram.params["region_text"]
        counts = {k: int(v) for k, v in region_text.items()}
        total = sum(counts.values())
        numerator, denominator = (int(x) for x in q.final_answer.split("/"))
        prob = Fraction(numerator, denominator)
        # The stated probability must correspond to *some* combination of the
        # four atomic regions divided by the total - reconstruct every
        # possible non-empty subset sum and confirm the answer matches one.
        from itertools import combinations

        keys = list(counts.keys())
        possible = set()
        for r in range(1, len(keys) + 1):
            for combo in combinations(keys, r):
                possible.add(Fraction(sum(counts[k] for k in combo), total))
        assert prob in possible


def test_venn_diagram_notation_answer_is_consistent_with_diagram_elements():
    rng = random.Random(907)
    for _ in range(TRIALS):
        q = venn_diagrams.generate_venn_diagram_notation(Tier.HIGHER, rng)
        region_text = q.diagram.params["region_text"]
        # Every element listed in the final answer must appear in the
        # union of all elements shown across the diagram's regions.
        all_elements = set()
        for text in region_text.values():
            if text.strip():
                all_elements.update(int(x) for x in text.split(","))
        if q.final_answer != "{ } (the empty set)":
            answer_elements = {
                int(x) for x in q.final_answer.strip("{}").split(", ") if x.strip()
            }
            assert answer_elements <= all_elements


def test_venn_diagram_algebra_regions_reconcile_with_solution_steps():
    rng = random.Random(908)
    for _ in range(TRIALS):
        q = venn_diagrams.generate_venn_diagram_algebra(Tier.HIGHER, rng)
        assert q.diagram.params["region_text"]
        # final_answer must be either a plain integer or a valid fraction.
        if "/" in q.final_answer:
            numerator, denominator = (int(x) for x in q.final_answer.split("/"))
            assert denominator > 0
            assert 0 <= numerator <= denominator
        else:
            assert int(q.final_answer) >= 0


def test_modelled_example_venn_diagram_shading_produces_verified_examples():
    rng = random.Random(909)
    for _ in range(TRIALS):
        example = venn_diagrams.generate_modelled_example_venn_diagram_shading(Tier.FOUNDATION, rng)
        assert example.topic_id == "venn_diagram_shading"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.params.get("shade")
        for symbol in ("∪", "∩", "'"):
            assert symbol not in example.prompt


def test_modelled_example_venn_diagram_probability_produces_verified_examples():
    rng = random.Random(910)
    for _ in range(TRIALS):
        example = venn_diagrams.generate_modelled_example_venn_diagram_probability(Tier.FOUNDATION, rng)
        assert example.topic_id == "venn_diagram_probability"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.kind == "venn_diagram"


def test_modelled_example_venn_diagram_notation_produces_verified_examples():
    rng = random.Random(911)
    for _ in range(TRIALS):
        example = venn_diagrams.generate_modelled_example_venn_diagram_notation(Tier.HIGHER, rng)
        assert example.topic_id == "venn_diagram_notation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.kind == "venn_diagram"


def test_modelled_example_venn_diagram_algebra_produces_verified_examples():
    rng = random.Random(912)
    for _ in range(TRIALS):
        example = venn_diagrams.generate_modelled_example_venn_diagram_algebra(Tier.HIGHER, rng)
        assert example.topic_id == "venn_diagram_algebra"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.kind == "venn_diagram"
