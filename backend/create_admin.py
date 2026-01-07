from database import SessionLocal
from models import User
from auth.utils import hash_password

db = SessionLocal()

# Create admin user
admin = User(
    username="admin",
    password_hash=hash_password("admin123"),
    role="admin",
    full_name="System Administrator",
    email="admin@spms.local"
)

db.add(admin)
db.commit()
db.refresh(admin)

print(f"✅ Admin user created successfully!")
print(f"Username: {admin.username}")
print(f"Password: admin123")
print(f"Role: {admin.role}")

db.close()