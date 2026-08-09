"""Inserts real, native Word equation objects (OMML - Office Math Markup
Language) into a python-docx paragraph. python-docx has no built-in support
for equations at all - every element here is built and appended via raw lxml
XML manipulation of the paragraph's own `<w:p>` element.

This is the Word (WordprocessingML) sibling of `app/bell_tasks/omml.py`, which
does the same job for PowerPoint. The two are deliberately separate because the
embedding mechanism differs by document type:

- PowerPoint (a slide's DrawingML) needs the Office-2010 math *extension*
  wrapper (`mc:AlternateContent` / `a14:m` / `m:oMathPara`) - a bare `<m:oMath>`
  is silently dropped there (see bell_tasks/omml.py's docstring).
- Word is simpler: a bare `<m:oMath>` sits **directly** as a child of the
  paragraph `<w:p>`, interleaved inline with ordinary `<w:r>` text runs, and
  renders correctly. No AlternateContent/fallback wrapper is needed, and unlike
  a DrawingML paragraph there is no trailing `endParaRPr` element to insert
  before - a `<w:p>` takes its runs/maths in plain document order, so appending
  each token's element in left-to-right order (which `render._add_runs` does)
  keeps everything in the right place.

Word renders every equation in Cambria Math by default; the font/size/colour of
each math run is nonetheless set explicitly on a standard `<w:rPr>` child of the
math run (`<w:rFonts>` Cambria Math, `<w:sz>` in half-points, `<w:color>`) so
the maths matches the surrounding prose's size and colour rather than falling
back to a Word default. Confirmed via a rendered-in-Word spike (build a minimal
fraction + superscript, open in real Word via COM automation, look at the
result) before this module was wired into the renderer, matching this project's
"verify the riskiest piece first" discipline.
"""

from lxml import etree
from docx.text.paragraph import Paragraph

_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XML_NS = "http://www.w3.org/XML/1998/namespace"

_NSMAP = {"m": _M_NS, "w": _W_NS}


def _q(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def _add_math_run(parent, text: str, font_size_pt: float, color_hex: str) -> None:
    """A single math run `<m:r>` carrying explicit font/size/colour so it
    matches the surrounding prose, then the literal text in `<m:t>`."""
    r = etree.SubElement(parent, _q(_M_NS, "r"))
    r_pr = etree.SubElement(r, _q(_W_NS, "rPr"))
    rfonts = etree.SubElement(r_pr, _q(_W_NS, "rFonts"))
    rfonts.set(_q(_W_NS, "ascii"), "Cambria Math")
    rfonts.set(_q(_W_NS, "hAnsi"), "Cambria Math")
    sz = etree.SubElement(r_pr, _q(_W_NS, "sz"))
    sz.set(_q(_W_NS, "val"), str(int(round(font_size_pt * 2))))  # Word uses half-points
    color = etree.SubElement(r_pr, _q(_W_NS, "color"))
    color.set(_q(_W_NS, "val"), color_hex)
    t = etree.SubElement(r, _q(_M_NS, "t"))
    t.set(_q(_XML_NS, "space"), "preserve")
    t.text = text


def _add_fraction_element(parent, numerator: str, denominator: str, font_size_pt: float, color_hex: str):
    f = etree.SubElement(parent, _q(_M_NS, "f"))
    f_pr = etree.SubElement(f, _q(_M_NS, "fPr"))
    etree.SubElement(f_pr, _q(_M_NS, "ctrlPr"))
    num_el = etree.SubElement(f, _q(_M_NS, "num"))
    _add_math_run(num_el, numerator, font_size_pt, color_hex)
    den_el = etree.SubElement(f, _q(_M_NS, "den"))
    _add_math_run(den_el, denominator, font_size_pt, color_hex)
    return f


def _start_equation(paragraph: Paragraph):
    """Appends a bare `<m:oMath>` to the paragraph's `<w:p>` (Word needs no
    AlternateContent wrapper, unlike the PowerPoint sibling), returning the
    empty `<m:oMath>` element to fill in."""
    o_math = etree.SubElement(paragraph._p, _q(_M_NS, "oMath"))
    return o_math


def add_fraction(
    paragraph: Paragraph, sign: str, numerator: str, denominator: str, font_size_pt: float, color_hex: str
) -> None:
    """Appends a real, native stacked-fraction equation object to `paragraph`."""
    o_math = _start_equation(paragraph)
    signed_numerator = f"{sign}{numerator}" if sign else numerator
    _add_fraction_element(o_math, signed_numerator, denominator, font_size_pt, color_hex)


def add_exponent(paragraph: Paragraph, base: str, exponent: str, font_size_pt: float, color_hex: str) -> None:
    """Appends a real, native superscript equation object to `paragraph`."""
    o_math = _start_equation(paragraph)
    s_sup = etree.SubElement(o_math, _q(_M_NS, "sSup"))
    s_sup_pr = etree.SubElement(s_sup, _q(_M_NS, "sSupPr"))
    etree.SubElement(s_sup_pr, _q(_M_NS, "ctrlPr"))
    e_el = etree.SubElement(s_sup, _q(_M_NS, "e"))
    _add_math_run(e_el, base, font_size_pt, color_hex)
    sup_el = etree.SubElement(s_sup, _q(_M_NS, "sup"))
    _add_math_run(sup_el, exponent, font_size_pt, color_hex)


def add_fractional_exponent(
    paragraph: Paragraph, base: str, numerator: str, denominator: str, font_size_pt: float, color_hex: str
) -> None:
    """Appends a real, native equation object to `paragraph` for a base raised
    to a fractional power - a superscript whose own content is a fraction."""
    o_math = _start_equation(paragraph)
    s_sup = etree.SubElement(o_math, _q(_M_NS, "sSup"))
    s_sup_pr = etree.SubElement(s_sup, _q(_M_NS, "sSupPr"))
    etree.SubElement(s_sup_pr, _q(_M_NS, "ctrlPr"))
    e_el = etree.SubElement(s_sup, _q(_M_NS, "e"))
    _add_math_run(e_el, base, font_size_pt, color_hex)
    sup_el = etree.SubElement(s_sup, _q(_M_NS, "sup"))
    _add_fraction_element(sup_el, numerator, denominator, font_size_pt, color_hex)


def add_column_vector(paragraph: Paragraph, top: str, bottom: str, font_size_pt: float, color_hex: str) -> None:
    """Appends a real, native column vector - a two-row, one-column matrix
    wrapped in round brackets (an `<m:d>` delimiter around an `<m:m>` matrix) -
    matching standard GCSE vector notation, rather than a flat "(top, bottom)"
    text fallback."""
    o_math = _start_equation(paragraph)
    delim = etree.SubElement(o_math, _q(_M_NS, "d"))
    d_pr = etree.SubElement(delim, _q(_M_NS, "dPr"))
    beg = etree.SubElement(d_pr, _q(_M_NS, "begChr"))
    beg.set(_q(_M_NS, "val"), "(")
    end = etree.SubElement(d_pr, _q(_M_NS, "endChr"))
    end.set(_q(_M_NS, "val"), ")")
    etree.SubElement(d_pr, _q(_M_NS, "ctrlPr"))
    d_e = etree.SubElement(delim, _q(_M_NS, "e"))
    matrix = etree.SubElement(d_e, _q(_M_NS, "m"))
    m_pr = etree.SubElement(matrix, _q(_M_NS, "mPr"))
    base_jc = etree.SubElement(m_pr, _q(_M_NS, "baseJc"))
    base_jc.set(_q(_M_NS, "val"), "center")
    plc_hide = etree.SubElement(m_pr, _q(_M_NS, "plcHide"))
    plc_hide.set(_q(_M_NS, "val"), "1")
    mcs = etree.SubElement(m_pr, _q(_M_NS, "mcs"))
    mc = etree.SubElement(mcs, _q(_M_NS, "mc"))
    mc_pr = etree.SubElement(mc, _q(_M_NS, "mcPr"))
    count = etree.SubElement(mc_pr, _q(_M_NS, "count"))
    count.set(_q(_M_NS, "val"), "1")
    mc_jc = etree.SubElement(mc_pr, _q(_M_NS, "mcJc"))
    mc_jc.set(_q(_M_NS, "val"), "center")
    etree.SubElement(m_pr, _q(_M_NS, "ctrlPr"))
    for value in (top, bottom):
        row = etree.SubElement(matrix, _q(_M_NS, "mr"))
        cell = etree.SubElement(row, _q(_M_NS, "e"))
        _add_math_run(cell, value, font_size_pt, color_hex)
