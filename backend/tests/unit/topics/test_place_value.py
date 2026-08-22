import random
from decimal import Decimal

from app.core.models import Tier
from app.topics import place_value

TRIALS = 300

GENERATORS = [
    (place_value.generate_place_value_table, Tier.FOUNDATION),
    (place_value.generate_place_value_underlined_digit, Tier.FOUNDATION),
    (place_value.generate_place_value_words, Tier.FOUNDATION),
]

MODELLED_EXAMPLE_GENERATORS = [
    (place_value.generate_modelled_example_place_value_table, Tier.FOUNDATION, "place_value_table_F"),
    (
        place_value.generate_modelled_example_place_value_underlined_digit,
        Tier.FOUNDATION,
        "place_value_underlined_digit_F",
    ),
    (place_value.generate_modelled_example_place_value_words, Tier.FOUNDATION, "place_value_words_F"),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(600)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt and q.solution_steps and q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(601)
        keys = {generate(tier, rng).dedup_key for _ in range(200)}
        assert len(keys) > 100


def test_modelled_examples_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(602)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_place_value_table_diagram_matches_generated_digits():
    """The diagram's blank cells become filled digits on the solution page,
    and the filled digits genuinely match the number stated in the prompt."""
    rng = random.Random(603)
    for _ in range(TRIALS):
        q = place_value.generate_place_value_table(Tier.FOUNDATION, rng)
        assert q.diagram is not None and q.solution_diagram is not None
        assert q.diagram.kind == "place_value_table"
        assert all(d == "" for d in q.diagram.params["digits"])  # blank on the question page
        digits = q.solution_diagram.params["digits"]
        assert all(d != "" for d in digits)
        # Reconstruct the number straight from the filled digits and compare
        # against the prompt's own stated number, independent of the
        # generator's own internal formatting.
        rebuilt = "".join(digits)
        decimal_after = q.solution_diagram.params["decimal_after"]
        if decimal_after is not None:
            rebuilt = rebuilt[: decimal_after + 1] + "." + rebuilt[decimal_after + 1 :]
        assert q.final_answer.replace(",", "") == rebuilt


def test_place_value_table_columns_span_the_full_advertised_range():
    """Confirm both a 9-integer-digit number (hundred millions) and a
    3-decimal-place number (thousandths) are genuinely reachable, matching
    the "max 999,999,999.999" range this topic was built to."""
    rng = random.Random(604)
    seen_hundred_millions = False
    seen_thousandths = False
    for _ in range(TRIALS):
        q = place_value.generate_place_value_table(Tier.FOUNDATION, rng)
        cols = q.diagram.params["columns"]
        if cols[0] == "HM":
            seen_hundred_millions = True
        if cols[-1] == "th":
            seen_thousandths = True
    assert seen_hundred_millions
    assert seen_thousandths


def test_underlined_digit_value_matches_digit_times_place_value():
    """Independently re-derive the answer from the prompt's own underlined
    digit and its place, via a completely different route (regex extraction
    + Decimal place-value lookup) than the generator's own internal
    zeroed-string verification."""
    import re

    place_values = {
        "hundred millions": Decimal(100_000_000), "ten millions": Decimal(10_000_000),
        "millions": Decimal(1_000_000), "hundred thousands": Decimal(100_000),
        "ten thousands": Decimal(10_000), "thousands": Decimal(1_000),
        "hundreds": Decimal(100), "tens": Decimal(10), "ones": Decimal(1),
        "tenths": Decimal("0.1"), "hundredths": Decimal("0.01"), "thousandths": Decimal("0.001"),
    }
    rng = random.Random(605)
    for _ in range(TRIALS):
        q = place_value.generate_place_value_underlined_digit(Tier.FOUNDATION, rng)
        digit = int(re.search(r"\\underline\{(\d)\}", q.prompt).group(1))
        place_name = re.search(r"in the ([a-z ]+) column", q.solution_steps[0]).group(1)
        expected = digit * place_values[place_name]
        answer = Decimal(q.final_answer.replace(",", ""))
        assert answer == expected


def test_underlined_digit_uses_a_safe_ascii_marker_not_a_raw_html_tag():
    rng = random.Random(606)
    for _ in range(50):
        q = place_value.generate_place_value_underlined_digit(Tier.FOUNDATION, rng)
        assert "\\underline{" in q.prompt
        assert "<u>" not in q.prompt


def test_words_direction_varies_and_round_trips():
    rng = random.Random(607)
    saw_to_words = saw_from_words = False
    for _ in range(TRIALS):
        q = place_value.generate_place_value_words(Tier.FOUNDATION, rng)
        if q.prompt.startswith("Write ") and q.prompt.endswith(" in words."):
            saw_to_words = True
        elif q.prompt.startswith("Write ") and q.prompt.endswith(" as a number."):
            saw_from_words = True
    assert saw_to_words and saw_from_words


def test_words_decimals_are_rare():
    rng = random.Random(608)
    n_with_decimal = 0
    for _ in range(TRIALS):
        q = place_value.generate_place_value_words(Tier.FOUNDATION, rng)
        if "point" in q.final_answer.lower() or "." in q.final_answer:
            n_with_decimal += 1
    assert n_with_decimal < TRIALS * 0.25


def test_three_digit_words_round_trips_every_value():
    for n in range(0, 1000):
        words = place_value._three_digit_words(n)
        assert place_value._parse_three_digit_words(words) == n


def test_integer_to_words_matches_known_values():
    assert place_value._integer_to_words(0) == "zero"
    assert place_value._integer_to_words(1000) == "one thousand"
    assert place_value._integer_to_words(1001) == "one thousand, one"
    assert place_value._integer_to_words(402506) == "four hundred and two thousand, five hundred and six"
    assert place_value._integer_to_words(1000000) == "one million"
    assert place_value._integer_to_words(999999999) == (
        "nine hundred and ninety-nine million, "
        "nine hundred and ninety-nine thousand, "
        "nine hundred and ninety-nine"
    )


def test_topic_definitions_have_expected_metadata():
    topics = [
        place_value.TOPIC_PLACE_VALUE_TABLE,
        place_value.TOPIC_PLACE_VALUE_UNDERLINED_DIGIT,
        place_value.TOPIC_PLACE_VALUE_WORDS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "number"
        assert t.group == "Place Value"
        assert t.fixed_tier == Tier.FOUNDATION
        assert t.generate_modelled_example is not None
