# File: app/dependencies.py
# Purpose: Reusable FastAPI dependencies for auth, DB, roles, and tenant
# Dependencies: app.database, app.models.ao, app.core.security, app.core.sentry

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_token
from app.core.sentry import set_sentry_user
from app.database import get_db
from app.models.ao import Tenant, User, UserRole

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_exception
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("sub") is None or payload.get("type") != "access":
        raise credentials_exception
    user_id = payload.get("sub")
    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant))
        .where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    set_sentry_user(
        str(user.id), str(user.tenant_id) if user.tenant_id else None, user.role.value
    )
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


require_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN])
require_manager = RoleChecker(
    [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.TENANT_MANAGER]
)
require_collaborator = RoleChecker(
    [
        UserRole.SUPER_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.TENANT_MANAGER,
        UserRole.TENANT_COLLABORATOR,
    ]
)
require_any_authenticated = RoleChecker(list(UserRole))


async def get_current_tenant(user: User = Depends(get_current_user)) -> Tenant:
    if user.tenant is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no tenant"
        )
    return user.tenant


async def set_request_state_user(
    request: Request, user: User = Depends(get_current_user)
) -> User:
    """Store user_id in request.state for rate limiting key derivation."""
    request.state.user_id = str(user.id)
    return user
