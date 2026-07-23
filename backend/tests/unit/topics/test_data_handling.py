import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import data_handling

TRIALS = 200

GENERATORS = [
    (data_handling.generate_set_notation, Tier.HIGHER),
    (data_handling.generate_set_notation_foundation, Tier.FOUNDATION),
    (data_handling.generate_product_rule_counting, Tier.HIGHER),
    (data_handling.generate_relative_frequency, Tier.FOUNDATION),
    (data_handling.generate_two_way_tables, Tier.FOUNDATION),
    (data_handling.generate_sample_space_diagrams, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(430)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_two_way_tables_diagram_matches_between_question_and_solution():
    rng = random.Random(431)
    for _ in range(TRIALS):
        q = data_handling.generate_two_way_tables(Tier.FOUNDATION, rng)
        assert q.diagram is not None and q.diagram.kind == "two_way_table"
        assert q.solution_diagram is not None and q.solution_diagram.kind == "two_way_table"
        question_cells = q.diagram.params["cells"]
        solution_cells = q.solution_diagram.params["cells"]
        blanks = [
            (r, c)
            for r, row in enumerate(question_cells)
            for c, val in enumerate(row)
            if val == "?"
        ]
        assert len(blanks) == 1
        r, c = blanks[0]
        assert solution_cells[r][c] == q.final_answer


def test_sample_space_diagram_highlights_match_the_stated_probability():
    rng = random.Random(432)
    for _ in range(TRIALS):
        q = data_handling.generate_sample_space_diagrams(Tier.FOUNDATION, rng)
        assert q.diagram is not None and q.diagram.kind == "sample_space_diagram"
        highlight = q.diagram.params["highlight"]
        total = len(q.diagram.params["row_values"]) * len(q.diagram.params["col_values"])
        numerator, denominator = (int(x) for x in q.final_answer.split("/"))
        assert Fraction(numerator, denominator) == Fraction(len(highlight), total)


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(433)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        data_handling.TOPIC_SET_NOTATION,
        data_handling.TOPIC_SET_NOTATION_FOUNDATION,
        data_handling.TOPIC_PRODUCT_RULE_COUNTING,
        data_handling.TOPIC_RELATIVE_FREQUENCY,
        data_handling.TOPIC_TWO_WAY_TABLES,
        data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 6
    for t in topics:
        assert t.section == "probability"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
        assert t.question_count is None
    assert data_handling.TOPIC_SET_NOTATION.group == "Sets and Counting"
    assert data_handling.TOPIC_SET_NOTATION_FOUNDATION.group == "Sets and Counting"
    assert data_handling.TOPIC_SET_NOTATION_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert data_handling.TOPIC_PRODUCT_RULE_COUNTING.group == "Sets and Counting"
    assert data_handling.TOPIC_RELATIVE_FREQUENCY.group == "Tables and Diagrams"
    assert data_handling.TOPIC_TWO_WAY_TABLES.group == "Tables and Diagrams"
    assert data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS.group == "Tables and Diagrams"


def test_set_notation_foundation_prompt_avoids_formal_notation():
    rng = random.Random(434)
    for _ in range(TRIALS):
        q = data_handling.generate_set_notation_foundation(Tier.FOUNDATION, rng)
        for symbol in ("∪", "∩", "'"):
            assert symbol not in q.prompt


def test_modelled_example_topics_are_wired_up():
    for t in (
        data_handling.TOPIC_SET_NOTATION,
        data_handling.TOPIC_SET_NOTATION_FOUNDATION,
        data_handling.TOPIC_PRODUCT_RULE_COUNTING,
        data_handling.TOPIC_RELATIVE_FREQUENCY,
        data_handling.TOPIC_TWO_WAY_TABLES,
        data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_set_notation_produces_verified_examples():
    rng = random.Random(440)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_set_notation(Tier.HIGHER, rng)
        assert example.topic_id == "set_notation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_set_notation_foundation_produces_verified_examples():
    rng = random.Random(445)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_set_notation_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "set_notation_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        for symbol in ("∪", "∩", "'"):
            assert symbol not in example.prompt


def test_modelled_example_product_rule_counting_produces_verified_examples():
    rng = random.Random(441)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_product_rule_counting(Tier.HIGHER, rng)
        assert example.topic_id == "product_rule_counting"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_relative_frequency_produces_verified_examples():
    rng = random.Random(442)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_relative_frequency(Tier.FOUNDATION, rng)
        assert example.topic_id == "relative_frequency"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_relative_frequency_attaches_a_dice_diagram_only_for_the_biased_dice_context():
    rng = random.Random(444)
    saw_dice_diagram = False
    saw_no_diagram = False
    for _ in range(TRIALS):
        q = data_handling.generate_relative_frequency(Tier.FOUNDATION, rng)
        if "A biased dice is tested" in q.prompt:
            assert q.diagram is not None
            assert q.diagram.kind == "dice"
            assert q.diagram.params["values"] == [6]
            saw_dice_diagram = True
        else:
            assert q.diagram is None
            saw_no_diagram = True
    assert saw_dice_diagram
    assert saw_no_diagram


def test_modelled_example_two_way_tables_produces_verified_examples():
    rng = random.Random(443)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_two_way_tables(Tier.FOUNDATION, rng)
        assert example.topic_id == "two_way_tables"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.kind == "two_way_table"


def test_modelled_example_sample_space_diagrams_produces_verified_examples():
    rng = random.Random(444)
    for _ in range(TRIALS):
        example = data_handling.generate_modelled_example_sample_space_diagrams(Tier.FOUNDATION, rng)
        assert example.topic_id == "sample_space_diagrams"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
        assert example.diagram is not None and example.diagram.kind == "sample_space_diagram"
