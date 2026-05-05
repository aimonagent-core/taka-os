"""Routes API pour l'autonomie du systeme."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User

router = APIRouter(prefix="/autonomy", tags=["autonomy"])


class SystemState:
    """Etat simplifie du systeme d'autonomie."""

    def __init__(self, level: str = "advisor", kill_switch: bool = False, frozen_reason: str | None = None, updated_at=None):
        self.level = level
        self.kill_switch = kill_switch
        self.frozen_reason = frozen_reason
        self.updated_at = updated_at


class AutonomyLevel:
    """Niveau d'autonomie simplifie."""

    def __init__(self, value: str = "advisor"):
        self.value = value
        self.description = {
            "advisor": "Mode conseiller — toute action necessite validation humaine",
            "semi_autonomous": "Mode semi-autonome — actions routine autorisees, critique en HIL",
            "fully_autonomous": "Mode autonome — le systeme decide et execute sans supervision",
        }.get(value, "Niveau inconnu")


async def get_system_state(db: AsyncSession) -> SystemState:
    """Retourne l'etat actuel du systeme (stub — peut etre etendu avec une table d'etat)."""
    return SystemState(level="advisor", kill_switch=False, frozen_reason=None)


async def get_autonomy_level(db: AsyncSession) -> AutonomyLevel:
    """Retourne le niveau d'autonomie actuel."""
    return AutonomyLevel(value="advisor")


@router.get("/state")
async def get_state(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne l'etat actuel du systeme (autonomy, kill_switch, etc.)."""
    state = await get_system_state(db)
    return {
        "autonomy_level": state.level,
        "kill_switch": state.kill_switch,
        "frozen_reason": state.frozen_reason,
        "last_updated": state.updated_at.isoformat() if state.updated_at else None,
    }


@router.get("/level")
async def get_level(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne le niveau d'autonomie actuel."""
    level = await get_autonomy_level(db)
    return {"level": level.value, "description": level.description}
