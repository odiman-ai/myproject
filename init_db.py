# init_db.py
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from backend.database import engine, get_db
from backend.models import Base, User
from backend.auth.utils import hash_password

# Configuration for default admin
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "Admin@12345",  # Change this after first login!
    "email": "admin@example.com",
    "role": "admin",
    "status": "active"
}

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def create_default_admin():
    """Create a default admin user if it doesn't exist."""
    from sqlalchemy.orm import Session
    db: Session = next(get_db())

    existing_admin = db.query(User).filter(User.username == DEFAULT_ADMIN["username"]).first()
    if existing_admin:
        print("ℹ️ Default admin already exists. Skipping creation.")
        return

    admin_user = User(
        username=DEFAULT_ADMIN["username"],
        email=DEFAULT_ADMIN["email"],
        role=DEFAULT_ADMIN["role"],
        status=DEFAULT_ADMIN["status"],
        password_hash=hash_password(DEFAULT_ADMIN["password"]),
        created_at=datetime.now(timezone.utc),
        last_login=None,
        failed_login_attempts=0,
        account_locked_until=None
    )
    db.add(admin_user)
    db.commit()
    print(f"✅ Default admin user created:\n   username: {DEFAULT_ADMIN['username']}\n   password: {DEFAULT_ADMIN['password']}")
    print("⚠️ Please change this password immediately after first login!")

if __name__ == "__main__":
    create_tables()
    create_default_admin()
