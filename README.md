<div align="center">

# FactoryVision AI

### AI-powered industrial visual inspection, quality intelligence & MLOps

**PatchCore anomaly detection · defect localization · FastAPI · React · MLflow · Azure DevOps · Docker · Bicep**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Dashboard-61DAFB?logo=react&logoColor=0F172A)
![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-0194E2)
![Azure](https://img.shields.io/badge/Azure-MLOps%20Ready-0078D4?logo=microsoftazure&logoColor=white)
![CI](https://github.com/chaima-menouar/FactoryVision-AI/actions/workflows/ci.yml/badge.svg)

</div>

FactoryVision AI is an end-to-end industrial quality-inspection platform for **detecting, localizing, tracking and explaining manufacturing anomalies**. It connects a validated PatchCore model to a production-style API, persistent inspection evidence, a modern React dashboard, release-quality gates and an Azure-oriented MLOps workflow.

> **Deployment truthfulness:** the Azure infrastructure and Azure DevOps pipeline are implemented and validated as code. The live Azure deployment is intentionally pending an active Azure subscription; this repository does not claim a runtime that has not been provisioned.

## Product architecture

![FactoryVision AI architecture](docs/architecture-modern.svg)

```text
Industrial image
      |
      v
PatchCore anomaly model
      |
      +--> anomaly score
      +--> defect localization
      |
      v
FastAPI
      |
      +--> inspection history / KPIs
      +--> model-ops evidence API
      +--> grounded copilot context
      |
      v
React quality dashboard
```

## What this project demonstrates

| Area | Implementation |
|---|---|
| Computer vision | PatchCore anomaly scoring and localization |
| Explainability | Heatmap / defect-localization overlays |
| Backend | FastAPI inference, history, model-ops and copilot-context endpoints |
| Persistence | SQLite locally; Cosmos DB adapter for the Azure target |
| Analytics | Inspection history, defect rate and quality KPIs |
| Frontend | React/Vite quality-engineering dashboard |
| MLOps | MLflow, model quality gates, SHA-256 release verification, versioned metadata |
| CI/CD | GitHub Actions + Azure DevOps pipeline definition |
| Containers | Multi-stage Docker runtime + verified model packaging workflow |
| Infrastructure as Code | Azure Bicep for Static Web Apps, Container Apps and Cosmos DB |
| Cost guardrails | Scale-to-zero, one-replica ceiling, daily inference limit, upload limit |

## Validated PatchCore baseline

Evaluated on five MVTec AD categories:

| Category | Image AUROC | Image F1 | Pixel AUROC | Pixel F1 |
|---|---:|---:|---:|---:|
| bottle | 1.0000 | 0.9920 | 0.9856 | 0.7263 |
| cable | 0.9829 | 0.9674 | 0.9847 | 0.6393 |
| metal_nut | 0.9971 | 0.9838 | 0.9867 | 0.8384 |
| transistor | 0.9958 | 0.9500 | 0.9740 | 0.6131 |
| zipper | 0.9753 | 0.9791 | 0.9814 | 0.5422 |

**Mean image AUROC: 0.9902 · Mean image F1: 0.9745 · Mean pixel AUROC: 0.9825 · Mean pixel F1: 0.6719**

Machine-readable results: `ml/results/patchcore_mvtec_baseline.csv`.

## Promoted model release

The selected `bottle` checkpoint has been restored and exercised through the FastAPI inference path.

- Release ID: `bottle-patchcore-v1`
- Runtime: PatchCore + `wide_resnet50_2`
- Layers: `layer2`, `layer3`
- Coreset sampling ratio: `0.1`
- Verified anomalous example score: `0.64147`
- Checkpoint size: ~231 MB
- SHA-256: `8c1e120c2554d055cf3c9d2779da2dbbd1fd8f022c632c9feab1366528d705db`
- Release metadata: `ml/releases/bottle_patchcore_v1.json`

Large checkpoints and release ZIPs are intentionally excluded from Git.

## MLOps lifecycle

```text
Kaggle training
      |
      v
Evaluation evidence
      |
      +--> MLflow experiment record
      |
      v
Model quality gate
      |
      v
SHA-256 release verification
      |
      +--> GitHub Actions
      +--> Azure DevOps pipeline
      |
      v
Docker image -> GHCR
      |
      v
Bicep-validated Azure target
```

The model quality gate is deterministic and version-controlled in `ml/quality_gate.json`. It validates the promoted category, portfolio-level mean metrics and release metadata before promotion. These are **internal portfolio gates**, not factory production acceptance criteria.

Run the gate:

```bash
python scripts/model_quality_gate.py --json
```

Validate the MLflow payload without installing MLflow:

```bash
python ml/log_baseline_mlflow.py --dry-run
```

Full MLOps documentation: [`docs/MLOPS.md`](docs/MLOPS.md).

## Azure-oriented engineering

The repository includes real Azure engineering artifacts rather than a generic cloud claim:

- `azure-pipelines.yml` — Azure DevOps validation pipeline;
- `infra/main.bicep` — Azure Infrastructure as Code;
- `infra/main.bicepparam.example` — safe deployment parameters;
- `Dockerfile.azure` — verified-model Azure runtime image;
- `.github/workflows/build-azure-image.yml` — manual verified model-image build;
- Cosmos DB persistence adapter in the backend;
- Container Apps cost guardrails and scale-to-zero configuration.

The Bicep target defines:

- Azure Static Web Apps — Free SKU;
- Azure Cosmos DB for NoSQL — Free Tier enabled, 400 RU/s shared throughput;
- Azure Container Apps — Consumption, `minReplicas = 0`, `maxReplicas = 1`;
- log storage disabled for the initial cost-conscious environment;
- no Azure OpenAI, GPU, AKS, VM, ACR or dedicated workload profile.

Current state: **Azure infrastructure-ready, not yet live-deployed**.

## API surface

```text
GET  /health
GET  /api/v1/model-ops
POST /api/v1/inspect
GET  /api/v1/inspections
GET  /api/v1/copilot/context
POST /api/v1/copilot/ask
```

`/api/v1/model-ops` exposes auditable release evidence to the dashboard: release ID, selected category, real evaluation metrics, quality-gate status, MLflow/CI tooling and the current Azure deployment state.

## Dashboard

The React workspace includes:

- image upload and live PatchCore inference;
- anomaly score and defect-localization overlay;
- model runtime readiness;
- persisted inspection history;
- defect-rate KPI;
- model release quality-gate status;
- real release AUROC metrics;
- MLOps toolchain and Azure target visibility.

## Zero-cost-first safeguards

FactoryVision AI is a portfolio/demo workload. Cost protection has higher priority than availability.

- maximum persisted inspections per UTC day: `25` by default;
- maximum image upload: `6 MB` by default;
- Container Apps minimum replicas: `0`;
- Container Apps maximum replicas: `1`;
- Cosmos target uses Free Tier and 400 RU/s shared throughput;
- Azure OpenAI and other usage-billed AI providers remain disabled;
- if an application safety limit is reached, inference fails closed instead of continuing unrestricted.

See [`docs/ZERO_COST_POLICY.md`](docs/ZERO_COST_POLICY.md).

## Repository layout

```text
backend/                 FastAPI service, inference, persistence and model-ops APIs
frontend/                React/Vite quality dashboard
ml/                      training, evaluation, MLflow logging, quality gates and releases
scripts/                 release packaging, verification and model promotion utilities
infra/                   Azure Bicep Infrastructure as Code
tests/                   API, persistence, release and MLOps gate tests
docs/                    architecture, training, MLOps and deployment documentation
.github/workflows/       GitHub CI and verified Azure-image build workflow
azure-pipelines.yml      Azure DevOps MLOps validation pipeline
```

## Local validation

Backend and MLOps tests:

```bash
pip install -r requirements.txt
python -m pytest -q
python scripts/model_quality_gate.py --json
python ml/log_baseline_mlflow.py --dry-run
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

Azure IaC compile check, without deploying resources:

```bash
az bicep build --file infra/main.bicep
```

## CI release checks

Every push to `main` validates:

1. backend/API tests;
2. zero-cost guardrails;
3. model-release integrity logic;
4. model promotion thresholds;
5. MLflow payload generation;
6. React production build;
7. Azure Bicep compilation.

The model binary itself is not committed and is only packaged by the manual verified-image workflow after a release URL is explicitly supplied.

## Responsible use

MVTec AD is a benchmark dataset. Real industrial deployment requires domain-specific data, production threshold calibration, drift monitoring and factory validation. The benchmark metrics in this repository are not presented as production guarantees.

## Status

**v1.0 — portfolio-complete MLOps foundation.**

Implemented: multi-category PatchCore evaluation, explainability review, verified model release, real inference, persistent history, analytics dashboard, model-ops evidence endpoint, grounded copilot context, MLflow experiment logging, deterministic model quality gates, GitHub CI, Azure DevOps pipeline definition, Docker/GHCR release workflow, Cosmos adapter and Bicep Azure infrastructure.

Pending external dependency: live Azure resource provisioning after an active Azure subscription becomes available.

## Author

Developed and maintained by **Chaima Menouar**.
