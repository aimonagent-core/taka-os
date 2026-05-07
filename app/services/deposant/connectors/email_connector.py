"""Connecteur de soumission par email direct a l'acheteur."""

import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from app.services.deposant.connectors.base_connector import (
    BasePlatformConnector,
    SubmissionResult,
)

logger = logging.getLogger(__name__)


class EmailDirectConnector(BasePlatformConnector):
    """Soumission par email direct a l'acheteur public.

    Config attendue (JSON):
    {
        "provider": "resend" | "smtp" | "sendgrid",
        "api_key": "re_xxxx" | null,          # pour Resend / SendGrid
        "smtp_host": "smtp.example.com",       # pour SMTP
        "smtp_port": 587,
        "smtp_user": "user@example.com",
        "smtp_password": "secret",
        "from_email": "depot@mon-entreprise.fr",
        "from_name": "Mon Entreprise",
        "template_html": "<html>...</html>",   # optionnel
    }
    """

    async def test_connection(self) -> bool:
        provider = self.config.get("provider", "resend")
        if provider == "resend":
            return await self._test_resend()
        if provider == "smtp":
            return await self._test_smtp()
        # Provider inconnu — on considere que c'est OK si la config est presente
        return bool(self.config.get("from_email"))

    async def _test_resend(self) -> bool:
        api_key = self.config.get("api_key")
        if not api_key:
            return False
        try:
            import resend
            resend.api_key = api_key
            # Liste des domaines — endpoint leger pour valider la cle
            resend.domains.list()
            return True
        except Exception as exc:
            logger.warning("[EmailConnector] Test Resend echoue: %s", exc)
            return False

    async def _test_smtp(self) -> bool:
        try:
            import aiosmtplib
            host = self.config.get("smtp_host")
            port = self.config.get("smtp_port", 587)
            if not host:
                return False
            await aiosmtplib.connect(hostname=host, port=port, timeout=5)
            return True
        except ImportError:
            logger.warning("[EmailConnector] aiosmtplib non installe")
            return False
        except Exception as exc:
            logger.warning("[EmailConnector] Test SMTP echoue: %s", exc)
            return False

    async def submit(
        self,
        ao_id: uuid.UUID,
        documents: list[dict],
        payload: dict,
    ) -> SubmissionResult:
        to_email = payload.get("buyer_email") or self.config.get("to_email")
        to_name = payload.get("buyer_name") or "Acheteur public"
        subject = payload.get("subject") or f"Candidature AO {ao_id}"
        body_text = payload.get("body_text") or self._build_body_text(payload)
        body_html = payload.get("body_html") or self.config.get("template_html") or self._build_body_html(payload)

        if not to_email:
            return SubmissionResult(
                status="error",
                platform="email_direct",
                message="Email acheteur manquant (buyer_email ou to_email requis)",
                is_mock=False,
            )

        provider = self.config.get("provider", "resend")
        try:
            if provider == "resend":
                await self._send_via_resend(to_email, to_name, subject, body_text, body_html, documents)
            elif provider == "smtp":
                await self._send_via_smtp(to_email, to_name, subject, body_text, body_html, documents)
            else:
                raise ValueError(f"Provider email inconnu: {provider}")

            external_id = f"EMAIL-{ao_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            return SubmissionResult(
                status="submitted",
                external_id=external_id,
                platform="email_direct",
                message=f"Email envoye a {to_email}",
                is_mock=False,
            )
        except Exception as exc:
            logger.exception("[EmailConnector] Echec envoi email pour AO %s", ao_id)
            return SubmissionResult(
                status="error",
                platform="email_direct",
                message=f"Erreur envoi email: {exc}",
                is_mock=False,
            )

    async def _send_via_resend(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_text: str,
        body_html: Optional[str],
        documents: list[dict],
    ) -> None:
        import resend
        resend.api_key = self.config["api_key"]
        params: dict = {
            "from": f"{self.config.get('from_name', 'TAKA OS')} <{self.config['from_email']}>",
            "to": [to_email],
            "subject": subject,
            "text": body_text,
        }
        if body_html:
            params["html"] = body_html
        if documents:
            params["attachments"] = [
                {
                    "filename": doc.get("name", "document.pdf"),
                    "content": doc.get("data", ""),
                }
                for doc in documents
            ]
        resend.Emails.send(params)

    async def _send_via_smtp(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_text: str,
        body_html: Optional[str],
        documents: list[dict],
    ) -> None:
        import aiosmtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = f"{self.config.get('from_name', 'TAKA OS')} <{self.config['from_email']}>"
        msg["To"] = f"{to_name} <{to_email}>"
        msg["Subject"] = subject

        if body_html:
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype="html")
        else:
            msg.set_content(body_text)

        for doc in documents:
            data = doc.get("data", b"")
            if isinstance(data, str):
                data = data.encode("utf-8")
            msg.add_attachment(
                data,
                maintype="application",
                subtype="pdf",
                filename=doc.get("name", "document.pdf"),
            )

        await aiosmtplib.send(
            msg,
            hostname=self.config["smtp_host"],
            port=self.config.get("smtp_port", 587),
            username=self.config.get("smtp_user"),
            password=self.config.get("smtp_password"),
            start_tls=True,
        )

    def _build_body_text(self, payload: dict) -> str:
        return (
            f"Madame, Monsieur,\n\n"
            f"Veuillez trouver ci-joint notre candidature.\n\n"
            f"{payload.get('response_text', '')[:2000]}\n\n"
            f"Cordialement,\n{self.config.get('from_name', 'Votre soumissionnaire TAKA OS')}"
        )

    def _build_body_html(self, payload: dict) -> str:
        return (
            f"<html><body>"
            f"<p>Madame, Monsieur,</p>"
            f"<p>Veuillez trouver ci-joint notre candidature.</p>"
            f"<pre>{payload.get('response_text', '')[:2000]}</pre>"
            f"<p>Cordialement,<br>{self.config.get('from_name', 'Votre soumissionnaire TAKA OS')}</p>"
            f"</body></html>"
        )

    async def get_status(self, external_id: str) -> dict:
        # Les emails n'ont pas de statut trackable via ce connecteur
        return {
            "status": "submitted",
            "external_id": external_id,
            "platform": "email_direct",
            "note": "Statut non trackable par email direct",
        }

    async def download_receipt(self, external_id: str) -> Optional[bytes]:
        return None
