import csv
import json
from pathlib import Path

from scripts.model_quality_gate import evaluate


def _write_results(path: Path, bottle_pixel_f1: float) -> None:
    rows = [
        {
            "category": "bottle",
            "image_AUROC": 1.0,
            "image_F1Score": 0.992,
            "pixel_AUROC": 0.985602,
            "pixel_F1Score": bottle_pixel_f1,
        },
        {
            "category": "cable",
            "image_AUROC": 0.99,
            "image_F1Score": 0.98,
            "pixel_AUROC": 0.98,
            "pixel_F1Score": 0.70,
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "image_AUROC", "image_F1Score", "pixel_AUROC", "pixel_F1Score"])
        writer.writeheader()
        writer.writerows(rows)


def _write_release(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "release_id": "bottle-patchcore-v1",
                "project": "FactoryVision AI",
                "category": "bottle",
                "checkpoint_sha256": "8c1e120c2554d055cf3c9d2779da2dbbd1fd8f022c632c9feab1366528d705db",
            }
        ),
        encoding="utf-8",
    )


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "release_category": "bottle",
                "release_thresholds": {
                    "image_AUROC": 0.99,
                    "image_F1Score": 0.98,
                    "pixel_AUROC": 0.98,
                    "pixel_F1Score": 0.70,
                },
                "portfolio_mean_thresholds": {
                    "image_AUROC": 0.98,
                    "image_F1Score": 0.96,
                    "pixel_AUROC": 0.97,
                    "pixel_F1Score": 0.60,
                },
            }
        ),
        encoding="utf-8",
    )


def test_quality_gate_passes_for_valid_release(tmp_path):
    results = tmp_path / "results.csv"
    release = tmp_path / "release.json"
    config = tmp_path / "quality_gate.json"
    _write_results(results, bottle_pixel_f1=0.73)
    _write_release(release)
    _write_config(config)

    report = evaluate(results, release, config)

    assert report["status"] == "pass"
    assert report["failures"] == []


def test_quality_gate_fails_when_release_metric_regresses(tmp_path):
    results = tmp_path / "results.csv"
    release = tmp_path / "release.json"
    config = tmp_path / "quality_gate.json"
    _write_results(results, bottle_pixel_f1=0.40)
    _write_release(release)
    _write_config(config)

    report = evaluate(results, release, config)

    assert report["status"] == "fail"
    assert any("release.pixel_F1Score" in failure for failure in report["failures"])
