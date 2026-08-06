import random
import re

from app.core.models import Tier
from app.topics import ratio

TRIALS = 200

GENERATORS = [
    (ratio.generate_share_two, Tier.FOUNDATION),
    (ratio.generate_find_share, Tier.FOUNDATION),
    (ratio.generate_share_three, Tier.HIGHER),
    (ratio.generate_share_three_foundation, Tier.FOUNDATION),
    (ratio.generate_combine_ratios, Tier.HIGHER),
    (ratio.generate_ratio_1_to_n, Tier.FOUNDATION),
    (ratio.generate_ratio_difference, Tier.FOUNDATION),
    (ratio.generate_ratio_difference_higher, Tier.HIGHER),
    (ratio.generate_ratio_to_equation, Tier.HIGHER),
    (ratio.generate_ratio_shape_similar_foundation, Tier.FOUNDATION),
    (ratio.generate_ratio_shape_similar_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(30)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(32)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        ratio.TOPIC_SHARE_TWO,
        ratio.TOPIC_FIND_SHARE,
        ratio.TOPIC_SHARE_THREE,
        ratio.TOPIC_SHARE_THREE_FOUNDATION,
        ratio.TOPIC_COMBINE,
        ratio.TOPIC_RATIO_1_TO_N,
        ratio.TOPIC_RATIO_DIFFERENCE,
        ratio.TOPIC_RATIO_DIFFERENCE_HIGHER,
        ratio.TOPIC_RATIO_TO_EQUATION,
        ratio.TOPIC_RATIO_SHAPE_SIMILAR_FOUNDATION,
        ratio.TOPIC_RATIO_SHAPE_SIMILAR_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 11
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Ratio"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert ratio.TOPIC_SHARE_THREE_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert ratio.TOPIC_RATIO_1_TO_N.fixed_tier == Tier.FOUNDATION
    assert ratio.TOPIC_RATIO_DIFFERENCE.fixed_tier == Tier.FOUNDATION
    assert ratio.TOPIC_RATIO_DIFFERENCE_HIGHER.fixed_tier == Tier.HIGHER
    assert ratio.TOPIC_RATIO_TO_EQUATION.fixed_tier == Tier.HIGHER
    assert ratio.TOPIC_RATIO_SHAPE_SIMILAR_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert ratio.TOPIC_RATIO_SHAPE_SIMILAR_HIGHER.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_have_generator_wired():
    for t in (
        ratio.TOPIC_SHARE_TWO, ratio.TOPIC_FIND_SHARE,
        ratio.TOPIC_SHARE_THREE, ratio.TOPIC_SHARE_THREE_FOUNDATION, ratio.TOPIC_COMBINE,
        ratio.TOPIC_RATIO_1_TO_N, ratio.TOPIC_RATIO_DIFFERENCE, ratio.TOPIC_RATIO_DIFFERENCE_HIGHER,
        ratio.TOPIC_RATIO_TO_EQUATION, ratio.TOPIC_RATIO_SHAPE_SIMILAR_FOUNDATION,
        ratio.TOPIC_RATIO_SHAPE_SIMILAR_HIGHER,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_share_two_produces_verified_examples():
    rng = random.Random(302)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_two(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_share_two_part"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_find_share_produces_verified_examples():
    rng = random.Random(303)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_find_share(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_find_missing_share"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_share_three_produces_verified_examples():
    rng = random.Random(304)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_three(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_share_three_part"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_share_three_foundation_produces_verified_examples():
    rng = random.Random(306)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_share_three_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_share_three_part_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_combine_ratios_produces_verified_examples():
    rng = random.Random(305)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_combine_ratios(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_combine"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_1_to_n_produces_verified_examples():
    rng = random.Random(307)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_1_to_n(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_1_to_n"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_difference_produces_verified_examples():
    rng = random.Random(308)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_difference(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_difference"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_difference_higher_produces_verified_examples():
    rng = random.Random(309)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_difference_higher(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_difference_higher"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_to_equation_produces_verified_examples():
    rng = random.Random(310)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_to_equation(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_to_equation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_shape_similar_foundation_produces_verified_examples():
    rng = random.Random(311)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_shape_similar_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "ratio_shape_similar_foundation"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_ratio_shape_similar_higher_produces_verified_examples():
    rng = random.Random(312)
    for _ in range(TRIALS):
        example = ratio.generate_modelled_example_ratio_shape_similar_higher(Tier.HIGHER, rng)
        assert example.topic_id == "ratio_shape_similar_higher"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_ratio_to_equation_smoke_test_no_exceptions():
    # ratio_to_equation has a bounded retry loop internally (_build_ratio_equation) -
    # call it directly in a raw loop with no try/except so a high internal rejection
    # rate would surface as an uncaught ValueError here.
    rng = random.Random(313)
    for _ in range(300):
        q = ratio.generate_ratio_to_equation(Tier.HIGHER, rng)
        assert q.final_answer


def test_ratio_shape_similar_higher_smoke_test_no_exceptions():
    rng = random.Random(314)
    for _ in range(300):
        q = ratio.generate_ratio_shape_similar_higher(Tier.HIGHER, rng)
        assert q.final_answer


def test_ratio_1_to_n_uses_the_plain_n_marker_not_a_literal_bare_n():
    # "n" here is a ratio-form placeholder ("1:n"), not a real algebraic
    # variable - it must go through the \plain{n} escape marker (see
    # mathtext.py), never appear as a literal un-marked "n" that the
    # engine's default italics pass would otherwise pick up.
    rng = random.Random(320)
    for _ in range(TRIALS):
        q = ratio.generate_ratio_1_to_n(Tier.FOUNDATION, rng)
        assert "\\plain{n}" in q.prompt
        assert re.search(r"(?<![A-Za-z{])n(?![A-Za-z}])", q.prompt) is None


def test_find_share_uses_the_letter_equation_style():
    rng = random.Random(321)
    seen_given_first_letter = set()
    for _ in range(TRIALS):
        q = ratio.generate_find_share(Tier.FOUNDATION, rng)
        assert re.match(r"^\w+ : \w+ = \d+ : \d+\. \w+ = \d+\. What is the value of \w+\?$", q.prompt)
        given_letter = q.prompt.split(". ")[1].split(" = ")[0]
        seen_given_first_letter.add(given_letter == q.prompt.split(" : ")[0])
    # Confirms the student is sometimes given the first letter's value and
    # sometimes the second's, per the explicit request.
    assert seen_given_first_letter == {True, False}


def test_ratio_difference_uses_the_letter_equation_style():
    # Each clause is on its own line (a literal "\n", rendered as a real
    # line break by mathtext.py's to_markup) - the initial ratio statement,
    # then the difference clause, then the "Find" instruction.
    rng = random.Random(322)
    for _ in range(TRIALS):
        q = ratio.generate_ratio_difference(Tier.FOUNDATION, rng)
        assert re.match(r"^\w+ : \w+ = \d+ : \d+\.\n\w+ - \w+ = \d+\.\nFind \w+ and \w+", q.prompt)


def test_ratio_difference_higher_uses_the_letter_equation_style():
    rng = random.Random(323)
    for _ in range(TRIALS):
        q = ratio.generate_ratio_difference_higher(Tier.HIGHER, rng)
        assert re.match(
            r"^\w+ : \w+ : \w+ = \d+ : \d+ : \d+\.\n\w+ - \w+ = \d+\.\nFind \w+, \w+ and \w+", q.prompt
        )


def test_ratio_shape_similar_foundation_has_a_diagram_and_no_bare_side_lengths_in_prompt():
    rng = random.Random(324)
    for _ in range(TRIALS):
        q = ratio.generate_ratio_shape_similar_foundation(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "two_similar_rectangles"
        letter = q.diagram.params["b_height_label"]
        assert letter in ("x", "y", "z")
        assert q.prompt == f"Shape A and Shape B are similar. Find the length of side {letter}."


def test_ratio_shape_similar_higher_has_a_diagram_and_no_bare_lengths_in_prompt():
    rng = random.Random(325)
    for _ in range(TRIALS):
        q = ratio.generate_ratio_shape_similar_higher(Tier.HIGHER, rng)
        assert "cm and" not in q.prompt  # the old "A length on shape A is X cm and..." sentence is gone
        assert q.diagram is not None
        assert q.diagram.kind == "two_similar_rectangles"
        assert "a_width_label" in q.diagram.params
        assert "b_width_label" in q.diagram.params


def test_new_ratio_topics_dedup_key_space_is_wide_enough():
    # Sanity check per CLAUDE.md: each topic's dedup key space should comfortably
    # exceed the 20-question worksheet size.
    generators = [
        ratio.generate_ratio_1_to_n,
        ratio.generate_ratio_difference,
        ratio.generate_ratio_difference_higher,
        ratio.generate_ratio_to_equation,
        ratio.generate_ratio_shape_similar_foundation,
        ratio.generate_ratio_shape_similar_higher,
    ]
    rng = random.Random(315)
    for generate in generators:
        keys = {generate(Tier.HIGHER, rng).dedup_key for _ in range(300)}
        assert len(keys) > 20
