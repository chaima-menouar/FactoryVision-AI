"""Log the validated FactoryVision PatchCore baseline to MLflow.

The default tracking URI is a local file store so the workflow remains free and
portable. Point --tracking-uri at another MLflow-compatible backend only when
that service has been intentionally provisioned.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "ml" / "results" / "patchcore_mvtec_baseline.csv"
RELEASE_PATH = ROOT / "ml" / "releases" / "bottle_patchcore_v1.json"
QUALITY_GATE_PATH = ROOT / "ml" / "quality_gate.json"
QUALITATIVE_PATH = ROOT / "ml" / "results" / "qualitative_evaluation.md"
METRICS = ("image_AUROC", "image_F1Score", "pixel_AUROC", "pixel_F1Score")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracking-uri", default=f"file:{(ROOT / 'mlruns').as_posix()}")
    parser.add_argument("--experiment", default="FactoryVision-PatchCore")
    parser.add_argument("--run-name", default="mvtec-baseline-v1")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the payload without importing or writing to MLflow.",
    )
    return parser


def build_payload() -> dict[str, object]:
    with RESULTS_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))

    metrics: dict[str, float] = {}
    for row in rows:
        category = row["category"]
        for metric in METRICS:
            metrics[f"{category}_{metric.lower()}"] = float(row[metric])

    for metric in METRICS:
        metrics[f"mean_{metric.lower()}"] = mean(float(row[metric]) for row in rows)

    params = {
        "dataset": "MVTec AD",
        "model_family": "PatchCore",
        "backbone": release["runtime"]["backbone"],
        "layers": ",".join(release["runtime"]["layers"]),
        "coreset_sampling_ratio": release["runtime"]["coreset_sampling_ratio"],
        "release_category": release["category"],
        "release_id": release["release_id"],
    }
    tags = {
        "project": "FactoryVision AI",
        "stage": "validated-baseline",
        "release_sha256": release["checkpoint_sha256"],
        "artifact_policy": "external-checkpoint",
    }
    return {"metrics": metrics, "params": params, "tags": tags}


def main() -> None:
    args = build_parser().parse_args()
    payload = build_payload()
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    try:
        import mlflow
    except ImportError as exc:
        raise SystemExit(
            "MLflow is not installed. Install ml/requirements-ml.txt or run with --dry-run."
        ) from exc

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)
    with mlflow.start_run(run_name=args.run_name):
        mlflow.log_params(payload["params"])
        mlflow.log_metrics(payload["metrics"])
        mlflow.set_tags(payload["tags"])
        for artifact in (RESULTS_PATH, RELEASE_PATH, QUALITY_GATE_PATH, QUALITATIVE_PATH):
            mlflow.log_artifact(str(artifact), artifact_path="evidence")

        print(f"MLflow run logged: {mlflow.active_run().info.run_id}")
        print(f"Tracking URI: {mlflow.get_tracking_uri()}")


if __name__ == "__main__":
    main()
