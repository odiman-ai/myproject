"""
Run:
  python reset_admin.py --password NewPass!234
  python reset_admin.py --username admin --password Secure!Pass

Purpose:
  Reset the password for an existing admin user in the SPMS database.
  - Updates only the password field
  - Prevents duplicate creation
"""

import argparse
from database import SessionLocal
from models import User
from auth.utils import hash_password

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Reset admin password in SPMS DB")
parser.add_argument("--username", "-u", default="admin", help="Admin username")
parser.add_argument("--password", "-p", required=True, help="New password to set")
args = parser.parse_args()

# -----------------------------
# DB session
# -----------------------------
db = SessionLocal()

try:
    user = db.query(User).filter(User.username == args.username).first()

    if not user:
        print(f"✗ No user found with username '{args.username}'.")
        print("Tip: Run create_admin.py first to create the admin user.")
    else:
        user.password_hash = hash_password(args.password)
        db.commit()
        print(f"✅ Password reset successfully for user '{args.username}'")
finally:
    db.close()
