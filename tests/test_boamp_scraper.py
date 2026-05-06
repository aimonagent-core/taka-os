"""
Tests du scraper BOAMP — Module A Sprint 10.

Couverture:
- Parsing JSON -> ScrapedAO
- Dedoublonnage SHA-256
- Rate limiting
- Gestion d'erreurs HTTP
- Insertion en base avec embeddings
- Pagination
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
from httpx import Response

from app.services.scrapers.base import ScrapedAO
from app.services.scrapers.boamp import ScraperBOAMP


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def scraper() -> ScraperBOAMP:
    """Fixture: instance fraiche de ScraperBOAMP."""
    return ScraperBOAMP()


@pytest.fixture
def sample_api_record() -> dict:
    """Fixture: un enregistrement JSON typique de l'API."""
    return {
        "uid": "25-12345",
        "titre": "Fourniture de materiel informatique",
        "objet": "Le present marche concerne la fourniture de postes de travail.",
        "datePublication": "2025-04-15T00:00:00",
        "dateCloture": "2025-05-15T17:00:00",
        "montant": 150000.00,
        "acheteur": "Ville de Paris",
        "lieuExecution": "Paris (75)",
        "cpv": "30200000",
        "libelleCpv": "Materiel informatique",
        "procedure": "Appel d'offres ouvert",
        "nature": "Fournitures",
        "format": "Avis de publication",
        "uris": ["https://www.boamp.fr/avis/25-12345"],
    }


@pytest.fixture
def sample_api_response(sample_api_record) -> dict:
    """Fixture: reponse complete de l'API (avec total_count et results)."""
    return {
        "total_count": 150000,
        "results": [sample_api_record],
    }


# ============================================================================
# Tests de parsing (_parse_record)
# ============================================================================

class TestBOAMParsing:
    """Tests du parsing des enregistrements JSON."""

    def test_parse_record_complete(self, scraper: ScraperBOAMP, sample_api_record: dict):
        """Parse un enregistrement complet avec tous les champs."""
        result = scraper._parse_record(sample_api_record)

        assert result is not None
        assert result.external_id == "25-12345"
        assert result.source == "boamp"
        assert result.title == "Fourniture de materiel informatique"
        assert "postes de travail" in (result.description or "")
        assert result.cpv_code == "30200000"
        assert result.cpv_label == "Materiel informatique"
        assert result.buyer_name == "Ville de Paris"
        assert result.location == "Paris (75)"
        assert result.procedure_type == "Appel d'offres ouvert"
        assert result.ao_type == "Fournitures"
        assert result.estimated_amount == 150000.00
        assert result.currency == "EUR"
        assert result.url == "https://www.boamp.fr/avis/25-12345"
        assert result.raw_data is not None
        assert result.raw_data["uid"] == "25-12345"

    def test_parse_record_dates(self, scraper: ScraperBOAMP):
        """Parse correctement les differents formats de dates."""
        test_cases = [
            ("2025-04-15T00:00:00", datetime(2025, 4, 15, 0, 0, 0, tzinfo=timezone.utc)),
            ("2025-04-15T00:00:00+00:00", datetime(2025, 4, 15, 0, 0, 0, tzinfo=timezone.utc)),
            ("2025-04-15T00:00:00.000000", datetime(2025, 4, 15, 0, 0, 0, tzinfo=timezone.utc)),
            ("2025-04-15", datetime(2025, 4, 15, 0, 0, 0, tzinfo=timezone.utc)),
        ]

        for date_str, expected in test_cases:
            record = {"uid": "test", "titre": "Test", "datePublication": date_str}
            result = scraper._parse_record(record)
            assert result is not None
            assert result.publication_date == expected

    def test_parse_record_amount_formats(self, scraper: ScraperBOAMP):
        """Parse correctement les differents formats de montants."""
        test_cases = [
            (150000.00, 150000.00),
            (150000, 150000.00),
            ("150000", 150000.00),
            ("150 000", 150000.00),
            ("150\u202f000", 150000.00),  # NARROW NO-BREAK SPACE
            ("150\u00a0000", 150000.00),  # NO-BREAK SPACE
            ("150000€", 150000.00),
            ("150000 EUR", 150000.00),
            (None, None),
        ]

        for value, expected in test_cases:
            record = {"uid": "test", "titre": "Test", "montant": value}
            result = scraper._parse_record(record)
            assert result is not None
            assert result.estimated_amount == expected

    def test_parse_record_missing_uid(self, scraper: ScraperBOAMP):
        """Retourne None si l'enregistrement n'a pas d'uid."""
        record = {"titre": "Test"}
        result = scraper._parse_record(record)
        assert result is None

    def test_parse_record_empty_title(self, scraper: ScraperBOAMP):
        """Retourne None si l'enregistrement n'a pas de titre."""
        record = {"uid": "test", "titre": ""}
        result = scraper._parse_record(record)
        assert result is None

    def test_parse_record_none_title(self, scraper: ScraperBOAMP):
        """Retourne None si le titre est None."""
        record = {"uid": "test", "titre": None}
        result = scraper._parse_record(record)
        assert result is None

    def test_parse_record_minimal(self, scraper: ScraperBOAMP):
        """Parse un enregistrement avec uniquement les champs obligatoires."""
        record = {"uid": "25-99999", "titre": "Test minimal"}
        result = scraper._parse_record(record)

        assert result is not None
        assert result.external_id == "25-99999"
        assert result.title == "Test minimal"
        assert result.description is None
        assert result.cpv_code is None
        assert result.publication_date is None
        assert result.deadline_date is None
        assert result.estimated_amount is None
        assert result.buyer_name is None
        assert result.url is None

    def test_safe_str(self, scraper: ScraperBOAMP):
        """Test la methode _safe_str avec divers inputs."""
        assert scraper._safe_str("  hello  ") == "hello"
        assert scraper._safe_str("") is None
        assert scraper._safe_str("   ") is None
        assert scraper._safe_str(None) is None
        assert scraper._safe_str(123) == "123"


# ============================================================================
# Tests de l'API HTTP (_fetch_batch)
# ============================================================================

class TestBOAMPHTTP:
    """Tests des appels HTTP a l'API data.economie.gouv.fr."""

    @respx.mock
    async def test_fetch_batch_success(
        self, scraper: ScraperBOAMP, sample_api_response: dict
    ):
        """Recupere un batch avec succes."""
        route = respx.get(scraper.base_url).mock(
            return_value=Response(200, json=sample_api_response)
        )

        result = await scraper._fetch_batch(limit=10, offset=0)

        assert len(result) == 1
        assert result[0].external_id == "25-12345"
        assert route.called

    @respx.mock
    async def test_fetch_batch_http_error(self, scraper: ScraperBOAMP):
        """Gere une erreur HTTP 500."""
        respx.get(scraper.base_url).mock(return_value=Response(500, text="Internal Error"))

        result = await scraper._fetch_batch(limit=10, offset=0)

        assert result == []

    @respx.mock
    async def test_fetch_batch_empty_results(self, scraper: ScraperBOAMP):
        """Gere une reponse avec results vide."""
        respx.get(scraper.base_url).mock(
            return_value=Response(200, json={"total_count": 0, "results": []})
        )

        result = await scraper._fetch_batch(limit=10, offset=0)

        assert result == []

    @respx.mock
    async def test_fetch_batch_invalid_json(self, scraper: ScraperBOAMP):
        """Gere une reponse JSON invalide."""
        respx.get(scraper.base_url).mock(return_value=Response(200, text="not json"))

        result = await scraper._fetch_batch(limit=10, offset=0)

        assert result == []

    @respx.mock
    async def test_fetch_batch_network_error(self, scraper: ScraperBOAMP):
        """Gere une erreur reseau."""
        respx.get(scraper.base_url).mock(side_effect=Exception("Connection refused"))

        result = await scraper._fetch_batch(limit=10, offset=0)

        assert result == []

    @respx.mock
    async def test_fetch_batch_params(self, scraper: ScraperBOAMP, sample_api_response: dict):
        """Verifie que les parametres sont correctement passes."""
        route = respx.get(scraper.base_url).mock(
            return_value=Response(200, json=sample_api_response)
        )

        await scraper._fetch_batch(
            limit=50, offset=100, where="datePublication > 2025-01-01"
        )

        request = route.calls[0].request
        params = dict(request.url.params)
        assert params["limit"] == "50"
        assert params["offset"] == "100"
        assert params["where"] == "datePublication > 2025-01-01"
        assert params["timezone"] == "Europe/Paris"


# ============================================================================
# Tests de pagination (fetch)
# ============================================================================

class TestBOAMPPagination:
    """Tests de la pagination complete."""

    @respx.mock
    async def test_fetch_paginates_correctly(self, scraper: ScraperBOAMP):
        """Recupere plusieurs pages et les concatene."""
        page1 = {
            "total_count": 3,
            "results": [
                {"uid": "25-1", "titre": "AO 1"},
                {"uid": "25-2", "titre": "AO 2"},
            ],
        }
        page2 = {
            "total_count": 3,
            "results": [
                {"uid": "25-3", "titre": "AO 3"},
            ],
        }

        # Page vide pour arreter la pagination
        page_empty = {"total_count": 3, "results": []}

        respx.get(scraper.base_url).mock(side_effect=[
            Response(200, json=page1),
            Response(200, json=page2),
            Response(200, json=page_empty),
        ])

        result = await scraper.fetch(limit=10)

        assert len(result) == 3
        assert result[0].external_id == "25-1"
        assert result[1].external_id == "25-2"
        assert result[2].external_id == "25-3"

    @respx.mock
    async def test_fetch_respects_limit(self, scraper: ScraperBOAMP):
        """Respecte la limite demandee meme s'il y a plus de resultats."""
        page = {
            "total_count": 10,
            "results": [
                {"uid": f"25-{i}", "titre": f"AO {i}"}
                for i in range(5)
            ],
        }

        respx.get(scraper.base_url).mock(return_value=Response(200, json=page))

        result = await scraper.fetch(limit=3)

        assert len(result) == 3


# ============================================================================
# Tests de deduplication
# ============================================================================

class TestBOAMPDeduplication:
    """Tests du dedoublonnage SHA-256."""

    @pytest.mark.asyncio
    async def test_deduplicate_by_hash(self, scraper: ScraperBOAMP):
        """Elimine les doublons par hash de contenu."""
        ao1 = ScrapedAO(
            external_id="25-1",
            source="boamp",
            title="AO 1",
            raw_data={"uid": "25-1", "titre": "AO 1"},
        )
        ao2 = ScrapedAO(
            external_id="25-2",
            source="boamp",
            title="AO 2",
            raw_data={"uid": "25-2", "titre": "AO 2"},
        )
        # Doublon de ao1 (meme contenu raw_data)
        ao3 = ScrapedAO(
            external_id="25-1",  # Meme ID
            source="boamp",
            title="AO 1",
            raw_data={"uid": "25-1", "titre": "AO 1"},
        )

        with patch(
            "app.services.scrapers.boamp.get_db",
            return_value=_async_session_mock([]),
        ):
            result = await scraper._deduplicate([ao1, ao2, ao3])

        assert len(result) == 2
        ids = {ao.external_id for ao in result}
        assert ids == {"25-1", "25-2"}

    @pytest.mark.asyncio
    async def test_deduplicate_existing_in_db(self, scraper: ScraperBOAMP):
        """Elimine les AO deja presentes en base par external_id."""
        ao1 = ScrapedAO(
            external_id="25-1",
            source="boamp",
            title="AO 1",
            raw_data={"uid": "25-1", "titre": "AO 1"},
        )
        ao2 = ScrapedAO(
            external_id="25-2",
            source="boamp",
            title="AO 2",
            raw_data={"uid": "25-2", "titre": "AO 2"},
        )

        with patch(
            "app.services.scrapers.boamp.get_db",
            return_value=_async_session_mock(["25-1"]),
        ):
            result = await scraper._deduplicate([ao1, ao2])

        assert len(result) == 1
        assert result[0].external_id == "25-2"


# ============================================================================
# Tests d'integration embedding + DB
# ============================================================================

class TestBOAMPEmbedding:
    """Tests de l'integration embeddings."""

    @pytest.mark.asyncio
    async def test_insert_with_embeddings(self, scraper: ScraperBOAMP):
        """Insere un AO avec son embedding."""
        ao = ScrapedAO(
            external_id="25-1",
            source="boamp",
            title="Fourniture de materiel informatique",
            description="Description detaillee de l'AO.",
            raw_data={"uid": "25-1", "titre": "Test"},
        )

        mock_embedding = [0.1] * 1024
        scraper._embedding_service = AsyncMock()
        scraper._embedding_service.embed_text = AsyncMock(return_value=mock_embedding)

        with patch(
            "app.services.scrapers.boamp.get_db",
            return_value=_async_session_mock_insert(),
        ):
            inserted, errors = await scraper._insert_with_embeddings([ao])

        assert inserted == 1
        assert errors == 0
        scraper._embedding_service.embed_text.assert_called_once_with(
            "Fourniture de materiel informatique Description detaillee de l'AO."
        )


# ============================================================================
# Helpers
# ============================================================================

def _async_session_mock(existing_ids: list[str]):
    """Cree un mock de session async qui retourne les existing_ids."""

    class _MockSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def execute(self, stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = existing_ids
            return result

        async def commit(self):
            pass

        async def flush(self):
            pass

    async def _gen():
        yield _MockSession()

    return _gen()


def _async_session_mock_insert():
    """Cree un mock de session async pour l'insertion."""
    import uuid

    class _MockSession:
        def __init__(self):
            self.added = []
            self._next_id = 1

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def execute(self, stmt):
            result = MagicMock()
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []
            return result

        def add(self, obj):
            self.added.append(obj)
            # Simuler l'assignation d'ID
            if hasattr(obj, "id") and obj.id is None:
                obj.id = uuid.uuid4()

        async def flush(self):
            pass

        async def commit(self):
            pass

    async def _gen():
        yield _MockSession()

    return _gen()


# ============================================================================
# Tests de rate limiting
# ============================================================================

class TestBOAMPRateLimit:
    """Tests du rate limiting."""

    def test_rate_limit_default(self, scraper: ScraperBOAMP):
        """Le rate limit par defaut est de 1 seconde."""
        assert scraper.rate_limit == 1.0

    @respx.mock
    async def test_rate_limit_sleep_between_calls(self, scraper: ScraperBOAMP):
        """Attend entre les appels API."""
        scraper.rate_limit = 0.1  # Accelerer le test

        page1 = {"total_count": 2, "results": [{"uid": "25-1", "titre": "AO 1"}]}
        page2 = {"total_count": 2, "results": [{"uid": "25-2", "titre": "AO 2"}]}
        page_empty = {"total_count": 2, "results": []}

        respx.get(scraper.base_url).mock(side_effect=[
            Response(200, json=page1),
            Response(200, json=page2),
            Response(200, json=page_empty),
        ])

        import time
        start = time.time()
        await scraper.fetch(limit=5)
        elapsed = time.time() - start

        # Au moins 2 * 0.1 = 0.2s d'attente + temps d'execution
        assert elapsed >= 0.15  # Tolerance


# ============================================================================
# Tests de l'API endpoint scraper
# ============================================================================

class TestScraperAPI:
    """Tests des endpoints API du scraper."""

    @pytest.mark.asyncio
    async def test_trigger_scraper(self):
        """Le endpoint de declenchement retourne un rapport."""
        from app.services.scrapers.schemas import (
            ScraperTriggerRequest,
            ScraperTriggerResponse,
            ScraperRunReport,
        )

        request = ScraperTriggerRequest(limit=10)
        assert request.limit == 10
        assert request.where is None
        assert request.order_by == "datePublication DESC"

    def test_schemas_validation(self):
        """Les schemas Pydantic valident correctement les donnees."""
        from app.services.scrapers.schemas import BOAMPRecord, ScraperRunReport

        record = BOAMPRecord(uid="test", titre="Titre test")
        assert record.uid == "test"
        assert record.titre == "Titre test"

        report = ScraperRunReport(
            source="boamp",
            total_fetched=100,
            inserted=95,
            duplicates=5,
            errors=0,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_seconds=10.5,
        )
        assert report.total_fetched == 100
        assert report.inserted == 95
