import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.errors import PdfRenderError, TopicNotFoundError, WorksheetGenerationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gcse_worksheets")

app = FastAPI(title="GCSE Maths Worksheet Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.exception_handler(TopicNotFoundError)
async def handle_topic_not_found(request: Request, exc: TopicNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(WorksheetGenerationError)
async def handle_worksheet_generation_error(
    request: Request, exc: WorksheetGenerationError
) -> JSONResponse:
    logger.error("Worksheet generation failed: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Could not generate the worksheet. Please try again."},
    )


@app.exception_handler(PdfRenderError)
async def handle_pdf_render_error(request: Request, exc: PdfRenderError) -> JSONResponse:
    logger.error("PDF rendering failed: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Could not render the worksheet PDF. Please try again."},
    )
