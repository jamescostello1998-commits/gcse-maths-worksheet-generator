import os
import re

from reportlab.lib.colors import HexColor

import app.pdf.mathtext as mathtext_module
from app.pdf.fraction_images import FractionImage
from app.pdf.mathtext import _VAR_FONT_BOLD_ITALIC, _VAR_FONT_ITALIC, to_markup

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")

_IMG_RE = re.compile(r'<img src="([^"]+)" width="([^"]+)" height="([^"]+)" valign="(?:bottom|baseline)"/>')

# The registered curved-italic font is used via an explicit <font name="...">
# tag instead of <i> - see mathtext.py's module docstring for why. Tests
# reference the real registered names rather than hardcoding the string, so
# they stay correct if the font is ever swapped.
_ITALIC = f'<font name="{_VAR_FONT_ITALIC}">'
_BOLD_ITALIC = f'<font name="{_VAR_FONT_BOLD_ITALIC}">'


def _markup(text: str, font_size: float = 11.5, color=INK, bold: bool = False) -> str:
    return to_markup(text, font_size=font_size, color=color, bold=bold)


def _italic(letter: str) -> str:
    return f"{_ITALIC}{letter}</font>"


def test_exponents_become_superscript():
    assert _markup("3x^2 + 5") == f"3{_italic('x')}<super>2</super> + 5"
    assert _markup("10^-3") == "10<super>-3</super>"


def test_fractional_exponent_is_raised_as_a_true_vinculum_in_superscript():
    # A fractional power is a reduced-size fraction image raised to true
    # exponent height via valign="super" ON THE IMAGE - NOT a <super> wrapper
    # around a baseline-aligned image, which left the fraction sitting low
    # next to the base looking like a coefficient rather than a power (the
    # bug the reference image flagged) - see the module docstring.
    markup = _markup("x^(1/4)")
    m = re.search(
        r'^' + re.escape(_italic("x")) + r'<img src="([^"]+)"[^>]*valign="super"/>$',
        markup,
    )
    assert m is not None, markup
    assert os.path.isfile(m.group(1))


def test_compound_exponent_is_raised_as_flat_text():
    # An exponent that ISN'T a plain numeric fraction (e.g. an algebraic
    # expression) has no vinculum-shaped sub-content to draw, so it's just
    # wrapped flat in <super> - its inner x has already been italicised by
    # the earlier pass.
    assert _markup("9^(x+2)") == f"9<super>({_italic('x')}+2)</super>"
    assert _markup("5^(3x)") == f"5<super>(3{_italic('x')})</super>"


def test_bare_variable_exponent_is_raised_and_italicised():
    assert _markup("8^x = 512") == f"8<super>{_italic('x')}</super> = 512"
    assert _markup("p^n") == f"p<super>{_italic('n')}</super>"


def test_bare_x_is_italicised():
    assert _markup("Solve for x.") == f"Solve for {_italic('x')}."
    assert _markup("3x + 1 = 7") == f"3{_italic('x')} + 1 = 7"


def test_bare_n_is_italicised():
    assert _markup("Find n.") == f"Find {_italic('n')}."
    assert _markup("(n - 2) × 180") == f"({_italic('n')} - 2) × 180"


def test_bold_context_uses_the_bold_italic_font():
    assert _markup("x = 5", bold=True) == f"{_BOLD_ITALIC}x</font> = 5"


def test_x_or_n_glued_to_another_letter_is_left_alone():
    # Real words containing x/n must not get a stray italic letter in the
    # middle of them.
    assert _markup("a box of pens") == "a box of pens"
    assert _markup("and any number in the list") == "and any number in the list"
    assert _markup("the next term") == "the next term"


def test_nth_is_a_known_limitation_left_unitalicised():
    # "n" glued directly to "th" (no separator) is indistinguishable from an
    # ordinary word by the same letter-adjacency rule that protects "and"/
    # "any" above - matches the pre-existing behaviour for "x" (e.g.
    # "x-axis" only italicises because of the hyphen, not because of special
    # "nth"/"xth" handling). This is intentional, not a bug.
    assert _markup("Find the nth term.") == "Find the nth term."


def test_indefinite_article_a_is_not_italicised():
    # Only x and n are covered - "a"/"b" (vectors) are explicitly out of
    # scope because "a" collides constantly with the English article.
    assert _markup("OAB is a triangle with OA = a and OB = b.") == (
        "OAB is a triangle with OA = a and OB = b."
    )


def test_real_ratio_1_to_n_sentence():
    assert _markup("Write the ratio 3:5 in the form 1:n.") == (
        f"Write the ratio 3:5 in the form 1:{_italic('n')}."
    )


def test_real_polygon_interior_sentence():
    text = "the interior angles always add up to (n - 2) × 180 degrees, where n is the number of sides."
    markup = _markup(text)
    assert markup.count(_italic("n")) == 2
    assert "number of sides" in markup


def test_surd_over_integer_is_left_as_plain_text():
    # A surd-over-integer exact trig value (see exact_trig_values.py) is a
    # single already-clear unit, deliberately not run through the standalone-
    # fraction OR the radical-image path - the trailing digits are the
    # radicand of the preceding "√", not an independent numerator to raise/
    # lower, and "√2" here must not become a full-length-radical image with a
    # dangling literal "/2" left after it.
    assert _markup("√2/2") == "√2/2"
    assert _markup("√3/2") == "√3/2"
    assert _markup("sin(45°) = √2/2") == "sin(45°) = √2/2"
    assert _markup("3√5/4") == "3√5/4"


def test_unit_rates_are_not_mistaken_for_fractions():
    # These all have a slash but letters (not digits) on at least one side,
    # so they must be left completely alone.
    assert _markup("60 km/h") == "60 km/h"
    assert _markup("3 m/s") == "3 m/s"
    assert _markup("2 g/cm³") == "2 g/cm³"
    assert _markup("5 N/cm²") == "5 N/cm²"


# ---------------------------------------------------------------------------
# Standalone fractions - rendered as an inline <img> (a true vinculum PNG,
# see app/pdf/fraction_images.py), not the old <super>/<sub> markup, so
# these tests check the tag's structure/attributes rather than an exact
# literal string (the src path is a dynamically-generated temp file).
# ---------------------------------------------------------------------------

def _assert_single_fraction_image(markup: str, expected_prefix: str, expected_suffix: str = "") -> re.Match:
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == f"{expected_prefix}{m.group(0)}{expected_suffix}"
    path, width, height = m.group(1), float(m.group(2)), float(m.group(3))
    assert os.path.isfile(path)
    assert width > 0
    assert height > 0
    return m


def test_fraction_is_rendered_as_an_inline_image():
    _assert_single_fraction_image(_markup("3/4"), "")
    _assert_single_fraction_image(_markup("Work out 3/4 of 60."), "Work out ", " of 60.")


def test_negative_fraction_sign_stays_a_plain_leading_character():
    # Only the numerator/denominator/rule are drawn as one image - the sign
    # is ordinary baseline text in front of it.
    _assert_single_fraction_image(_markup("-3/4"), "-")


def test_mixed_number_only_turns_the_fractional_part_into_an_image():
    _assert_single_fraction_image(_markup("3 1/2 cm"), "3 ", " cm")


def test_fraction_followed_by_comma_has_no_special_casing_needed():
    # The old <sub>+comma ReportLab glue quirk doesn't apply to an <img> tag,
    # so (unlike the previous <super>/<sub> markup) no extra spacer is
    # inserted here - the comma sits immediately after the image.
    markup = _markup("20/90, 2/9")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 2
    assert markup == f"{matches[0].group(0)}, {matches[1].group(0)}"


def test_fraction_followed_by_other_punctuation_is_untouched():
    _assert_single_fraction_image(_markup("3/4."), "", ".")
    _assert_single_fraction_image(_markup("3/4:"), "", ":")
    _assert_single_fraction_image(_markup("(3/4)"), "(", ")")


def test_same_fraction_is_cached_to_the_same_file():
    first = _IMG_RE.search(_markup("1/3")).group(1)
    second = _IMG_RE.search(_markup("1/3")).group(1)
    assert first == second


def test_different_font_size_or_colour_produces_a_different_cached_image():
    base = _IMG_RE.search(_markup("1/3", font_size=11.5, color=INK)).group(1)
    bigger = _IMG_RE.search(_markup("1/3", font_size=16, color=INK)).group(1)
    coloured = _IMG_RE.search(_markup("1/3", font_size=11.5, color=ACCENT)).group(1)
    bold = _IMG_RE.search(_markup("1/3", font_size=11.5, color=INK, bold=True)).group(1)
    assert len({base, bigger, coloured, bold}) == 4


def test_multi_digit_fraction_renders_correctly():
    _assert_single_fraction_image(_markup("123/456"), "")


def test_a_bare_x_or_n_inside_the_generated_file_path_is_never_italicised(monkeypatch):
    # Real regression: tempfile.mkdtemp's random suffix can itself contain a
    # bare "x" or "n" flanked by non-letters (e.g. ".../gcse_fractions_k_
    # x7ili6/frac_0.png"). Italicising must run BEFORE the fraction/exponent
    # substitution that inserts this path, not after - otherwise the
    # italics pass re-scans the inserted <img> markup and corrupts the path
    # itself (caught by rendering an actual worksheet PDF, not a unit test -
    # the earlier synthetic spike text never happened to hit a matching
    # random suffix). This test forces the exact scenario deterministically
    # rather than relying on a lucky/unlucky random tempfile name.
    fake_path = r"C:\Users\James\AppData\Local\Temp\gcse_fractions_k_x7ili6\frac_0.png"
    monkeypatch.setattr(
        mathtext_module, "get_fraction_image",
        lambda num, den, font_size, bold, color: FractionImage(path=fake_path, width_pt=8.5, height_pt=16.0),
    )
    markup = _markup("3/4")
    m = _IMG_RE.search(markup)
    assert m is not None
    assert m.group(1) == fake_path


# ---------------------------------------------------------------------------
# Full-length radical ("√n") - rendered as an inline <img> (hook + bar
# spanning the radicand, see app/pdf/radical_images.py).
# ---------------------------------------------------------------------------

def test_radical_is_rendered_as_an_inline_image():
    markup = _markup("√72")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == m.group(0)
    assert os.path.isfile(m.group(1))


def test_radical_within_a_sentence():
    # Both a bare-digit radicand ("72") AND a single-letter radicand ("√b" in
    # the "form a√b" phrasing) get a full radical image, so the bar spans the
    # letter b too (user review feedback - the bar must go the whole way across
    # the b, not leave it as a bare glyph).
    markup = _markup("Simplify √72, giving your answer in the form a√b.")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 2
    assert markup == (
        f"Simplify {matches[0].group(0)}, giving your answer in the form a{matches[1].group(0)}."
    )


def test_radical_wrapping_non_digit_content_is_left_as_plain_text():
    # Only bare-digit radicands are matched - a radical wrapping an
    # unevaluated expression stays plain literal text, unchanged.
    assert _markup("√(4^2 × 3)") == "√(4<super>2</super> × 3)"


def test_radical_with_a_decimal_radicand_covers_the_whole_number():
    # Real bug found via rendering: "√205.1" (an intermediate decimal value,
    # e.g. bearings_cosine_rule's AC² display) only matched the integer part
    # "205" originally, leaving ".1" stranded as plain text right after the
    # radical image instead of under its bar. The whole decimal must now be
    # part of one match/image.
    markup = _markup("AC = √205.1 = 14.32 km")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 1
    assert markup == f"AC = {matches[0].group(0)} = 14.32 km"


# ---------------------------------------------------------------------------
# Explicit \frac{}{} / \recur{}{} sentinel markers - for content the
# automatic digit-only regexes above can't safely auto-detect (an unknown
# placeholder, an algebraic/surd numerator, or a specific recurring block).
# ---------------------------------------------------------------------------

def test_frac_marker_renders_an_unknown_placeholder():
    markup = _markup(r"\frac{?}{12}")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == m.group(0)
    assert os.path.isfile(m.group(1))


def test_frac_marker_renders_an_algebraic_surd_numerator():
    markup = _markup(r"\frac{21 - 4√5}{11}")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == m.group(0)


def test_frac_marker_content_is_not_re_scanned_by_italics_pass():
    # A bare "n" inside a \frac{}{} numerator must render as part of the
    # fraction image, not get corrupted by the earlier italics pass (the
    # same bug class as the file-path regression above, now for marker
    # content instead of a random temp path).
    markup = _markup(r"\frac{n}{2} + 1")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 1
    assert markup == f"{matches[0].group(0)} + 1"


def test_recur_marker_single_digit_block():
    markup = _markup(r"The recurring decimal \recur{0.}{3} can be written as a fraction.")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 1
    assert markup == (
        f"The recurring decimal {matches[0].group(0)} can be written as a fraction."
    )
    assert os.path.isfile(matches[0].group(1))


def test_recur_marker_multi_digit_block():
    markup = _markup(r"\recur{0.1}{428571}")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == m.group(0)


def test_recur_marker_and_frac_marker_can_coexist():
    markup = _markup(r"\recur{0.}{3} = \frac{1}{3}")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 2
    assert markup == f"{matches[0].group(0)} = {matches[1].group(0)}"


def test_colvec_marker_renders_a_column_vector_image():
    markup = _markup(r"\colvec{2}{3}")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == m.group(0)
    assert os.path.isfile(m.group(1))


def test_colvec_marker_handles_negative_components():
    markup = _markup(r"a = \colvec{-2}{5}")
    m = _IMG_RE.search(markup)
    assert m is not None, markup
    assert markup == f"a = {m.group(0)}"


def test_colvec_marker_content_is_not_re_scanned_by_italics_pass():
    # A bare "n" inside a \colvec{}{} component must not get corrupted by the
    # earlier italics pass - same bug class as the \frac{}{} marker test above.
    markup = _markup(r"\colvec{n}{2} + 1")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 1
    assert markup == f"{matches[0].group(0)} + 1"


def test_colvec_and_frac_markers_can_coexist():
    markup = _markup(r"\colvec{2}{3} = \frac{1}{2}\colvec{4}{6}")
    matches = list(_IMG_RE.finditer(markup))
    assert len(matches) == 3


# ---------------------------------------------------------------------------
# \plain{X} - opts a bare letter OUT of the default x/n italics.
# ---------------------------------------------------------------------------

def test_plain_marker_renders_n_upright():
    assert _markup(r"Write the ratio in the form 1:\plain{n}.") == "Write the ratio in the form 1:n."


def test_plain_marker_leaves_other_bare_n_occurrences_italicised():
    # Only the explicitly-marked occurrence is exempted - a different, unmarked
    # "n" elsewhere in the same string is still italicised as normal.
    assert _markup(r"n and \plain{n}") == f"{_italic('n')} and n"


def test_plain_marker_content_is_not_re_scanned_by_other_passes():
    # The bare content is spliced back verbatim after every other pass - a
    # fraction-looking "1/2" inside \plain{} must NOT become a vinculum image.
    assert _markup(r"\plain{1/2}") == "1/2"


# ---------------------------------------------------------------------------
# Trailing full stop directly after a decimal number.
# ---------------------------------------------------------------------------

def test_trailing_period_after_decimal_is_stripped():
    assert _markup("Work out 3.5 × 2.1.") == "Work out 3.5 × 2.1"
    assert _markup("The answer is 12.75.") == "The answer is 12.75"


def test_trailing_period_is_only_stripped_at_the_very_end():
    # A decimal followed by more prose (not the end of the string) must be
    # left completely untouched - only a literal end-of-sentence period
    # directly after a decimal number is in scope.
    assert _markup("3.5 is bigger than 2.1. Now try the next one.") == (
        "3.5 is bigger than 2.1. Now try the next one."
    )


def test_period_after_an_integer_is_not_touched():
    assert _markup("Work out 3 + 4.") == "Work out 3 + 4."


# ---------------------------------------------------------------------------
# Bold vector labels (\vec{a} / \vec{b}) - see app/topics/vectors.py, which
# writes this marker directly in generator source rather than relying on a
# blanket regex (bare "a" collides constantly with the English article).
# ---------------------------------------------------------------------------

def test_vec_sentinel_becomes_bold():
    assert _markup("Find \\vec{a} + \\vec{b}.") == "Find <b>a</b> + <b>b</b>."


def test_vec_sentinel_does_not_bold_a_nearby_unrelated_article():
    assert _markup("a triangle has OA = \\vec{a}") == "a triangle has OA = <b>a</b>"


def test_plain_unmarked_a_or_b_stays_untouched():
    # Confirms the marker, not the bare letter, is what triggers bolding -
    # this is the same sentence CLAUDE.md's deferred-item note uses as the
    # canonical ambiguous example.
    assert _markup("OAB is a triangle with OA = a and OB = b.") == (
        "OAB is a triangle with OA = a and OB = b."
    )


def test_vec_sentinel_survives_alongside_a_coefficient():
    assert _markup("3\\vec{a} - \\vec{b}") == "3<b>a</b> - <b>b</b>"


def test_subscript_bare_digit():
    assert _markup("x_0 = 2") == f"{_italic('x')}<sub>0</sub> = 2"


def test_subscript_bare_letter_is_italicised_inside_sub():
    assert _markup("x_n") == f"{_italic('x')}<sub>{_italic('n')}</sub>"


def test_subscript_parenthesised_expression_drops_the_parens():
    assert _markup("x_(n+1) = g(x_n)") == (
        f"{_italic('x')}<sub>{_italic('n')}+1</sub> = g({_italic('x')}<sub>{_italic('n')}</sub>)"
    )


def test_subscript_composes_with_a_trailing_exponent():
    # "x_n^2" means (x_n)^2 - the subscript and superscript both attach to
    # the same x, giving a real subscript immediately followed by a real
    # superscript, not a nested "n^2".
    assert _markup("x_n^2") == f"{_italic('x')}<sub>{_italic('n')}</sub><super>2</super>"


def test_subscript_followed_by_comma_gets_a_thin_space_not_a_glued_comma():
    # Reintroducing <sub> revives a documented ReportLab quirk (a comma
    # glued/raised immediately after </sub> with zero gap) - confirmed via a
    # real rendered-PDF spike before shipping. A thin space (U+2009) fixes
    # it with a negligible visible gap.
    assert _markup("x_1, x_2") == (
        f"{_italic('x')}<sub>1</sub> , {_italic('x')}<sub>2</sub>"
    )


def test_subscript_not_followed_by_comma_is_untouched():
    assert _markup("x_1 = 2") == f"{_italic('x')}<sub>1</sub> = 2"
