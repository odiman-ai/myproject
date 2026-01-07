# dependencies.py
from fastapi import Depends, HTTPException, status
from spms_db.backend.database import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# simple role-based auth dependency (replace with your JWT logic)
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # decode token, fetch user; raise 401 if invalid
    # placeholder:
    if token == "fake-admin-token":
        return {"id": 1, "username": "admin", "role": "admin"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
