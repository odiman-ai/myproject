# manage.py
import click
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User
from backend.auth.utils import hash_password


@click.group()
def cli():
    """SPMS Management CLI"""
    pass


# =========================
# RESET PASSWORD COMMAND
# =========================
@cli.command("reset-password")
@click.option(
    "--username",
    default="admin",
    show_default=True,
    help="Username to reset password for",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
)
def reset_password(username, new_password):
    """Reset a user's password"""
    db: Session = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        click.echo(f"❌ User '{username}' not found")
        db.close()
        return

    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    db.close()

    click.echo(f"✅ Password reset successfully for '{username}'")


# =========================
# CREATE USER COMMAND
# =========================
@cli.command("create-user")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", prompt=True)
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=True)
def create_user(username, password, role, full_name, email):
    """Create a new user"""
    db: Session = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        click.echo(f"⚠️ User '{username}' already exists")
        db.close()
        return

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        full_name=full_name,
        email=email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    click.echo(f"✅ Created user '{username}' with role '{role}'")


# =========================
# UNLOCK ACCOUNT COMMAND
@cli.command("unlock-account")
@click.option("--username", prompt=True, help="Username to unlock")
def unlock_account(username):
    """Unlock a locked user account"""
    db: Session = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        click.echo(f"❌ User '{username}' not found")
        db.close()
        return

    # Reset lockout fields
    user.failed_login_attempts = 0
    user.account_locked_until = None

    db.commit()
    db.refresh(user)
    db.close()

    click.echo(f"🔓 Account '{username}' unlocked successfully")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    cli()
