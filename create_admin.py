from database import SessionLocal
from models import User
from auth.utils import hash_password

db = SessionLocal()

# Check if admin already exists
existing_admin = db.query(User).filter(User.username == "admin").first()

if existing_admin:
    print("⚠️ Admin user already exists!")
    print(f"Username: {existing_admin.username}")
    print(f"Role: {existing_admin.role}")
else:
    # Create admin user
    admin = User(
        username="admin",
        password_hash=hash_password("Admin123"),
        role="admin",
        full_name="System Administrator",
        email="admin@spms.local"
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("✅ Admin user created successfully!")
    print(f"Username: {admin.username}")
    print(f"Password: Admin123")
    print(f"Role: {admin.role}")

db.close()