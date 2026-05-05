"""Extension du EventBus existant pour les événements S3.
En MVP : asyncio in-memory. En v0.5 : NATS.
"""
import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """Bus d'événements asynchrone in-memory (MVP)."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Abonne un handler à un type d'événement."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug("[EventBus] Handler ajouté pour %s", event_type)

    async def publish(self, event_type: str, payload: dict):
        """Publie un événement à tous les handlers abonnés."""
        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug("[EventBus] Aucun handler pour %s", event_type)
            return

        logger.info("[EventBus] Publication %s → %s handlers", event_type, len(handlers))
        tasks = [handler(payload) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)


# Instance globale (singleton)
event_bus = EventBus()

# Événements S3
EVENT_AO_SCORED = "ao.scored"
EVENT_RESPONSE_GENERATED = "response.generated"
EVENT_RESPONSE_APPROVED = "response.approved"
EVENT_SUBMISSION_SUBMITTED = "submission.submitted"
EVENT_SUBMISSION_CONFIRMED = "submission.confirmed"
