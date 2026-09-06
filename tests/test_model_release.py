from __future__ import annotations

import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_model_release.py"
SPEC = importlib.util.spec_from_file_location("install_model_release", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _build_release(path: Path, payload: bytes, sha256: str | None = None) -> None:
    digest = sha256 or hashlib.sha256(payload).hexdigest()
    manifest = {
        "project": "FactoryVision AI",
        "model_name": "patchcore-test",
        "category": "bottle",
        "checkpoint_filename": "model.ckpt",
        "checkpoint_sha256": digest,
    }

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("model.ckpt", payload)
        archive.writestr("manifest.json", json.dumps(manifest))


def test_install_release_verifies_and_extracts(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    destination = tmp_path / "artifacts"
    payload = b"factoryvision-test-checkpoint"
    _build_release(archive, payload)

    checkpoint, manifest_path, manifest = MODULE.install_release(
        archive,
        destination,
    )

    assert checkpoint.read_bytes() == payload
    assert manifest_path.is_file()
    assert manifest["category"] == "bottle"
    assert MODULE.sha256_file(checkpoint) == manifest["checkpoint_sha256"]


def test_install_release_rejects_checksum_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    _build_release(archive, b"tampered", sha256="0" * 64)

    try:
        MODULE.install_release(archive, tmp_path / "artifacts")
    except ValueError as exc:
        assert "SHA256 mismatch" in str(exc)
    else:
        raise AssertionError("Checksum mismatch should fail installation")
