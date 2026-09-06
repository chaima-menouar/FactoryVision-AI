from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class InspectionStore:
    """Small SQLite-backed inspection history store.

    The path is configurable so local development, tests, containers and the
    later Azure deployment can each choose an appropriate persistent volume.
    """

    def __init__(self, database_path: str | None = None) -> None:
        configured_path = database_path or os.getenv(
            "FACTORYVISION_DB_PATH",
            "runtime/factoryvision.db",
        )
        self.database_path = Path(configured_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    predicted_label TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    threshold REAL NOT NULL,
                    model_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def record(
        self,
        *,
        filename: str,
        predicted_label: str,
        anomaly_score: float,
        threshold: float,
        model_name: str,
    ) -> tuple[int, str]:
        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO inspections (
                    filename,
                    predicted_label,
                    anomaly_score,
                    threshold,
                    model_name,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    predicted_label,
                    anomaly_score,
                    threshold,
                    model_name,
                    created_at,
                ),
            )
            connection.commit()
            inspection_id = int(cursor.lastrowid)

        return inspection_id, created_at

    def list_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 100))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    filename,
                    predicted_label,
                    anomaly_score,
                    threshold,
                    model_name,
                    created_at
                FROM inspections
                ORDER BY id DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, float | int]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN predicted_label = 'anomalous' THEN 1 ELSE 0 END) AS anomalous,
                    SUM(CASE WHEN predicted_label = 'normal' THEN 1 ELSE 0 END) AS normal
                FROM inspections
                """
            ).fetchone()

        total = int(row["total"] or 0)
        anomalous = int(row["anomalous"] or 0)
        normal = int(row["normal"] or 0)
        defect_rate = (anomalous / total) if total else 0.0

        return {
            "total": total,
            "anomalous": anomalous,
            "normal": normal,
            "defect_rate": defect_rate,
        }
