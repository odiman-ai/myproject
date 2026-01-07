# setup_db.py
import sys
import os
from pathlib import Path

# Get absolute path to project root
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Change to project directory
os.chdir(project_root)

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")
print("=" * 60)

from backend.database import Base, engine, SessionLocal
from backend.models import User
from backend.auth.utils import hash_password

print("Setting up SPMS Database")
print("=" * 60)

try:
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Create test user
    print("\nCreating test user...")
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.username == "admin").first()
        
        if existing:
            print("⚠ User 'admin' already exists")
            print(f"  ID: {existing.id}")
            print(f"  Username: {existing.username}")
            print(f"  Role: {existing.role}")
            print(f"  Status: {existing.status}")
        else:
            # Create new user
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="System Administrator",
                email="admin@spms.local",
                phone="+256773965088",
                role="admin",
                status="active"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            print("✓ Test user created successfully!")
            print(f"  ID: {admin.id}")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  Role: {admin.role}")
            print(f"  Status: {admin.status}")
    finally:
        db.close()
    
    # Verify database file
    db_file = project_root / "spms_dev.db"
    if db_file.exists():
        print(f"\n✓ Database file created: {db_file}")
        print(f"  Size: {db_file.stat().st_size} bytes")
    
    print("\n" + "=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)
    print("\nNow run the server:")
    print("  python -m uvicorn test_server:app --reload --port 8000")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()