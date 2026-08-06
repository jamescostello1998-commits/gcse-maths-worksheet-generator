"""Rasterizes a ReportLab ``Drawing`` (as returned by ``app.pdf.diagrams.render_diagram``)
to PNG bytes, for embedding as a picture shape in a generated Bell Tasks .pptx.

ReportLab's own bitmap renderer (``renderPM``) isn't installed here (needs Cairo bindings
- see CLAUDE.md). Instead this renders the Drawing to a small in-memory one-page PDF via
``reportlab.graphics.renderPDF`` (pure vector-to-PDF, always available) and rasterizes that
page with ``fitz``/pymupdf, which is already a pinned dependency used elsewhere in this
project for dev-time visual verification.
"""

import io

import fitz
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

DEFAULT_DPI = 300


def rasterize_drawing(drawing: Drawing, dpi: int = DEFAULT_DPI) -> bytes:
    buf = io.BytesIO()
    renderPDF.drawToFile(drawing, buf)
    pdf_bytes = buf.getvalue()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page = doc[0]
        pixmap = page.get_pixmap(dpi=dpi, alpha=True)
        return pixmap.tobytes("png")
    finally:
        doc.close()
