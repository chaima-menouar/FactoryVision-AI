from __future__ import annotations

import base64
import io
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from ..schemas import InspectionResponse


class AnomalyInferenceService:
    """PatchCore model adapter used by the FactoryVision API.

    The backend remains lightweight when no checkpoint is configured. When a
    real hosted-training checkpoint is available, the Anomalib runtime is
    imported lazily and real predictions are enabled.
    """

    def __init__(
        self,
        checkpoint_path: str | None = None,
        threshold: float = 0.5,
    ) -> None:
        configured_path = checkpoint_path or os.getenv(
            "FACTORYVISION_MODEL_CHECKPOINT",
            "artifacts/model.ckpt",
        )

        self.checkpoint_path = Path(configured_path)
        self.threshold = threshold
        self.model_name = "patchcore-wide_resnet50_2"
        self.model_ready = False
        self.load_error: str | None = None
        self._model: Any = None
        self._engine: Any = None

        if self.checkpoint_path.is_file():
            self._initialize_runtime()

    def _initialize_runtime(self) -> None:
        try:
            from anomalib.engine import Engine
            from anomalib.models import Patchcore

            self._model = Patchcore(
                backbone="wide_resnet50_2",
                layers=["layer2", "layer3"],
                pre_trained=True,
                coreset_sampling_ratio=0.1,
            )
            self._engine = Engine(accelerator="auto", devices=1)
            self.model_ready = True
        except Exception as exc:  # pragma: no cover - depends on ML runtime
            self.load_error = f"Failed to initialize PatchCore runtime: {exc}"
            self.model_ready = False

    @staticmethod
    def _to_python_scalar(value: Any) -> Any:
        if value is None:
            return None
        if hasattr(value, "detach"):
            value = value.detach().cpu()
        if hasattr(value, "numel") and value.numel() == 1:
            return value.item()
        return value

    @staticmethod
    def _tensor_to_array(value: Any) -> np.ndarray | None:
        if value is None:
            return None
        if hasattr(value, "detach"):
            value = value.detach().cpu()
        if hasattr(value, "numpy"):
            value = value.numpy()
        array = np.asarray(value, dtype=np.float32).squeeze()
        if array.ndim != 2:
            return None
        return array

    @staticmethod
    def _build_localization_overlay(
        image: Image.Image,
        anomaly_map: np.ndarray | None,
    ) -> str | None:
        if anomaly_map is None:
            return None

        finite_map = np.nan_to_num(anomaly_map, nan=0.0, posinf=1.0, neginf=0.0)
        minimum = float(finite_map.min())
        maximum = float(finite_map.max())

        if maximum > minimum:
            normalized = (finite_map - minimum) / (maximum - minimum)
        else:
            normalized = np.zeros_like(finite_map)

        height, width = normalized.shape
        base = image.convert("RGBA").resize((width, height))
        alpha = np.clip(normalized * 185.0, 0, 185).astype(np.uint8)

        overlay_array = np.zeros((height, width, 4), dtype=np.uint8)
        overlay_array[..., 0] = 255
        overlay_array[..., 1] = 45
        overlay_array[..., 2] = 45
        overlay_array[..., 3] = alpha

        overlay = Image.fromarray(overlay_array, mode="RGBA")
        localized = Image.alpha_composite(base, overlay).convert("RGB")

        buffer = io.BytesIO()
        localized.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def predict(self, image: Image.Image, filename: str) -> InspectionResponse:
        if not self.model_ready:
            if self.checkpoint_path.is_file() and self.load_error:
                note = self.load_error
            else:
                note = (
                    "Set FACTORYVISION_MODEL_CHECKPOINT to a real PatchCore "
                    "checkpoint produced by the hosted training pipeline."
                )

            return InspectionResponse(
                filename=filename,
                predicted_label="model_not_ready",
                anomaly_score=0.0,
                threshold=self.threshold,
                model_name=self.model_name,
                model_ready=False,
                note=note,
            )

        temp_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
                temp_path = Path(handle.name)

            image.convert("RGB").save(temp_path, format="PNG")

            predictions = self._engine.predict(
                model=self._model,
                data_path=temp_path,
                ckpt_path=self.checkpoint_path,
                return_predictions=True,
            )

            if not predictions:
                raise RuntimeError("PatchCore returned no prediction.")

            prediction = predictions[0]
            pred_label = bool(
                self._to_python_scalar(getattr(prediction, "pred_label", False))
            )
            pred_score = self._to_python_scalar(
                getattr(prediction, "pred_score", 0.0)
            )
            anomaly_score = float(pred_score or 0.0)
            anomaly_map = self._tensor_to_array(
                getattr(prediction, "anomaly_map", None)
            )
            localization_base64 = self._build_localization_overlay(
                image,
                anomaly_map,
            )

            return InspectionResponse(
                filename=filename,
                predicted_label="anomalous" if pred_label else "normal",
                anomaly_score=anomaly_score,
                threshold=self.threshold,
                model_name=self.model_name,
                model_ready=True,
                localization_base64=localization_base64,
                note="Real PatchCore inference from the configured checkpoint.",
            )
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
