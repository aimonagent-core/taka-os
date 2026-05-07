"""Connecteur generique pour plateformes avec API ouverte."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.services.deposant.connectors.base_connector import (
    BasePlatformConnector,
    SubmissionResult,
)

logger = logging.getLogger(__name__)


class GenericAPIConnector(BasePlatformConnector):
    """Connecteur generique pour plateformes avec API REST.

    Config attendue (JSON):
    {
        "base_url": "https://api.plateforme.example.com/v1",
        "auth_type": "api_key" | "oauth2" | "bearer",
        "api_key": "xxx",
        "api_key_header": "X-API-Key",
        "oauth_token_url": "https://auth.example.com/token",
        "oauth_client_id": "xxx",
        "oauth_client_secret": "xxx",
        "bearer_token": "xxx",
        "timeout_seconds": 30,
        "submit_endpoint": "/submissions",
        "status_endpoint": "/submissions/{external_id}/status",
        "receipt_endpoint": "/submissions/{external_id}/receipt",
    }
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get("base_url", "")
        self.timeout = config.get("timeout_seconds", 30)
        self._oauth_token: Optional[str] = None
        self._oauth_expires: Optional[datetime] = None

    def _get_headers(self) -> dict[str, str]:
        auth_type = self.config.get("auth_type", "api_key")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if auth_type == "api_key":
            header_name = self.config.get("api_key_header", "X-API-Key")
            headers[header_name] = self.config.get("api_key", "")
        elif auth_type == "bearer":
            headers["Authorization"] = f"Bearer {self.config.get('bearer_token', '')}"
        elif auth_type == "oauth2":
            if self._oauth_token:
                headers["Authorization"] = f"Bearer {self._oauth_token}"
        return headers

    async def _ensure_oauth_token(self) -> None:
        if self.config.get("auth_type") != "oauth2":
            return
        if self._oauth_token and self._oauth_expires and datetime.now(timezone.utc) < self._oauth_expires:
            return

        token_url = self.config.get("oauth_token_url", "")
        client_id = self.config.get("oauth_client_id", "")
        client_secret = self.config.get("oauth_client_secret", "")

        if not token_url or not client_id:
            raise ValueError("Configuration OAuth2 incomplete")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            self._oauth_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            self._oauth_expires = datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(seconds=expires_in - 60)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        await self._ensure_oauth_token()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.request(method, url, headers=headers, **kwargs)
            resp.raise_for_status()
            return resp

    async def test_connection(self) -> bool:
        try:
            # Si un endpoint health existe, on l'utilise ; sinon un GET sur base_url
            await self._request("GET", "/health")
            return True
        except Exception:
            try:
                await self._request("GET", "/")
                return True
            except Exception as exc:
                logger.warning("[GenericAPIConnector] Test connexion echoue: %s", exc)
                return False

    async def submit(
        self,
        ao_id: uuid.UUID,
        documents: list[dict],
        payload: dict,
    ) -> SubmissionResult:
        endpoint = self.config.get("submit_endpoint", "/submissions")
        body = {
            "ao_id": str(ao_id),
            "payload": payload,
            "documents": documents,
        }
        try:
            resp = await self._request("POST", endpoint, json=body)
            data = resp.json()
            return SubmissionResult(
                status="submitted",
                external_id=data.get("id") or data.get("submission_id"),
                platform=self.platform_name,
                message=data.get("message", "Soumission OK"),
                is_mock=False,
                raw_response=data,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("[GenericAPIConnector] HTTP %s: %s", exc.response.status_code, exc.response.text)
            return SubmissionResult(
                status="error",
                platform=self.platform_name,
                message=f"HTTP {exc.response.status_code}: {exc.response.text[:500]}",
                is_mock=False,
                raw_response={"status_code": exc.response.status_code, "body": exc.response.text},
            )
        except Exception as exc:
            logger.exception("[GenericAPIConnector] Erreur soumission")
            return SubmissionResult(
                status="error",
                platform=self.platform_name,
                message=f"Erreur: {exc}",
                is_mock=False,
            )

    async def get_status(self, external_id: str) -> dict:
        endpoint = self.config.get("status_endpoint", "/submissions/{external_id}/status")
        path = endpoint.replace("{external_id}", external_id)
        try:
            resp = await self._request("GET", path)
            return resp.json()
        except Exception as exc:
            logger.warning("[GenericAPIConnector] Erreur statut %s: %s", external_id, exc)
            return {"status": "unknown", "error": str(exc), "external_id": external_id}

    async def download_receipt(self, external_id: str) -> Optional[bytes]:
        endpoint = self.config.get("receipt_endpoint", "/submissions/{external_id}/receipt")
        path = endpoint.replace("{external_id}", external_id)
        try:
            resp = await self._request("GET", path)
            return resp.content
        except Exception as exc:
            logger.warning("[GenericAPIConnector] Erreur recu %s: %s", external_id, exc)
            return None
