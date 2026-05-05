"""Simulateurs de plateformes d'achat public pour le MVP."""
import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class MockPlatformError(Exception):
    """Erreur simulée de plateforme."""
    pass


class MockSubmissionResult:
    """Résultat d'un dépôt simulé."""

    def __init__(
        self,
        success: bool,
        reference: Optional[str] = None,
        error: Optional[str] = None,
        latency_ms: int = 0,
    ):
        self.success = success
        self.reference = reference
        self.error = error
        self.latency_ms = latency_ms
        self.timestamp = datetime.now(timezone.utc)


class MockBOAMPPlatform:
    """Simulateur BOAMP — taux de succès 90%, latence 1-3s."""

    async def submit(self, dossier: dict) -> MockSubmissionResult:
        start = datetime.now(timezone.utc)
        await asyncio.sleep(random.uniform(1.0, 3.0))

        if random.random() < 0.1:
            return MockSubmissionResult(
                success=False,
                error="Erreur temporaire du service BOAMP — réessayer plus tard",
                latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
            )

        ref = f"BOAMP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        return MockSubmissionResult(
            success=True,
            reference=ref,
            latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
        )

    async def check_status(self, reference: str) -> dict:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        statuses = ["submitted", "under_review", "accepted", "rejected"]
        weights = [0.3, 0.4, 0.2, 0.1]
        status = random.choices(statuses, weights=weights)[0]
        return {
            "reference": reference,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


class MockJouePlatform:
    """Simulateur JOUE/TED — taux de succès 85%, latence 2-5s."""

    async def submit(self, dossier: dict) -> MockSubmissionResult:
        start = datetime.now(timezone.utc)
        await asyncio.sleep(random.uniform(2.0, 5.0))

        if random.random() < 0.15:
            return MockSubmissionResult(
                success=False,
                error="TED API rate limit exceeded — retry after 60s",
                latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
            )

        ref = f"TED-{random.randint(100000, 999999)}"
        return MockSubmissionResult(
            success=True,
            reference=ref,
            latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
        )

    async def check_status(self, reference: str) -> dict:
        await asyncio.sleep(random.uniform(1.0, 2.0))
        return {
            "reference": reference,
            "status": random.choice(["received", "processing", "published"]),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


class MockMarchePublicPlatform:
    """Simulateur MarchesPublics.ma — taux de succès 95%, latence 3-6s."""

    async def submit(self, dossier: dict) -> MockSubmissionResult:
        start = datetime.now(timezone.utc)
        await asyncio.sleep(random.uniform(3.0, 6.0))

        if random.random() < 0.05:
            return MockSubmissionResult(
                success=False,
                error="Session expirée — reconnecter",
                latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
            )

        ref = f"MA-{random.randint(10000, 99999)}-{datetime.now(timezone.utc).strftime('%Y')}"
        return MockSubmissionResult(
            success=True,
            reference=ref,
            latency_ms=int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
        )

    async def check_status(self, reference: str) -> dict:
        await asyncio.sleep(random.uniform(2.0, 4.0))
        return {
            "reference": reference,
            "status": random.choice(["en_attente", "reçu", "en_instruction", "attribué"]),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


PLATFORM_REGISTRY = {
    "boamp": MockBOAMPPlatform,
    "joue": MockJouePlatform,
    "marche_public": MockMarchePublicPlatform,
}
