# FactoryVision AI — Azure Free-Conscious Deployment Stack

This document defines the Azure deployment target for FactoryVision AI with a strict cost-conscious design. The goal is to use Azure-native services that have a free plan or monthly free grant, while avoiding services that would add fixed recurring cost.

## Target architecture

```text
GitHub repository
      |
      +--> GitHub Actions
      |       |
      |       +--> React build --> Azure Static Web Apps (Free)
      |       |
      |       +--> backend container --> GitHub Container Registry (GHCR)
      |                                |
      |                                v
      |                    Azure Container Apps (Consumption)
      |                                |
      |                                +--> PatchCore model
      |                                +--> FastAPI
      |                                +--> grounded quality copilot
      |                                |
      |                                v
      +----------------------> Azure Cosmos DB for NoSQL (Free Tier)
```

## Azure resources

### 1. Resource Group

- Name: `factoryvision-rg`
- Recommended region: `West Europe`
- Purpose: keep all FactoryVision Azure resources grouped together.

### 2. Azure Static Web Apps

- Name: `factoryvision-web`
- Plan: `Free`
- Purpose: host the React/Vite frontend.
- GitHub remains the deployment source.
- The Free plan currently includes 100 GB/month of bandwidth and up to 10 apps per subscription.

### 3. Azure Container Apps

- Name: `factoryvision-api`
- Plan: `Consumption`
- Purpose: run FastAPI + PatchCore inference.
- Container registry: GitHub Container Registry, not Azure Container Registry.
- Minimum replicas: `0`
- Maximum replicas: `1`
- Initial CPU: `2 vCPU`
- Initial memory: `4 GiB`
- Ingress: external HTTPS
- Target port: backend HTTP port

Cost guardrail:

- Keep `minReplicas=0` so the app scales to zero when idle.
- Keep `maxReplicas=1` to prevent unexpected scale-out.
- Do not enable serverless GPU.
- Do not create a Dedicated workload profile.

Azure Container Apps Consumption currently includes a monthly free grant of 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests per subscription. Usage beyond the grant is billable on a Pay-As-You-Go subscription.

### 4. Azure Cosmos DB for NoSQL

- Account name: globally unique name based on `factoryvision-cosmos`
- Capacity mode: `Provisioned throughput`
- Apply Free Tier discount: `Yes`
- Region: `West Europe`
- Database: `factoryvision`
- Shared database throughput: maximum `1000 RU/s`
- Container: `inspections`
- Partition key: `/id`

Important: Cosmos DB Free Tier is not available for serverless accounts. The Free Tier must be enabled when the account is created. The lifetime free allowance is currently 1000 RU/s and 25 GB storage per eligible subscription.

## Services intentionally not used

The following services are intentionally excluded from the first deployment because they can add recurring cost or are unnecessary for this portfolio workload:

- Azure Container Registry — use GHCR instead.
- Azure OpenAI / Azure AI model inference — keep the existing grounded local copilot until a separately approved AI budget exists.
- Azure Key Vault — use Container Apps secrets for the first version.
- Azure SQL Database — use Cosmos DB Free Tier for cloud inspection persistence.
- Virtual Machines — no always-on VM.
- Azure Kubernetes Service — unnecessary operational and cost overhead.
- Dedicated Container Apps workload profiles — use Consumption only.
- Serverless GPU — disabled.
- Application Insights / Log Analytics paid ingestion — not part of the initial deployment plan.

## Runtime environment variables

Backend:

```text
FACTORYVISION_MODEL_CHECKPOINT=/app/artifacts/model.ckpt
FACTORYVISION_DB_BACKEND=cosmos
FACTORYVISION_COSMOS_ENDPOINT=<container-app-secret>
FACTORYVISION_COSMOS_DATABASE=factoryvision
FACTORYVISION_COSMOS_CONTAINER=inspections
FACTORYVISION_CORS_ORIGINS=https://<static-web-app-hostname>
```

Frontend:

```text
VITE_API_BASE_URL=https://<container-app-hostname>
```

## Model artifact strategy

The trained PatchCore checkpoint is intentionally not committed to GitHub. The verified release package remains an external artifact.

Deployment options, in order of preference:

1. Install the verified model during a controlled image-build step from a private/approved artifact source.
2. Mount or download the model at startup from an approved external location.

The model checksum must be verified before use.

## CI/CD

Use GitHub Actions rather than Azure DevOps:

- frontend: build and deploy to Azure Static Web Apps.
- backend: build the Docker image and push it to GHCR.
- deployment: update Azure Container Apps to the new GHCR image.

No Azure Container Registry is required.

## Cost safety rules

1. Use only the Free plan for Static Web Apps.
2. Use only the Consumption plan for Container Apps.
3. Set Container Apps minimum replicas to `0` and maximum replicas to `1`.
4. Enable Cosmos DB Free Tier at account creation and keep provisioned throughput at or below the free allowance.
5. Do not enable Azure OpenAI, GPU, AKS, VM, ACR, Azure SQL, Dedicated Container Apps profiles, or paid monitoring.
6. Configure an Azure Cost Management budget alert as an additional warning mechanism.
7. Remember that a budget alert does not hard-stop spending on a Pay-As-You-Go subscription.
8. If using Azure for Students, keep the subscription spending limit enabled and do not upgrade it to unrestricted Pay-As-You-Go unless explicitly intended.

## Planned resource names

| Purpose | Resource name |
|---|---|
| Resource group | `factoryvision-rg` |
| Static Web App | `factoryvision-web` |
| Container App | `factoryvision-api` |
| Container Apps environment | `factoryvision-env` |
| Cosmos DB account | `factoryvision-cosmos-<unique-suffix>` |
| Cosmos database | `factoryvision` |
| Cosmos container | `inspections` |

## Deployment order

1. Activate a usable Azure subscription.
2. Create `factoryvision-rg`.
3. Create Cosmos DB with Free Tier enabled.
4. Create Azure Static Web Apps on the Free plan.
5. Create Container Apps Consumption environment and backend app.
6. Configure secrets and environment variables.
7. Deploy the verified PatchCore runtime.
8. Connect the frontend to the Container App URL.
9. Run end-to-end inspection tests.
10. Add a cost budget alert and verify that no excluded paid services exist in the resource group.
