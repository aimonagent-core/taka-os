# File: app/core/circuit_breaker.py
# Purpose: Circuit breaker definitions for external service calls
# Dependencies: pybreaker

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from pybreaker import CircuitBreaker

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Default breaker config: 5 failures, 60s recovery timeout
_BREAKER_CONFIG = {
    "fail_max": 5,
    "reset_timeout": 60,
}

sentry_breaker = CircuitBreaker(name="sentry", **_BREAKER_CONFIG)
llm_api_breaker = CircuitBreaker(name="llm_api", fail_max=3, reset_timeout=120)
email_breaker = CircuitBreaker(name="email", fail_max=5, reset_timeout=60)
storage_breaker = CircuitBreaker(name="storage", fail_max=5, reset_timeout=60)


def circuit_breaker_call(breaker: CircuitBreaker, func: F) -> F:
    """Decorator to wrap a function with a circuit breaker."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return breaker(func)(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def get_breaker_status() -> dict[str, str]:
    """Return current status of all circuit breakers."""
    breakers = {
        "sentry": sentry_breaker,
        "llm_api": llm_api_breaker,
        "email": email_breaker,
        "storage": storage_breaker,
    }
    return {name: str(brk.current_state) for name, brk in breakers.items()}
