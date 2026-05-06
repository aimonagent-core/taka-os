"""Registre des connecteurs de depot."""

from typing import Type

from app.agents.deposant.connectors.base import BaseConnector
from app.agents.deposant.connectors.boamp_real import BoampRealConnector
from app.agents.deposant.connectors.enotification_real import ENotificationRealConnector
from app.agents.deposant.connectors.mock_wrappers import (
    MockBOAMPConnector,
    MockJoueConnector,
    MockMarocConnector,
)

_CONNECTOR_REGISTRY: dict[str, dict[str, Type[BaseConnector]]] = {
    "mock": {
        "boamp": MockBOAMPConnector,
        "joue": MockJoueConnector,
        "marche_public": MockMarocConnector,
    },
    "real": {
        "boamp": BoampRealConnector,
        "e_notification": ENotificationRealConnector,
    },
}


def get_connector(platform_type: str, use_real: bool = False) -> Type[BaseConnector]:
    """Recupere la classe connecteur pour une plateforme."""
    connector_type = "real" if use_real else "mock"
    registry = _CONNECTOR_REGISTRY.get(connector_type, {})

    if platform_type not in registry:
        available = list(_CONNECTOR_REGISTRY["mock"].keys()) + list(_CONNECTOR_REGISTRY["real"].keys())
        raise ValueError(
            f"Aucun connecteur {connector_type} pour '{platform_type}'. "
            f"Disponibles : {available}"
        )

    return registry[platform_type]


def list_available_platforms() -> dict[str, list[str]]:
    """Liste toutes les plateformes supportees par categorie."""
    return {
        "mock": list(_CONNECTOR_REGISTRY["mock"].keys()),
        "real": list(_CONNECTOR_REGISTRY["real"].keys()),
    }
