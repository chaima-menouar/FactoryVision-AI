# FactoryVision AI — MLOps Lifecycle

FactoryVision AI treats the anomaly detector as a versioned software artifact rather than a notebook-only model. The current MLOps workflow is intentionally portable and free-first: Kaggle is used for GPU training, MLflow can track experiments locally, GitHub and Azure DevOps YAML validate releases, GHCR stores the runtime image, and Bicep defines the Azure target infrastructure.

## Lifecycle

```text
MVTec AD
   |
   v
Kaggle training (PatchCore)
   |
   +--> metrics CSV + qualitative evaluation
   |
   +--> packaged checkpoint release
             |
             v
     SHA-256 integrity check
             |
             v
      model quality gate
             |
      +------+------+
      |             |
      v             v
  MLflow log     CI validation
                    |
          +---------+----------+
          |                    |
          v                    v
   GitHub Actions       Azure DevOps pipeline
          |                    |
          +---------+----------+
                    |
                    v
        Docker image -> GHCR
                    |
                    v
        Azure-ready Bicep IaC
```

## 1. Experiment tracking

`ml/log_baseline_mlflow.py` converts the real five-category evaluation into an MLflow run. The default tracking store is local (`mlruns/`) so experiment tracking does not require a paid hosted service.

The run records:

- MVTec AD as the evaluation dataset;
- PatchCore as the model family;
- `wide_resnet50_2` backbone;
- feature layers `layer2` and `layer3`;
- coreset sampling ratio `0.1`;
- per-category metrics;
- mean metrics;
- the promoted release ID and checkpoint digest;
- evaluation and quality-gate files as evidence artifacts.

Use:

```bash
pip install -r ml/requirements-ml.txt
python ml/log_baseline_mlflow.py
mlflow ui --backend-store-uri ./mlruns
```

A CI-safe payload check is available without installing MLflow:

```bash
python ml/log_baseline_mlflow.py --dry-run
```

## 2. Model quality gate

`scripts/model_quality_gate.py` is the promotion gate for `bottle-patchcore-v1`. It reads the committed baseline metrics, release metadata and `ml/quality_gate.json`.

The gate verifies:

- metric values are valid probabilities;
- the selected release category has a single evaluation row;
- the selected release passes its internal portfolio thresholds;
- the five-category mean passes the portfolio thresholds;
- release metadata identifies FactoryVision AI;
- the release category matches the quality-gate configuration;
- the checkpoint digest is a valid SHA-256 value.

Run:

```bash
python scripts/model_quality_gate.py --json
```

These thresholds are internal portfolio release gates. They are not presented as factory production acceptance criteria.

## 3. Model packaging and integrity

The selected checkpoint is kept outside Git because the binary is approximately 231 MB. `scripts/install_model_release.py` extracts the release and verifies the checkpoint SHA-256 before it is accepted into `artifacts/model.ckpt`.

Release metadata:

- release: `bottle-patchcore-v1`;
- model: `patchcore-wide_resnet50_2`;
- category: `bottle`;
- checkpoint SHA-256: `8c1e120c2554d055cf3c9d2779da2dbbd1fd8f022c632c9feab1366528d705db`.

The Azure runtime workflow requires a model release URL and does not silently create or substitute a model artifact.

## 4. Continuous integration

GitHub Actions is the active CI system. Every push to `main` validates:

- FastAPI tests;
- persistence and cost guardrails;
- model-release integrity logic;
- model quality gate;
- MLflow payload generation;
- React production build;
- Azure Bicep compilation.

`.github/workflows/build-azure-image.yml` is intentionally manual because the large model release lives outside the repository. It verifies the release before building the Azure runtime image and pushing it to GHCR.

## 5. Azure DevOps pipeline

`azure-pipelines.yml` mirrors the release validation lifecycle for Azure DevOps. It contains validation stages for model quality, backend tests, frontend build and Bicep compilation, then marks the candidate release-ready.

It does **not** claim or execute an Azure deployment yet. The deployment stage is intentionally absent until an active Azure subscription and service connection are available.

Once an Azure DevOps organization is available:

1. Create a pipeline from the existing GitHub repository.
2. Select `azure-pipelines.yml`.
3. Run the pipeline on a Microsoft-hosted agent.
4. Keep deployment disabled until the Azure subscription is active.

This makes Azure DevOps a real part of the engineering workflow without fabricating an Azure runtime that has not been provisioned.

## 6. Infrastructure as Code

`infra/main.bicep` defines the intended Azure deployment:

- Azure Static Web Apps Free plan;
- Azure Cosmos DB for NoSQL with `enableFreeTier: true`;
- a 400 RU/s shared-throughput database;
- Azure Container Apps environment with log storage disabled;
- Container App scale-to-zero (`minReplicas = 0`);
- one-replica ceiling (`maxReplicas = 1`);
- no GPU or dedicated workload profile;
- Cosmos credentials stored as a Container Apps secret;
- application-level daily inference and upload-size limits.

`deployBackend` defaults to `false`. This allows the low-risk resources and template to be validated before a runtime image or active subscription exists.

Compile locally without deploying:

```bash
az bicep build --file infra/main.bicep
```

## 7. Release strategy

The release flow is:

```text
experiment evidence
      -> quality gate
      -> checkpoint integrity verification
      -> application tests
      -> image build
      -> GHCR image
      -> Azure infrastructure validation
      -> controlled deployment when a subscription is available
```

Rollback is image-based: keep the previous verified GHCR tag and point the Container App revision back to that image if a new release fails runtime validation.

## What can be claimed today

Accurate portfolio wording:

> Built an Azure-oriented MLOps workflow for industrial anomaly detection using PatchCore, MLflow, Docker, GitHub Actions, Azure DevOps pipeline definitions, model quality gates, SHA-256 model-release verification and Bicep Infrastructure as Code.

Do not claim that the production API is deployed on Azure Container Apps until that deployment has actually been completed.
