# create_users.py
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User
from auth.utils import hash_password

# Define the users you want to add
users_to_create = [
    {
        "username": "SIMON Akalees Odiman",
        "password": "admin123",   # default password
        "role": "admin",
        "full_name": "System Admin",
        "email": "simon@spms.local"
    },
    {
        "username": "ODEKE David",
        "password": "password123",
        "role": "staff",
        "full_name": "Staff",
        "email": "odeke@spms.local"
    },
    {
        "username": "JOL Duop",
        "password": "password123",
        "role": "staff",
        "full_name": "Staff",
        "email": "jol@spms.local"
    },
    {
        "username": "AYUGI Grace",
        "password": "password123",
        "role": "staff",
        "full_name": "Staff",
        "email": "ayugi@spms.local"
    },
    {
        "username": "MANSHUR Isa",
        "password": "password123",
        "role": "staff",
        "full_name": "Staff",
        "email": "manshur@spms.local"
    },
    {
        "username": "DUKU James",
        "password": "password123",
        "role": "staff",
        "full_name": "Staff",
        "email": "duku@spms.local"
    },
]

def main():
    db: Session = SessionLocal()

    for u in users_to_create:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            print(f"⚠️ User {u['username']} already exists, skipping...")
            continue

        new_user = User(
            username=u["username"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            full_name=u["full_name"],
            email=u["email"]
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ Created user: {new_user.username} ({new_user.role})")

    db.close()

if __name__ == "__main__":
    main()
