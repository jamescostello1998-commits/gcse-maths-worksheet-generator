"""Inserts real, native PowerPoint equation objects (OMML - Office Math Markup
Language) into a python-pptx paragraph. python-pptx has no built-in support
for this at all - every element here is built and inserted via raw lxml XML
manipulation of the paragraph's own `_p` element.

Confirmed working via a direct spike, done before writing any of this module's
"real" logic (matching this project's own established "verify the riskiest
piece first" discipline): a bare `<m:oMath>` inserted as a plain child of
`<a:p>` is silently dropped by PowerPoint - a slide's DrawingML text uses a
different equation-embedding mechanism than a Word document's WordprocessingML
does. The mechanism that actually works is the Office 2010 math extension:

    <mc:AlternateContent>
      <mc:Choice Requires="a14">
        <a14:m>
          <m:oMathPara><m:oMath> ... </m:oMath></m:oMathPara>
        </a14:m>
      </mc:Choice>
      <mc:Fallback>
        <a:r><a:t>plain-text fallback for older PowerPoint</a:t></a:r>
      </mc:Fallback>
    </mc:AlternateContent>

as a paragraph-level child sitting alongside plain `<a:r>` runs (confirmed:
regular text runs before/after this block render correctly inline on the same
line). Font size/colour are threaded onto each math run's own `<a:rPr>`
(nested inside `<m:rPr>`) - also confirmed empirically (rendered side by side
with plain 18pt text and compared) to genuinely take effect, matching the
surrounding prose rather than falling back to some OMML default.
"""

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.text.text import _Paragraph

_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
_A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"
_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

_NSMAP = {"mc": _MC_NS, "a14": _A14_NS, "m": _M_NS}


def _q(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def _add_math_run(parent, text: str, font_size_pt: float, color: RGBColor) -> None:
    r = etree.SubElement(parent, _q(_M_NS, "r"))
    r_pr = etree.SubElement(r, _q(_M_NS, "rPr"))
    a_rpr = etree.SubElement(r_pr, _q(_A_NS, "rPr"))
    a_rpr.set("sz", str(int(font_size_pt * 100)))
    solid_fill = etree.SubElement(a_rpr, _q(_A_NS, "solidFill"))
    srgb_clr = etree.SubElement(solid_fill, _q(_A_NS, "srgbClr"))
    srgb_clr.set("val", str(color))
    latin = etree.SubElement(a_rpr, _q(_A_NS, "latin"))
    latin.set("typeface", "Cambria Math")
    t = etree.SubElement(r, _q(_M_NS, "t"))
    t.text = text


def _add_fraction_element(parent, numerator: str, denominator: str, font_size_pt: float, color: RGBColor):
    f = etree.SubElement(parent, _q(_M_NS, "f"))
    f_pr = etree.SubElement(f, _q(_M_NS, "fPr"))
    etree.SubElement(f_pr, _q(_M_NS, "ctrlPr"))
    num_el = etree.SubElement(f, _q(_M_NS, "num"))
    _add_math_run(num_el, numerator, font_size_pt, color)
    den_el = etree.SubElement(f, _q(_M_NS, "den"))
    _add_math_run(den_el, denominator, font_size_pt, color)
    return f


def _insert_before_end_para_rpr(paragraph_xml, element) -> None:
    """Inserts `element` as a child of `paragraph_xml`, positioned before any
    trailing `<a:endParaRPr>` rather than appended at the very end.

    A real bug, found via visual inspection of an actual rendered slide (not
    a unit test - equation XML is well-formed either way, so nothing would
    have failed structurally): `<a:endParaRPr>` must always be the LAST child
    of a paragraph per the DrawingML schema (it carries formatting for a
    hypothetical run after the last character). `python-pptx`'s own
    `add_run()` already respects this (every plain-text run in this feature
    lands correctly before it), but a raw `etree.SubElement(paragraph_xml,
    ...)` call has no schema awareness and just appends at the end - placing
    an equation block after `endParaRPr` violates that ordering, and
    PowerPoint silently drops it rather than rendering it or erroring, which
    is why the fraction/bare-math-text cases (added via `add_run()`) worked
    immediately in testing while every exponent case appeared blank until
    this was found and fixed."""
    end_para_rpr = paragraph_xml.find(_q(_A_NS, "endParaRPr"))
    if end_para_rpr is not None:
        end_para_rpr.addprevious(element)
    else:
        paragraph_xml.append(element)


def _start_equation(paragraph_xml, fallback_text: str):
    """Builds the AlternateContent/Choice/a14:m/oMathPara/oMath wrapper (plus
    its plain-text mc:Fallback for older PowerPoint versions), inserted at the
    correct position in the paragraph (before any trailing `endParaRPr` - see
    `_insert_before_end_para_rpr`), returning the empty <m:oMath> element to
    fill in."""
    alt = etree.Element(_q(_MC_NS, "AlternateContent"), nsmap=_NSMAP)
    _insert_before_end_para_rpr(paragraph_xml, alt)
    choice = etree.SubElement(alt, _q(_MC_NS, "Choice"))
    choice.set("Requires", "a14")
    a14_m = etree.SubElement(choice, _q(_A14_NS, "m"))
    o_math_para = etree.SubElement(a14_m, _q(_M_NS, "oMathPara"))
    o_math = etree.SubElement(o_math_para, _q(_M_NS, "oMath"))

    fallback = etree.SubElement(alt, _q(_MC_NS, "Fallback"))
    fb_r = etree.SubElement(fallback, _q(_A_NS, "r"))
    fb_t = etree.SubElement(fb_r, _q(_A_NS, "t"))
    fb_t.text = fallback_text

    return o_math


def add_fraction(
    paragraph: _Paragraph,
    sign: str,
    numerator: str,
    denominator: str,
    font_size_pt: float,
    color: RGBColor,
) -> None:
    """Appends a real, native stacked-fraction equation object to `paragraph`."""
    fallback_text = f"{sign}{numerator}/{denominator}"
    o_math = _start_equation(paragraph._p, fallback_text)
    signed_numerator = f"{sign}{numerator}" if sign else numerator
    _add_fraction_element(o_math, signed_numerator, denominator, font_size_pt, color)


def add_exponent(paragraph: _Paragraph, base: str, exponent: str, font_size_pt: float, color: RGBColor) -> None:
    """Appends a real, native superscript equation object to `paragraph`."""
    fallback_text = f"{base}^{exponent}"
    o_math = _start_equation(paragraph._p, fallback_text)
    s_sup = etree.SubElement(o_math, _q(_M_NS, "sSup"))
    s_sup_pr = etree.SubElement(s_sup, _q(_M_NS, "sSupPr"))
    etree.SubElement(s_sup_pr, _q(_M_NS, "ctrlPr"))
    e_el = etree.SubElement(s_sup, _q(_M_NS, "e"))
    _add_math_run(e_el, base, font_size_pt, color)
    sup_el = etree.SubElement(s_sup, _q(_M_NS, "sup"))
    _add_math_run(sup_el, exponent, font_size_pt, color)


def add_fractional_exponent(
    paragraph: _Paragraph,
    base: str,
    numerator: str,
    denominator: str,
    font_size_pt: float,
    color: RGBColor,
) -> None:
    """Appends a real, native equation object to `paragraph` for a base raised
    to a fractional power - a superscript whose own content is a fraction."""
    fallback_text = f"{base}^({numerator}/{denominator})"
    o_math = _start_equation(paragraph._p, fallback_text)
    s_sup = etree.SubElement(o_math, _q(_M_NS, "sSup"))
    s_sup_pr = etree.SubElement(s_sup, _q(_M_NS, "sSupPr"))
    etree.SubElement(s_sup_pr, _q(_M_NS, "ctrlPr"))
    e_el = etree.SubElement(s_sup, _q(_M_NS, "e"))
    _add_math_run(e_el, base, font_size_pt, color)
    sup_el = etree.SubElement(s_sup, _q(_M_NS, "sup"))
    _add_fraction_element(sup_el, numerator, denominator, font_size_pt, color)
