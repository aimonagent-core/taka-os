"""
Service d'embeddings via l'API Mistral.
Calcule les vecteurs 1024 dimensions pour les textes des AO.
"""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

MISTRAL_EMBED_API_URL = "https://api.mistral.ai/v1/embeddings"
MISTRAL_MODEL = "mistral-embed"
EMBEDDING_DIMENSION = 1024


class EmbeddingService:
    """
    Service qui calcule les embeddings via l'API Mistral.
    Retourne des vecteurs de 1024 dimensions (float).
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY", "")
        if not self.api_key:
            logger.warning("EmbeddingService: MISTRAL_API_KEY non configuree")

    async def embed_text(self, text: str) -> list[float]:
        """
        Calcule l'embedding 1024d pour un texte via l'API Mistral.

        Args:
            text: Texte a vectoriser (titre + description de l'AO).

        Returns:
            Vecteur de 1024 dimensions (list[float]).

        Raises:
            RuntimeError: Si l'API retourne une erreur apres retries.
        """
        if not text or not text.strip():
            return [0.0] * EMBEDDING_DIMENSION

        # Tronquer si trop long (limite Mistral ~8000 tokens)
        truncated = text[:8000]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MISTRAL_MODEL,
            "input": truncated,
            "encoding_format": "float",
        }

        max_retries = 3
        last_error: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(30.0)
                ) as client:
                    response = await client.post(
                        MISTRAL_EMBED_API_URL,
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()

                    embedding = data["data"][0]["embedding"]

                    # Validation dimension
                    if len(embedding) != EMBEDDING_DIMENSION:
                        raise ValueError(
                            f"Dimension inattendue: {len(embedding)}, "
                            f"attendu: {EMBEDDING_DIMENSION}"
                        )

                    return embedding

            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.warning(
                    f"[Embedding] Tentative {attempt}/{max_retries} echouee — "
                    f"HTTP {exc.response.status_code}"
                )
            except (KeyError, IndexError) as exc:
                last_error = exc
                logger.warning(
                    f"[Embedding] Tentative {attempt}/{max_retries} — "
                    f"Reponse invalide: {exc}"
                )
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    f"[Embedding] Tentative {attempt}/{max_retries} — "
                    f"Erreur reseau: {exc}"
                )

        logger.error(f"[Embedding] Echec apres {max_retries} tentatives")
        raise RuntimeError(
            f"Impossible de calculer l'embedding apres {max_retries} tentatives: {last_error}"
        )

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Calcule les embeddings pour plusieurs textes en batch.
        """
        results: list[list[float]] = []
        for text in texts:
            embedding = await self.embed_text(text)
            results.append(embedding)
        return results
