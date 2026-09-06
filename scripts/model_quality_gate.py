"""Validate FactoryVision model metrics and release metadata before promotion."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "ml" / "results" / "patchcore_mvtec_baseline.csv"
DEFAULT_RELEASE = ROOT / "ml" / "releases" / "bottle_patchcore_v1.json"
DEFAULT_CONFIG = ROOT / "ml" / "quality_gate.json"
METRICS = ("image_AUROC", "image_F1Score", "pixel_AUROC", "pixel_F1Score")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json", action="store_true", help="Print a JSON report.")
    return parser


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_results(path: Path) -> list[dict[str, float | str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(("category", *METRICS)).issubset(reader.fieldnames):
            raise ValueError("Baseline CSV is missing one or more required metric columns.")

        rows: list[dict[str, float | str]] = []
        for raw in reader:
            row: dict[str, float | str] = {"category": str(raw["category"])}
            for metric in METRICS:
                value = float(raw[metric])
                if not 0.0 <= value <= 1.0:
                    raise ValueError(f"Metric {metric} is outside [0, 1] for {raw['category']}.")
                row[metric] = value
            rows.append(row)

    if not rows:
        raise ValueError("Baseline CSV contains no result rows.")
    return rows


def _threshold_failures(
    values: dict[str, float], thresholds: dict[str, Any], prefix: str
) -> list[str]:
    failures: list[str] = []
    for metric in METRICS:
        threshold = float(thresholds[metric])
        actual = float(values[metric])
        if actual < threshold:
            failures.append(
                f"{prefix}.{metric}: {actual:.6f} is below required {threshold:.6f}"
            )
    return failures


def evaluate(
    results_path: Path = DEFAULT_RESULTS,
    release_path: Path = DEFAULT_RELEASE,
    config_path: Path = DEFAULT_CONFIG,
) -> dict[str, Any]:
    rows = _load_results(results_path)
    release = _load_json(release_path)
    config = _load_json(config_path)

    release_category = str(config["release_category"])
    matching = [row for row in rows if row["category"] == release_category]
    if len(matching) != 1:
        raise ValueError(
            f"Expected exactly one baseline row for release category {release_category!r}."
        )

    release_row = matching[0]
    release_metrics = {metric: float(release_row[metric]) for metric in METRICS}
    mean_metrics = {
        metric: mean(float(row[metric]) for row in rows)
        for metric in METRICS
    }

    failures: list[str] = []
    failures.extend(
        _threshold_failures(
            release_metrics,
            dict(config["release_thresholds"]),
            "release",
        )
    )
    failures.extend(
        _threshold_failures(
            mean_metrics,
            dict(config["portfolio_mean_thresholds"]),
            "portfolio_mean",
        )
    )

    if release.get("project") != "FactoryVision AI":
        failures.append("release.project does not identify FactoryVision AI")
    if release.get("category") != release_category:
        failures.append(
            f"release.category is {release.get('category')!r}, expected {release_category!r}"
        )
    if not release.get("release_id"):
        failures.append("release.release_id is missing")
    checkpoint_sha256 = str(release.get("checkpoint_sha256", ""))
    if not SHA256_PATTERN.fullmatch(checkpoint_sha256):
        failures.append("release.checkpoint_sha256 is not a valid lowercase SHA-256 digest")

    return {
        "status": "pass" if not failures else "fail",
        "release_id": release.get("release_id"),
        "release_category": release_category,
        "release_metrics": release_metrics,
        "portfolio_mean_metrics": mean_metrics,
        "failures": failures,
    }


def main() -> None:
    args = build_parser().parse_args()
    report = evaluate(args.results, args.release, args.config)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"FactoryVision model quality gate: {report['status'].upper()}")
        print(f"Release: {report['release_id']}")
        print(f"Category: {report['release_category']}")
        for metric, value in report["release_metrics"].items():
            print(f"Release {metric}: {value:.6f}")
        for metric, value in report["portfolio_mean_metrics"].items():
            print(f"Mean {metric}: {value:.6f}")
        for failure in report["failures"]:
            print(f"FAIL: {failure}")

    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
