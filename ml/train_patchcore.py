"""FactoryVision AI - hosted PatchCore baseline.

Run this on Kaggle/Colab, not on a personal computer. The script trains one
MVTec AD category at a time, evaluates it with Anomalib, and writes artifacts
under the selected output directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from anomalib.data import MVTecAD
from anomalib.engine import Engine
from anomalib.models import Patchcore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("./datasets/MVTecAD"))
    parser.add_argument("--category", default="bottle")
    parser.add_argument("--output-dir", type=Path, default=Path("./factoryvision-artifacts"))
    parser.add_argument("--train-batch-size", type=int, default=16)
    parser.add_argument("--eval-batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--coreset-ratio", type=float, default=0.1)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    category_dir = args.output_dir / args.category
    category_dir.mkdir(parents=True, exist_ok=True)

    datamodule = MVTecAD(
        root=args.data_root,
        category=args.category,
        train_batch_size=args.train_batch_size,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
        seed=42,
    )

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=["layer2", "layer3"],
        pre_trained=True,
        coreset_sampling_ratio=args.coreset_ratio,
    )

    engine = Engine(
        default_root_dir=str(category_dir),
        accelerator="auto",
        devices=1,
    )

    engine.fit(model=model, datamodule=datamodule)
    test_results = engine.test(model=model, datamodule=datamodule)

    serializable = test_results if isinstance(test_results, list) else [test_results]
    with (category_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, default=str)

    print(f"FactoryVision baseline complete for: {args.category}")
    print(f"Artifacts: {category_dir.resolve()}")
    print(json.dumps(serializable, indent=2, default=str))


if __name__ == "__main__":
    main()
