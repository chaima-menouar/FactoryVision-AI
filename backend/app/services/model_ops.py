"""Expose auditable model-release and MLOps readiness metadata."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from scripts.model_quality_gate import evaluate


class ModelOpsService:
    def __init__(self) -> None:
        self.release_path = Path(
            os.getenv(
                "FACTORYVISION_MODEL_RELEASE_METADATA",
                "ml/releases/bottle_patchcore_v1.json",
            )
        )
        self.results_path = Path(
            os.getenv(
                "FACTORYVISION_MODEL_RESULTS",
                "ml/results/patchcore_mvtec_baseline.csv",
            )
        )
        self.quality_gate_path = Path(
            os.getenv("FACTORYVISION_MODEL_QUALITY_GATE", "ml/quality_gate.json")
        )

    def _release(self) -> dict[str, Any]:
        if not self.release_path.is_file():
            return {}
        try:
            return json.loads(self.release_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def snapshot(self) -> dict[str, Any]:
        release = self._release()
        quality_report: dict[str, Any] | None = None

        if (
            self.release_path.is_file()
            and self.results_path.is_file()
            and self.quality_gate_path.is_file()
        ):
            try:
                quality_report = evaluate(
                    results_path=self.results_path,
                    release_path=self.release_path,
                    config_path=self.quality_gate_path,
                )
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                quality_report = None

        release_metrics = quality_report.get("release_metrics", {}) if quality_report else {}
        mean_metrics = quality_report.get("portfolio_mean_metrics", {}) if quality_report else {}

        return {
            "release_id": release.get("release_id"),
            "category": release.get("category"),
            "model_name": release.get("model_name"),
            "checkpoint_sha256": release.get("checkpoint_sha256"),
            "quality_gate_status": quality_report.get("status", "unavailable") if quality_report else "unavailable",
            "release_image_auroc": release_metrics.get("image_AUROC"),
            "release_pixel_auroc": release_metrics.get("pixel_AUROC"),
            "mean_image_auroc": mean_metrics.get("image_AUROC"),
            "mean_pixel_auroc": mean_metrics.get("pixel_AUROC"),
            "experiment_tracking": "MLflow",
            "ci_cd": "GitHub Actions + Azure DevOps",
            "infrastructure_as_code": "Bicep",
            "container_registry": "GitHub Container Registry",
            "azure_target": "Azure Static Web Apps + Container Apps + Cosmos DB",
            "azure_deployment_state": os.getenv(
                "FACTORYVISION_AZURE_DEPLOYMENT_STATE",
                "infrastructure-ready",
            ),
        }
