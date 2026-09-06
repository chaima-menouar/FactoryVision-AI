"""Install and verify a packaged FactoryVision model release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=Path("artifacts"))
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_member_name(name: str) -> None:
    candidate = Path(name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe archive member: {name}")


def read_manifest(archive: zipfile.ZipFile) -> dict[str, Any]:
    try:
        raw = archive.read("manifest.json")
    except KeyError as exc:
        raise ValueError("Release archive is missing manifest.json") from exc

    manifest = json.loads(raw.decode("utf-8"))
    if manifest.get("project") != "FactoryVision AI":
        raise ValueError("Release archive is not a FactoryVision AI package")

    checkpoint_filename = manifest.get("checkpoint_filename")
    checkpoint_sha256 = manifest.get("checkpoint_sha256")
    if not checkpoint_filename or not checkpoint_sha256:
        raise ValueError("Release manifest is missing checkpoint metadata")

    _validate_member_name(str(checkpoint_filename))
    return manifest


def install_release(
    archive_path: Path,
    destination: Path,
) -> tuple[Path, Path, dict[str, Any]]:
    if not archive_path.is_file():
        raise FileNotFoundError(f"Release archive not found: {archive_path}")

    destination.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            _validate_member_name(member)

        manifest = read_manifest(archive)
        checkpoint_filename = str(manifest["checkpoint_filename"])

        if checkpoint_filename not in archive.namelist():
            raise ValueError(
                f"Release archive is missing checkpoint: {checkpoint_filename}"
            )

        with tempfile.TemporaryDirectory(prefix="factoryvision-release-") as tmp:
            temp_dir = Path(tmp)
            temp_checkpoint = temp_dir / "model.ckpt"

            with archive.open(checkpoint_filename) as source, temp_checkpoint.open(
                "wb"
            ) as target:
                shutil.copyfileobj(source, target)

            actual_sha256 = sha256_file(temp_checkpoint)
            expected_sha256 = str(manifest["checkpoint_sha256"])
            if actual_sha256 != expected_sha256:
                raise ValueError(
                    "Checkpoint SHA256 mismatch: "
                    f"expected {expected_sha256}, got {actual_sha256}"
                )

            checkpoint_target = destination / "model.ckpt"
            manifest_target = destination / "manifest.json"

            shutil.copy2(temp_checkpoint, checkpoint_target)
            manifest_target.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )

    return checkpoint_target, manifest_target, manifest


def main() -> None:
    args = build_parser().parse_args()
    checkpoint, manifest_path, manifest = install_release(
        args.archive,
        args.destination,
    )

    print("FactoryVision model release installation: OK")
    print(f"Model: {manifest.get('model_name', 'unknown')}")
    print(f"Category: {manifest.get('category', 'unknown')}")
    print(f"Checkpoint: {checkpoint.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    print(f"Checkpoint SHA256: {manifest['checkpoint_sha256']}")


if __name__ == "__main__":
    main()
