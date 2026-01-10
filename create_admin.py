"""
Run:
  python create_admin.py --username admin --password NewPass!234

Purpose:
  Create or reset the admin user in the SPMS database.
  - Prevents duplicate creation
  - Hashes password securely
  - Allows username/password via command line
"""

import argparse
from database import SessionLocal
from models import User
from auth.utils import hash_password

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Create or reset admin user in SPMS DB")
parser.add_argument("--username", "-u", default="admin", help="Admin username")
parser.add_argument("--password", "-p", default="admin123", help="Admin password")
parser.add_argument("--email", "-e", default="admin@spms.local", help="Admin email")
parser.add_argument("--full-name", "-f", default="System Administrator", help="Admin full name")
args = parser.parse_args()

# -----------------------------
# DB session
# -----------------------------
db = SessionLocal()

try:
    existing = db.query(User).filter(User.username == args.username).first()

    if existing:
        print(f"⚠️ User '{args.username}' already exists. Updating password instead...")
        existing.password_hash = hash_password(args.password)
        db.commit()
        print(f"✅ Password updated successfully for user '{args.username}'")
    else:
        admin = User(
            username=args.username,
            password_hash=hash_password(args.password),
            role="admin",
            full_name=args.full_name,
            email=args.email
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Admin user created successfully!")
        print(f"Username: {admin.username}")
        print("Password: (set securely)")
        print(f"Role: {admin.role}")

finally:
    db.close()
