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
ml/             training/inference code and experiment configuration
frontend/       React/Vite dashboard
scripts/        data preparation utilities
data/           dataset documentation only (raw data ignored)
docs/           architecture and roadmap
tests/          backend tests
.github/        CI workflows
```

## Planned phases

1. **Foundation & data pipeline** — repository structure, reproducible dataset preparation, baseline API.
2. **Computer vision baseline** — PatchCore/EfficientAD experiments on MVTec AD using Kaggle GPU/CPU.
3. **Evaluation & explainability** — image/pixel AUROC, F1, anomaly maps, error analysis.
4. **Backend & persistence** — production inference endpoints, inspection history, metrics.
5. **Dashboard** — quality KPIs, defect explorer, inspection detail view.
6. **AI Copilot** — grounded assistant over inspection history and quality documentation.
7. **Azure cloud phase** — containerization, Azure-hosted API/app/database/storage, monitoring and CI/CD.

## Current status

**v0.1 foundation started.** The initial codebase, data preparation workflow, API contract, training configuration and CI are being built directly in this repository.

## Important data note

Do not commit MVTec AD images or other large datasets to this repository. Keep them in Kaggle/Colab storage or another approved dataset location and respect each dataset's license.
