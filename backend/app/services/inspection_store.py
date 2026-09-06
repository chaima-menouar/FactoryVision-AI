from __future__ import annotations

import itertools
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SQLiteInspectionStore:
    """SQLite-backed inspection history for local development and tests."""

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


class CosmosInspectionStore:
    """Azure Cosmos DB for NoSQL inspection history backend.

    The Azure account, database, container and free-tier settings are created
    outside the application. This service only connects to those resources so
    the application cannot accidentally provision billable cloud resources.
    """

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        key: str | None = None,
        database: str | None = None,
        container: str | None = None,
    ) -> None:
        try:
            from azure.cosmos import CosmosClient
        except ImportError as exc:
            raise RuntimeError(
                "Cosmos DB backend requires the azure-cosmos package."
            ) from exc

        endpoint = endpoint or os.getenv("FACTORYVISION_COSMOS_ENDPOINT", "")
        key = key or os.getenv("FACTORYVISION_COSMOS_KEY", "")
        database = database or os.getenv(
            "FACTORYVISION_COSMOS_DATABASE",
            "factoryvision",
        )
        container = container or os.getenv(
            "FACTORYVISION_COSMOS_CONTAINER",
            "inspections",
        )

        if not endpoint or not key:
            raise RuntimeError(
                "Cosmos DB backend requires FACTORYVISION_COSMOS_ENDPOINT and "
                "FACTORYVISION_COSMOS_KEY."
            )

        client = CosmosClient(endpoint, credential=key)
        database_client = client.get_database_client(database)
        self.container = database_client.get_container_client(container)

    def record(
        self,
        *,
        filename: str,
        predicted_label: str,
        anomaly_score: float,
        threshold: float,
        model_name: str,
    ) -> tuple[int, str]:
        inspection_id = time.time_ns()
        created_at = datetime.now(timezone.utc).isoformat()
        self.container.create_item(
            {
                "id": str(inspection_id),
                "inspection_id": inspection_id,
                "filename": filename,
                "predicted_label": predicted_label,
                "anomaly_score": anomaly_score,
                "threshold": threshold,
                "model_name": model_name,
                "created_at": created_at,
            }
        )
        return inspection_id, created_at

    def list_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 100))
        query = """
            SELECT
                c.inspection_id AS id,
                c.filename,
                c.predicted_label,
                c.anomaly_score,
                c.threshold,
                c.model_name,
                c.created_at
            FROM c
            ORDER BY c.created_at DESC
        """
        items = self.container.query_items(
            query=query,
            enable_cross_partition_query=True,
        )
        return list(itertools.islice(items, safe_limit))

    def _count(self, where_clause: str = "") -> int:
        query = f"SELECT VALUE COUNT(1) FROM c {where_clause}".strip()
        values = self.container.query_items(
            query=query,
            enable_cross_partition_query=True,
        )
        return int(next(iter(values), 0) or 0)

    def summary(self) -> dict[str, float | int]:
        total = self._count()
        anomalous = self._count("WHERE c.predicted_label = 'anomalous'")
        normal = self._count("WHERE c.predicted_label = 'normal'")
        defect_rate = (anomalous / total) if total else 0.0
        return {
            "total": total,
            "anomalous": anomalous,
            "normal": normal,
            "defect_rate": defect_rate,
        }


class InspectionStore:
    """Select the configured inspection persistence backend."""

    def __init__(
        self,
        database_path: str | None = None,
        backend: str | None = None,
    ) -> None:
        selected_backend = (
            backend or os.getenv("FACTORYVISION_DB_BACKEND", "sqlite")
        ).strip().lower()

        if selected_backend == "sqlite":
            self._store = SQLiteInspectionStore(database_path=database_path)
        elif selected_backend == "cosmos":
            self._store = CosmosInspectionStore()
        else:
            raise ValueError(
                "FACTORYVISION_DB_BACKEND must be either 'sqlite' or 'cosmos'."
            )

    def record(self, **kwargs: Any) -> tuple[int, str]:
        return self._store.record(**kwargs)

    def list_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._store.list_recent(limit=limit)

    def summary(self) -> dict[str, float | int]:
        return self._store.summary()
