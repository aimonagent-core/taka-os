"""
Tests du monitoring et health checks — Module C Sprint 10.

Couverture:
- Health check general
- Health DB (connexion)
- Health scrapers (etat)
- Historique des runs
- Modele ScraperRun
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.audit import ScraperRun, SubmissionLog


# ============================================================================
# Tests ScraperRun model
# ============================================================================

class TestScraperRunModel:
    """Tests du modele ScraperRun."""

    def test_scraper_run_creation(self):
        """Cree un ScraperRun avec les valeurs par defaut."""
        from datetime import datetime, timezone
        run = ScraperRun(
            source="boamp",
            status="ok",
            count=100,
            inserted=95,
            duplicates=5,
            errors=0,
            started_at=datetime.now(timezone.utc),
        )

        assert run.source == "boamp"
        assert run.status == "ok"
        assert run.count == 100
        assert run.inserted == 95
        assert run.duplicates == 5
        assert run.errors == 0
        assert run.started_at is not None
        assert run.finished_at is None
        assert run.error_message is None
        assert run.filter_where is None

    def test_scraper_run_duration(self):
        """Calcule la duree correctement."""
        start = datetime(2025, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 4, 1, 10, 0, 30, tzinfo=timezone.utc)

        run = ScraperRun(
            source="boamp",
            status="ok",
            started_at=start,
            finished_at=end,
        )

        assert run.duration_seconds == 30.0

    def test_scraper_run_duration_none(self):
        """Retourne None si pas de finished_at."""
        run = ScraperRun(
            source="boamp",
            status="running",
            started_at=datetime.now(timezone.utc),
        )

        assert run.duration_seconds is None

    def test_scraper_run_repr(self):
        """Le repr est informatif."""
        run = ScraperRun(id=1, source="boamp", status="ok", count=10)
        repr_str = repr(run)

        assert "ScraperRun" in repr_str
        assert "boamp" in repr_str
        assert "ok" in repr_str

    def test_scraper_run_error_status(self):
        """Peut avoir un statut 'error'."""
        run = ScraperRun(
            source="boamp",
            status="error",
            count=0,
            error_message="Timeout API",
        )

        assert run.status == "error"
        assert run.error_message == "Timeout API"

    def test_scraper_run_partial_status(self):
        """Peut avoir un statut 'partial'."""
        run = ScraperRun(
            source="boamp",
            status="partial",
            count=100,
            inserted=80,
            errors=20,
        )

        assert run.status == "partial"
        assert run.errors == 20


# ============================================================================
# Tests SubmissionLog model
# ============================================================================

class TestSubmissionLogModel:
    """Tests du modele SubmissionLog."""

    def test_submission_log_creation(self):
        """Cree un SubmissionLog mock."""
        import uuid

        log = SubmissionLog(
            ao_id=uuid.uuid4(),
            platform="marches_publics_gouv",
            status="mock_submitted",
            is_mock=True,
            warning_message="Simulation",
            submitted_at=datetime.now(timezone.utc),
        )

        assert log.platform == "marches_publics_gouv"
        assert log.status == "mock_submitted"
        assert log.is_mock is True
        assert log.warning_message == "Simulation"
        assert log.submitted_at is not None

    def test_submission_log_real(self):
        """Cree un SubmissionLog reel."""
        import uuid

        log = SubmissionLog(
            ao_id=uuid.uuid4(),
            platform="marches_publics_gouv",
            status="submitted",
            is_mock=False,
            external_submission_id="EXT-12345",
        )

        assert log.is_mock is False
        assert log.external_submission_id == "EXT-12345"
        assert log.warning_message is None

    def test_submission_log_error(self):
        """Cree un SubmissionLog avec erreur."""
        import uuid

        log = SubmissionLog(
            ao_id=uuid.uuid4(),
            platform="aws",
            status="error",
            is_mock=False,
            error_message="Erreur reseau",
        )

        assert log.status == "error"
        assert log.error_message == "Erreur reseau"

    def test_submission_log_repr(self):
        """Le repr est informatif."""
        import uuid

        log = SubmissionLog(
            id=1, ao_id=uuid.uuid4(), platform="test", status="mock_submitted", is_mock=True
        )
        repr_str = repr(log)

        assert "SubmissionLog" in repr_str
        assert "mock_submitted" in repr_str


# ============================================================================
# Tests endpoint health scrapers
# ============================================================================

class TestHealthScrapers:
    """Tests du endpoint /health/scrapers."""

    @pytest.mark.asyncio
    async def test_health_scrapers_never_run(self):
        """Retourne 'never_run' si le scraper n'a jamais ete execute."""
        from app.api.v1.health import health_scrapers

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await health_scrapers(session=mock_session, _=MagicMock())

        assert result["status"] == "ok"
        assert len(result["scrapers"]) >= 1

        boamp = [s for s in result["scrapers"] if s["source"] == "boamp"][0]
        assert boamp["last_run_status"] == "never_run"
        assert boamp["is_healthy"] is True
        assert boamp["last_run_at"] is None

    @pytest.mark.asyncio
    async def test_health_scrapers_last_run_ok(self):
        """Retourne les infos du dernier run reussi."""
        from app.api.v1.health import health_scrapers

        mock_run = MagicMock()
        mock_run.source = "boamp"
        mock_run.status = "ok"
        mock_run.count = 100
        mock_run.started_at = datetime(2025, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_run.finished_at = datetime(2025, 4, 1, 10, 0, 30, tzinfo=timezone.utc)
        mock_run.error_message = None

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_run
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await health_scrapers(session=mock_session, _=MagicMock())

        boamp = [s for s in result["scrapers"] if s["source"] == "boamp"][0]
        assert boamp["last_run_status"] == "ok"
        assert boamp["is_healthy"] is True
        assert boamp["last_run_count"] == 100
        assert boamp["last_run_at"] is not None

    @pytest.mark.asyncio
    async def test_health_scrapers_last_run_error(self):
        """Retourne is_healthy=False si le dernier run a echoue."""
        from app.api.v1.health import health_scrapers

        mock_run = MagicMock()
        mock_run.source = "boamp"
        mock_run.status = "error"
        mock_run.count = 0
        mock_run.started_at = datetime(2025, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_run.finished_at = None
        mock_run.error_message = "Timeout API"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_run
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await health_scrapers(session=mock_session, _=MagicMock())

        boamp = [s for s in result["scrapers"] if s["source"] == "boamp"][0]
        assert boamp["last_run_status"] == "error"
        assert boamp["is_healthy"] is False
        assert boamp["error_message"] == "Timeout API"


# ============================================================================
# Tests historique scraper
# ============================================================================

class TestScraperHistory:
    """Tests du endpoint /health/scrapers/{source}/history."""

    @pytest.mark.asyncio
    async def test_history_returns_list(self):
        """Retourne l'historique des runs."""
        from app.api.v1.health import scraper_history

        mock_run1 = MagicMock()
        mock_run1.id = 1
        mock_run1.source = "boamp"
        mock_run1.status = "ok"
        mock_run1.count = 100
        mock_run1.started_at = datetime(2025, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_run1.finished_at = datetime(2025, 4, 1, 10, 0, 30, tzinfo=timezone.utc)
        mock_run1.error_message = None

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_run1]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await scraper_history(
            source="boamp", limit=10, session=mock_session, _=MagicMock()
        )

        assert result["source"] == "boamp"
        assert len(result["history"]) == 1
        assert result["total"] == 1

        entry = result["history"][0]
        assert entry["id"] == 1
        assert entry["status"] == "ok"
        assert entry["count"] == 100
        assert entry["duration_seconds"] == 30.0

    @pytest.mark.asyncio
    async def test_history_empty(self):
        """Retourne une liste vide si pas d'historique."""
        from app.api.v1.health import scraper_history

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await scraper_history(
            source="boamp", limit=10, session=mock_session, _=MagicMock()
        )

        assert result["source"] == "boamp"
        assert result["history"] == []
        assert result["total"] == 0
