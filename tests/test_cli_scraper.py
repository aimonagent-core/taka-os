"""
Tests de la CLI scrape_boamp — Module C Sprint 10.

Couverture:
- Parsing des arguments
- Execution avec differents parametres
- Gestion des erreurs
- Sortie JSON du rapport
"""

import asyncio
import sys
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.cli.scrape_boamp import main, run_scraper


# ============================================================================
# Tests de run_scraper
# ============================================================================

class TestRunScraper:
    """Tests de la fonction principale run_scraper."""

    @pytest.mark.asyncio
    async def test_run_scraper_success(self):
        """Execute le scraper avec succes."""
        mock_report = {
            "total_fetched": 10,
            "inserted": 10,
            "duplicates": 0,
            "errors": 0,
        }

        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(return_value=mock_report)
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=10, where=None, order_by="datePublication DESC", verbose=False
            )

        assert exit_code == 0
        mock_scraper.fetch_and_store.assert_called_once_with(
            limit=10, where=None, order_by="datePublication DESC"
        )

    @pytest.mark.asyncio
    async def test_run_scraper_with_where(self):
        """Execute avec un filtre WHERE."""
        mock_report = {
            "total_fetched": 5,
            "inserted": 5,
            "duplicates": 0,
            "errors": 0,
        }

        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(return_value=mock_report)
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=5,
                where="datePublication > 2025-01-01",
                order_by="datePublication DESC",
                verbose=False,
            )

        assert exit_code == 0
        mock_scraper.fetch_and_store.assert_called_once_with(
            limit=5,
            where="datePublication > 2025-01-01",
            order_by="datePublication DESC",
        )

    @pytest.mark.asyncio
    async def test_run_scraper_with_errors(self):
        """Retourne code 1 si des erreurs sont survenues."""
        mock_report = {
            "total_fetched": 10,
            "inserted": 8,
            "duplicates": 0,
            "errors": 2,
        }

        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(return_value=mock_report)
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=10, where=None, order_by="datePublication DESC", verbose=False
            )

        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_run_scraper_empty(self):
        """Retourne code 0 si aucune annonce."""
        mock_report = {
            "total_fetched": 0,
            "inserted": 0,
            "duplicates": 0,
            "errors": 0,
        }

        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(return_value=mock_report)
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=10, where=None, order_by="datePublication DESC", verbose=False
            )

        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_run_scraper_exception(self):
        """Retourne code 1 en cas d'exception."""
        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(
                side_effect=Exception("Fatal error")
            )
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=10, where=None, order_by="datePublication DESC", verbose=False
            )

        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_run_scraper_keyboard_interrupt(self):
        """Retourne code 130 sur Ctrl+C."""
        with patch(
            "app.services.scrapers.boamp.ScraperBOAMP"
        ) as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_and_store = AsyncMock(
                side_effect=KeyboardInterrupt()
            )
            mock_scraper_class.return_value = mock_scraper

            exit_code = await run_scraper(
                limit=10, where=None, order_by="datePublication DESC", verbose=False
            )

        assert exit_code == 130


# ============================================================================
# Tests de main() — parsing arguments
# ============================================================================

class TestCLIMain:
    """Tests du parsing des arguments CLI."""

    def test_main_parsing_limit(self):
        """Parse l'argument --limit."""
        with patch.object(sys, "argv", ["scrape_boamp", "--limit", "50"]):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                try:
                    main()
                except SystemExit as exc:
                    assert exc.code == 0

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args.kwargs
                assert call_kwargs["limit"] == 50

    def test_main_parsing_where(self):
        """Parse l'argument --where."""
        with patch.object(
            sys, "argv", ["scrape_boamp", "--where", "datePublication > 2025-01-01"]
        ):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                try:
                    main()
                except SystemExit:
                    pass

                call_kwargs = mock_run.call_args.kwargs
                assert call_kwargs["where"] == "datePublication > 2025-01-01"

    def test_main_parsing_order_by(self):
        """Parse l'argument --order-by."""
        with patch.object(
            sys, "argv", ["scrape_boamp", "--order-by", "montant DESC"]
        ):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                try:
                    main()
                except SystemExit:
                    pass

                call_kwargs = mock_run.call_args.kwargs
                assert call_kwargs["order_by"] == "montant DESC"

    def test_main_parsing_verbose(self):
        """Parse l'argument --verbose."""
        with patch.object(sys, "argv", ["scrape_boamp", "--verbose"]):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                try:
                    main()
                except SystemExit:
                    pass

                call_kwargs = mock_run.call_args.kwargs
                assert call_kwargs["verbose"] is True

    def test_main_default_values(self):
        """Les valeurs par defaut sont correctes."""
        with patch.object(sys, "argv", ["scrape_boamp"]):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                try:
                    main()
                except SystemExit:
                    pass

                call_kwargs = mock_run.call_args.kwargs
                assert call_kwargs["limit"] == 100
                assert call_kwargs["where"] is None
                assert call_kwargs["order_by"] == "dateparution DESC"
                assert call_kwargs["verbose"] is False

    def test_main_invalid_limit_low(self):
        """Refuse une limite < 1."""
        with patch.object(sys, "argv", ["scrape_boamp", "--limit", "0"]):
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
                assert "1 et 1000" in mock_stderr.getvalue()

    def test_main_invalid_limit_high(self):
        """Refuse une limite > 1000."""
        with patch.object(sys, "argv", ["scrape_boamp", "--limit", "1001"]):
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
                assert "1 et 1000" in mock_stderr.getvalue()

    def test_main_exit_code_success(self):
        """Sort avec code 0 en cas de succes."""
        with patch.object(sys, "argv", ["scrape_boamp"]):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 0
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_exit_code_error(self):
        """Sort avec code 1 en cas d'erreur."""
        with patch.object(sys, "argv", ["scrape_boamp"]):
            with patch(
                "app.cli.scrape_boamp.run_scraper", new_callable=AsyncMock
            ) as mock_run:
                mock_run.return_value = 1
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
