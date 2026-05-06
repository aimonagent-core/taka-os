"""Classe abstraite de base pour tous les connecteurs de depot."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SubmissionResultStatus(str, PyEnum):
    """Statuts possibles apres une soumission."""
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    NEEDS_DOCUMENTS = "needs_documents"
    VALIDATION_ERROR = "validation_error"
    PLATFORM_ERROR = "platform_error"
    TIMEOUT = "timeout"


@dataclass
class SubmissionResult:
    """Resultat d'une tentative de soumission."""
    status: SubmissionResultStatus
    platform_reference: Optional[str] = None
    platform_receipt_url: Optional[str] = None
    message: str = ""
    platform_submitted_at: Optional[datetime] = None
    requires_manual_action: bool = False
    next_steps: list[str] = field(default_factory=list)
    raw_response: Optional[dict] = None


@dataclass
class PlatformCredentials:
    """Credentials deconnexes pour un connecteur."""
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    certificate_pem: Optional[str] = None
    base_url: Optional[str] = None
    additional_data: Optional[dict] = None


class BaseConnector(ABC):
    """Classe de base pour tous les connecteurs de depot."""

    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.platform_name = self.__class__.__name__

    @abstractmethod
    async def authenticate(self) -> bool:
        """Teste l'authentification avec les credentials."""
        pass

    @abstractmethod
    async def submit(
        self,
        ao_reference: str,
        response_text: str,
        documents: list[dict],
    ) -> SubmissionResult:
        """Soumet une reponse a un appel d'offres."""
        pass

    @abstractmethod
    async def check_status(self, platform_reference: str) -> SubmissionResult:
        """Verifie le statut d'une soumission existante."""
        pass

    @abstractmethod
    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        """Telecharge l'accuse de reception au format PDF."""
        pass

    @abstractmethod
    async def upload_document(
        self,
        platform_reference: str,
        document: dict,
    ) -> dict:
        """Upload un document supplementaire sur une soumission existante."""
        pass

    async def health_check(self) -> dict:
        """Verifie la sante du connecteur."""
        import time
        start = time.monotonic()
        try:
            auth_ok = await self.authenticate()
            latency = int((time.monotonic() - start) * 1000)
            if auth_ok:
                return {"status": "healthy", "details": "Auth OK", "latency_ms": latency}
            return {"status": "unhealthy", "details": "Auth failed", "latency_ms": latency}
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return {"status": "unhealthy", "details": str(e), "latency_ms": latency}

    def _mask_credentials(self) -> dict:
        """Retourne une version masquee des credentials pour les logs."""
        return {
            "username": self._mask(self.credentials.username),
            "password": "***" if self.credentials.password else None,
            "api_key": "***" if self.credentials.api_key else None,
            "certificate": "present" if self.credentials.certificate_pem else None,
            "base_url": self.credentials.base_url,
        }

    @staticmethod
    def _mask(value: Optional[str], visible: int = 4) -> Optional[str]:
        """Masque une valeur sensible (garde N caracteres visibles)."""
        if not value:
            return None
        if len(value) <= visible * 2:
            return "*" * len(value)
        return value[:visible] + "***" + value[-visible:]
