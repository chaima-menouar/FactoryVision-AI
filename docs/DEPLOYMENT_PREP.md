# FactoryVision AI deployment preparation

This document prepares the application boundary for deployment without creating or charging any cloud resources.

## Single-container runtime

The repository now includes a multi-stage `Dockerfile` that:

1. Builds the React/Vite frontend.
2. Installs the FastAPI and PatchCore inference runtime.
3. Serves the built frontend from the same FastAPI process.
4. Keeps the model checkpoint and SQLite database outside the container image.

This avoids cross-origin complexity in production and keeps large model artifacts out of Git history and Docker build context.

## Required runtime paths

The container expects the selected checkpoint at:

```text
/app/artifacts/model.ckpt
```

and persists inspection history at:

```text
/app/runtime/factoryvision.db
```

Both paths should be backed by persistent storage in the eventual hosting environment.

## Installing a verified model release

A release ZIP should be verified and unpacked before the application starts:

```bash
python scripts/install_model_release.py \
  --archive /path/to/factoryvision-bottle-patchcore-release.zip \
  --destination artifacts
```

The installer validates the release manifest and checkpoint SHA-256 before writing `artifacts/model.ckpt`.

The verified `bottle-patchcore-v1` checksum is registered in:

```text
ml/releases/bottle_patchcore_v1.json
```

## Runtime environment

```text
FACTORYVISION_MODEL_CHECKPOINT=/app/artifacts/model.ckpt
FACTORYVISION_DB_PATH=/app/runtime/factoryvision.db
FACTORYVISION_FRONTEND_DIST=/app/frontend/dist
FACTORYVISION_CORS_ORIGINS=http://localhost:5173
```

The frontend is built with a same-origin API base inside the production image.

## Azure boundary

No Azure resources are created by this repository. When the Azure phase starts, the remaining decisions are hosting service, persistent model/database storage, secrets, monitoring and CI/CD. Those choices should be made only after validating the container locally or in a free build environment.
