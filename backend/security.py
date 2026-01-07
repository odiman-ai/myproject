import os
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from enum import Enum

from backend.core.redis import redis_client
from pwned_passwords import PasswordChecker

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("spms.security")

# ------------------------------------------------------------------------------
# Environment / Config
# ------------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
REQUIRE_UPPERCASE = os.getenv("REQUIRE_UPPERCASE", "true") == "true"
REQUIRE_LOWERCASE = os.getenv("REQUIRE_LOWERCASE", "true") == "true"
REQUIRE_DIGIT = os.getenv("REQUIRE_DIGIT", "true") == "true"
REQUIRE_SPECIAL = os.getenv("REQUIRE_SPECIAL", "true") == "true"

BCRYPT_MAX_BYTES = 72

# ------------------------------------------------------------------------------
# Password Hashing
# ------------------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

hibp_checker = PasswordChecker()

# ------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------
class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def now_utc() -> datetime:
    return datetime.now(timezone.utc)

# ------------------------------------------------------------------------------
# Password Policy
# ------------------------------------------------------------------------------
def validate_password_policy(password: str) -> tuple[bool, Optional[str]]:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    if REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter"

    if REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter"

    if REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "Password must contain a digit"

    if REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain a special character"

    if hibp_checker.is_pwned(password):
        return False, "Password has appeared in a known data breach"

    return True, None

def _bcrypt_safe(password: str) -> str:
    encoded = password.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return password
    logger.warning("Password exceeded bcrypt limit; truncated")
    return encoded[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")

def hash_password(password: str) -> str:
    valid, error = validate_password_policy(password)
    if not valid:
        raise ValueError(error)
    return pwd_context.hash(_bcrypt_safe(password))

def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(_bcrypt_safe(password), hashed)
    except Exception:
        return False

def needs_rehash(hashed: str) -> bool:
    return pwd_context.needs_update(hashed)

# ------------------------------------------------------------------------------
# JWT Creation
# ------------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any]) -> str:
    now = now_utc()
    payload = {
        **data,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": TokenType.ACCESS.value,
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> tuple[str, str, datetime]:
    jti = secrets.token_urlsafe(16)
    now = now_utc()
    exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        **data,
        "iat": now,
        "exp": exp,
        "type": TokenType.REFRESH.value,
        "jti": jti,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, exp

# ------------------------------------------------------------------------------
# Token Decoding & Revocation (Redis)
# ------------------------------------------------------------------------------
def revoke_token(jti: str, exp: int):
    ttl = max(0, exp - int(now_utc().timestamp()))
    redis_client.setex(f"revoked:{jti}", ttl, "1")

def is_token_revoked(jti: str) -> bool:
    return redis_client.exists(f"revoked:{jti}") == 1

def decode_token(token: str, expected_type: TokenType) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != expected_type.value:
            raise JWTError("Invalid token type")

        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            raise JWTError("Token revoked")

        return payload
    except JWTError:
        raise

def decode_access_token(token: str) -> Dict[str, Any]:
    return decode_token(token, TokenType.ACCESS)

def decode_refresh_token(token: str) -> Dict[str, Any]:
    return decode_token(token, TokenType.REFRESH)

# ------------------------------------------------------------------------------
# API KEY SUPPORT
# ------------------------------------------------------------------------------
def hash_api_key(key: str) -> str:
    return pwd_context.hash(key)

def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return pwd_context.verify(raw_key, stored_hash)

# ------------------------------------------------------------------------------
# Aliases
# ------------------------------------------------------------------------------
get_password_hash = hash_password
verify_password_hash = verify_password
