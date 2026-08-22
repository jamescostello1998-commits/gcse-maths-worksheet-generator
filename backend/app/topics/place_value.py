"""Place value: writing a number into a place-value table, finding the value
of an underlined digit, and converting a number to/from words - all drawn
from the same range (0 to 999,999,999.999, decimals up to thousandths).

Every generator shares two digit-drawing helpers (_rand_digits /
_rand_digits_rare_decimal) and a small set of place-name/place-value lookup
tables, so the three topics stay genuinely consistent with each other rather
than each inventing its own number range.
"""

import random
from decimal import Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Place Value"

# Place names/abbreviations/values, ordered most- to least-significant -
# indexed from the END (via [-n_int:]) so a number with fewer integer digits
# just uses the rightmost (smallest-place) slice of these lists.
_PLACE_ABBR_INT = ["HM", "TM", "M", "HTh", "TTh", "Th", "H", "T", "O"]
_PLACE_FULL_INT = [
    "hundred millions", "ten millions", "millions",
    "hundred thousands", "ten thousands", "thousands",
    "hundreds", "tens", "ones",
]
_PLACE_VALUE_INT = [100_000_000, 10_000_000, 1_000_000, 100_000, 10_000, 1_000, 100, 10, 1]

_PLACE_ABBR_DEC = ["t", "h", "th"]
_PLACE_FULL_DEC = ["tenths", "hundredths", "thousandths"]
_PLACE_VALUE_DEC = [Decimal("0.1"), Decimal("0.01"), Decimal("0.001")]


def _rand_digits(rng: random.Random) -> tuple[list[int], list[int]]:
    """A random number's digits: 1-9 integer digits (no leading zero unless
    the number is a single 0) and 0-3 decimal digits, weighted toward fewer
    - the full "0 to 999,999,999.999" range shared by place_value_table_F
    and place_value_underlined_digit_F."""
    n_int = rng.randint(1, 9)
    if n_int == 1:
        int_digits = [rng.randint(0, 9)]
    else:
        int_digits = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(n_int - 1)]
    n_dec = rng.choices([0, 1, 2, 3], weights=[15, 25, 30, 30])[0]
    dec_digits = [rng.randint(0, 9) for _ in range(n_dec)]
    return int_digits, dec_digits


def _rand_digits_rare_decimal(rng: random.Random) -> tuple[list[int], list[int]]:
    """Same integer-digit range as _rand_digits, but a decimal part is rare -
    used only by place_value_words_F, per the topic's own request that
    decimals should stay uncommon (most numbers being converted to/from
    words are whole numbers)."""
    n_int = rng.randint(1, 9)
    if n_int == 1:
        int_digits = [rng.randint(0, 9)]
    else:
        int_digits = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(n_int - 1)]
    n_dec = rng.choices([0, 1, 2, 3], weights=[85, 6, 5, 4])[0]
    dec_digits = [rng.randint(0, 9) for _ in range(n_dec)]
    return int_digits, dec_digits


def _fmt_commas(int_digits: list[int]) -> str:
    s = "".join(map(str, int_digits))
    groups = []
    for i, ch in enumerate(reversed(s)):
        if i and i % 3 == 0:
            groups.append(",")
        groups.append(ch)
    return "".join(reversed(groups))


def _fmt_number(int_digits: list[int], dec_digits: list[int]) -> str:
    s = _fmt_commas(int_digits)
    if dec_digits:
        s += "." + "".join(map(str, dec_digits))
    return s


def _fmt_number_with_underline(int_digits: list[int], dec_digits: list[int], idx: int) -> str:
    """Same display as _fmt_number, but the digit at position `idx` (0 =
    most-significant integer digit, counting on into the decimal digits) is
    wrapped in the \\underline{} marker - built by locating that digit's real
    character position inside the already-comma-formatted integer string,
    rather than re-deriving the comma placement by hand."""
    n_int = len(int_digits)
    int_str = _fmt_commas(int_digits)
    digit_positions = [p for p, ch in enumerate(int_str) if ch != ","]
    chars = list(int_str)
    if idx < n_int:
        pos = digit_positions[idx]
        chars[pos] = f"\\underline{{{chars[pos]}}}"
        result = "".join(chars)
        if dec_digits:
            result += "." + "".join(map(str, dec_digits))
        return result

    result = "".join(chars)
    dec_chars = [str(d) for d in dec_digits]
    dec_chars[idx - n_int] = f"\\underline{{{dec_chars[idx - n_int]}}}"
    return result + "." + "".join(dec_chars)


def _fmt_place_value(pv) -> str:
    return f"{pv:,}" if isinstance(pv, int) else str(pv)


def _fmt_digit_value(value: Decimal) -> str:
    if value == value.to_integral_value():
        return f"{int(value):,}"
    return format(value, "f")


# --------------------------------------------------------------------------
# Place value table (Foundation)
# --------------------------------------------------------------------------


def _build_place_value_table(rng: random.Random) -> tuple[list[int], list[int], list[str], list[str], str, str]:
    int_digits, dec_digits = _rand_digits(rng)
    n_int = len(int_digits)
    columns = _PLACE_ABBR_INT[-n_int:] + _PLACE_ABBR_DEC[: len(dec_digits)]
    full_names = _PLACE_FULL_INT[-n_int:] + _PLACE_FULL_DEC[: len(dec_digits)]
    digit_strs = [str(d) for d in int_digits + dec_digits]

    # Independent verification: reconstruct the number, in exact Decimal
    # arithmetic, from the digit -> place-value lookup, and confirm it
    # matches the plain formatted string built by a completely different
    # route (comma-insertion string logic, not place-value multiplication).
    int_value = sum(d * v for d, v in zip(int_digits, _PLACE_VALUE_INT[-n_int:]))
    dec_value = sum(Decimal(d) * v for d, v in zip(dec_digits, _PLACE_VALUE_DEC[: len(dec_digits)]))
    reconstructed = Decimal(int_value) + dec_value
    formatted = _fmt_number(int_digits, dec_digits)
    if reconstructed != Decimal(formatted.replace(",", "")):
        raise ValueError("place_value_table verification failed")

    header_desc = ", ".join(full_names)
    return int_digits, dec_digits, columns, full_names, digit_strs, header_desc


def generate_place_value_table(tier: Tier, rng: random.Random) -> Question:
    int_digits, dec_digits, columns, full_names, digit_strs, header_desc = _build_place_value_table(rng)
    n_int = len(int_digits)
    decimal_after = n_int - 1 if dec_digits else None
    formatted = _fmt_number(int_digits, dec_digits)

    steps = [
        f"The place-value columns here, from left to right, are: {header_desc}.",
        "Write one digit into each column, in order: "
        + ", ".join(f"{name} = {d}" for name, d in zip(full_names, digit_strs)) + ".",
    ]
    return Question(
        topic_id="place_value_table_F",
        tier=Tier.FOUNDATION,
        prompt=f"Write the number {formatted} into the place value table below.",
        solution_steps=tuple(steps),
        final_answer=formatted,
        dedup_key=f"pvt:{int_digits}:{dec_digits}",
        diagram=DiagramSpec(
            kind="place_value_table",
            params={"columns": columns, "digits": [""] * len(columns), "decimal_after": decimal_after},
        ),
        solution_diagram=DiagramSpec(
            kind="place_value_table",
            params={"columns": columns, "digits": digit_strs, "decimal_after": decimal_after},
        ),
    )


def generate_modelled_example_place_value_table(tier: Tier, rng: random.Random) -> ModelledExample:
    int_digits, dec_digits, columns, full_names, digit_strs, header_desc = _build_place_value_table(rng)
    n_int = len(int_digits)
    decimal_after = n_int - 1 if dec_digits else None
    formatted = _fmt_number(int_digits, dec_digits)

    teaching_steps = [
        f"A place-value table has one column for every place a digit can occupy - here, from left "
        f"(most significant) to right (least significant): {header_desc}.",
        f"To fill it in, line {formatted} up against the columns and copy exactly one digit into "
        "each one, keeping the digits in the same left-to-right order they appear in the number - "
        "the units digit always sits in the 'Ones' column, everything to its left is the whole-number "
        "part, and everything to its right (past the decimal point) is the fractional part.",
        "Filling it in: " + ", ".join(f"{name} = {d}" for name, d in zip(full_names, digit_strs)) + ".",
    ]
    worked_calculation = [f"{formatted}"] + [f"{name}: {d}" for name, d in zip(full_names, digit_strs)]
    return ModelledExample(
        topic_id="place_value_table_F",
        tier=Tier.FOUNDATION,
        prompt=f"Write the number {formatted} into the place value table below.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=formatted,
        diagram=DiagramSpec(
            kind="place_value_table",
            params={"columns": columns, "digits": digit_strs, "decimal_after": decimal_after},
        ),
    )


# --------------------------------------------------------------------------
# Value of an underlined digit (Foundation)
# --------------------------------------------------------------------------


def _build_underlined_digit(rng: random.Random):
    int_digits, dec_digits = _rand_digits(rng)
    n_int = len(int_digits)
    all_digits = int_digits + dec_digits
    idx = rng.randrange(len(all_digits))
    digit = all_digits[idx]

    place_values = _PLACE_VALUE_INT[-n_int:] + list(_PLACE_VALUE_DEC[: len(dec_digits)])
    full_names = _PLACE_FULL_INT[-n_int:] + _PLACE_FULL_DEC[: len(dec_digits)]
    place_value = place_values[idx]
    place_name = full_names[idx]
    value = Decimal(digit) * Decimal(place_value)

    # Independent verification: rebuild the number as a plain digit string
    # with every OTHER digit zeroed out (keeping only the target digit in
    # its own position), re-insert the decimal point, and parse the result
    # as a Decimal - a genuinely different route (string surgery + reparse)
    # than the direct digit x place-value multiplication above.
    zeroed = [0] * len(all_digits)
    zeroed[idx] = digit
    zeroed_str = "".join(map(str, zeroed[:n_int]))
    if dec_digits:
        zeroed_str += "." + "".join(map(str, zeroed[n_int:]))
    if Decimal(zeroed_str) != value:
        raise ValueError("place_value_underlined_digit verification failed")

    underlined_str = _fmt_number_with_underline(int_digits, dec_digits, idx)
    answer = _fmt_digit_value(value)
    return digit, place_name, place_value, answer, underlined_str


def generate_place_value_underlined_digit(tier: Tier, rng: random.Random) -> Question:
    digit, place_name, place_value, answer, underlined_str = _build_underlined_digit(rng)
    steps = [
        f"The underlined digit, {digit}, is in the {place_name} column.",
        f"Its value is {digit} × {_fmt_place_value(place_value)} = {answer}.",
    ]
    return Question(
        topic_id="place_value_underlined_digit_F",
        tier=Tier.FOUNDATION,
        prompt=f"In the number {underlined_str}, what is the value of the underlined digit?",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"pvu:{underlined_str}",
    )


def generate_modelled_example_place_value_underlined_digit(tier: Tier, rng: random.Random) -> ModelledExample:
    digit, place_name, place_value, answer, underlined_str = _build_underlined_digit(rng)
    teaching_steps = [
        f"The 'value' of a digit is not just the digit itself - it depends entirely on WHICH column "
        f"(place) it sits in. Here the underlined digit is {digit}, and it sits in the {place_name} column.",
        f"To find its value, multiply the digit by the place value of that column: "
        f"{digit} × {_fmt_place_value(place_value)}.",
        f"So the underlined {digit} is worth {answer} - not just '{digit}'.",
    ]
    worked_calculation = [
        f"underlined digit = {digit}",
        f"column = {place_name} (× {_fmt_place_value(place_value)})",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="place_value_underlined_digit_F",
        tier=Tier.FOUNDATION,
        prompt=f"In the number {underlined_str}, what is the value of the underlined digit?",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# --------------------------------------------------------------------------
# Converting numbers to/from words (Foundation)
# --------------------------------------------------------------------------

_ONES = [
    "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
_ONES_REV = {w: i for i, w in enumerate(_ONES) if w}
_TENS_REV = {w: i * 10 for i, w in enumerate(_TENS) if w}
_DIGIT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
_SCALE_WORDS = ["", " thousand", " million"]


def _three_digit_words(n: int) -> str:
    if n == 0:
        return ""
    parts = []
    hundreds, rem = divmod(n, 100)
    if hundreds:
        parts.append(f"{_ONES[hundreds]} hundred")
    if rem:
        if hundreds:
            parts.append("and")
        if rem < 20:
            parts.append(_ONES[rem])
        else:
            tens, ones = divmod(rem, 10)
            parts.append(_TENS[tens] + (f"-{_ONES[ones]}" if ones else ""))
    return " ".join(parts)


def _parse_three_digit_words(s: str) -> int:
    """Inverts _three_digit_words - used only as an independent round-trip
    check (words -> number), a genuinely different direction from the
    number -> words construction it's checking."""
    if not s:
        return 0
    total = 0
    words = s.split()
    i = 0
    while i < len(words):
        w = words[i]
        if w == "and":
            i += 1
        elif w in _ONES_REV and i + 1 < len(words) and words[i + 1] == "hundred":
            total += _ONES_REV[w] * 100
            i += 2
        elif "-" in w:
            t, o = w.split("-")
            total += _TENS_REV[t] + _ONES_REV[o]
            i += 1
        elif w in _TENS_REV:
            total += _TENS_REV[w]
            i += 1
        elif w in _ONES_REV:
            total += _ONES_REV[w]
            i += 1
        else:
            i += 1
    return total


def _integer_to_words(n: int) -> str:
    if n == 0:
        return "zero"
    group_vals = []
    temp = n
    while temp > 0:
        group_vals.append(temp % 1000)
        temp //= 1000
    parts = []
    for i in reversed(range(len(group_vals))):
        val = group_vals[i]
        if val:
            words = _three_digit_words(val)
            if _parse_three_digit_words(words) != val:
                raise ValueError("place_value_words: three-digit words round-trip failed")
            parts.append(words + _SCALE_WORDS[i])
    return ", ".join(parts)


def _decimal_part_to_words(dec_digits: list[int]) -> str:
    if not dec_digits:
        return ""
    words = "point " + " ".join(_DIGIT_WORDS[d] for d in dec_digits)
    parsed = [_DIGIT_WORDS.index(w) for w in words.split()[1:]]
    if parsed != dec_digits:
        raise ValueError("place_value_words: decimal words round-trip failed")
    return words


def _number_to_words(int_digits: list[int], dec_digits: list[int]) -> str:
    n = int("".join(map(str, int_digits)))
    words = _integer_to_words(n)
    dec_words = _decimal_part_to_words(dec_digits)
    return f"{words} {dec_words}" if dec_words else words


def _capitalize(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _build_place_value_words(rng: random.Random) -> tuple[str, str, str]:
    int_digits, dec_digits = _rand_digits_rare_decimal(rng)
    formatted = _fmt_number(int_digits, dec_digits)
    words = _number_to_words(int_digits, dec_digits)
    direction = rng.choice(["to_words", "from_words"])
    return formatted, words, direction


def generate_place_value_words(tier: Tier, rng: random.Random) -> Question:
    formatted, words, direction = _build_place_value_words(rng)
    if direction == "to_words":
        prompt = f"Write {formatted} in words."
        answer = _capitalize(words)
        steps = [
            f"Break {formatted} into its place-value groups (millions, thousands, then the rest) "
            "and read each group in turn.",
            f"{formatted} = {answer}.",
        ]
    else:
        prompt = f"Write {_capitalize(words)} as a number."
        answer = formatted
        steps = [
            "Convert each place-value group of words back into digits, then combine them in order.",
            f"{_capitalize(words)} = {answer}.",
        ]
    return Question(
        topic_id="place_value_words_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"pvw:{formatted}:{direction}",
    )


def generate_modelled_example_place_value_words(tier: Tier, rng: random.Random) -> ModelledExample:
    formatted, words, direction = _build_place_value_words(rng)
    if direction == "to_words":
        prompt = f"Write {formatted} in words."
        answer = _capitalize(words)
        teaching_steps = [
            f"To write {formatted} in words, split it into its place-value groups of three digits - "
            "millions, then thousands, then the final hundreds/tens/ones - reading from left to right.",
            "Read each group of three digits exactly as you would a number under 1000 (e.g. 'four "
            "hundred and two'), then say the group's own scale word ('thousand', 'million') straight "
            "after it, before moving on to the next group.",
            "If there's a decimal part, it's read differently to the whole-number part: say 'point', "
            "then read every digit after it individually, one at a time (never as a whole number).",
            f"Putting it all together: {formatted} = {answer}.",
        ]
        worked_calculation = [formatted, f"= {answer}"]
    else:
        prompt = f"Write {_capitalize(words)} as a number."
        answer = formatted
        teaching_steps = [
            "To convert words back to digits, work through the number a scale word at a time - every "
            "'hundred and ...' phrase becomes a group of (up to) three digits, and words like "
            "'thousand'/'million' tell you where that group of digits sits.",
            "Any digits read individually after the word 'point' are the decimal part - write them "
            "down in the same order, straight after a decimal point.",
            f"Putting the digits back together: {_capitalize(words)} = {answer}.",
        ]
        worked_calculation = [_capitalize(words), f"= {answer}"]
    return ModelledExample(
        topic_id="place_value_words_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_PLACE_VALUE_TABLE = TopicDefinition(
    id="place_value_table_F",
    display_name="Place Value Tables",
    description="Write a number into a place value table, from hundred millions down to thousandths.",
    generate=generate_place_value_table,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_place_value_table,
)

TOPIC_PLACE_VALUE_UNDERLINED_DIGIT = TopicDefinition(
    id="place_value_underlined_digit_F",
    display_name="Value of an Underlined Digit",
    description="Find the value of an underlined digit in a number.",
    generate=generate_place_value_underlined_digit,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_place_value_underlined_digit,
)

TOPIC_PLACE_VALUE_WORDS = TopicDefinition(
    id="place_value_words_F",
    display_name="Numbers in Words",
    description="Convert a number to words, or words to a number.",
    generate=generate_place_value_words,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_place_value_words,
)
