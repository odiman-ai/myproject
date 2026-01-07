# (Updated)
import os
import logging
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set, Tuple
from enum import Enum

from jose import jwt, JWTError
from passlib.context import CryptContext

# Configuration from environment with validation
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY == "change-this-in-production":
    if os.getenv("SPMS_ENV", "development").lower() in ("production", "prod"):
        raise ValueError("SECRET_KEY must be set in production environment")
    SECRET_KEY = secrets.token_urlsafe(32)
    logging.warning("Using auto-generated SECRET_KEY for development. Set SECRET_KEY in production!")

ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password policy configuration
MIN_PASSWORD_LENGTH: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
REQUIRE_UPPERCASE: bool = os.getenv("REQUIRE_UPPERCASE", "true").lower() == "true"
REQUIRE_LOWERCASE: bool = os.getenv("REQUIRE_LOWERCASE", "true").lower() == "true"
REQUIRE_DIGIT: bool = os.getenv("REQUIRE_DIGIT", "true").lower() == "true"
REQUIRE_SPECIAL: bool = os.getenv("REQUIRE_SPECIAL", "true").lower() == "true"

# bcrypt has a 72-byte input limit
BCRYPT_MAX_BYTES: int = 72

# Logging
logger = logging.getLogger("spms_auth_utils")

# Password hashing context with improved configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased from default 10 for better security
)

# Token blacklist (in production, use Redis or database)
_token_blacklist: Set[str] = set()
_blacklist_lock = threading.Lock()


class TokenType(str, Enum):
    """Token type enumeration"""
    ACCESS = "access"
    REFRESH = "refresh"


class PasswordValidationError(Exception):
    """Custom exception for password validation failures"""
    pass


# -------------------------
# Password Policy Validation
# -------------------------
def validate_password_policy(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password against security policy.

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"

    if REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    # Check for common weak passwords
    common_passwords = {"password", "12345678", "qwerty", "abc123", "password123"}
    if password.lower() in common_passwords:
        return False, "Password is too common. Please choose a stronger password"

    return True, None


# -------------------------
# Password helpers
# -------------------------
def _ensure_bcrypt_length(password: str) -> str:
    """
    Ensure password length is safe for bcrypt (72 bytes).
    If the UTF-8 encoded password exceeds the limit, truncate and log a warning.

    Note: This is a pragmatic safety measure. For long passwords consider pre-hashing
    (e.g. SHA-256) prior to bcrypt to avoid truncation issues.
    """
    encoded = password.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return password

    truncated = encoded[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")
    logger.warning(
        "Password exceeded %d bytes and was truncated for bcrypt hashing. "
        "Consider implementing password pre-hashing for long passwords.",
        BCRYPT_MAX_BYTES
    )
    return truncated


def hash_password(password: str, validate_policy: bool = True) -> str:
    """
    Hash a plain password using bcrypt via passlib.

    Args:
        password: Plain text password to hash
        validate_policy: Whether to validate password against policy (default: True)

    Returns:
        str: Bcrypt hashed password

    Raises:
        PasswordValidationError: If password doesn't meet policy requirements
    """
    if validate_policy:
        is_valid, error_msg = validate_password_policy(password)
        if not is_valid:
            raise PasswordValidationError(error_msg)

    safe_password = _ensure_bcrypt_length(password)
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its bcrypt hash.
    Applies the same truncation rule before verification.
    Uses constant-time comparison via passlib.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        bool: True if password matches, False otherwise
    """
    safe_password = _ensure_bcrypt_length(plain_password)
    try:
        return pwd_context.verify(safe_password, hashed_password)
    except Exception as exc:
        logger.error("Error verifying password: %s", exc, exc_info=True)
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated.
    Useful for upgrading hashes when changing bcrypt rounds.

    Args:
        hashed_password: The hash to check

    Returns:
        bool: True if hash should be regenerated
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception as exc:
        logger.warning("Error checking hash update status: %s", exc)
        return False


# -------------------------
# JWT Token helpers
# -------------------------
def _now_timestamp() -> int:
    """Return current UTC time as integer Unix timestamp (seconds)."""
    return int(datetime.now(timezone.utc).timestamp())


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Claims to encode (should include {"sub": "username", "role": "..."})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    now_ts = _now_timestamp()
    expire_ts = now_ts + int((expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).total_seconds())

    to_encode.update({
        "iat": now_ts,
        "exp": expire_ts,
        "type": TokenType.ACCESS.value,
        "jti": secrets.token_urlsafe(16)  # Unique token ID for blacklisting
    })

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Claims to encode (should include {"sub": "username"})

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    now_ts = _now_timestamp()
    expire_ts = now_ts + int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())

    to_encode.update({
        "iat": now_ts,
        "exp": expire_ts,
        "type": TokenType.REFRESH.value,
        "jti": secrets.token_urlsafe(16)
    })

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str, verify_type: bool = True) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token to decode
        verify_type: Whether to verify token type (default: True)

    Returns:
        dict: Token payload

    Raises:
        JWTError: If token is invalid, expired, or blacklisted
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti:
            with _blacklist_lock:
                if jti in _token_blacklist:
                    logger.warning("Attempted use of blacklisted token: %s", jti)
                    raise JWTError("Token has been revoked")

        # Verify token type
        if verify_type and payload.get("type") != TokenType.ACCESS.value:
            raise JWTError("Invalid token type")

        return payload
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", exc)
        raise


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.

    Args:
        token: JWT refresh token to decode

    Returns:
        dict: Token payload

    Raises:
        JWTError: If token is invalid, expired, or not a refresh token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti:
            with _blacklist_lock:
                if jti in _token_blacklist:
                    raise JWTError("Token has been revoked")

        # Verify token type
        if payload.get("type") != TokenType.REFRESH.value:
            raise JWTError("Invalid token type - expected refresh token")

        return payload
    except JWTError as exc:
        logger.debug("Refresh token decode failed: %s", exc)
        raise


def revoke_token(token: str) -> bool:
    """
    Add a token to the blacklist (logout functionality).

    Note: In production, implement this with Redis or a database table
    with TTL matching the token expiration.

    Args:
        token: JWT token to revoke

    Returns:
        bool: True if token was revoked successfully
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            with _blacklist_lock:
                _token_blacklist.add(jti)
            logger.info("Token revoked: %s", jti)
            return True
        return False
    except JWTError as exc:
        logger.warning("Failed to revoke token: %s", exc)
        return False


def clear_expired_blacklist() -> int:
    """
    Clean up expired tokens from blacklist.
    Should be called periodically by a background task.

    Returns:
        int: Number of tokens removed
    """
    # This is a simplified version. In production with Redis/DB,
    # tokens would expire automatically via TTL.
    with _blacklist_lock:
        initial_count = len(_token_blacklist)
        _token_blacklist.clear()
        removed = initial_count - len(_token_blacklist)
    if removed > 0:
        logger.info("Cleared %d expired tokens from blacklist", removed)
    return removed


def verify_token_not_expired(payload: Dict[str, Any]) -> bool:
    """
    Verify that a decoded token payload has not expired.

    Args:
        payload: Decoded JWT payload

    Returns:
        bool: True if token is still valid
    """
    exp = payload.get("exp")
    if exp is None:
        return False

    try:
        # exp is expected to be an integer timestamp (seconds)
        exp_datetime = datetime.fromtimestamp(int(exp), tz=timezone.utc)
    except Exception:
        return False

    return datetime.now(timezone.utc) < exp_datetime


# -------------------------
# Convenience aliases
# -------------------------
get_password_hash = hash_password
verify_password_hash = verify_password