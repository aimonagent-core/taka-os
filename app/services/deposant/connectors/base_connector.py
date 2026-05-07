"""Classe abstraite de base pour tous les connecteurs de depot generiques."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Any, Optional
import uuid


class ConnectorTestStatus(str, PyEnum):
    """Statut du dernier test de connexion."""
    OK = "ok"
    ERROR = "error"
    NEVER_TESTED = "never_tested"


@dataclass
class SubmissionResult:
    """Resultat d'une tentative de soumission via un connecteur generique."""
    status: str  # "submitted" | "mock_submitted" | "error" | "pending"
    external_id: Optional[str] = None
    platform: Optional[str] = None
    message: Optional[str] = None
    is_mock: bool = False
    receipt_url: Optional[str] = None
    raw_response: Optional[dict] = None
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BasePlatformConnector(ABC):
    """Classe de base pour tous les connecteurs de depot generiques.

    Sprint 12 Module 3 : connecteurs email, API, et mock.
    """

    def __init__(self, config: dict):
        self.config = config
        self.platform_name = self.__class__.__name__

    @abstractmethod
    async def test_connection(self) -> bool:
        """Verifie que les credentials / configuration fonctionnent."""
        pass

    @abstractmethod
    async def submit(
        self,
        ao_id: uuid.UUID,
        documents: list[dict],
        payload: dict,
    ) -> SubmissionResult:
        """Soumet un dossier de candidature.

        Args:
            ao_id: UUID de l'AO cible.
            documents: Liste de documents a joindre (dicts avec name, content_type, data/base64).
            payload: Donnees de soumission (reponse, infos candidat, etc.).
        """
        pass

    @abstractmethod
    async def get_status(self, external_id: str) -> dict:
        """Verifie le statut d'une soumission existante.

        Returns:
            Dict avec au moins 'status' et 'external_id'.
        """
        pass

    @abstractmethod
    async def download_receipt(self, external_id: str) -> Optional[bytes]:
        """Telecharge l'accuse de reception au format PDF ou autre.

        Returns:
            Contenu binaire du recu, ou None si non disponible.
        """
        pass

    def _mask(self, value: Optional[str], visible: int = 4) -> Optional[str]:
        """Masque une valeur sensible pour les logs."""
        if not value:
            return None
        if len(value) <= visible * 2:
            return "*" * len(value)
        return value[:visible] + "***" + value[-visible:]
