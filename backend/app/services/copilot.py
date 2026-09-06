from __future__ import annotations

import json
import os
from typing import Any

import httpx


class CopilotNotConfiguredError(RuntimeError):
    pass


class QualityCopilotService:
    """LLM adapter for grounded quality answers.

    The provider is disabled by default. When Azure OpenAI settings are present,
    the service sends only the user's question plus structured inspection
    evidence. The system prompt explicitly forbids inventing factory facts that
    are not present in that evidence bundle.
    """

    def __init__(self) -> None:
        self.provider = os.getenv("FACTORYVISION_COPILOT_PROVIDER", "disabled")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        self.azure_model = os.getenv("AZURE_OPENAI_MODEL", "").strip()
        self.timeout_seconds = float(
            os.getenv("FACTORYVISION_COPILOT_TIMEOUT_SECONDS", "30")
        )

    @property
    def ready(self) -> bool:
        return (
            self.provider == "azure_openai"
            and bool(self.azure_endpoint)
            and bool(self.azure_api_key)
            and bool(self.azure_model)
        )

    def _chat_url(self) -> str:
        base = self.azure_endpoint.rstrip("/")
        if not base.endswith("/openai/v1"):
            base = f"{base}/openai/v1"
        return f"{base}/chat/completions"

    @staticmethod
    def _system_prompt(context: dict[str, Any]) -> str:
        evidence = json.dumps(context, ensure_ascii=False, indent=2)
        return (
            "You are FactoryVision AI's manufacturing quality copilot. "
            "Answer only from the inspection evidence below. Do not invent "
            "root causes, machine conditions, operators, maintenance events, "
            "or production facts that are not present in the evidence. If the "
            "evidence is insufficient, say exactly what additional evidence is "
            "needed. Keep answers concise and useful to a quality engineer.\n\n"
            f"INSPECTION EVIDENCE:\n{evidence}"
        )

    def answer(self, question: str, context: dict[str, Any]) -> str:
        if not self.ready:
            raise CopilotNotConfiguredError(
                "The quality copilot provider is not configured."
            )

        payload = {
            "model": self.azure_model,
            "messages": [
                {"role": "system", "content": self._system_prompt(context)},
                {"role": "user", "content": question},
            ],
            "temperature": 0.2,
        }
        headers = {
            "api-key": self.azure_api_key,
            "content-type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self._chat_url(), headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        try:
            answer = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Azure OpenAI returned an unexpected response.") from exc

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("Azure OpenAI returned an empty answer.")

        return answer.strip()
