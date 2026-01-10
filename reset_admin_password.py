"""
Run:
  python reset_admin_password.py
  python reset_admin_password.py --password "NewPass!234"
  python reset_admin_password.py --username admin
  python reset_admin_password.py --email admin@spms.local

Purpose:
  Reset the admin password using your app's SQLAlchemy ORM models, ensuring tables exist.
"""

import os
import sys
import argparse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Ensure imports work when running from the backend folder
# Adds the project root to sys.path so "backend.*" resolves
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your app's DB and models
try:
    from backend.database import engine, Base
except Exception as ex:
    print(f"✗ Failed to import backend.database (engine/Base): {ex}")
    print("Tip: run this script from the project root: python backend\\reset_admin_password.py")
    sys.exit(1)

# Adjust the import below to match your actual User model location:
# Common paths: backend.models.user, backend.models.users, backend.models
try:
    from backend.models import User  # change if your User is in a submodule (e.g., backend.models.user)
except Exception as ex:
    print(f"✗ Failed to import User model from backend.models: {ex}")
    print("Try: from backend.models.user import User")
    sys.exit(1)

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Reset admin password (ORM) in SPMS DB")
parser.add_argument("--password", "-p", default="Admin@123", help="New password to set")
parser.add_argument("--username", "-u", default="admin", help="Username to update (ignored if --email provided)")
parser.add_argument("--email", "-e", default=None, help="Email to update (optional)")
args = parser.parse_args()

NEW_PASSWORD = args.password
USERNAME = args.username
EMAIL = args.email

# -----------------------------
# Ensure tables exist
# -----------------------------
try:
    Base.metadata.create_all(bind=engine)
except Exception as ex:
    print(f"✗ Failed to create tables via Base.metadata.create_all: {ex}")
    sys.exit(1)

# -----------------------------
# Hash the new password
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(NEW_PASSWORD)
print(f"Generated hash: {hashed_password}")

# -----------------------------
# Update via ORM
# -----------------------------
def set_user_password(user_obj, hashed):
    """
    Sets the password on the User model, supporting either 'password_hash' or 'hashed_password'.
    """
    if hasattr(user_obj, "password_hash"):
        user_obj.password_hash = hashed
    elif hasattr(user_obj, "hashed_password"):
        user_obj.hashed_password = hashed
    else:
        raise AttributeError("User model lacks a password field ('password_hash' or 'hashed_password').")

with Session(engine) as session:
    # Find target user by email (preferred if provided) or by username
    if EMAIL:
        user = session.query(User).filter(User.email == EMAIL).first()
        target_desc = f"email='{EMAIL}'"
    else:
        user = session.query(User).filter(User.username == USERNAME).first()
        target_desc = f"username='{USERNAME}'"

    if not user:
        print(f"⚠️ No user found with {target_desc}.")
        print("If the admin user doesn't exist, create it via the setup endpoint:")
        print("  POST /setup/create-admin")
        sys.exit(2)

    try:
        set_user_password(user, hashed_password)
        session.commit()
        print(f"✓ Admin password reset successfully for {target_desc}")
    except Exception as ex:
        session.rollback()
        print(f"✗ Failed to update password: {ex}")
        sys.exit(1)

print("\nYou can now log in with:")
print(f"  username: {user.username}")
print(f"  password: {NEW_PASSWORD}")
print("\nNext:")
print("  1) Log in at /login (Swagger or Postman)")
print("  2) Copy access_token from response")
print("  3) Authorize with 'Bearer <token>'")
