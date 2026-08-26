"""Generates a Bell Tasks .pptx: N chosen topics, one permanently assigned to
each of the chosen template's N numbered boxes, with that topic's 5 generated
questions (one per weekday slide) filling that box across all 5 slides.
Reuses the existing verified generation pipeline end to end
(`build_worksheet`) - this module only adds a new *renderer* (pptx instead of
PDF) on top of it, no new question-generation logic.

Two templates/year groups are supported (`YEAR_10`/`YEAR_11`, see
`_TEMPLATES` below) - each with its own template file, box count, and grid
geometry (`app/bell_tasks/layout.py`). Both templates happen to share the
same grid table shape name and 5-slide weekday structure, but nothing here
assumes a third template would too - `_TEMPLATES` is the single place a
future template's own file/box-count/geometry would be registered.
"""

import importlib.resources
import io
import random
from typing import NamedTuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

from app.bell_tasks import omml
from app.bell_tasks.diagram_raster import rasterize_drawing
from app.bell_tasks.layout import GEOMETRY_YEAR_10, GEOMETRY_YEAR_11, GridGeometry, box_bounds, diagram_rect
from app.bell_tasks.math_tokenizer import ExponentSpan, FractionalExponentSpan, FractionSpan, TextSpan, tokenize
from app.core.registry import get_topic
from app.pdf.diagrams import render_diagram
from app.worksheet.builder import build_worksheet

NUM_SLIDES = 5
QUESTIONS_PER_TOPIC = 5
PURPLE = RGBColor(0x53, 0x1D, 0x60)
FONT_SIZE = Pt(18)
FONT_SIZE_PT = 18.0

YEAR_10 = "year_10"
YEAR_11 = "year_11"

_GRID_TABLE_SHAPE_NAME = "Google Shape;146;p3"


class _BellTasksTemplate(NamedTuple):
    filename: str
    num_boxes: int
    geometry: GridGeometry


_TEMPLATES: dict[str, _BellTasksTemplate] = {
    YEAR_10: _BellTasksTemplate("bell_task_template.pptx", 6, GEOMETRY_YEAR_10),
    YEAR_11: _BellTasksTemplate("bell_task_template_year11.pptx", 8, GEOMETRY_YEAR_11),
}

# Exported for the API schema's validator, so "how many topic ids does this
# year need" has exactly one source of truth.
BOX_COUNTS: dict[str, int] = {year: t.num_boxes for year, t in _TEMPLATES.items()}

# Backward-compat alias for existing callers/tests that predate multi-template
# support and always meant Year 10's 6-box template.
NUM_BOXES = _TEMPLATES[YEAR_10].num_boxes


def _template_path(year: str = YEAR_10) -> str:
    return str(importlib.resources.files("app.bell_tasks") / "assets" / _TEMPLATES[year].filename)


def _grid_table(slide):
    for shape in slide.shapes:
        if shape.has_table and shape.name == _GRID_TABLE_SHAPE_NAME:
            return shape.table
    raise RuntimeError("Bell Tasks template slide is missing its question grid table")


def _set_cell_content(cell, box: int, prompt: str) -> None:
    text_frame = cell.text_frame
    text_frame.clear()
    paragraph = text_frame.paragraphs[0]

    tokens: list = [TextSpan(f"{box}. ", "Calibri"), *tokenize(prompt)]
    for token in tokens:
        if isinstance(token, TextSpan):
            run = paragraph.add_run()
            run.text = token.text
            run.font.name = token.font
            run.font.size = FONT_SIZE
            run.font.color.rgb = PURPLE
        elif isinstance(token, FractionSpan):
            omml.add_fraction(paragraph, token.sign, token.numerator, token.denominator, FONT_SIZE_PT, PURPLE)
        elif isinstance(token, ExponentSpan):
            omml.add_exponent(paragraph, token.base, token.exponent, FONT_SIZE_PT, PURPLE)
        elif isinstance(token, FractionalExponentSpan):
            omml.add_fractional_exponent(
                paragraph, token.base, token.numerator, token.denominator, FONT_SIZE_PT, PURPLE
            )


def generate_bell_tasks_pptx(topic_ids: list[str], year: str = YEAR_10) -> bytes:
    if year not in _TEMPLATES:
        raise ValueError(f"Unknown Bell Tasks year {year!r}, expected one of {sorted(_TEMPLATES)}")
    template = _TEMPLATES[year]
    num_boxes = template.num_boxes

    if len(topic_ids) != num_boxes:
        raise ValueError(f"Bell Tasks for {year} needs exactly {num_boxes} topic ids, got {len(topic_ids)}")
    if len(set(topic_ids)) != num_boxes:
        raise ValueError("Bell Tasks topic ids must all be distinct")

    rng = random.Random()

    questions_by_box: dict[int, tuple] = {}
    for box, topic_id in enumerate(topic_ids, start=1):
        topic = get_topic(topic_id)
        worksheet = build_worksheet(topic_id, topic.fixed_tier, count=QUESTIONS_PER_TOPIC, rng=rng)
        questions_by_box[box] = worksheet.questions

    prs = Presentation(_template_path(year))

    for slide_idx in range(NUM_SLIDES):
        slide = prs.slides[slide_idx]
        table = _grid_table(slide)

        for box in range(1, num_boxes + 1):
            row, col = template.geometry.box_to_row_col[box]
            question = questions_by_box[box][slide_idx]

            cell = table.cell(row, col)
            _set_cell_content(cell, box, question.prompt)

            if question.diagram is not None:
                drawing = render_diagram(question.diagram)
                rect = diagram_rect(box_bounds(box, template.geometry), question.prompt, drawing.width, drawing.height)
                if rect is not None:
                    png_bytes = rasterize_drawing(drawing)
                    left, top, width, height = rect
                    slide.shapes.add_picture(io.BytesIO(png_bytes), left, top, width, height)

    out = io.BytesIO()
    prs.save(out)
    return out.getvalue()
