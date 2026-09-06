from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import httpx
import io
import os
from pathlib import Path

from .schemas import (
    CopilotAnswerResponse,
    CopilotContextResponse,
    CopilotQuestion,
    HealthResponse,
    InspectionHistoryResponse,
    InspectionResponse,
)
from .services.copilot import CopilotNotConfiguredError, QualityCopilotService
from .services.inference import AnomalyInferenceService
from .services.inspection_store import InspectionStore
from .services.quality_context import QualityContextService


def _cors_origins() -> list[str]:
    raw = os.getenv("FACTORYVISION_CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _frontend_dist() -> Path:
    return Path(os.getenv("FACTORYVISION_FRONTEND_DIST", "frontend/dist"))


app = FastAPI(
    title="FactoryVision AI API",
    version="0.8.0",
    description="Industrial visual anomaly inspection API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inference = AnomalyInferenceService()
store = InspectionStore()
quality_context = QualityContextService(store)
copilot = QualityCopilotService()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_ready=inference.model_ready,
        copilot_ready=copilot.ready,
    )


@app.get("/api/v1/inspections", response_model=InspectionHistoryResponse)
def inspections(
    limit: int = Query(default=25, ge=1, le=100),
) -> InspectionHistoryResponse:
    summary = store.summary()
    return InspectionHistoryResponse(
        **summary,
        items=store.list_recent(limit=limit),
    )


@app.get("/api/v1/copilot/context", response_model=CopilotContextResponse)
def copilot_context(
    limit: int = Query(default=20, ge=1, le=100),
) -> CopilotContextResponse:
    return CopilotContextResponse(**quality_context.build(limit=limit))


@app.post("/api/v1/copilot/ask", response_model=CopilotAnswerResponse)
def copilot_ask(payload: CopilotQuestion) -> CopilotAnswerResponse:
    context = quality_context.build(limit=20)
    try:
        answer = copilot.answer(payload.question, context)
    except CopilotNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="The configured copilot provider request failed.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return CopilotAnswerResponse(
        answer=answer,
        provider=copilot.provider,
        evidence_total=int(context["total"]),
        evidence_anomalous=int(context["anomalous"]),
    )


@app.post("/api/v1/inspect", response_model=InspectionResponse)
async def inspect(file: UploadFile = File(...)) -> InspectionResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="An image file is required.")

    payload = await file.read()
    try:
        image = Image.open(io.BytesIO(payload)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file.") from exc

    result = inference.predict(image=image, filename=file.filename or "upload")

    if not result.model_ready:
        return result

    inspection_id, created_at = store.record(
        filename=result.filename,
        predicted_label=result.predicted_label,
        anomaly_score=result.anomaly_score,
        threshold=result.threshold,
        model_name=result.model_name,
    )

    return result.model_copy(
        update={
            "inspection_id": inspection_id,
            "created_at": created_at,
        }
    )


frontend_dist = _frontend_dist()
assets_dir = frontend_dist / "assets"
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")


@app.get("/", include_in_schema=False)
def frontend_index():
    index_path = frontend_dist / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Frontend build is not available.")
    return FileResponse(index_path)
