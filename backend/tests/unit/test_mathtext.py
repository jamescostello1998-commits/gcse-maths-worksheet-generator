import os
import re

from reportlab.lib.colors import HexColor

import app.pdf.mathtext as mathtext_module
from app.pdf.fraction_images import FractionImage
from app.pdf.mathtext import to_markup

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")

_IMG_RE = re.compile(r'<img src="([^"]+)" width="([^"]+)" height="([^"]+)" valign="bottom"/>')


def _markup(text: str, font_size: float = 11.5, color=INK, bold: bool = False) -> str:
    return to_markup(text, font_size=font_size, color=color, bold=bold)


def test_exponents_become_superscript():
    assert _markup("3x^2 + 5") == "3<i>x</i><super>2</super> + 5"
    assert _markup("10^-3") == "10<super>-3</super>"


def test_fractional_exponent_is_raised_as_one_unit():
    assert _markup("x^(1/4)") == "<i>x</i><super>(1/4)</super>"
    assert _markup("(9x^6)^(1/2)") == "(9<i>x</i><super>6</super>)<super>(1/2)</super>"
    assert _markup("x^(-1/2)") == "<i>x</i><super>(-1/2)</super>"


def test_bare_x_is_italicised():
    assert _markup("Solve for x.") == "Solve for <i>x</i>."
    assert _markup("3x + 1 = 7") == "3<i>x</i> + 1 = 7"


def test_bare_n_is_italicised():
    assert _markup("Find n.") == "Find <i>n</i>."
    assert _markup("(n - 2) × 180") == "(<i>n</i> - 2) × 180"


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
        "Write the ratio 3:5 in the form 1:<i>n</i>."
    )


def test_real_polygon_interior_sentence():
    text = "the interior angles always add up to (n - 2) × 180 degrees, where n is the number of sides."
    markup = _markup(text)
    assert markup.count("<i>n</i>") == 2
    assert "number of sides" in markup


def test_surd_over_integer_is_left_as_plain_text():
    # A surd-over-integer exact trig value (see exact_trig_values.py) is a
    # single already-clear unit, deliberately not run through the standalone-
    # fraction path - the trailing digits are the radicand of the preceding
    # "√", not an independent numerator to raise/lower.
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
