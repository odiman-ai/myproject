"""
Manage Admin User in SPMS DB

Usage examples:
  # Create a new admin (default username/password)
  python manage_admin.py --create --password admin123

  # Create a new admin with custom credentials
  python manage_admin.py --create --username superadmin --password UltraSecure!456 --email super@spms.local --full-name "Super Admin"

  # Reset password for existing admin
  python manage_admin.py --reset --username admin --password NewPass!234

  # List all users
  python manage_admin.py --list
"""

import argparse
from database import SessionLocal   # ✅ relative import
from models import User             # ✅ relative import
from auth.utils import hash_password  # ✅ relative import

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Manage admin user in SPMS DB")
parser.add_argument("--create", action="store_true", help="Create a new admin user")
parser.add_argument("--reset", action="store_true", help="Reset password for an existing admin user")
parser.add_argument("--list", action="store_true", help="List all users in the database")
parser.add_argument("--username", "-u", default="admin", help="Username")
parser.add_argument("--password", "-p", help="Password (required for create/reset)")
parser.add_argument("--email", "-e", default="admin@spms.local", help="Email (for create only)")
parser.add_argument("--full-name", "-f", default="System Administrator", help="Full name (for create only)")
args = parser.parse_args()

# -----------------------------
# DB session
# -----------------------------
db = SessionLocal()

try:
    if args.create:
        if not args.password:
            print("✗ Please provide --password when creating a user")
        else:
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

    elif args.reset:
        if not args.password:
            print("✗ Please provide --password when resetting a user")
        else:
            user = db.query(User).filter(User.username == args.username).first()
            if not user:
                print(f"✗ No user found with username '{args.username}'.")
                print("Tip: Use --create to create a new admin user.")
            else:
                user.password_hash = hash_password(args.password)
                db.commit()
                print(f"✅ Password reset successfully for user '{args.username}'")

    elif args.list:
        users = db.query(User).all()
        if not users:
            print("✗ No users found in the database.")
        else:
            print("📋 Users in the database:")
            for u in users:
                print(f"- ID: {u.id}, Username: {u.username}, Role: {u.role}, Email: {u.email}")

    else:
        print("✗ Please specify one of --create, --reset, or --list")

finally:
    db.close()
