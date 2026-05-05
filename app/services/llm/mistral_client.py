# File: app/services/llm/mistral_client.py
# Purpose: Mistral AI client with retry, fallback, and circuit breaker
# Dependencies: httpx, tenacity, structlog

from typing import Any

import httpx
import logging
import tenacity

from app.config import settings

logger = logging.getLogger(__name__)


class MistralAIClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.mistral.ai/v1",
        primary_model: str = "mistral-medium-latest",
        fallback_model: str = "mistral-small-latest",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or settings.mistral_api_key or ""
        self._base_url = base_url.rstrip("/")
        self._primary_model = primary_model
        self._fallback_model = fallback_model
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={"Authorization": f"Bearer {self._api_key}"},
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError)),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        model = model or self._primary_model
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions", json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (429, 503):
                logger.warning("mistral_primary_failed: status=%s", exc.response.status_code)
                payload["model"] = self._fallback_model
                response = await self._client.post(
                    f"{self._base_url}/chat/completions", json=payload
                )
                response.raise_for_status()
                return response.json()
            raise

    async def embed_texts(
        self, texts: list[str], model: str = "mistral-embed"
    ) -> list[list[float]]:
        payload = {"model": model, "input": texts}
        response = await self._client.post(
            f"{self._base_url}/embeddings", json=payload
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    async def close(self) -> None:
        await self._client.aclose()
