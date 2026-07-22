from app.pdf.mathtext import to_markup


def test_exponents_become_superscript():
    assert to_markup("3x^2 + 5") == "3<i>x</i><super>2</super> + 5"
    assert to_markup("10^-3") == "10<super>-3</super>"


def test_fractional_exponent_is_raised_as_one_unit():
    assert to_markup("x^(1/4)") == "<i>x</i><super>(1/4)</super>"
    assert to_markup("(9x^6)^(1/2)") == "(9<i>x</i><super>6</super>)<super>(1/2)</super>"
    assert to_markup("x^(-1/2)") == "<i>x</i><super>(-1/2)</super>"


def test_bare_x_is_italicised():
    assert to_markup("Solve for x.") == "Solve for <i>x</i>."
    assert to_markup("3x + 1 = 7") == "3<i>x</i> + 1 = 7"


def test_bare_n_is_italicised():
    assert to_markup("Find n.") == "Find <i>n</i>."
    assert to_markup("(n - 2) × 180") == "(<i>n</i> - 2) × 180"


def test_x_or_n_glued_to_another_letter_is_left_alone():
    # Real words containing x/n must not get a stray italic letter in the
    # middle of them.
    assert to_markup("a box of pens") == "a box of pens"
    assert to_markup("and any number in the list") == "and any number in the list"
    assert to_markup("the next term") == "the next term"


def test_nth_is_a_known_limitation_left_unitalicised():
    # "n" glued directly to "th" (no separator) is indistinguishable from an
    # ordinary word by the same letter-adjacency rule that protects "and"/
    # "any" above - matches the pre-existing behaviour for "x" (e.g.
    # "x-axis" only italicises because of the hyphen, not because of special
    # "nth"/"xth" handling). This is intentional, not a bug.
    assert to_markup("Find the nth term.") == "Find the nth term."


def test_indefinite_article_a_is_not_italicised():
    # Only x and n are covered - "a"/"b" (vectors) are explicitly out of
    # scope because "a" collides constantly with the English article.
    assert to_markup("OAB is a triangle with OA = a and OB = b.") == (
        "OAB is a triangle with OA = a and OB = b."
    )


def test_real_ratio_1_to_n_sentence():
    assert to_markup("Write the ratio 3:5 in the form 1:n.") == (
        "Write the ratio 3:5 in the form 1:<i>n</i>."
    )


def test_real_polygon_interior_sentence():
    text = "the interior angles always add up to (n - 2) × 180 degrees, where n is the number of sides."
    markup = to_markup(text)
    assert markup.count("<i>n</i>") == 2
    assert "number of sides" in markup


def test_fraction_numerator_raised_denominator_lowered():
    assert to_markup("3/4") == "<super>3</super>/<sub>4</sub>"
    assert to_markup("Work out 3/4 of 60.") == "Work out <super>3</super>/<sub>4</sub> of 60."


def test_negative_fraction_sign_stays_on_the_baseline():
    assert to_markup("-3/4") == "-<super>3</super>/<sub>4</sub>"


def test_mixed_number_only_lowers_the_fractional_part():
    assert to_markup("3 1/2 cm") == "3 <super>1</super>/<sub>2</sub> cm"


def test_fraction_followed_by_comma_gets_a_spacer():
    # ReportLab renders a comma glued to the raised baseline when it follows
    # a closing </sub> with zero gap (verified in isolation - see the
    # mathtext.py module docstring) - a non-breaking space dodges it without
    # visibly changing the "num/den," look.
    markup = to_markup("20/90, 2/9")
    assert markup == "<super>20</super>/<sub>90</sub> , <super>2</super>/<sub>9</sub>"


def test_fraction_followed_by_other_punctuation_is_untouched():
    # Only comma is affected - periods, colons etc. render fine as-is.
    assert to_markup("3/4.") == "<super>3</super>/<sub>4</sub>."
    assert to_markup("3/4:") == "<super>3</super>/<sub>4</sub>:"
    assert to_markup("(3/4)") == "(<super>3</super>/<sub>4</sub>)"


def test_unit_rates_are_not_mistaken_for_fractions():
    # These all have a slash but letters (not digits) on at least one side,
    # so they must be left completely alone.
    assert to_markup("60 km/h") == "60 km/h"
    assert to_markup("3 m/s") == "3 m/s"
    assert to_markup("2 g/cm³") == "2 g/cm³"
    assert to_markup("5 N/cm²") == "5 N/cm²"
