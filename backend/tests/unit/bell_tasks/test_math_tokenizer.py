from app.bell_tasks.math_tokenizer import (
    FONT_MATH,
    FONT_WORDS,
    ExponentSpan,
    FractionalExponentSpan,
    FractionSpan,
    TextSpan,
    tokenize,
)


def _reconstructed_text(tokens) -> str:
    """Best-effort flattening back to plain text, for a lossless-ish sanity
    check - structural tokens render their own literal ASCII form."""
    parts = []
    for t in tokens:
        if isinstance(t, TextSpan):
            parts.append(t.text)
        elif isinstance(t, FractionSpan):
            parts.append(f"{t.sign}{t.numerator}/{t.denominator}")
        elif isinstance(t, ExponentSpan):
            parts.append(f"{t.base}^{t.exponent}")
        elif isinstance(t, FractionalExponentSpan):
            parts.append(f"{t.base}^({t.numerator}/{t.denominator})")
    return "".join(parts)


def test_plain_prose_is_all_calibri_text_spans():
    tokens = tokenize("Find the value of the missing angle.")
    assert all(isinstance(t, TextSpan) and t.font == FONT_WORDS for t in tokens)


def test_empty_string():
    assert tokenize("") == []


def test_standalone_fraction_becomes_a_fraction_span():
    tokens = tokenize("Simplify 3/4")
    fractions = [t for t in tokens if isinstance(t, FractionSpan)]
    assert fractions == [FractionSpan(sign="", numerator="3", denominator="4")]


def test_negative_standalone_fraction_keeps_its_sign():
    tokens = tokenize("Answer: -3/4")
    fractions = [t for t in tokens if isinstance(t, FractionSpan)]
    assert fractions == [FractionSpan(sign="-", numerator="3", denominator="4")]


def test_single_letter_base_exponent_becomes_an_exponent_span():
    tokens = tokenize("Evaluate x^2 + 5")
    exponents = [t for t in tokens if isinstance(t, ExponentSpan)]
    assert exponents == [ExponentSpan(base="x", exponent="2")]


def test_digit_base_exponent_becomes_an_exponent_span():
    tokens = tokenize("Write 10^-3 in standard form")
    exponents = [t for t in tokens if isinstance(t, ExponentSpan)]
    assert exponents == [ExponentSpan(base="10", exponent="-3")]


def test_inverse_function_single_letter_base_becomes_an_exponent_span():
    tokens = tokenize("Find f^-1(x)")
    exponents = [t for t in tokens if isinstance(t, ExponentSpan)]
    assert exponents == [ExponentSpan(base="f", exponent="-1")]


def test_fractional_exponent_with_single_letter_base_becomes_structural():
    tokens = tokenize("Simplify x^(1/4)")
    fractional_exponents = [t for t in tokens if isinstance(t, FractionalExponentSpan)]
    assert fractional_exponents == [FractionalExponentSpan(base="x", numerator="1", denominator="4")]


def test_bracketed_base_exponent_falls_back_to_plain_text():
    # (x - 3)^2 - the true base is a whole bracketed expression, which this
    # tokenizer deliberately does not attempt to identify (see module
    # docstring) - falls back to the pre-existing plain Cambria Math text
    # rendering of just the "^2" portion, not a structural ExponentSpan.
    tokens = tokenize("Expand (x - 3)^2")
    assert not any(isinstance(t, ExponentSpan) for t in tokens)
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert "^2" in math_texts


def test_multiletter_base_exponent_falls_back_to_plain_text():
    # cos^-1 - "s" (the character immediately before "^") is the tail of the
    # word "cos", not a standalone variable - must not be promoted.
    tokens = tokenize("Find cos^-1(0.5)")
    assert not any(isinstance(t, ExponentSpan) for t in tokens)
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert "^-1" in math_texts


def test_run_together_coefficient_and_variable_exponent_falls_back_to_plain_text():
    # at^2 means a * t^2, not (at)^2 - "t" is preceded by the letter "a", so
    # this must not be promoted to a structural ExponentSpan either.
    tokens = tokenize("s = ut + 0.5 * at^2")
    assert not any(isinstance(t, ExponentSpan) for t in tokens)
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert "^2" in math_texts


def test_surd_over_integer_not_treated_as_a_fraction_span():
    # Mirrors mathtext.py's own documented gotcha: a fraction glued directly
    # after a literal root sign must not be mangled into a FractionSpan.
    tokens = tokenize("cos(60°) = √2/2")
    assert not any(isinstance(t, FractionSpan) for t in tokens)


def test_currency_percent_and_degree_symbols_stay_plain_math_text():
    tokens = tokenize("A £15 item is reduced by 20% to give an angle of 37°")
    math_texts = {t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH}
    assert "£15" in math_texts
    assert "20%" in math_texts
    assert "37°" in math_texts


def test_vector_marker_collapses_to_bare_letter():
    tokens = tokenize(r"OA = \vec{a} and OB = \vec{b}")
    assert not any(isinstance(t, TextSpan) and "vec" in t.text for t in tokens)
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert math_texts.count("a") == 1
    assert math_texts.count("b") == 1


def test_variable_word_boundary_does_not_grab_letters_inside_words():
    tokens = tokenize("Find x when the box contains n items and the band plays")
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert math_texts.count("x") == 1
    assert math_texts.count("n") == 1


def test_compound_word_hyphen_is_not_treated_as_minus_sign():
    tokens = tokenize("In the right-angled triangle shown, find angle x.")
    assert all(
        t.font == FONT_WORDS for t in tokens if isinstance(t, TextSpan) and t.text == "-"
    )

    tokens2 = tokenize("How many vertices does a square-based pyramid have?")
    assert all(
        t.font == FONT_WORDS for t in tokens2 if isinstance(t, TextSpan) and t.text == "-"
    )


def test_genuine_minus_sign_still_classified_as_math():
    tokens = tokenize("Work out 10 - 3")
    math_texts = [t.text for t in tokens if isinstance(t, TextSpan) and t.font == FONT_MATH]
    assert "-" in math_texts


def test_no_math_symbols_at_all():
    text = "Describe the transformation shown in the diagram."
    tokens = tokenize(text)
    assert all(isinstance(t, TextSpan) and t.font == FONT_WORDS for t in tokens)
    assert _reconstructed_text(tokens) == text
