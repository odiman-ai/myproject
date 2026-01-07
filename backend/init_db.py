# backend/init_db.py
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import Base, engine, get_db_context
from backend.models import User
from backend.auth.utils import hash_password

def create_test_user():
    """Create a test user for login testing"""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Create test user
    with get_db_context() as db:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if existing_user:
            print("⚠ Test user 'admin' already exists")
            print(f"  Username: admin")
            print(f"  Role: {existing_user.role}")
            return
        
        # Create new admin user
        test_user = User(
            username="admin",
            password_hash=hash_password("admin123"),  # Password: admin123
            full_name="System Administrator",
            email="admin@spms.local",
            phone="+256773965088",
            role="admin",
            status="active"
        )
        
        db.add(test_user)
        db.commit()
        
        print("✓ Test user created successfully!")
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS:")
        print("="*50)
        print("Username: admin")
        print("Password: admin123")
        print("Role: admin")
        print("="*50)

if __name__ == "__main__":
    create_test_user()