from __future__ import annotations

from typing import Any

from .inspection_store import InspectionStore


class QualityContextService:
    """Build structured, grounded context for the future quality copilot.

    This layer deliberately contains no LLM call. It turns persisted inspection
    history into a compact evidence bundle that can later be passed to the
    selected model provider without inventing manufacturing facts.
    """

    def __init__(self, store: InspectionStore) -> None:
        self.store = store

    def build(self, limit: int = 20) -> dict[str, Any]:
        summary = self.store.summary()
        recent = self.store.list_recent(limit=limit)
        anomalous_items = [
            item for item in recent if item["predicted_label"] == "anomalous"
        ]

        if recent:
            average_anomaly_score = sum(
                float(item["anomaly_score"]) for item in recent
            ) / len(recent)
        else:
            average_anomaly_score = 0.0

        recent_anomalies = anomalous_items[:5]

        suggested_questions = [
            "What changed in the recent defect rate?",
            "Which recent inspections have the highest anomaly scores?",
            "Summarize the latest anomalous inspections.",
        ]

        return {
            **summary,
            "average_anomaly_score": average_anomaly_score,
            "recent_anomalies": recent_anomalies,
            "suggested_questions": suggested_questions,
        }
