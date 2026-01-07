#!/usr/bin/env python3
"""
Small script to unlock a user account by resetting failed_login_attempts
and clearing account_locked_until.

Usage:
  python scripts/unlock_user.py --username admin
  python scripts/unlock_user.py --username "john" --commit
By default it will perform a dry-run and show what it would change.
"""
import argparse
from sqlalchemy import func
from backend.database import SessionLocal
from backend.models import User

def unlock_user(username: str, commit: bool = False) -> None:
    db = SessionLocal()
    try:
        uname_norm = (username or "").strip().lower()
        user = db.query(User).filter(func.lower(User.username) == uname_norm).first()
        if not user:
            print(f"User not found: {username}")
            return

        print(f"Found user: id={user.id}, username={user.username}, status={getattr(user, 'status', None)}")

        changed = False
        # Try common names for failed attempts
        if hasattr(user, "failed_login_attempts"):
            if getattr(user, "failed_login_attempts") != 0:
                print(f" - will reset failed_login_attempts from {getattr(user, 'failed_login_attempts')} -> 0")
                user.failed_login_attempts = 0
                changed = True
        elif hasattr(user, "failed_attempts"):
            if getattr(user, "failed_attempts") != 0:
                print(f" - will reset failed_attempts from {getattr(user, 'failed_attempts')} -> 0")
                user.failed_attempts = 0
                changed = True
        else:
            print(" - no failed attempts column found on User model")

        # Try common names for lock timestamp
        if hasattr(user, "account_locked_until"):
            if getattr(user, "account_locked_until") is not None:
                print(f" - will clear account_locked_until (was {getattr(user, 'account_locked_until')})")
                user.account_locked_until = None
                changed = True
        elif hasattr(user, "locked_until"):
            if getattr(user, "locked_until") is not None:
                print(f" - will clear locked_until (was {getattr(user, 'locked_until')})")
                user.locked_until = None
                changed = True
        else:
            print(" - no lock timestamp column found on User model")

        if not changed:
            print("Nothing to change for this user.")
            return

        if commit:
            db.commit()
            print("Changes committed.")
        else:
            db.rollback()
            print("Dry-run (no changes committed). Rerun with --commit to apply changes.")
    except Exception as exc:
        db.rollback()
        print(f"Error: {exc}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Unlock a user account (reset failed attempts and clear lock timestamp)")
    p.add_argument("--username", "-u", required=True, help="Username to unlock")
    p.add_argument("--commit", action="store_true", help="If set, commit changes. Otherwise run as dry-run.")
    args = p.parse_args()
    unlock_user(args.username, commit=args.commit)