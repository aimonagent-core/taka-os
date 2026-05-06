"""
CLI — Commande pour scraper le BOAMP.

Usage:
    python -m app.cli.scrape_boamp --limit 100
    python -m app.cli.scrape_boamp --limit 50 --where "datePublication > 2025-01-01"
    python -m app.cli.scrape_boamp --limit 200 --order-by "datePublication DESC"
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone

# Configuration du logging AVANT les imports internes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def run_scraper(
    limit: int,
    where: str | None,
    order_by: str,
    verbose: bool,
) -> int:
    """
    Execute le scraper BOAMP et affiche les resultats.

    Returns:
        Code de sortie (0 = succes, 1 = erreur).
    """
    from app.services.scrapers.boamp import ScraperBOAMP

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    started_at = datetime.now(timezone.utc)
    logger.info("=== BOAMP Scraper CLI — Demarrage ===")
    logger.info(f"Limit: {limit}")
    logger.info(f"Where: {where}")
    logger.info(f"Order by: {order_by}")

    try:
        scraper = ScraperBOAMP()
        report = await scraper.fetch_and_store(
            limit=limit,
            where=where,
            order_by=order_by,
        )

        finished_at = datetime.now(timezone.utc)
        duration = (finished_at - started_at).total_seconds()

        logger.info("=== BOAMP Scraper CLI — Termine ===")
        logger.info(f"Duree: {duration:.2f}s")
        logger.info(f"Recuperes: {report['total_fetched']}")
        logger.info(f"Inseres: {report['inserted']}")
        logger.info(f"Doublons: {report['duplicates']}")
        logger.info(f"Erreurs: {report['errors']}")

        # Resume structure (parsable par un orchestrateur)
        print("\n--- RAPPORT JSON ---")
        import json

        print(
            json.dumps(
                {
                    "success": True,
                    "source": "boamp",
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                    "duration_seconds": round(duration, 2),
                    "total_fetched": report["total_fetched"],
                    "inserted": report["inserted"],
                    "duplicates": report["duplicates"],
                    "errors": report["errors"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )

        return 0 if report["errors"] == 0 else 1

    except KeyboardInterrupt:
        logger.warning("Interrompu par l'utilisateur (Ctrl+C)")
        return 130
    except Exception as exc:
        logger.exception(f"Erreur fatale: {exc}")
        return 1


def main() -> None:
    """Point d'entree CLI."""
    parser = argparse.ArgumentParser(
        description="Scraper BOAMP — Extrait les annonces du Bulletin Officiel des Marches Publics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python -m app.cli.scrape_boamp --limit 100
  python -m app.cli.scrape_boamp --limit 50 --where "datePublication > 2025-01-01"
  python -m app.cli.scrape_boamp --limit 200 --verbose
        """,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Nombre maximum d'annonces a recuperer (defaut: 100, max: 1000)",
    )
    parser.add_argument(
        "--where",
        type=str,
        default=None,
        help="Filtre WHERE SQL-like (ex: 'datePublication > 2025-01-01')",
    )
    parser.add_argument(
        "--order-by",
        type=str,
        default="datePublication DESC",
        help="Tri des resultats (defaut: 'datePublication DESC')",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mode verbeux (DEBUG)",
    )

    args = parser.parse_args()

    # Validation
    if args.limit < 1 or args.limit > 1000:
        print("Erreur: --limit doit etre entre 1 et 1000", file=sys.stderr)
        sys.exit(1)

    exit_code = asyncio.run(
        run_scraper(
            limit=args.limit,
            where=args.where,
            order_by=args.order_by,
            verbose=args.verbose,
        )
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
