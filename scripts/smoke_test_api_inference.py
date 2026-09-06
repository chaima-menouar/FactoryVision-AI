"""Smoke-test the FastAPI inspection endpoint with a real PatchCore checkpoint."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    if not args.image.is_file():
        raise FileNotFoundError(f"Image not found: {args.image}")

    os.environ["FACTORYVISION_MODEL_CHECKPOINT"] = str(args.checkpoint)

    from backend.app.main import app

    client = TestClient(app)

    health_response = client.get("/health")
    health_response.raise_for_status()

    with args.image.open("rb") as image_file:
        inspection_response = client.post(
            "/api/v1/inspect",
            files={"file": (args.image.name, image_file, "image/png")},
        )
    inspection_response.raise_for_status()

    print("FactoryVision API checkpoint smoke test: OK")
    print("Health:", health_response.json())
    print("Inspection:", inspection_response.json())


if __name__ == "__main__":
    main()
