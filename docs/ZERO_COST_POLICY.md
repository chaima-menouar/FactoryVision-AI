# FactoryVision AI — Zero-Cost Deployment Policy

FactoryVision AI is a portfolio/demo workload. Cost protection has higher priority than availability. If a free allowance is at risk, the preferred behavior is to pause inference or disable the cloud backend rather than continue into billable usage.

## Approved services

### Azure Static Web Apps — Free plan

Use the Free plan only. The frontend is small and static. Do not upgrade the site to Standard.

### Azure Container Apps — Consumption plan

Use Consumption only with:

- `minReplicas = 0`
- `maxReplicas = 1`
- no GPU
- no Dedicated workload profile
- no minimum always-on replica

The API also applies application-level safeguards:

- `FACTORYVISION_DAILY_INSPECTION_LIMIT=25`
- `FACTORYVISION_MAX_UPLOAD_BYTES=6291456`

When the daily inspection limit is reached, `/api/v1/inspect` returns HTTP 429 before running PatchCore inference.

### Azure Cosmos DB for NoSQL — Free Tier

The Azure account must be created manually with Free Tier enabled. The application never creates Azure accounts, databases, containers or throughput settings.

Runtime settings:

```text
FACTORYVISION_DB_BACKEND=cosmos
FACTORYVISION_COSMOS_ENDPOINT=<secret>
FACTORYVISION_COSMOS_KEY=<secret>
FACTORYVISION_COSMOS_DATABASE=factoryvision
FACTORYVISION_COSMOS_CONTAINER=inspections
```

Use a shared-throughput database and keep the account within the Free Tier allowance. Do not use serverless mode for this deployment.

### GitHub Actions and GitHub Container Registry

The repository is public. Use standard GitHub-hosted runners and a public GHCR container image. Do not use larger GitHub runners.

The Azure runtime image is built only through the manual `Build Azure Runtime Image` workflow. The workflow downloads the packaged model, verifies the checkpoint checksum through `scripts/install_model_release.py`, builds `Dockerfile.azure`, and pushes the image to GHCR.

## Explicitly prohibited for the zero-cost deployment

Do not enable any of the following without a separate user decision:

- Azure OpenAI or other usage-billed AI endpoints
- Azure Container Registry
- serverless GPU
- Azure Kubernetes Service
- Virtual Machines
- Azure SQL Database
- Dedicated Container Apps workload profiles
- always-on Container Apps replicas
- paid Application Insights or Log Analytics ingestion

## Fail-closed behavior

The API is designed to fail closed when a safety condition is reached:

1. Unsupported upload types are rejected before inference.
2. Oversized images are rejected before image decoding or inference.
3. The daily persisted inspection count is checked before inference.
4. If the configured daily limit is reached, inference pauses until the next UTC day.
5. When Cosmos DB is the persistence backend, the limit survives Container Apps scale-to-zero and replica replacement because the count is stored outside the container.

These application safeguards reduce cost risk but are not an Azure billing hard-stop. Azure budget alerts are warnings, not spending caps. The deployment must therefore remain on the approved free plans and be disabled manually if Azure usage approaches a billable threshold.

## Priority order

1. No unapproved charge.
2. Preserve project source code and model artifacts.
3. Keep the static portfolio experience available where possible.
4. Run live PatchCore inference only while the zero-cost safety conditions are satisfied.
