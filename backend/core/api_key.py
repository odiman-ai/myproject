"""
API Key Security Module
----------------------

Used for:
- External integrations
- Reports access
- System-to-system authentication

API Keys are:
- Random & unguessable
- Stored hashed (never plaintext)
- Scoped & time-limited
- Revocable via Redis
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from backend.core.redis import redis_client

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
API_KEY_HEADER_NAME = "X-API-Key"
API_KEY_PREFIX = "spms_"
DEFAULT_API_KEY_TTL_DAYS = 90

api_key_header = APIKeyHeader(
    name=API_KEY_HEADER_NAME,
    auto_error=False,
)

# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------
class APIKeyData(BaseModel):
    key_id: str
    scopes: List[str]
    expires_at: datetime
    owner: Optional[str] = None


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_key(api_key: str) -> str:
    """
    Hash API key using SHA-256 (safe for lookup).
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def _redis_key(key_hash: str) -> str:
    return f"api_key:{key_hash}"


# ------------------------------------------------------------------------------
# API Key Creation
# ------------------------------------------------------------------------------
def generate_api_key(
    *,
    scopes: List[str],
    owner: Optional[str] = None,
    expires_in_days: int = DEFAULT_API_KEY_TTL_DAYS,
) -> tuple[str, APIKeyData]:
    """
    Generate a new API key.

    Returns:
        plaintext_key (str) – shown ONCE
        APIKeyData – stored metadata
    """
    raw_key = f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"
    key_hash = _hash_key(raw_key)

    expires_at = _utc_now() + timedelta(days=expires_in_days)

    data = APIKeyData(
        key_id=key_hash[:12],
        scopes=scopes,
        expires_at=expires_at,
        owner=owner,
    )

    ttl = int((expires_at - _utc_now()).total_seconds())

    redis_client.setex(
        _redis_key(key_hash),
        ttl,
        data.json(),
    )

    return raw_key, data


# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------
def verify_api_key(
    api_key: str,
    required_scopes: Optional[List[str]] = None,
) -> APIKeyData:
    """
    Validate API key and scope permissions.
    """
    key_hash = _hash_key(api_key)
    raw = redis_client.get(_redis_key(key_hash))

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    data = APIKeyData.parse_raw(raw)

    if data.expires_at < _utc_now():
        redis_client.delete(_redis_key(key_hash))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired",
        )

    if required_scopes:
        missing = set(required_scopes) - set(data.scopes)
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing API key scopes: {', '.join(missing)}",
            )

    return data


# ------------------------------------------------------------------------------
# FastAPI Dependencies
# ------------------------------------------------------------------------------
def require_api_key(
    required_scopes: Optional[List[str]] = None,
):
    """
    Dependency factory for API key protected endpoints.

    Usage:
        @router.get("/reports")
        def reports(
            api_key: APIKeyData = Depends(require_api_key(["reports:read"]))
        ):
            ...
    """
    def _dependency(
        api_key: str = Security(api_key_header),
    ) -> APIKeyData:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
            )
        return verify_api_key(api_key, required_scopes)

    return _dependency


# ------------------------------------------------------------------------------
# Revocation
# ------------------------------------------------------------------------------
def revoke_api_key(api_key: str) -> None:
    """
    Revoke API key immediately.
    """
    key_hash = _hash_key(api_key)
    redis_client.delete(_redis_key(key_hash))


def revoke_all_api_keys_for_owner(owner: str) -> int:
    """
    Revoke all API keys belonging to an owner.
    """
    count = 0
    for key in redis_client.scan_iter("api_key:*"):
        raw = redis_client.get(key)
        if not raw:
            continue

        data = APIKeyData.parse_raw(raw)
        if data.owner == owner:
            redis_client.delete(key)
            count += 1

    return count
