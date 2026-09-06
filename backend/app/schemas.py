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
    inspection_id: int | None = None
    created_at: str | None = None
    localization_base64: str | None = None
    note: str | None = None


class InspectionHistoryItem(BaseModel):
    id: int
    filename: str
    predicted_label: str
    anomaly_score: float
    threshold: float
    model_name: str
    created_at: str


class InspectionHistoryResponse(BaseModel):
    total: int
    anomalous: int
    normal: int
    defect_rate: float = Field(ge=0.0, le=1.0)
    items: list[InspectionHistoryItem]


class CopilotContextResponse(BaseModel):
    total: int
    anomalous: int
    normal: int
    defect_rate: float = Field(ge=0.0, le=1.0)
    average_anomaly_score: float = Field(ge=0.0, le=1.0)
    recent_anomalies: list[InspectionHistoryItem]
    suggested_questions: list[str]


class CopilotQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class CopilotAnswerResponse(BaseModel):
    answer: str
    provider: str
    evidence_total: int
    evidence_anomalous: int
