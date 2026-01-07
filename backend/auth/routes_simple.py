from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.schemas import LoginRequest, TokenResponse
import bcrypt
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Secret key for JWT (replace with env variable in production)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# In-memory failed attempts tracker (replace with DB logic in production)
FAILED_ATTEMPTS = {}
LOCKED_ACCOUNTS = {}

def is_account_locked(username: str) -> bool:
    if username in LOCKED_ACCOUNTS:
        unlock_time = LOCKED_ACCOUNTS[username]
        if datetime.utcnow() < unlock_time:
            return True
        else:
            del LOCKED_ACCOUNTS[username]
    return False

def lock_account(username: str, duration_seconds: int = 900):
    LOCKED_ACCOUNTS[username] = datetime.utcnow() + timedelta(seconds=duration_seconds)

def increment_failed_attempts(username: str):
    FAILED_ATTEMPTS[username] = FAILED_ATTEMPTS.get(username, 0) + 1
    if FAILED_ATTEMPTS[username] >= 5:
        lock_account(username)

def reset_failed_attempts(username: str):
    FAILED_ATTEMPTS[username] = 0

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=TokenResponse, summary="User Login")
def login(request: LoginRequest):
    username = request.username
    password = request.password

    # Check if account is locked
    if is_account_locked(username):
        raise HTTPException(status_code=403, detail="Account locked. Try again later.")

    # Example: hardcoded admin user (replace with DB lookup)
    if username != "admin" or password != "admin123":
        increment_failed_attempts(username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Reset failed attempts on success
    reset_failed_attempts(username)

    # Generate JWT token
    access_token = create_access_token(data={"sub": username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
