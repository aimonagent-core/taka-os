"""Connecteur mock — simulation locale sans depot reel."""

import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from app.services.deposant.connectors.base_connector import (
    BasePlatformConnector,
    SubmissionResult,
)

logger = logging.getLogger(__name__)


class MockConnector(BasePlatformConnector):
    """Fallback mock explicite pour tests et demos.

    Conformement a l'Article L121-1 du Code de la consommation,
    toute soumission simulee DOIT etre signalee.
    """

    async def test_connection(self) -> bool:
        return True

    async def submit(
        self,
        ao_id: uuid.UUID,
        documents: list[dict],
        payload: dict,
    ) -> SubmissionResult:
        external_id = f"MOCK-{ao_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        logger.warning(
            "[MockConnector] Soumission SIMULEE pour AO %s — aucun depot reel. "
            "Article L121-1 Code conso.",
            ao_id,
        )
        return SubmissionResult(
            status="mock_submitted",
            external_id=external_id,
            platform="mock",
            message=(
                "Ce depot est une SIMULATION. Aucun dossier n'a ete soumis "
                "sur la plateforme reelle. Les donnees ont ete enregistrees "
                "localement uniquement."
            ),
            is_mock=True,
            raw_response={
                "is_mock": True,
                "warning": (
                    "[ATTENTION] Cette soumission est une simulation locale. "
                    "Aucun dossier n'a ete transmis a la plateforme reelle. "
                    "Article L121-1 Code de la consommation — obligation d'information."
                ),
                "requires_action": "Configurer un connecteur dans Parametres > Plateformes",
            },
        )

    async def get_status(self, external_id: str) -> dict:
        return {
            "status": "mock_submitted",
            "external_id": external_id,
            "is_mock": True,
        }

    async def download_receipt(self, external_id: str) -> Optional[bytes]:
        return b"%PDF-1.4 MOCK RECEIPT\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT /F1 12 Tf 100 700 Td (Recu Mock) Tj ET\nendstream\nendobj\n5 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000266 00000 n\n0000000360 00000 n\ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n439\n%%EOF\n"
