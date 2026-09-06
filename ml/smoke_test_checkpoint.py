"""Smoke-test a trained FactoryVision PatchCore checkpoint on a single image.

Designed for Kaggle/Colab after a hosted training run. This verifies that the
saved Lightning checkpoint can be loaded independently and used for real
inference before the model adapter is wired into the FastAPI backend.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from anomalib.engine import Engine
from anomalib.models import Patchcore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    return parser


def to_python(value: Any) -> Any:
    """Convert scalar tensor-like values to a readable Python value."""
    if value is None:
        return None
    if hasattr(value, "detach"):
        value = value.detach().cpu()
    if hasattr(value, "numel") and value.numel() == 1:
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def main() -> None:
    args = build_parser().parse_args()

    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    if not args.image.is_file():
        raise FileNotFoundError(f"Image not found: {args.image}")

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=["layer2", "layer3"],
        pre_trained=True,
        coreset_sampling_ratio=0.1,
    )
    engine = Engine(accelerator="auto", devices=1)

    predictions = engine.predict(
        model=model,
        data_path=args.image,
        ckpt_path=args.checkpoint,
        return_predictions=True,
    )

    if not predictions:
        raise RuntimeError("No prediction was returned.")

    prediction = predictions[0]

    print("FactoryVision checkpoint smoke test: OK")
    print(f"Image: {args.image}")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Predicted label: {to_python(getattr(prediction, 'pred_label', None))}")
    print(f"Anomaly score: {to_python(getattr(prediction, 'pred_score', None))}")

    anomaly_map = getattr(prediction, "anomaly_map", None)
    if anomaly_map is not None:
        print(f"Anomaly map shape: {tuple(anomaly_map.shape)}")

    pred_mask = getattr(prediction, "pred_mask", None)
    if pred_mask is not None:
        print(f"Prediction mask shape: {tuple(pred_mask.shape)}")


if __name__ == "__main__":
    main()
