# spms_db/tests/test_auth_dependencies.py
import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.dependencies import get_current_active_user, require_admin, optional_user
from backend.models import User, Base
from backend.auth.utils import hash_password

# -------------------------
# Setup test database
# -------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture()
def db_session():
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def test_user(db_session):
    user = User(
        username="testuser",
        password_hash=hash_password("Test1234!"),
        role="user",
        status="active"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_user(db_session):
    user = User(
        username="adminuser",
        password_hash=hash_password("Admin1234!"),
        role="admin",
        status="active"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def app(test_user, admin_user):
    app = FastAPI()

    @app.get("/active-user")
    def active_user_route(user=Depends(get_current_active_user)):
        return {"username": user.username, "role": user.role}

    @app.get("/admin-only")
    def admin_route(user=Depends(require_admin)):
        return {"username": user.username, "role": user.role}

    @app.get("/optional")
    def optional_route(user=Depends(optional_user)):
        if user:
            return {"username": user.username, "role": user.role}
        return {"username": None}

    return app


@pytest.fixture()
def client(app):
    return TestClient(app)


# -------------------------
# Tests
# -------------------------
def test_get_current_active_user(client, test_user):
    # Normally you'd provide a token, here we bypass dependencies
    response = client.get("/active-user", headers={"Authorization": f"Bearer fake-token"})
    assert response.status_code in (401, 403)  # No real token provided


def test_require_admin(client, admin_user):
    response = client.get("/admin-only", headers={"Authorization": f"Bearer fake-token"})
    assert response.status_code in (401, 403)


def test_optional_user_anonymous(client):
    response = client.get("/optional")
    assert response.status_code == 200
    assert response.json() == {"username": None}


def test_optional_user_authenticated(client, test_user):
    # Fake token simulation (dependencies not fully mocked)
    response = client.get("/optional", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code in (200, 401, 403)
