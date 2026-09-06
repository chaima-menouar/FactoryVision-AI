# FactoryVision AI quality copilot

## Grounding contract

The quality copilot is designed to answer from FactoryVision inspection evidence, not from invented factory context.

`GET /api/v1/copilot/context` builds a compact evidence bundle from persisted inspections. The bundle includes inspection counts, defect rate, average anomaly score, recent anomalous inspections and suggested quality questions.

`POST /api/v1/copilot/ask` passes that evidence bundle with the user's question to the configured provider. The system instruction explicitly forbids inventing root causes, machine conditions, operator actions, maintenance events or production facts that are absent from the evidence.

## Provider state

The provider is intentionally disabled by default:

```text
FACTORYVISION_COPILOT_PROVIDER=disabled
```

When an Azure OpenAI resource is intentionally provisioned, the runtime can be enabled with:

```text
FACTORYVISION_COPILOT_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
AZURE_OPENAI_API_KEY=<runtime-secret>
AZURE_OPENAI_MODEL=<deployment-or-model-name>
```

Secrets must never be committed to GitHub. Use the hosting platform's secret-management mechanism when the Azure phase begins.

## Runtime behavior

- If the provider is disabled or incomplete, `/api/v1/copilot/ask` returns HTTP 503.
- Provider/network failures are surfaced as HTTP 502.
- The inspection context endpoint remains available without an LLM provider.
- The application can therefore develop and test the grounding layer without cloud spend.

## Azure API boundary

The adapter targets the current Azure OpenAI v1 chat-completions route under `/openai/v1/chat/completions` using API-key authentication. The resource endpoint, model/deployment and secret are supplied only through environment variables.
