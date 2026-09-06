from __future__ import annotations

from pathlib import Path
from PIL import Image

from ..schemas import InspectionResponse


class AnomalyInferenceService:
    """Model adapter used by the API.

    v0.1 intentionally ships without a checkpoint. During phase 2 the Kaggle-trained
    PatchCore/EfficientAD artifact will be connected here. Keeping the adapter stable
    lets the frontend/backend progress without pretending that a model is already trained.
    """

    def __init__(self, checkpoint_path: str = "artifacts/model.ckpt", threshold: float = 0.5):
        self.checkpoint_path = Path(checkpoint_path)
        self.threshold = threshold
        self.model_name = "baseline-not-trained"
        self.model_ready = self.checkpoint_path.exists()

    def predict(self, image: Image.Image, filename: str) -> InspectionResponse:
        # No fake ML predictions: until a real checkpoint is available, return a
        # transparent placeholder result. Phase 2 replaces this branch with the
        # exported anomaly detector.
        if not self.model_ready:
            return InspectionResponse(
                filename=filename,
                predicted_label="model_not_ready",
                anomaly_score=0.0,
                threshold=self.threshold,
                model_name=self.model_name,
                model_ready=False,
                note="Train/export the baseline model in the hosted training phase.",
            )

        raise NotImplementedError("Checkpoint loading is added after baseline model selection.")
