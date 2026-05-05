"""Pipeline E2E d'ingestion d'un AO : chunk → embed → score → memoire.
Declenche automatiquement apres detection par l'Agent Veilleur.
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.ao_s2 import AO, AOChunk
from app.models.ao import MemoryEntry, MemoryType
from app.services.business_lines.service import BusinessLineService
from app.services.llm.mistral_client import MistralAIClient
from app.services.scoring.engine import ScoringEngine

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class IngestionPipeline:
    """Pipeline complet : chunking → embedding → scoring → memoire."""

    def __init__(self):
        self.mistral = MistralAIClient()
        self.scoring = ScoringEngine()

    async def process_ao(self, ao_id: str) -> dict:
        result = {"status": "error", "chunks": 0, "scored": False, "bl_assigned": False}

        async with AsyncSessionLocal() as db:
            try:
                stmt = select(AO).where(AO.id == ao_id)
                row = await db.execute(stmt)
                ao = row.scalar_one_or_none()
                if not ao:
                    logger.error("[Pipeline] AO %s introuvable", ao_id)
                    return result

                ao.status = "parsing"
                await db.commit()

                chunks = await self._create_chunks(ao, db)
                result["chunks"] = len(chunks)
                ao.status = "parsed"
                await db.commit()

                await self._embed_chunks(chunks, db)

                tenant_id = None
                if ao.source:
                    # Source n'a pas de tenant_id direct, on utilise le business_line
                    pass

                bl = await BusinessLineService.match_ao_to_bl(db, ao, tenant_id or "")
                if bl:
                    ao.business_line_id = bl.id
                    result["bl_assigned"] = True
                    logger.info("[Pipeline] AO %s assigne a BL '%s'", ao_id, bl.name)

                await db.commit()

                profile = bl.default_profile if bl else "prudent"
                scoring_run = await self.scoring.score_and_save(
                    ao_id=ao_id,
                    profile=profile,
                    db=db,
                    triggered_by="auto",
                )
                result["scored"] = True
                result["status"] = "success"

                await self._store_memory(ao, scoring_run, db)

                logger.info(
                    "[Pipeline] AO %s traite : %s chunks, score=%s",
                    ao_id,
                    len(chunks),
                    scoring_run.verdict,
                )

            except Exception as e:
                logger.error("[Pipeline] Erreur traitement AO %s: %s", ao_id, e)
                try:
                    ao.status = "error"
                    await db.commit()
                except Exception:
                    pass
                result["status"] = "error"
                result["error"] = str(e)

        return result

    async def _create_chunks(self, ao: AO, db: AsyncSession) -> list[AOChunk]:
        text = f"{ao.title or ''}\n\n{ao.description or ''}"
        if not text.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            if end < len(text):
                while end > start and text[end] not in (" ", "\n", ".", "!"):
                    end -= 1

            chunk_text = text[start:end].strip()
            if len(chunk_text) > 50:
                chunk = AOChunk(
                    ao_id=ao.id,
                    chunk_text=chunk_text,
                    chunk_index=chunk_index,
                    extra_metadata={
                        "char_range": [start, end],
                        "section": "auto",
                    },
                )
                db.add(chunk)
                chunks.append(chunk)
                chunk_index += 1

            start = end - CHUNK_OVERLAP if end < len(text) else end

        await db.commit()
        for c in chunks:
            await db.refresh(c)

        return chunks

    async def _embed_chunks(self, chunks: list[AOChunk], db: AsyncSession):
        if not chunks:
            return

        texts = [c.chunk_text for c in chunks]
        try:
            embeddings = await self.mistral.embed_batch(texts)
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            await db.commit()
        except Exception as e:
            logger.error("[Pipeline] Erreur embedding: %s", e)

    async def _store_memory(self, ao: AO, scoring_run, db: AsyncSession):
        try:
            memory = MemoryEntry(
                memory_type=MemoryType.EPISODIC,
                content={
                    "ao_id": str(ao.id),
                    "title": ao.title,
                    "verdict": scoring_run.verdict,
                    "score_global": float(scoring_run.score_global),
                    "profile": scoring_run.profile,
                },
                content_hash="",
                source_type="pipeline_scoring",
            )
            db.add(memory)
            await db.commit()
        except Exception as e:
            logger.warning("[Pipeline] Erreur memoire: %s", e)
