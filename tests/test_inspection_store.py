from backend.app.services.inspection_store import InspectionStore


def test_sqlite_store_records_and_summarizes(tmp_path):
    store = InspectionStore(
        database_path=str(tmp_path / "factoryvision-test.db"),
        backend="sqlite",
    )

    first_id, first_created_at = store.record(
        filename="normal.png",
        predicted_label="normal",
        anomaly_score=0.12,
        threshold=0.5,
        model_name="patchcore-test",
    )
    second_id, second_created_at = store.record(
        filename="defect.png",
        predicted_label="anomalous",
        anomaly_score=0.91,
        threshold=0.5,
        model_name="patchcore-test",
    )

    assert first_id > 0
    assert second_id > first_id
    assert first_created_at
    assert second_created_at

    recent = store.list_recent(limit=10)
    assert len(recent) == 2
    assert recent[0]["filename"] == "defect.png"

    assert store.count_since("2000-01-01T00:00:00+00:00") == 2
    assert store.count_since("2999-01-01T00:00:00+00:00") == 0

    summary = store.summary()
    assert summary == {
        "total": 2,
        "anomalous": 1,
        "normal": 1,
        "defect_rate": 0.5,
    }


def test_store_rejects_unknown_backend(tmp_path):
    try:
        InspectionStore(
            database_path=str(tmp_path / "factoryvision-test.db"),
            backend="unknown",
        )
    except ValueError as exc:
        assert "sqlite" in str(exc)
        assert "cosmos" in str(exc)
    else:
        raise AssertionError("Unknown persistence backend must be rejected.")
