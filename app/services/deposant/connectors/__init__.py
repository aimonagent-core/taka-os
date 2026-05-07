"""Registre des connecteurs de depot generiques (Sprint 12 Module 3)."""

from app.services.deposant.connectors.base_connector import (
    BasePlatformConnector,
    ConnectorTestStatus,
    SubmissionResult,
)
from app.services.deposant.connectors.mock_connector import MockConnector
from app.services.deposant.connectors.email_connector import EmailDirectConnector
from app.services.deposant.connectors.api_connector import GenericAPIConnector

__all__ = [
    "BasePlatformConnector",
    "ConnectorTestStatus",
    "SubmissionResult",
    "MockConnector",
    "EmailDirectConnector",
    "GenericAPIConnector",
]
