"""
Scraper BOAMP reel — API DILA / OpenDataSoft (boamp-datadila.opendatasoft.com)
Extrait les marches publics francais via la nouvelle API officielle ouverte.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.database import get_db
from app.models.ao_s2 import AO, AOChunk, Source
from app.services.llm.embeddings import EmbeddingService
from app.services.scrapers.base import BaseScraperV2, ScrapedAO

logger = logging.getLogger(__name__)


def _is_retryable_http_error(exc: BaseException) -> bool:
    """Détermine si une exception HTTP mérite un retry exponentiel."""
    if isinstance(exc, httpx.HTTPStatusError):
        # Retry uniquement sur 5xx et timeout gateway
        return exc.response.status_code >= 500
    if isinstance(exc, httpx.RequestError):
        # Retry sur timeout, connexion perdue, DNS, etc.
        return True
    return False


class ScraperBOAMP(BaseScraperV2):
    """
    Scraper reel pour le BOAMP (Bulletin Officiel des Annonces des Marches Publics).
    Utilise l'API boamp-datadila.opendatasoft.com (nouvelle API DILA).
    """

    source_name: str = "boamp"
    base_url: str = (
        "https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
        "boamp/records"
    )
    rate_limit: float = 1.0  # 1 requete par seconde max

    def __init__(self) -> None:
        super().__init__()
        self._embedding_service: Optional[EmbeddingService] = None

    @property
    def embedding_service(self) -> EmbeddingService:
        """Lazy init de l'EmbeddingService."""
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    async def fetch(
        self,
        limit: int = 100,
        where: Optional[str] = None,
        order_by: str = "dateparution DESC",
    ) -> list[ScrapedAO]:
        """
        Recupere les annonces BOAMP depuis l'API DILA / OpenDataSoft.

        Args:
            limit: Nombre maximum d'annonces a recuperer (max 100 par appel).
            where: Clause WHERE pour filtrer (ex: "dateparution > 2024-01-01").
            order_by: Tri des resultats.

        Returns:
            Liste de ScrapedAO prets a etre inseres en base.
        """
        all_aos: list[ScrapedAO] = []
        offset = 0
        batch_size = min(limit, 100)  # API limite a 100 par requete

        logger.info(
            f"[BOAMP] Debut extraction — limit={limit}, where={where}, order_by={order_by}"
        )

        while len(all_aos) < limit:
            batch = await self._fetch_batch(
                limit=batch_size,
                offset=offset,
                where=where,
                order_by=order_by,
            )

            if not batch:
                logger.info(f"[BOAMP] Plus de resultats a offset={offset}")
                break

            all_aos.extend(batch)
            offset += batch_size

            # Rate limiting — attente entre les appels
            if len(all_aos) < limit:
                await asyncio.sleep(self.rate_limit)

        logger.info(f"[BOAMP] Extraction terminee — {len(all_aos)} annonces recuperees")
        return all_aos[:limit]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_is_retryable_http_error),
        reraise=True,
    )
    async def _http_get(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any],
    ) -> httpx.Response:
        """Requete HTTP GET avec retry exponentiel sur 5xx/timeout."""
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response

    async def _fetch_batch(
        self,
        limit: int,
        offset: int,
        where: Optional[str] = None,
        order_by: str = "dateparution DESC",
    ) -> list[ScrapedAO]:
        """
        Recupere un batch d'annonces depuis l'API.

        Returns:
            Liste de ScrapedAO pour ce batch.
        """
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "timezone": "Europe/Paris",
        }
        if where:
            params["where"] = where

        logger.debug(f"[BOAMP] Appel API — offset={offset}, limit={limit}")

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await self._http_get(client, self.base_url, params)
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"[BOAMP] Erreur HTTP {exc.response.status_code} — {exc.response.text[:500]}"
            )
            return []
        except httpx.RequestError as exc:
            logger.error(f"[BOAMP] Erreur reseau — {type(exc).__name__}: {exc}")
            return []

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            logger.error(f"[BOAMP] JSON invalide — {exc}")
            return []

        results = data.get("results", [])
        if not results:
            return []

        scraped_aos: list[ScrapedAO] = []
        for record in results:
            try:
                ao = self._parse_record(record)
                if ao:
                    scraped_aos.append(ao)
            except Exception as exc:
                uid = record.get("idweb", "UNKNOWN")
                logger.warning(f"[BOAMP] Echec parsing record {uid} — {exc}")
                continue

        logger.debug(f"[BOAMP] Batch recupere — {len(scraped_aos)} annonces")
        return scraped_aos

    def _parse_json_str(self, value: Any) -> dict[str, Any]:
        """Parse une chaine JSON ou retourne un dict vide."""
        if not value:
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return {}

    def _extract_cpv(self, data: dict[str, Any]) -> Optional[str]:
        """Extrait le premier code CPV trouve dans les donnees eForms."""

        def _find(obj: Any) -> Optional[str]:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "cbc:ItemClassificationCode" and isinstance(v, dict):
                        text = v.get("#text")
                        if text:
                            return str(text)
                    result = _find(v)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = _find(item)
                    if result:
                        return result
            return None

        return _find(data)

    def _extract_amount(self, data: dict[str, Any]) -> Optional[float]:
        """Extrait le montant estime total depuis les donnees eForms."""

        def _find(obj: Any) -> Optional[str]:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "cbc:EstimatedOverallContractAmount" and isinstance(v, dict):
                        text = v.get("#text")
                        if text:
                            return str(text)
                    result = _find(v)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = _find(item)
                    if result:
                        return result
            return None

        raw = _find(data)
        if raw:
            return self._parse_amount(raw)
        return None

    def _parse_record(self, record: dict[str, Any]) -> Optional[ScrapedAO]:
        """
        Parse un enregistrement JSON de l'API et le mappe vers ScrapedAO.

        Args:
            record: Dictionnaire JSON d'un enregistrement API.

        Returns:
            ScrapedAO ou None si l'enregistrement est invalide.
        """
        idweb = record.get("idweb")
        if not idweb:
            logger.debug("[BOAMP] Record sans idweb — ignore")
            return None

        objet = record.get("objet", "")
        if not objet:
            logger.debug(f"[BOAMP] Record {idweb} sans objet — ignore")
            return None

        # Parsing des donnees JSON imbriquees
        donnees = self._parse_json_str(record.get("donnees", "{}"))

        # CPV et montant depuis les donnees eForms
        cpv_code = self._extract_cpv(donnees)
        montant = self._extract_amount(donnees)

        # Parsing des dates
        publication_date = self._parse_date(record.get("dateparution"))
        deadline_date = self._parse_date(record.get("datelimitereponse"))

        # Localisation (departements)
        code_dept = record.get("code_departement") or []
        code_dept_prestation = record.get("code_departement_prestation")
        if code_dept_prestation:
            location = str(code_dept_prestation)
        elif code_dept:
            location = ", ".join(str(d) for d in code_dept if d)
        else:
            location = None

        # URL officielle de l'avis
        url = record.get("url_avis")

        # Construction du raw_data complet
        raw_data = dict(record)

        scraped = ScrapedAO(
            external_id=str(idweb),
            source=self.source_name,
            title=str(objet).strip(),
            description=self._safe_str(record.get("objet")),
            cpv_code=cpv_code,
            cpv_label=None,  # Label CPV non fourni directement par la nouvelle API
            publication_date=publication_date,
            deadline_date=deadline_date,
            estimated_amount=montant,
            currency="EUR",
            buyer_name=self._safe_str(record.get("nomacheteur")),
            location=location,
            procedure_type=self._safe_str(record.get("procedure_libelle")),
            ao_type=self._safe_str(record.get("nature_libelle")),
            url=url,
            raw_data=raw_data,
        )

        return scraped

    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse une date depuis divers formats possibles."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        if isinstance(value, str):
            # Essayer plusieurs formats
            formats = [
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]
            for fmt in formats:
                try:
                    parsed = datetime.strptime(value, fmt)
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    return parsed
                except ValueError:
                    continue
        logger.debug(f"[BOAMP] Impossible de parser la date: {value!r}")
        return None

    def _parse_amount(self, value: Any) -> Optional[float]:
        """Parse un montant depuis divers formats."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(" ", "").replace("\u202f", "").replace("\u00a0", "")
            cleaned = cleaned.replace("€", "").replace("EUR", "").replace(",", ".")
            try:
                return float(cleaned)
            except ValueError:
                pass
        logger.debug(f"[BOAMP] Impossible de parser le montant: {value!r}")
        return None

    def _safe_str(self, value: Any) -> Optional[str]:
        """Convertit une valeur en chaine de caracteres sure."""
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() if value.strip() else None
        return str(value).strip()

    async def fetch_and_store(
        self,
        limit: int = 100,
        where: Optional[str] = None,
        order_by: str = "dateparution DESC",
    ) -> dict[str, Any]:
        """
        Recupere les annonces et les insere en base avec embeddings.

        Returns:
            Rapport d'execution : {"total_fetched": int, "inserted": int, "duplicates": int, "errors": int}
        """
        # Recuperation
        aos = await self.fetch(limit=limit, where=where, order_by=order_by)

        if not aos:
            logger.info("[BOAMP] Aucune annonce a inserer")
            return {"total_fetched": 0, "inserted": 0, "duplicates": 0, "errors": 0}

        # Dedoublonnage SHA-256 sur idweb + objet + dateparution
        unique_aos = await self._deduplicate(aos)

        # Insertion avec embeddings
        inserted, errors = await self._insert_with_embeddings(unique_aos)

        result = {
            "total_fetched": len(aos),
            "inserted": inserted,
            "duplicates": len(aos) - len(unique_aos),
            "errors": errors,
        }

        logger.info(
            f"[BOAMP] Stockage termine — fetched={result['total_fetched']}, "
            f"inserted={result['inserted']}, duplicates={result['duplicates']}, "
            f"errors={result['errors']}"
        )
        return result

    async def _deduplicate(self, aos: list[ScrapedAO]) -> list[ScrapedAO]:
        """
        Dedupplique les AO par SHA-256 des champs cles (idweb + objet + dateparution).
        Verifie aussi l'existence en base par external_id.
        """
        # Verification base de donnees par external_id
        existing_ids: set[str] = set()
        async for session in get_db():
            existing_ids_result = await session.execute(
                select(AO.external_id).where(
                    AO.external_id.in_([ao.external_id for ao in aos])
                )
            )
            existing_ids = set(existing_ids_result.scalars().all())
            break

        unique_aos: list[ScrapedAO] = []
        seen_hashes: set[str] = set()

        for ao in aos:
            # Skip si deja en base par external_id
            if ao.external_id in existing_ids:
                continue

            # Hash SHA-256 sur les champs cles
            dedup_key = (
                f"{ao.external_id}|{ao.title}|"
                f"{ao.publication_date.isoformat() if ao.publication_date else ''}"
            )
            content_hash = hashlib.sha256(dedup_key.encode("utf-8")).hexdigest()

            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)
            unique_aos.append(ao)

        logger.info(
            f"[BOAMP] Dedoublonnage — {len(aos)} total, {len(unique_aos)} uniques, "
            f"{len(existing_ids)} deja en base"
        )
        return unique_aos

    async def _insert_with_embeddings(
        self, aos: list[ScrapedAO]
    ) -> tuple[int, int]:
        """
        Insere les AO en base avec leurs embeddings.

        Returns:
            (nombre_insere, nombre_erreurs)
        """
        inserted = 0
        errors = 0

        async for session in get_db():
            # Recuperer ou creer la source BOAMP
            source_result = await session.execute(
                select(Source).where(Source.name == self.source_name)
            )
            source = source_result.scalar_one_or_none()
            if source is None:
                source = Source(
                    name=self.source_name,
                    label="BOAMP — Bulletin Officiel",
                    base_url=self.base_url,
                    country="FR",
                )
                session.add(source)
                await session.flush()

            for ao in aos:
                try:
                    # 1. Creer l'AO
                    db_ao = AO(
                        source_id=source.id,
                        external_id=ao.external_id,
                        title=ao.title,
                        description=ao.description,
                        cpv_codes=[ao.cpv_code] if ao.cpv_code else [],
                        cpv_descriptions=[ao.cpv_label] if ao.cpv_label else [],
                        publication_date=ao.publication_date,
                        deadline_date=ao.deadline_date,
                        estimated_amount=ao.estimated_amount,
                        currency=ao.currency or "EUR",
                        buyer_name=ao.buyer_name,
                        region=ao.location,
                        notice_type=ao.procedure_type,
                        raw_data=ao.raw_data,
                        external_url=ao.url,
                        status="detected",
                        country="FR",
                    )
                    session.add(db_ao)
                    await session.flush()  # Pour obtenir l'ID

                    # 2. Calculer l'embedding
                    embed_text = ao.title
                    if ao.description:
                        embed_text = f"{ao.title} {ao.description}"

                    embedding = await self.embedding_service.embed_text(embed_text)

                    # 3. Creer le chunk avec embedding
                    chunk = AOChunk(
                        ao_id=db_ao.id,
                        chunk_text=embed_text[:8000],  # Limite de securite
                        chunk_index=0,
                        embedding=embedding,
                        extra_metadata={"chunk_type": "description"},
                    )
                    session.add(chunk)

                    inserted += 1

                except Exception as exc:
                    logger.error(
                        f"[BOAMP] Erreur insertion AO {ao.external_id} — {exc}"
                    )
                    errors += 1
                    continue

            await session.commit()
            break

        return inserted, errors
