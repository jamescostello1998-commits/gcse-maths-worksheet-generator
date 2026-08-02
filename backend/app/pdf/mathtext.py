r"""Centralised plain-text -> ReportLab Paragraph markup conversion for maths
text (question prompts, solution steps, final answers).

Topic generators emit plain text like "3x^2 + 5", "10^-3", "3/4", "x^(1/4)",
"8^x", "9^(x+2)" or "√72" using an ASCII convention (bare 'x'/'n' for
algebraic variables, '^n'/'^x'/'^(expr)' for exponents, "num/den" for a
standalone fraction, "√n" for a square root) so they stay easy to write,
verify, and unit-test. `to_markup` is applied once, centrally, at PDF-render
time to turn that into real typesetting: x and n are italicised in a
genuinely curved font, '^n'/'^x'/'^(expr)' become a real superscript, a
standalone fraction is drawn as a true stacked vinculum, and "√n" is drawn as
a true full-length radical (a hook + bar spanning the whole radicand) -
rather than sitting inline as plain ASCII. Any future topic that follows the
same ASCII convention gets correct typesetting for free.

Only x and n are italicised via a blanket regex - see CLAUDE.md for why a
blanket rule can't safely cover every single-letter variable (e.g. "a"
collides constantly with the English indefinite article). Vector labels "a"/
"b" are bolded instead (matching real exam convention), but via an explicit
per-occurrence marker written directly in generator source - `\vec{a}` /
`\vec{b}` - rather than a blanket regex, since there's no way to tell a
genuine vector mention from the English article by pattern alone. This is
still a plain-ASCII convention parsed centrally here (consistent with `^n`/
`num/den`), not hand-written PDF markup - see `_VECTOR_RE` below and
`app/topics/vectors.py`.

**Italic x/n use a registered curved-italic TrueType font, not `<i>`.**
ReportLab's `<i>` tag resolves to the *Standard-14* family's own oblique face
(`Helvetica-Oblique` here) regardless of any other font registered under a
different name - rebinding what `<i>` means would need a second
`registerFontFamily`/`addMapping` call, an unnecessarily fragile extra step.
Instead `_VARIABLE_RE`'s substitution emits an explicit
`<font name="...">` tag naming one of two registered TTF fonts
(`_VAR_FONT_ITALIC`/`_VAR_FONT_BOLD_ITALIC`, chosen via the same `bold` param
already threaded through for fraction images) - exactly the idiom
`app/pdf/diagrams.py` already uses for its own (parallel, independent) label
rendering, just via `<font name>` markup instead of a `String(fontName=...)`
call. Times New Roman Italic/Bold Italic were chosen for a genuinely curved
"x" glyph, visually distinct from the straight-stroked Helvetica-Oblique "x"
(easily confused with the × multiplication sign) - confirmed via a real
rendered-PDF spike (standalone, nested inside `<super>`, inside a bold
`ParagraphStyle`, and at the smallest font size fractions appear anywhere in
the app) before being adopted app-wide. `diagrams.py` imports the same two
registered font names directly for its own `String(fontName=...)` calls, so
prose text and diagram labels always render the identical italic face.

**Standalone fractions are rendered as a small PNG and embedded inline via
`<img>`** (app/pdf/fraction_images.py) - a true vinculum can't be built from
Paragraph markup alone (there's no tag for "numerator, rule, denominator"),
and ReportLab's own image rasteriser (`renderPM`, which could otherwise turn
a vector `Drawing` into an embeddable image) isn't installed in this
environment (needs Cairo bindings) - so PIL draws the digits and rule
directly onto a transparent-background PNG instead, using the same font
files ReportLab/Windows already use, cached per unique (num, den, size,
bold, colour) so a repeated fraction like "1/2" isn't re-rendered on every
occurrence. `to_markup` therefore needs the caller's font size/colour/weight
(the surrounding Paragraph style) to size and colour the image to match -
see the `font_size`/`color`/`bold` parameters. `valign="bottom"` on the
`<img>` tag was confirmed (by rendering real text side by side at several
valign values and comparing pixel-for-pixel) to align the fraction's own
"baseline" - the bottom of the denominator digits - with the surrounding
text's baseline, with no extra offset math needed. The leading sign of a
negative fraction (e.g. "-3/4") stays a plain baseline character before the
`<img>` tag - only the num/den/rule are drawn as one unit. See
app/pdf/diagrams.py's `_draw_fraction` for the same true-vinculum idea
applied to diagram labels, which draws directly as vector shapes instead
(diagrams don't have Paragraph markup's inline-image constraint).

**A fractional exponent (e.g. "x^(1/4)") is now ALSO a true raised vinculum**
- `get_fraction_image` at a reduced font size, placed inside `<super>` -
reversing an earlier deliberate decision (kept flat raised text, judged "not
worth the complexity") once a spike confirmed the nested image rises and
aligns correctly, including at the smallest font size fractions appear
anywhere in the app (the practice-test mark scheme's 9pt table). A generic
*compound* exponent (e.g. "9^(x+2)", "5^(3x)" - anything in parens after `^`
that ISN'T a plain numeric fraction) is instead wrapped as flat
`<super>(...)</super>` - its contents (already italicised by the earlier
`_VARIABLE_RE` pass) are just raised as-is, since there's no vinculum-shaped
sub-content to draw. A bare single-variable exponent ("8^x", "9^n") is raised
italic text, `<super><font name="...">x</font></super>`.

**A standalone "√n" is now a true full-length radical** (app/pdf/radical_images.py)
- a hook plus a horizontal bar spanning the whole radicand, matching real
exam typesetting - rather than the bare Unicode "√" glyph glued directly in
front of the digits with no bar at all. Only bare-digit radicands are
matched (`√(?P<radn>\d+)`); a radical wrapping non-digit content (e.g. an
unevaluated "√(k^2 × m)" mid-working expression) is left as plain literal
text, unchanged - confirmed by audit that no topic currently needs the full
treatment there. **Deliberately excluded via a `(?!/\d)` lookahead**: a
radical immediately followed by "/digit" (e.g. exact trig values like
"√2/2", "√3/2") - these are a single already-clear unit, meant to stay a
flat literal string (see the "Surd-over-integer gotcha" further down), not
be split into a radical-image "√2" plus a dangling literal "/2". Any topic
that genuinely wants a fraction with a surd numerator (e.g.
`rationalise_denominator`'s "3√5/2") should use the `\frac{}{}` marker below
instead of relying on this auto-detection - within a `\frac{}{}` marker, a
"√" renders as plain Arial glyph text (not the fancy full-length-bar
treatment), which is legible enough for the short expressions that appear
there and avoids recursive-rendering complexity.

**Two explicit ASCII sentinel markers - `\frac{NUM}{DEN}` and
`\recur{PREFIX}{BLOCK}`** - let a generator ask for a fraction/recurring-
decimal image directly, for content the automatic digit-only regexes below
can't safely auto-detect (an unknown placeholder like "?", an algebraic/surd
numerator like "21 - 4√5", or which specific digits are the recurring block
of a decimal). This is the same precedent as `\vec{a}`/`\vec{b}`: a blanket
regex can't safely disambiguate this content from ordinary text, so the
generator marks it explicitly instead. `\frac{}{}`'s NUM/DEN are passed
straight through to `get_fraction_image` with no validation (that function
already accepts arbitrary strings, not just digits). `\recur{}{}`'s PREFIX
is the non-recurring digits before the repeating block (may be empty, e.g.
`\recur{}{3}` for "0.(3)"), BLOCK is the repeating digits - dots are placed
over the single digit (if BLOCK has length 1) or over both the first and
last digit of BLOCK (matching the confirmed UK GCSE convention).

**A third sentinel, `\plain{X}`, opts a bare letter OUT of the automatic
x/n italics** - for the rare case where "n" (or "x") appears as a plain
notational placeholder rather than a genuine algebraic variable, e.g.
`ratio_1_to_n`'s "1:n"/"n:1" ratio-form notation, where real exam
convention leaves the "n" upright. This is the same "blanket regex can't
safely disambiguate, so the generator marks it explicitly" precedent as
`\vec{a}`/`\vec{b}` and the fraction/recurring-decimal markers, just in the
opposite direction (opt OUT of styling rather than opt IN) - `x`/`n` are
italicised by default everywhere else, so this stays a rare, explicit
exception, not a new default.

**Marker content is protected from the italics/vector passes via an early
extraction step.** `\frac{}{}`/`\recur{}{}`/`\plain{}` spans are pulled out
and replaced with an opaque placeholder *before* `_VARIABLE_RE`/`_VECTOR_RE`
run, then the real markup (rendered `<img>` for the first two, the bare
literal content for `\plain{}`) is spliced back in after `_MATH_RE`'s pass. This
forecloses the exact bug class already documented below for the fraction-
image temp-path: a bare `x`/`n` or `\vec{}` sitting inside a marker's braces
(plausible for an algebraic numerator) would otherwise get corrupted by the
earlier italics/bold pass before the marker's own regex ever saw it as one
unit. The placeholder is a Private Use Area Unicode character
(`chr(0xE000 + i)`) - guaranteed not to collide with any real generator
content and not matched by any other regex in this file (no letters/digits/
punctuation), and never reaches ReportLab, since it's replaced back to real
markup before `to_markup` returns.

All the numeric/marker patterns above are matched by ONE combined regex
(`_MATH_RE`) in a single `re.sub` pass, rather than several separate
sequential passes - a fractional exponent's raised fraction-image would
otherwise be indistinguishable from a standalone fraction once substituted,
and a later, separate fraction pass would re-match and re-process it
(producing a broken doubly-nested result). Matching everything in one pass
means each character is claimed by exactly one alternative and never
re-scanned. Within the alternation, the numeric fractional-exponent
alternative is listed BEFORE the generic compound-exponent alternative, so
"^(1/4)" still preferentially matches the specific (now vinculum-in-super)
case while "^(x+2)" falls through to the generic flat-raise case.

**Glyph gotcha**: the unicode division slash U+2215 ("∕") is NOT in Helvetica
either (renders as a missing-glyph box, same class of issue as the "⁻¹"
gotcha documented in CLAUDE.md) - a fractional exponent's "/" must stay a
plain ASCII slash.

**Surd-over-integer gotcha**: an exact trig value like "√2/2" or "√3/2" (see
exact_trig_values.py) is a single already-clear unit, deliberately written as
a flat literal string, not run through the standalone-fraction OR the new
radical-image path - see the radical-image paragraph above for the
`(?!/\d)` lookahead that keeps this working, and the pre-existing `(?<!√)`
lookbehind on the plain-fraction alternative that does the equivalent job
for the fraction side (so the trailing "2/2"/"3/2" digits aren't turned into
a fraction image with a stray literal "√" left dangling in front of it).

**A trailing full stop directly after a decimal number is stripped** (e.g.
"...Work out 3.5 × 2.1." -> "...Work out 3.5 × 2.1") - a defensive,
end-anchored regex applied first, before any other pass. This is a
punctuation normalisation, not a math substitution, but lives here because
`to_markup` is the one function shared by all three PDF renderers, so a
single fix here covers every topic's prompt without needing to touch the
~40 files that hardcode a trailing period into their prompt strings.

**A real subscript for "x_n"/"x_(n+1)"-style notation** (chronology step
after 36 - the iteration.py fix that had been blocked pending a reference
image): `iteration.py`'s recurrence notation was previously a literal
underscore character glued between "x" and the index (e.g. "x_(n+1)"
rendered exactly as those 7 characters), never given any real subscript
treatment - the reference image the user supplied showed a true subscript
with no visible underscore or parentheses, matching standard exam
notation. `_SUBSCRIPT_RE` matches "x_" followed by either a parenthesised
group (parens stripped, not shown) or a single bare alnum run, and wraps
the content in a real `<sub>` tag - run BEFORE the italics pass, so a bare
"n" inside still gets italicised normally by `_VARIABLE_RE` afterward (the
outer "x" does too, since it's left as plain text). This is a genuine
engine capability, not a one-off patch to iteration.py's strings - any
future topic using the same "x_" ASCII convention gets it for free.

**Reintroducing `<sub>` revived a documented historical ReportLab quirk**:
a comma immediately following a closing `</sub>` with zero gap renders
glued to, and slightly raised with, the preceding subscript (confirmed via
a real rendered-PDF spike before shipping this - iteration.py's own prompt
text has exactly this shape, e.g. "x_1, x_2 and x_3"). A zero-width space
was tried first and rejected (Helvetica has no glyph for it, same class of
issue as the "⁻¹" gotcha in CLAUDE.md - it rendered as a missing-glyph
box); a thin space (U+2009, which Helvetica does have) fixes the glue with
only a negligible visible gap, confirmed the same way. `_SUB_COMMA_RE`
inserts it wherever `</sub>` is immediately followed by ",".

**A subscript embedded inside a `\frac{}{}` marker's own numerator/
denominator is a separate, narrower fix** - see `app/pdf/fraction_images.py`,
since that content is drawn as raw PIL text, not Paragraph markup, and
never passes through this module's regexes at all (it's already extracted
into an opaque placeholder and rendered to an image before `_SUBSCRIPT_RE`
would ever see it).
"""

import re

from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.pdf.fraction_images import get_fraction_image
from app.pdf.radical_images import get_radical_image
from app.pdf.recurring_decimal_images import get_recurring_decimal_image

# Registered once at import time - see the module docstring for why a
# registered TTF + explicit <font name> tag is used instead of <i>.
_VAR_FONT_ITALIC = "MathsVariableItalic"
_VAR_FONT_BOLD_ITALIC = "MathsVariableBoldItalic"
pdfmetrics.registerFont(TTFont(_VAR_FONT_ITALIC, r"C:\Windows\Fonts\timesi.ttf"))
pdfmetrics.registerFont(TTFont(_VAR_FONT_BOLD_ITALIC, r"C:\Windows\Fonts\timesbi.ttf"))

# Reduced size for a fraction image raised inside <super> - roughly matches
# how a real superscript sits visibly smaller than the base text.
_SUP_FRACTION_SCALE = 0.75

# Matches, in priority order within one alternation so each span is consumed
# exactly once: (1) a fractional exponent "^(num/den)" -> vinculum-in-super,
# (2) a generic compound exponent "^(...)" -> flat raised text, (3) a plain
# integer exponent "^n", (4) a bare single-variable exponent "^x"/"^n",
# (5) a full-length radical "√n", (6) a standalone "num/den" fraction.
_MATH_RE = re.compile(
    r"\^\((?P<epnum>-?\d+)/(?P<epden>-?\d+)\)"
    r"|\^\((?P<cexp>[^()]*)\)"
    r"|\^(?P<exp>-?\d+)"
    r"|\^(?P<vexp>[xn])(?![A-Za-z])"
    r"|√(?P<radn>\d+)(?!/\d)"
    r"|(?<!√)(?P<fsign>-?)(?P<fnum>\d+)/(?P<fden>\d+)"
)
# Matches a lone x or n not glued to another letter (so "box" or "and" are
# left alone), and NOT immediately preceded by "^" (that case is a bare
# variable exponent, handled by _MATH_RE's `vexp` alternative instead, which
# needs the raw un-italicised "x"/"n" available to match against) - single
# pass over the original text so italicising one variable can never change
# what the other one sees as its neighbour.
_VARIABLE_RE = re.compile(r"(?<![A-Za-z^])[xn](?![A-Za-z])")
# Matches the explicit vector-letter marker \vec{a} / \vec{b} - written
# directly in generator source (see app/topics/vectors.py) rather than
# matched by a blanket letter pattern, since "a" collides constantly with
# the English indefinite article and can't be disambiguated by regex alone.
_VECTOR_RE = re.compile(r"\\vec\{([ab])\}")
# The three explicit sentinel markers - see the module docstring's "Two
# explicit ASCII sentinel markers" and "A third sentinel, \plain{X}" sections.
_MARKER_RE = re.compile(
    r"\\frac\{(?P<mnum>[^{}]*)\}\{(?P<mden>[^{}]*)\}"
    r"|\\recur\{(?P<mprefix>[^{}]*)\}\{(?P<mblock>[^{}]*)\}"
    r"|\\plain\{(?P<mplain>[^{}]*)\}"
)
# A literal "." immediately after a decimal number, at the very end of the
# string - see the module docstring's final paragraph.
_TRAILING_DECIMAL_PERIOD_RE = re.compile(r"(\d+\.\d+)\.$")

# "x_n" / "x_(n+1)" -style subscript notation - see the module docstring's
# "A real subscript" paragraph. The base "x" is left as plain text (picked
# up by the italics pass below like any other bare "x"); only the part
# after "_" is wrapped in <sub>, with its parentheses (if any) stripped.
_SUBSCRIPT_RE = re.compile(r"(?<![A-Za-z])x_(?:\((?P<sub_paren>[^()]+)\)|(?P<sub_bare>[A-Za-z0-9]+))")

# The historical "comma glued to </sub>" ReportLab quirk - see the module
# docstring's "Reintroducing <sub>" paragraph.
_SUB_COMMA_RE = re.compile(r"</sub>(?=,)")

# Private Use Area base codepoint for marker placeholders - see the module
# docstring's "Marker content is protected..." paragraph.
_PLACEHOLDER_BASE = 0xE000


def _extract_markers(text: str, font_size: float, color: Color, bold: bool) -> tuple[str, list[str]]:
    placeholders: list[str] = []

    def repl(m: re.Match) -> str:
        if m.group("mplain") is not None:
            placeholders.append(m.group("mplain"))
            return chr(_PLACEHOLDER_BASE + len(placeholders) - 1)
        if m.group("mnum") is not None:
            img = get_fraction_image(m.group("mnum"), m.group("mden"), font_size, bold, color)
            valign = "bottom"
        else:
            img = get_recurring_decimal_image(m.group("mprefix"), m.group("mblock"), font_size, bold, color)
            # Unlike fraction/radical images (whose ink touches both the top
            # AND bottom of the image, so "bottom" already lands correctly),
            # this image only has padding ABOVE the digits (reserved for the
            # dot mark) - "bottom" would align to the line's descender space
            # instead of the true text baseline, visibly sinking the digits.
            # Confirmed via a real rendered-PDF spike comparing valign values
            # side by side (same discipline as fraction_images.py's own
            # valign spike).
            valign = "baseline"
        placeholders.append(f'<img src="{img.path}" width="{img.width_pt:.2f}" height="{img.height_pt:.2f}" valign="{valign}"/>')
        return chr(_PLACEHOLDER_BASE + len(placeholders) - 1)

    return _MARKER_RE.sub(repl, text), placeholders


def _reinsert_markers(text: str, placeholders: list[str]) -> str:
    for i, markup in enumerate(placeholders):
        text = text.replace(chr(_PLACEHOLDER_BASE + i), markup)
    return text


def _replace_math(m: re.Match, font_size: float, color: Color, bold: bool) -> str:
    if m.group("epnum") is not None:
        img = get_fraction_image(m.group("epnum"), m.group("epden"), font_size * _SUP_FRACTION_SCALE, bold, color)
        return f'<super><img src="{img.path}" width="{img.width_pt:.2f}" height="{img.height_pt:.2f}" valign="bottom"/></super>'
    if m.group("cexp") is not None:
        return f"<super>({m.group('cexp')})</super>"
    if m.group("exp") is not None:
        return f"<super>{m.group('exp')}</super>"
    if m.group("vexp") is not None:
        font_name = _VAR_FONT_BOLD_ITALIC if bold else _VAR_FONT_ITALIC
        return f'<super><font name="{font_name}">{m.group("vexp")}</font></super>'
    if m.group("radn") is not None:
        img = get_radical_image(m.group("radn"), font_size, bold, color)
        return f'<img src="{img.path}" width="{img.width_pt:.2f}" height="{img.height_pt:.2f}" valign="bottom"/>'
    sign, num, den = m.group("fsign"), m.group("fnum"), m.group("fden")
    img = get_fraction_image(num, den, font_size, bold, color)
    return f'{sign}<img src="{img.path}" width="{img.width_pt:.2f}" height="{img.height_pt:.2f}" valign="bottom"/>'


def to_markup(text: str, *, font_size: float, color: Color, bold: bool = False) -> str:
    # A generator can force a real line break in rendered prose by putting a
    # literal "\n" in its prompt/step text - _escape() (which runs before
    # this function, in every renderer) only touches &/</>, so a raw
    # newline survives untouched and is safe to convert to ReportLab's own
    # <br/> tag here, unlike hand-writing "<br/>" directly in generator
    # code (which _escape() would mangle into visible "&lt;br/&gt;" text).
    text = text.replace("\n", "<br/>")

    # Punctuation normalisation first (pure string op, no interaction with
    # anything else - see the module docstring's final paragraph).
    text = _TRAILING_DECIMAL_PERIOD_RE.sub(r"\1", text)

    # Extract \frac{}{}/\recur{}{} markers into opaque placeholders BEFORE
    # italicising, so their raw content is never re-scanned/corrupted by the
    # passes below (see the module docstring's "Marker content is
    # protected..." paragraph).
    text, placeholders = _extract_markers(text, font_size, color, bold)

    # Convert "x_n"/"x_(n+1)"-style subscript notation to a real <sub> tag
    # BEFORE italicising, so the bare letter(s) inside are still available
    # for _VARIABLE_RE to italicise normally in the next step (see the
    # module docstring's "A real subscript" paragraph). Immediately fix up
    # the historical comma-after-</sub> ReportLab quirk this can expose.
    text = _SUBSCRIPT_RE.sub(
        lambda m: f"x<sub>{m.group('sub_paren') if m.group('sub_paren') is not None else m.group('sub_bare')}</sub>",
        text,
    )
    text = _SUB_COMMA_RE.sub("</sub> ", text)

    # Italicise x/n and bold \vec{a}/\vec{b} BEFORE substituting fractions/
    # exponents/radicals, not after: those substitutions insert <img
    # src="..."/> tags whose file paths are randomly-named temp files
    # (tempfile.mkdtemp), and that random suffix can itself contain a bare
    # "x" or "n" flanked by non-letters (e.g.
    # ".../gcse_fractions_k_x7ili6/frac_0.png") - running _VARIABLE_RE
    # afterward would re-scan and italicise part of the file path, corrupting
    # it (found via an actual end-to-end worksheet render, not a unit test -
    # the synthetic spike text never happened to produce a matching random
    # suffix). Doing the math substitution last means its inserted markup is
    # never re-scanned by anything else. _VECTOR_RE has no actual collision
    # risk (\vec{a}/\vec{b} contain no digits or bare x/n), but runs in this
    # same early pass for the same safety-discipline reason.
    var_font = _VAR_FONT_BOLD_ITALIC if bold else _VAR_FONT_ITALIC
    text = _VARIABLE_RE.sub(lambda m: f'<font name="{var_font}">{m.group(0)}</font>', text)
    text = _VECTOR_RE.sub(lambda m: f"<b>{m.group(1)}</b>", text)
    text = _MATH_RE.sub(lambda m: _replace_math(m, font_size, color, bold), text)

    return _reinsert_markers(text, placeholders)
