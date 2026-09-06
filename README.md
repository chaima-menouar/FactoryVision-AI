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

We will **not train locally**. Model training is designed for free hosted notebooks (Kaggle first, Colab as fallback). Raw industrial datasets and trained checkpoints are not committed to GitHub.

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
backend/        FastAPI service
ml/             hosted training code, inference code and experiment configuration
frontend/       React/Vite dashboard
scripts/        data validation/preparation utilities
data/           dataset documentation only (raw data ignored)
docs/           architecture and Kaggle training runbook
tests/          backend tests
.github/        CI workflows
```

## Planned phases

1. **Foundation & data pipeline** — repository structure, reproducible dataset preparation, baseline API. ✅
2. **Computer vision baseline** — PatchCore experiments on MVTec AD using hosted Kaggle compute. ✅
3. **Evaluation & explainability** — image/pixel AUROC, F1, anomaly maps, error analysis. **In progress.**
4. **Backend & persistence** — production inference endpoints, inspection history, metrics.
5. **Dashboard** — quality KPIs, defect explorer, inspection detail view.
6. **AI Copilot** — grounded assistant over inspection history and quality documentation.
7. **Azure cloud phase** — containerization, Azure-hosted API/app/database/storage, monitoring and CI/CD.

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

Initial interpretation: image-level anomaly detection is consistently strong across all five categories, while pixel-level F1 varies more substantially. `metal_nut` currently has the strongest localization F1, while `zipper` is the main localization failure-analysis target. These findings will be validated visually with anomaly maps before a production baseline is selected.

## Current status

**v0.4 — five-category hosted baseline completed.** The baseline stage is complete with real Kaggle measurements across five MVTec AD categories. The project is now in evaluation and explainability: inspect anomaly heatmaps and failure cases, decide whether PatchCore is sufficient or should be compared with another detector, export the selected model artifact, and connect it to the inference API.

## Important data note

Do not commit MVTec AD images or other large datasets to this repository. Keep them in Kaggle/Colab storage or another approved dataset location and respect each dataset's license.
