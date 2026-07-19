import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import data_handling

TRIALS = 200

GENERATORS = [
    (data_handling.generate_set_notation, Tier.HIGHER),
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
        data_handling.TOPIC_PRODUCT_RULE_COUNTING,
        data_handling.TOPIC_RELATIVE_FREQUENCY,
        data_handling.TOPIC_TWO_WAY_TABLES,
        data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "probability"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
        assert t.question_count is None
    assert data_handling.TOPIC_SET_NOTATION.group == "Sets and Counting"
    assert data_handling.TOPIC_PRODUCT_RULE_COUNTING.group == "Sets and Counting"
    assert data_handling.TOPIC_RELATIVE_FREQUENCY.group == "Tables and Diagrams"
    assert data_handling.TOPIC_TWO_WAY_TABLES.group == "Tables and Diagrams"
    assert data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS.group == "Tables and Diagrams"
