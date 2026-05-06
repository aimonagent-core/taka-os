"""Connecteur reel pour e-Notification (Belgique)."""

import logging
import os
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

E_NOTIFICATION_DEFAULT_BASE_URL = "https://enotification.belgium.be/ws/rest"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3


class ENotificationRealConnector(BaseConnector):
    """Connecteur reel e-Notification (Belgique)."""

    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = credentials.base_url or E_NOTIFICATION_DEFAULT_BASE_URL
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._temp_cert_file: Optional[str] = None
        self._temp_key_file: Optional[str] = None

    def _get_client(self) -> httpx.AsyncClient:
        client_kwargs: dict = {
            "timeout": DEFAULT_TIMEOUT,
            "headers": {
                "Accept": "application/json",
                "User-Agent": "TAKA-OS/1.0",
            },
        }
        if self.credentials.certificate_pem:
            import tempfile
            cert_file = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False)
            key_file = tempfile.NamedTemporaryFile(mode="w", suffix=".key", delete=False)
            cert_file.write(self.credentials.certificate_pem)
            cert_file.close()
            key_file.close()
            client_kwargs["cert"] = (cert_file.name, key_file.name)
            self._temp_cert_file = cert_file.name
            self._temp_key_file = key_file.name

        return httpx.AsyncClient(**client_kwargs)

    async def authenticate(self) -> bool:
        if self._access_token and self._token_expires_at and datetime.now(timezone.utc) < self._token_expires_at:
            return True

        if not self.credentials.username or not self.credentials.password:
            logger.error("e-Notification: username (ISINC) et password requis")
            return False

        url = f"{self.base_url}/auth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.credentials.username,
            "client_secret": self.credentials.password,
            "scope": "soumission:write soumission:read avis:read",
        }

        for attempt in range(MAX_RETRIES):
            client = None
            try:
                client = self._get_client()
                resp = await client.post(url, data=data)
                resp.raise_for_status()
                token_data = resp.json()

                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)

                logger.info(f"e-Notification: authentification reussie (ISINC: {self._mask(self.credentials.username)})")
                return True

            except httpx.HTTPStatusError as e:
                logger.error(f"e-Notification: HTTP {e.response.status_code} auth tentative {attempt+1}")
                if e.response.status_code in (401, 403):
                    return False
            except Exception as e:
                logger.error(f"e-Notification: erreur auth tentative {attempt+1}: {e}")
            finally:
                if client:
                    await client.aclose()
                self._cleanup_temp_files()

        return False

    def _get_headers(self) -> dict[str, str]:
        if not self._access_token:
            raise RuntimeError("Non authentifie")
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TAKA-OS/1.0",
        }

    def _cleanup_temp_files(self):
        for attr in ["_temp_cert_file", "_temp_key_file"]:
            path = getattr(self, attr, None)
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception:
                    pass

    async def submit(
        self,
        ao_reference: str,
        response_text: str,
        documents: list[dict],
    ) -> SubmissionResult:
        logger.info(f"e-Notification: tentative soumission AO {ao_reference}")

        if not await self.authenticate():
            return SubmissionResult(
                status=SubmissionResultStatus.FAILED,
                message="Echec d'authentification e-Notification",
                requires_manual_action=True,
                next_steps=["Verifiez votre certificat eID/ISINC", "Assurez-vous que votre compte est actif"],
            )

        client = None
        try:
            client = self._get_client()

            avis_resp = await client.get(
                f"{self.base_url}/avis/{ao_reference}",
                headers=self._get_headers(),
            )
            if avis_resp.status_code == 404:
                return SubmissionResult(
                    status=SubmissionResultStatus.VALIDATION_ERROR,
                    message=f"Avis {ao_reference} non trouve sur e-Notification",
                )
            avis_resp.raise_for_status()
            avis_data = avis_resp.json()

            if avis_data.get("statut") not in ("publie", "ouvert"):
                return SubmissionResult(
                    status=SubmissionResultStatus.VALIDATION_ERROR,
                    message=f"Avis {ao_reference} n'accepte plus de soumissions (statut: {avis_data.get('statut')})",
                )

            org_name = (self.credentials.additional_data or {}).get("organization_name", "")
            submission_payload = {
                "avis_reference": ao_reference,
                "soumissionnaire": {
                    "isinc": self.credentials.username,
                    "denomination": org_name,
                },
                "message_soumission": response_text,
                "langue": "fr",
                "nombre_documents": len(documents),
            }

            submit_resp = await client.post(
                f"{self.base_url}/soumissions",
                json=submission_payload,
                headers=self._get_headers(),
            )
            submit_resp.raise_for_status()
            submit_data = submit_resp.json()

            platform_ref = submit_data["id"]
            logger.info(f"e-Notification: soumission creee {platform_ref}")

            doc_results = []
            for doc in documents:
                doc_resp = await client.post(
                    f"{self.base_url}/soumissions/{platform_ref}/documents",
                    files={
                        "file": (doc["name"], doc["content"], doc.get("mime_type", "application/pdf")),
                    },
                    headers={"Authorization": f"Bearer {self._access_token}"},
                )
                doc_results.append({
                    "name": doc["name"],
                    "status": "uploaded" if doc_resp.status_code in (200, 201) else "failed",
                })

            finalize_resp = await client.post(
                f"{self.base_url}/soumissions/{platform_ref}/finaliser",
                headers=self._get_headers(),
            )
            if finalize_resp.status_code in (200, 201):
                final_data = finalize_resp.json()
                receipt_url = final_data.get("url_recu")
                submitted_at = _parse_be_datetime(final_data.get("date_soumission"))

                return SubmissionResult(
                    status=SubmissionResultStatus.SUCCESS,
                    platform_reference=platform_ref,
                    platform_receipt_url=receipt_url,
                    platform_submitted_at=submitted_at,
                    message=f"Soumission envoyee sur e-Notification (reference: {platform_ref})",
                    raw_response={"submission": submit_data, "finalization": final_data, "documents": doc_results},
                )
            else:
                return SubmissionResult(
                    status=SubmissionResultStatus.PENDING,
                    platform_reference=platform_ref,
                    message="Soumission creee mais finalisation en attente — connectez-vous sur e-Notification",
                    requires_manual_action=True,
                    next_steps=["Connectez-vous sur e-Notification.be pour finaliser", "Verifiez que tous les documents sont complets"],
                    raw_response={"submission": submit_data, "documents": doc_results},
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"e-Notification: HTTP {e.response.status_code} — {e.response.text[:1000]}")
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur e-Notification ({e.response.status_code})",
                requires_manual_action=True,
                next_steps=["Reessayez dans quelques minutes", "Contactez le support e-Notification"],
            )
        except httpx.TimeoutException:
            return SubmissionResult(
                status=SubmissionResultStatus.TIMEOUT,
                message="Timeout e-Notification",
                requires_manual_action=True,
            )
        except Exception as e:
            logger.exception(f"e-Notification: erreur soumission {ao_reference}")
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur: {str(e)}",
                requires_manual_action=True,
            )
        finally:
            if client:
                await client.aclose()
            self._cleanup_temp_files()

    async def check_status(self, platform_reference: str) -> SubmissionResult:
        if not await self.authenticate():
            return SubmissionResult(
                status=SubmissionResultStatus.FAILED,
                message="Authentification requise",
            )

        client = None
        try:
            client = self._get_client()
            resp = await client.get(
                f"{self.base_url}/soumissions/{platform_reference}/statut",
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            data = resp.json()

            status_map = {
                "brouillon": SubmissionResultStatus.PENDING,
                "en_attente": SubmissionResultStatus.PENDING,
                "soumise": SubmissionResultStatus.PENDING,
                "acceptee": SubmissionResultStatus.SUCCESS,
                "refusee": SubmissionResultStatus.FAILED,
                "incomplete": SubmissionResultStatus.NEEDS_DOCUMENTS,
            }

            return SubmissionResult(
                status=status_map.get(data.get("statut"), SubmissionResultStatus.PENDING),
                platform_reference=platform_reference,
                message=f"Statut e-Notification: {data.get('statut', 'inconnu')}",
                raw_response=data,
            )
        except Exception as e:
            logger.error(f"e-Notification: erreur check_status {platform_reference}: {e}")
            return SubmissionResult(
                status=SubmissionResultStatus.PLATFORM_ERROR,
                message=f"Erreur: {str(e)}",
            )
        finally:
            if client:
                await client.aclose()
            self._cleanup_temp_files()

    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        if not await self.authenticate():
            return None

        client = None
        try:
            client = self._get_client()
            resp = await client.get(
                f"{self.base_url}/soumissions/{platform_reference}/recu",
                headers={**self._get_headers(), "Accept": "application/pdf"},
            )
            if resp.status_code == 200:
                return resp.content
            return None
        except Exception as e:
            logger.error(f"e-Notification: erreur recu {platform_reference}: {e}")
            return None
        finally:
            if client:
                await client.aclose()
            self._cleanup_temp_files()

    async def upload_document(self, platform_reference: str, document: dict) -> dict:
        if not await self.authenticate():
            return {"uploaded": False, "error": "Non authentifie"}

        client = None
        try:
            client = self._get_client()
            resp = await client.post(
                f"{self.base_url}/soumissions/{platform_reference}/documents",
                files={"file": (document["name"], document["content"], document.get("mime_type", "application/pdf"))},
                headers={"Authorization": f"Bearer {self._access_token}"},
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return {"uploaded": True, "document_id": data.get("id")}
            return {"uploaded": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"uploaded": False, "error": str(e)}
        finally:
            if client:
                await client.aclose()
            self._cleanup_temp_files()


def _parse_be_datetime(value) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    try:
        from dateutil import parser
        dt = parser.isoparse(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        try:
            dt = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None
