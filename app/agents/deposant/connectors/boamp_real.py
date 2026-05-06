"""Connecteur reel pour la plateforme BOAMP (France)."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

from app.agents.deposant.connectors.base import (
    BaseConnector,
    PlatformCredentials,
    SubmissionResult,
    SubmissionResultStatus,
)

logger = logging.getLogger(__name__)

BOAMP_DEFAULT_BASE_URL = "https://api.boamp.fr/api/v2"
TOKEN_ENDPOINT = "/auth/token"
AVIS_ENDPOINT = "/avis"
SOUMISSIONS_ENDPOINT = "/soumissions"
DOCUMENTS_ENDPOINT = "/soumissions/{id}/documents"
RECU_ENDPOINT = "/soumissions/{id}/recu"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3


class BoampRealConnector(BaseConnector):
    """Connecteur reel BOAMP pour soumissions electroniques."""

    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = credentials.base_url or BOAMP_DEFAULT_BASE_URL
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def authenticate(self) -> bool:
        """Obtient un token OAuth2 aupres de BOAMP."""
        if not self.credentials.username or not self.credentials.password:
            logger.error("BOAMP: username (SIRET) et password requis")
            return False

        if self._access_token and self._token_expires_at and datetime.now(timezone.utc) < self._token_expires_at:
            return True

        url = f"{self.base_url}{TOKEN_ENDPOINT}"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.credentials.username,
            "client_secret": self.credentials.password,
            "scope": "soumission:write soumission:read avis:read",
        }

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, data=data)
                    resp.raise_for_status()
                    token_data = resp.json()

                    self._access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)

                    logger.info(f"BOAMP: authentification reussie (SIRET: {self._mask(self.credentials.username)})")
                    return True

            except httpx.HTTPStatusError as e:
                logger.error(f"BOAMP: erreur HTTP {e.response.status_code} auth tentative {attempt+1}: {e.response.text[:500]}")
                if e.response.status_code in (401, 403):
                    return False
            except httpx.TimeoutException:
                logger.warning(f"BOAMP: timeout auth tentative {attempt+1}")
            except Exception as e:
                logger.error(f"BOAMP: erreur auth tentative {attempt+1}: {e}")

        return False

    def _get_headers(self) -> dict[str, str]:
        if not self._access_token:
            raise RuntimeError("Non authentifie — appeler authenticate() d'abord")
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TAKA-OS/1.0",
        }

    async def submit(
        self,
        ao_reference: str,
        response_text: str,
        documents: list[dict],
    ) -> SubmissionResult:
        logger.info(f"BOAMP: tentative soumission AO {ao_reference}")

        if not await self.authenticate():
            return SubmissionResult(
                status=SubmissionResultStatus.FAILED,
                message="Echec d'authentification BOAMP — verifiez vos credentials",
                requires_manual_action=True,
                next_steps=[
                    "Verifiez votre SIRET et mot de passe BOAMP",
                    "Assurez-vous que votre compte est actif",
                    "Contactez le support BOAMP si le probleme persiste",
                ],
            )

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                avis_resp = await client.get(
                    f"{self.base_url}{AVIS_ENDPOINT}/{ao_reference}",
                    headers=self._get_headers(),
                )
                if avis_resp.status_code == 404:
                    return SubmissionResult(
                        status=SubmissionResultStatus.VALIDATION_ERROR,
                        message=f"AO {ao_reference} non trouve sur BOAMP",
                    )
                avis_resp.raise_for_status()
                avis_data = avis_resp.json()

                if avis_data.get("statut") != "ouvert":
                    return SubmissionResult(
                        status=SubmissionResultStatus.VALIDATION_ERROR,
                        message=f"AO {ao_reference} n'est plus ouvert (statut: {avis_data.get('statut')})",
                    )

                org_id = self.credentials.additional_data.get("organization_id") if self.credentials.additional_data else None
                submission_payload = {
                    "avis_reference": ao_reference,
                    "soumissionnaire": {
                        "siret": self.credentials.username,
                        "raison_sociale": org_id or "",
                    },
                    "message": response_text,
                    "nombre_documents": len(documents),
                }

                submit_resp = await client.post(
                    f"{self.base_url}{SOUMISSIONS_ENDPOINT}",
                    json=submission_payload,
                    headers=self._get_headers(),
                )
                submit_resp.raise_for_status()
                submit_data = submit_resp.json()

                platform_ref = submit_data["id"]
                logger.info(f"BOAMP: soumission creee {platform_ref}")

                doc_uploads = []
                for doc in documents:
                    doc_resp = await client.post(
                        f"{self.base_url}{DOCUMENTS_ENDPOINT.format(id=platform_ref)}",
                        files={
                            "file": (doc["name"], doc["content"], doc.get("mime_type", "application/pdf")),
                        },
                        headers={"Authorization": f"Bearer {self._access_token}"},
                    )
                    if doc_resp.status_code in (200, 201):
                        doc_uploads.append({"name": doc["name"], "status": "uploaded"})
                    else:
                        doc_uploads.append({"name": doc["name"], "status": "failed", "error": doc_resp.text[:200]})
                        logger.warning(f"BOAMP: echec upload document {doc['name']}: {doc_resp.status_code}")

                failed_docs = [d for d in doc_uploads if d["status"] == "failed"]
                if failed_docs and len(failed_docs) == len(documents):
                    return SubmissionResult(
                        status=SubmissionResultStatus.NEEDS_DOCUMENTS,
                        platform_reference=platform_ref,
                        message=f"Soumission creee mais {len(failed_docs)} document(s) non uploades",
                        requires_manual_action=True,
                        next_steps=["Connectez-vous sur BOAMP pour uploader les documents manquants"],
                        raw_response={"submission": submit_data, "documents": doc_uploads},
                    )

                receipt_resp = await client.get(
                    f"{self.base_url}{RECU_ENDPOINT.format(id=platform_ref)}",
                    headers=self._get_headers(),
                )
                receipt_url = None
                if receipt_resp.status_code == 200:
                    receipt_data = receipt_resp.json()
                    receipt_url = receipt_data.get("url_recu")

                return SubmissionResult(
                    status=SubmissionResultStatus.SUCCESS,
                    platform_reference=platform_ref,
                    platform_receipt_url=receipt_url,
                    platform_submitted_at=datetime.now(timezone.utc),
                    message=f"Soumission envoyee avec succes sur BOAMP (reference: {platform_ref})",
                    raw_response={"submission": submit_data, "documents": doc_uploads},
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"BOAMP: HTTP {e.response.status_code} — {e.response.text[:1000]}")
            error_detail = self._parse_boamp_error(e.response)
            if e.response.status_code == 422:
                return SubmissionResult(
                    status=SubmissionResultStatus.VALIDATION_ERROR,
                    message=f"Donnees invalides : {error_detail}",
                    raw_response={"status_code": e.response.status_code, "detail": error_detail},
                )
            if e.response.status_code in (401, 403):
                return SubmissionResult(
                    status=SubmissionResultStatus.FAILED,
                    message=f"Authentification invalide ou permissions insuffisantes : {error_detail}",
                    requires_manual_action=True,
                    next_steps=["Renouvelez vos credentials BOAMP"],
                )
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur BOAMP ({e.response.status_code}): {error_detail}",
                requires_manual_action=True,
                next_steps=["Reessayez dans quelques minutes", "Contactez le support BOAMP"],
            )

        except httpx.TimeoutException:
            logger.error(f"BOAMP: timeout soumission AO {ao_reference}")
            return SubmissionResult(
                status=SubmissionResultStatus.TIMEOUT,
                message="Timeout lors de la soumission — le serveur BOAMP ne repond pas",
                requires_manual_action=True,
                next_steps=["Reessayez dans quelques minutes", "Verifiez l'etat de BOAMP"],
            )

        except Exception as e:
            logger.exception(f"BOAMP: erreur inattendue soumission AO {ao_reference}")
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur inattendue : {str(e)}",
                requires_manual_action=True,
            )

    async def check_status(self, platform_reference: str) -> SubmissionResult:
        if not await self.authenticate():
            return SubmissionResult(
                status=SubmissionResultStatus.FAILED,
                message="Authentification BOAMP requise",
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}{SOUMISSIONS_ENDPOINT}/{platform_reference}",
                    headers=self._get_headers(),
                )
                resp.raise_for_status()
                data = resp.json()

                statut_map = {
                    "brouillon": SubmissionResultStatus.PENDING,
                    "en_cours": SubmissionResultStatus.PENDING,
                    "soumise": SubmissionResultStatus.PENDING,
                    "validee": SubmissionResultStatus.SUCCESS,
                    "refusee": SubmissionResultStatus.FAILED,
                    "annulee": SubmissionResultStatus.FAILED,
                }

                return SubmissionResult(
                    status=statut_map.get(data.get("statut"), SubmissionResultStatus.PENDING),
                    platform_reference=platform_reference,
                    platform_submitted_at=_parse_datetime(data.get("date_soumission")),
                    message=f"Statut BOAMP: {data.get('statut', 'inconnu')}",
                    raw_response=data,
                )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return SubmissionResult(
                    status=SubmissionResultStatus.FAILED,
                    platform_reference=platform_reference,
                    message="Soumission non trouvee sur BOAMP",
                )
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur BOAMP: {e.response.status_code}",
            )
        except Exception as e:
            logger.exception(f"BOAMP: erreur check_status {platform_reference}")
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur: {str(e)}",
            )

    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        if not await self.authenticate():
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{self.base_url}{RECU_ENDPOINT.format(id=platform_reference)}",
                    headers={**self._get_headers(), "Accept": "application/pdf"},
                )
                if resp.status_code == 200:
                    return resp.content
                return None
        except Exception as e:
            logger.error(f"BOAMP: erreur telechargement recu {platform_reference}: {e}")
            return None

    async def upload_document(self, platform_reference: str, document: dict) -> dict:
        if not await self.authenticate():
            return {"uploaded": False, "error": "Non authentifie"}

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(
                    f"{self.base_url}{DOCUMENTS_ENDPOINT.format(id=platform_reference)}",
                    files={"file": (document["name"], document["content"], document.get("mime_type", "application/pdf"))},
                    headers={"Authorization": f"Bearer {self._access_token}"},
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    return {"uploaded": True, "document_id": data.get("id"), "url": data.get("url")}
                return {"uploaded": False, "error": f"HTTP {resp.status_code}: {resp.text[:500]}"}
        except Exception as e:
            return {"uploaded": False, "error": str(e)}

    @staticmethod
    def _parse_boamp_error(response) -> str:
        try:
            data = response.json()
            if "detail" in data:
                return str(data["detail"])
            if "message" in data:
                return str(data["message"])
            if "error" in data:
                return str(data["error"])
            return str(data)[:500]
        except Exception:
            return response.text[:500]


def _parse_datetime(value) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    try:
        from dateutil import parser
        dt = parser.isoparse(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None
