from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db
from backend.models import User  # adjust import path if needed
from fastapi import Depends
import typer

app = typer.Typer()

@app.command()
def unlock_user(username: str, commit: bool = False, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Database connection check failed: {e}")

    user = db.query(User).filter(User.username == username).first()

    if not user:
        print(f"User '{username}' not found.")
        return

    print(f"Found user: id={user.id}, username={user.username}, status={user.status}")

    changes = False

    if user.failed_login_attempts > 0:
        print(f" - will reset failed_login_attempts from {user.failed_login_attempts} -> 0")
        user.failed_login_attempts = 0
        changes = True

    if user.account_locked:
        print(" - will clear account_locked flag")
        user.account_locked = False
        changes = True

    if changes:
        if commit:
            db.commit()
            print("✅ Changes committed.")
        else:
            print("ℹ️ Run with --commit to apply changes.")
    else:
        print("Nothing to change for this user.")
