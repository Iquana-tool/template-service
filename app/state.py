import os
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_REGISTRATION_TOKEN = os.getenv("SERVICE_REGISTRATION_TOKEN", os.getenv("SERVICE_SECRET", "default-secret"))


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# If true, missing required model entries are created as placeholders.
REGISTRY_CREATE_MISSING = _env_bool("REGISTRY_CREATE_MISSING", False)

# If true and create-missing is disabled, registration fails when required entries are missing.
REGISTRY_ENFORCE_REQUIRED = _env_bool("REGISTRY_ENFORCE_REQUIRED", True)


@dataclass(frozen=True)
class Backend:
    """Resolved backend configuration bound to an authentication token."""

    token: str
    backend_address: str
    celery_broker_url: str
    mlflow_tracking_uri: str
    api_key: Optional[str]
    created_at: str


def _utc_iso_now() -> str:
    """Return an ISO8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()

def verify_registration_token(token: str) -> bool:
    """Verify the registration token."""
    return token == _REGISTRATION_TOKEN

# Single-backend state (populated on registration)
_backend: Optional["Backend"] = None
_backend_token: Optional[str] = None


def register_backend(
    backend_address: str,
    celery_broker_url: str,
    mlflow_tracking_uri: str,
    api_key: Optional[str] = None,
) -> str:
    """Register the single backend and return a bearer token. Re-registration replaces the previous config."""
    global _backend, _backend_token
    if _backend is not None:
        logger.warning("Re-registering backend; replacing previous config for '%s'", _backend.backend_address)
    token = secrets.token_urlsafe(32)
    _backend_token = token
    _backend = Backend(
        token=token,
        backend_address=backend_address,
        celery_broker_url=celery_broker_url,
        mlflow_tracking_uri=mlflow_tracking_uri,
        api_key=api_key or None,
        created_at=_utc_iso_now(),
    )
    logger.info("Registered backend '%s' and issued token", backend_address)
    return token


def verify_backend_token(token: Optional[str]) -> bool:
    """Verify that the given token matches the registered backend token."""
    return bool(token and token == _backend_token)


def get_backend(token: str) -> Optional[Backend]:
    """Return the registered backend if the token matches."""
    if token == _backend_token:
        return _backend
    return None

def update_celery_config(broker_url: str) -> bool:
    """Update Celery broker configuration."""
    try:
        import celery_app
        celery_app.app.conf.update(broker_url=broker_url, result_backend=broker_url)
        logger.info(f"Celery configured with broker: {broker_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Celery: {e}")
        return False


