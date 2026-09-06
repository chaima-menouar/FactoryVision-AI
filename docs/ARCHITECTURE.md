# FactoryVision AI — Architecture

## 1. Inspection path

```text
Image source
  -> preprocessing
  -> anomaly detection model
  -> anomaly score + heatmap/mask
  -> FastAPI
  -> inspection persistence
  -> dashboard + alerts
```

## 2. ML path

```text
MVTec AD
  -> dataset validation
  -> hosted training notebook (Kaggle)
  -> experiment metrics
  -> model selection
  -> exported checkpoint
  -> inference adapter
```

## 3. Application components

### ML
- Baseline: PatchCore.
- Candidate comparison: EfficientAD.
- Primary task: one-class industrial anomaly detection.
- Outputs: image anomaly score, binary decision, anomaly map.

### Backend
- FastAPI.
- Versioned REST endpoints under `/api/v1`.
- Model adapter separated from API routes.
- Persistence layer added after baseline model contract is fixed.

### Frontend
- React + Vite.
- Quality overview, inspection explorer, image detail, anomaly visualization, trend analytics.

### Copilot
Added only after inspection records exist. The copilot must use grounded factory/inspection data and should not invent root causes. Recommendations are presented as hypotheses requiring engineer validation.

## 4. Cloud strategy

Azure is intentionally deferred until the cloud phase. Local development should not require paid Azure resources.

Planned Azure mapping (subject to free-tier availability at deployment time):
- frontend/static web hosting
- API/container hosting
- object storage for inspection images/model artifacts
- managed database
- application monitoring
- CI/CD from GitHub

Before provisioning any Azure resource, we will check the current free-tier limits and expected cost.

## 5. Security and engineering constraints

- No secrets committed to Git.
- No raw industrial datasets committed to Git.
- No fabricated model results before training.
- Input validation on uploaded images.
- Model version recorded with every future inspection.
- Reproducible experiment configuration.
