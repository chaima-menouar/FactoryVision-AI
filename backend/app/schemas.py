from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    model_ready: bool


class InspectionResponse(BaseModel):
    filename: str
    predicted_label: str
    anomaly_score: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0)
    model_name: str
    model_ready: bool
    note: str | None = None
