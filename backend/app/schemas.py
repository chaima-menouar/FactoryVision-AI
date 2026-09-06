from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    model_ready: bool
    copilot_ready: bool = False


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


class ModelOpsResponse(BaseModel):
    release_id: str | None = None
    category: str | None = None
    model_name: str | None = None
    checkpoint_sha256: str | None = None
    quality_gate_status: str
    release_image_auroc: float | None = Field(default=None, ge=0.0, le=1.0)
    release_pixel_auroc: float | None = Field(default=None, ge=0.0, le=1.0)
    mean_image_auroc: float | None = Field(default=None, ge=0.0, le=1.0)
    mean_pixel_auroc: float | None = Field(default=None, ge=0.0, le=1.0)
    experiment_tracking: str
    ci_cd: str
    infrastructure_as_code: str
    container_registry: str
    azure_target: str
    azure_deployment_state: str
