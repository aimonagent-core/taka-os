"""Wrappers pour les mocks existants — adaptent l'interface BaseConnector."""

from datetime import datetime, timezone
from typing import Optional

from app.agents.deposant.connectors.base import (
    BaseConnector,
    PlatformCredentials,
    SubmissionResult,
    SubmissionResultStatus,
)
from app.agents.deposant.mock_platforms import (
    MockBOAMPPlatform,
    MockJouePlatform,
    MockMarchePublicPlatform,
)


class MockBOAMPConnector(BaseConnector):
    """Wrapper Mock BOAMP compatible BaseConnector."""

    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self._mock = MockBOAMPPlatform()

    async def authenticate(self) -> bool:
        return True

    async def submit(self, ao_reference: str, response_text: str, documents: list[dict]) -> SubmissionResult:
        dossier = {"ao_reference": ao_reference, "response_text": response_text, "documents": len(documents)}
        result = await self._mock.submit(dossier)
        return SubmissionResult(
            status=SubmissionResultStatus.SUCCESS if result.success else SubmissionResultStatus.FAILED,
            platform_reference=result.reference,
            message=result.error or f"Mock BOAMP — reference: {result.reference}",
            platform_submitted_at=result.timestamp,
        )

    async def check_status(self, platform_reference: str) -> SubmissionResult:
        data = await self._mock.check_status(platform_reference)
        return SubmissionResult(
            status=SubmissionResultStatus.PENDING,
            platform_reference=platform_reference,
            message=f"Mock statut: {data.get('status')}",
        )

    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        return None

    async def upload_document(self, platform_reference: str, document: dict) -> dict:
        return {"uploaded": True, "document_id": "mock-doc-id"}


class MockJoueConnector(BaseConnector):
    """Wrapper Mock JOUE/TED compatible BaseConnector."""

    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self._mock = MockJouePlatform()

    async def authenticate(self) -> bool:
        return True

    async def submit(self, ao_reference: str, response_text: str, documents: list[dict]) -> SubmissionResult:
        dossier = {"ao_reference": ao_reference, "response_text": response_text, "documents": len(documents)}
        result = await self._mock.submit(dossier)
        return SubmissionResult(
            status=SubmissionResultStatus.SUCCESS if result.success else SubmissionResultStatus.FAILED,
            platform_reference=result.reference,
            message=result.error or f"Mock JOUE — reference: {result.reference}",
            platform_submitted_at=result.timestamp,
        )

    async def check_status(self, platform_reference: str) -> SubmissionResult:
        data = await self._mock.check_status(platform_reference)
        return SubmissionResult(
            status=SubmissionResultStatus.PENDING,
            platform_reference=platform_reference,
            message=f"Mock statut: {data.get('status')}",
        )

    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        return None

    async def upload_document(self, platform_reference: str, document: dict) -> dict:
        return {"uploaded": True, "document_id": "mock-doc-id"}


class MockMarocConnector(BaseConnector):
    """Wrapper Mock Maroc compatible BaseConnector."""

    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self._mock = MockMarchePublicPlatform()

    async def authenticate(self) -> bool:
        return True

    async def submit(self, ao_reference: str, response_text: str, documents: list[dict]) -> SubmissionResult:
        dossier = {"ao_reference": ao_reference, "response_text": response_text, "documents": len(documents)}
        result = await self._mock.submit(dossier)
        return SubmissionResult(
            status=SubmissionResultStatus.SUCCESS if result.success else SubmissionResultStatus.FAILED,
            platform_reference=result.reference,
            message=result.error or f"Mock Maroc — reference: {result.reference}",
            platform_submitted_at=result.timestamp,
        )

    async def check_status(self, platform_reference: str) -> SubmissionResult:
        data = await self._mock.check_status(platform_reference)
        return SubmissionResult(
            status=SubmissionResultStatus.PENDING,
            platform_reference=platform_reference,
            message=f"Mock statut: {data.get('status')}",
        )

    async def get_receipt(self, platform_reference: str) -> Optional[bytes]:
        return None

    async def upload_document(self, platform_reference: str, document: dict) -> dict:
        return {"uploaded": True, "document_id": "mock-doc-id"}
