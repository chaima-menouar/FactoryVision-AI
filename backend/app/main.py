from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from .schemas import HealthResponse, InspectionResponse
from .services.inference import AnomalyInferenceService

app = FastAPI(
    title="FactoryVision AI API",
    version="0.1.0",
    description="Industrial visual anomaly inspection API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inference = AnomalyInferenceService()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_ready=inference.model_ready)


@app.post("/api/v1/inspect", response_model=InspectionResponse)
async def inspect(file: UploadFile = File(...)) -> InspectionResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="An image file is required.")

    payload = await file.read()
    try:
        image = Image.open(io.BytesIO(payload)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file.") from exc

    return inference.predict(image=image, filename=file.filename or "upload")
