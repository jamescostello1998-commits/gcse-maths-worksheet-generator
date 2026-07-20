from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#6b6b6b")
ACCENT = colors.HexColor("#2f6f4f")
RULE = colors.HexColor("#dddddd")
GRID = colors.HexColor("#dcdcdc")
HIGHLIGHT = colors.HexColor("#fdf0d5")

MARGIN = 22 * mm

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def build_styles() -> dict[str, ParagraphStyle]:
    return {
        "Title": ParagraphStyle(
            "Title", fontName=FONT_BOLD, fontSize=20, leading=24, textColor=INK,
            spaceAfter=4, alignment=TA_LEFT,
        ),
        "Meta": ParagraphStyle(
            "Meta", fontName=FONT, fontSize=10.5, leading=13, textColor=MUTED, spaceAfter=16,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading", fontName=FONT_BOLD, fontSize=17, leading=20, textColor=INK,
            spaceBefore=0, spaceAfter=14,
        ),
        "QuestionText": ParagraphStyle(
            "QuestionText", fontName=FONT, fontSize=11.5, textColor=INK,
            leading=17, spaceAfter=10,
        ),
        "SolutionHeading": ParagraphStyle(
            "SolutionHeading", fontName=FONT_BOLD, fontSize=11.5, leading=14, textColor=ACCENT,
            spaceBefore=8, spaceAfter=4,
        ),
        "SolutionStep": ParagraphStyle(
            "SolutionStep", fontName=FONT, fontSize=10.5, textColor=INK,
            leftIndent=14, leading=15, spaceAfter=2,
        ),
        "FinalAnswer": ParagraphStyle(
            "FinalAnswer", fontName=FONT_BOLD, fontSize=10.5, leading=13, textColor=INK,
            leftIndent=14, spaceBefore=4, spaceAfter=10,
        ),
        "WorkedPrompt": ParagraphStyle(
            "WorkedPrompt", fontName=FONT_BOLD, fontSize=13.5, leading=19, textColor=INK,
            spaceAfter=16,
        ),
        "TeachingStep": ParagraphStyle(
            "TeachingStep", fontName=FONT, fontSize=11.5, textColor=INK,
            leftIndent=16, leading=17, spaceAfter=14,
        ),
        "TeachingAnswer": ParagraphStyle(
            "TeachingAnswer", fontName=FONT_BOLD, fontSize=13, leading=16, textColor=ACCENT,
            spaceBefore=10, spaceAfter=6,
        ),
        "PracticeIntro": ParagraphStyle(
            "PracticeIntro", fontName=FONT, fontSize=10.5, leading=14, textColor=MUTED,
            spaceAfter=16,
        ),
        "PracticeQuestion": ParagraphStyle(
            "PracticeQuestion", fontName=FONT_BOLD, fontSize=11.5, leading=16, textColor=INK,
            spaceBefore=10, spaceAfter=8,
        ),
        "ScaffoldGiven": ParagraphStyle(
            "ScaffoldGiven", fontName=FONT, fontSize=10.5, textColor=INK,
            leftIndent=14, leading=15, spaceAfter=4,
        ),
        "ScaffoldBlank": ParagraphStyle(
            "ScaffoldBlank", fontName=FONT, fontSize=10.5, textColor=MUTED,
            leftIndent=14, leading=18, spaceAfter=4,
        ),
    }
