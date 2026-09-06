# FactoryVision AI

**AI-Powered Quality Inspection & Manufacturing Copilot**

FactoryVision AI is an end-to-end industrial visual inspection platform for detecting, localizing, tracking, and explaining manufacturing defects.

## Project goals

- Detect anomalous/defective products from images.
- Localize defects with anomaly heatmaps or segmentation masks.
- Expose model inference through a FastAPI backend.
- Track inspections and quality metrics.
- Provide a React dashboard for quality engineers.
- Add an AI quality copilot in a later phase.
- Deploy the production stack on **Microsoft Azure** only when the cloud phase begins.

## Zero-cost development strategy

We do **not train locally**. Model training is designed for free hosted notebooks (Kaggle first, Colab as fallback). Raw industrial datasets and trained checkpoints are not committed to GitHub.

Initial dataset: **MVTec AD**. The repository also leaves room for VisA/BTAD later for robustness testing.

## Architecture

```text
Industrial image / camera
        |
        v
Computer Vision anomaly detector
        |
        +--> anomaly score
        +--> defect localization heatmap/mask
        |
        v
FastAPI inference service
        |
        v
Inspection database / analytics
        |
        v
React quality dashboard
        |
        v
AI Quality Copilot (later)
        |
        v
Azure deployment (cloud phase)
```

## Repository layout

```text
backend/        FastAPI service and SQLite-backed inspection persistence
ml/             hosted training code, experiment configuration and release metadata
frontend/       React/Vite quality inspection dashboard
scripts/        data validation, smoke-test, model packaging and verified installation utilities
data/           dataset documentation only (raw data ignored)
docs/           architecture and hosted-training documentation
tests/          backend and release-integrity tests
.github/        CI workflows
```

## Planned phases

1. **Foundation & data pipeline** — repository structure, reproducible dataset preparation, baseline API. ✅
2. **Computer vision baseline** — PatchCore experiments on MVTec AD using hosted Kaggle compute. ✅
3. **Evaluation & explainability** — image/pixel AUROC, F1, anomaly maps, error analysis. ✅
4. **Backend & persistence** — real PatchCore inference, inspection history and SQLite persistence. ✅
5. **Dashboard** — live image upload, anomaly score, localization, quality KPIs and recent history. ✅
6. **AI Copilot** — grounded assistant over inspection history and quality documentation. **Next.**
7. **Azure cloud phase** — containerization, Azure-hosted API/app/database/storage, monitoring and CI/CD. **Not started; no Azure resources provisioned yet.**

## Hosted baseline

The reproducible PatchCore entrypoint is available at `ml/train_patchcore.py`. Hosted ML dependencies are isolated in `ml/requirements-ml.txt`, and the Kaggle procedure is documented in `docs/TRAINING_KAGGLE.md`.

The first baseline covers `bottle`, `cable`, `metal_nut`, `transistor`, and `zipper`.

### Real PatchCore baseline results

| Category | Image AUROC | Image F1 | Pixel AUROC | Pixel F1 |
|---|---:|---:|---:|---:|
| bottle | 1.0000 | 0.9920 | 0.9856 | 0.7263 |
| cable | 0.9829 | 0.9674 | 0.9847 | 0.6393 |
| metal_nut | 0.9971 | 0.9838 | 0.9867 | 0.8384 |
| transistor | 0.9958 | 0.9500 | 0.9740 | 0.6131 |
| zipper | 0.9753 | 0.9791 | 0.9814 | 0.5422 |

Mean metrics across the five categories:

- Image AUROC: **0.9902**
- Image F1: **0.9745**
- Pixel AUROC: **0.9825**
- Pixel F1: **0.6719**

The machine-readable summary is stored in `ml/results/patchcore_mvtec_baseline.csv`. Large checkpoints and raw dataset files remain outside GitHub.

Qualitative review confirmed that PatchCore localizes representative `bottle` and `zipper` defects in the correct regions. Zipper anomaly maps are broader than the ground-truth masks, which is consistent with its lower pixel F1.

## Verified model release

The selected `bottle` PatchCore checkpoint was independently restored and exercised through the FastAPI endpoint. The API returned a real anomalous prediction for `broken_small/000.png` with an anomaly score of `0.64147`, while `/health` reported `model_ready: true`.

The portable release archive has also been verified outside Kaggle:

- Release: `bottle-patchcore-v1`
- Archive: `factoryvision-bottle-patchcore-release.zip`
- Archive size: **231,213,915 bytes**
- Checkpoint size: **231,213,223 bytes**
- Checkpoint SHA-256: `8c1e120c2554d055cf3c9d2779da2dbbd1fd8f022c632c9feab1366528d705db`
- Registry metadata: `ml/releases/bottle_patchcore_v1.json`

Use `scripts/package_model_release.py` to create a release archive and `scripts/install_model_release.py` to verify its manifest/checksum before installing it into `artifacts/model.ckpt`. Release ZIP files and checkpoints remain external artifacts and are intentionally ignored by Git.

## Product integration

The backend now provides:

- `GET /health` for runtime/model readiness.
- `POST /api/v1/inspect` for real PatchCore image inference.
- `GET /api/v1/inspections` for persisted inspection history and quality summary metrics.
- Base64 PNG defect-localization overlays in inspection responses.
- Configurable `FACTORYVISION_MODEL_CHECKPOINT`, `FACTORYVISION_DB_PATH`, and `FACTORYVISION_CORS_ORIGINS` runtime settings.

The React dashboard now provides live image upload, model readiness, anomaly score, defect localization, inspection count, defect rate, and recent inspection history.

## Current status

**v0.6 — inspection intelligence layer complete.** The project now has reproducible hosted training, five-category evaluation, qualitative explainability review, a verified portable model release, real FastAPI inference, defect-localization output, persistent inspection history, quality KPIs, and a connected React dashboard. The next engineering phase is the grounded quality copilot. Azure provisioning will begin only after the application/runtime boundary is finalized.

## Important data note

Do not commit MVTec AD images, release ZIP files, or trained checkpoints to this repository. Keep them in approved external storage and respect each dataset's license.
