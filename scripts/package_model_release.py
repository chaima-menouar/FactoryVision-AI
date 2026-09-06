"""Package a trained FactoryVision checkpoint into a portable release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--category", default="bottle")
    parser.add_argument("--model-name", default="patchcore-wide_resnet50_2")
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = build_parser().parse_args()

    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "project": "FactoryVision AI",
        "model_name": args.model_name,
        "category": args.category,
        "checkpoint_filename": "model.ckpt",
        "checkpoint_sha256": sha256_file(args.checkpoint),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "framework": "Anomalib PatchCore",
            "backbone": "wide_resnet50_2",
            "layers": ["layer2", "layer3"],
            "coreset_sampling_ratio": 0.1,
        },
    }

    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.write(args.checkpoint, arcname="model.ckpt")
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))

    print("FactoryVision model release package: OK")
    print(f"Archive: {args.output}")
    print(f"Size bytes: {args.output.stat().st_size}")
    print(f"Checkpoint SHA256: {manifest['checkpoint_sha256']}")


if __name__ == "__main__":
    main()
