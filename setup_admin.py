# setup_admin.py
"""
Setup script to create initial admin user for SPMS
Run this once after database initialization

Usage:
    python setup_admin.py
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine, Base
from backend.models import User
from backend.auth import hash_password


def create_admin_user():
    """Create the initial admin user if it doesn't exist"""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("\n⚠️  Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Status: {existing_admin.status}")
            
            response = input("\nDo you want to reset the admin password? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                new_password = input("Enter new password (must have uppercase, lowercase, number): ")
                existing_admin.password_hash = hash_password(new_password)
                existing_admin.failed_login_attempts = 0
                existing_admin.account_locked_until = None
                existing_admin.status = "active"
                db.commit()
                print(f"✓ Admin password reset successfully!")
                print(f"\n🔐 Login Credentials:")
                print(f"   Username: admin")
                print(f"   Password: {new_password}")
            return
        
        # Create new admin user
        print("\nCreating admin user...")
        
        admin_user = User(
            username="admin",
            password_hash=hash_password("Admin123!"),  # Strong default password
            full_name="System Administrator",
            email="admin@spms.local",
            role="admin",
            status="active",
            created_at=datetime.now(timezone.utc),
            failed_login_attempts=0,
            account_locked_until=None,
            last_login=None
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("\n✅ Admin user created successfully!")
        print("\n" + "="*50)
        print("🔐 DEFAULT LOGIN CREDENTIALS")
        print("="*50)
        print(f"Username: admin")
        print(f"Password: Admin123!")
        print(f"Role:     {admin_user.role}")
        print(f"Email:    {admin_user.email}")
        print("="*50)
        print("\n⚠️  IMPORTANT: Change the default password after first login!")
        print("\n📝 Next Steps:")
        print("1. Start your FastAPI server: uvicorn main:app --reload")
        print("2. Go to http://localhost:8000/docs")
        print("3. Click 'Authorize' button (🔓)")
        print("4. Login with above credentials")
        print("5. All endpoints will work automatically!")
        
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_users():
    """Create sample users for testing"""
    db = SessionLocal()
    
    try:
        print("\n\nDo you want to create sample users for testing?")
        response = input("(yes/no): ")
        
        if response.lower() not in ['yes', 'y']:
            return
        
        # FIXED: Updated passwords to meet validation requirements
        sample_users = [
            {
                "username": "john_staff",
                "password": "Staff123!",  # Strong password
                "full_name": "John Doe",
                "email": "john.staff@example.com",
                "role": "staff"
            },
            {
                "username": "jane_participant",
                "password": "Participant123!",  # Strong password
                "full_name": "Jane Smith",
                "email": "jane.participant@example.com",
                "role": "participant"
            },
            {
                "username": "bob_staff",
                "password": "Staff456!",  # Strong password
                "full_name": "Bob Johnson",
                "email": "bob.staff@example.com",
                "role": "staff"
            }
        ]
        
        print("\nCreating sample users...")
        created_count = 0
        
        for user_data in sample_users:
            try:
                existing = db.query(User).filter(
                    User.username == user_data["username"]
                ).first()
                
                if existing:
                    print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
                    continue
                
                new_user = User(
                    username=user_data["username"],
                    password_hash=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    role=user_data["role"],
                    status="active",
                    created_at=datetime.now(timezone.utc),
                    failed_login_attempts=0
                )
                
                db.add(new_user)
                db.flush()  # Flush to catch validation errors per user
                
                print(f"✓ Created {user_data['role']}: {user_data['username']} (password: {user_data['password']})")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Failed to create {user_data['username']}: {e}")
                db.rollback()
                continue
        
        if created_count > 0:
            db.commit()
            print(f"\n✅ {created_count} sample user(s) created successfully!")
        else:
            print("\n⚠️  No new users were created")
        
    except Exception as e:
        print(f"\n❌ Error in create_sample_users: {e}")
        db.rollback()
    finally:
        db.close()


def verify_database():
    """Verify database connection and tables"""
    print("\nVerifying database setup...")
    db = SessionLocal()
    
    try:
        # Test database connection
        user_count = db.query(User).count()
        print(f"✓ Database connection successful")
        print(f"✓ Total users in database: {user_count}")
        
        # List all users - with better error handling
        if user_count > 0:
            print("\n📋 Current Users:")
            print("-" * 75)
            print(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<15} {'Status':<10}")
            print("-" * 75)
            
            try:
                users = db.query(User).all()
                for user in users:
                    # Safe access to user properties
                    user_id = getattr(user, 'id', 'N/A')
                    username = getattr(user, 'username', 'N/A')
                    full_name = getattr(user, 'full_name', 'N/A')
                    role = getattr(user, 'role', 'N/A')
                    status = getattr(user, 'status', 'N/A')
                    
                    print(f"{user_id:<5} {username:<20} {full_name:<25} {role:<15} {status:<10}")
                print("-" * 75)
            except Exception as e:
                print(f"⚠️  Could not display all users: {e}")
                print("    This might be due to existing users with invalid role values")
                print("    New users created by this script should work correctly")
    
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        raise
    finally:
        db.close()


def cleanup_invalid_users():
    """Optional: Clean up users with invalid roles"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*50)
        print("DATABASE CLEANUP (Optional)")
        print("="*50)
        print("\nYour database has users with invalid role 'user'.")
        print("Valid roles are: admin, staff, participant")
        print("\nOptions:")
        print("1. Delete users with invalid roles")
        print("2. Update 'user' role to 'participant'")
        print("3. Skip cleanup")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            # Delete invalid users
            result = db.execute(
                "DELETE FROM users WHERE role NOT IN ('admin', 'staff', 'participant')"
            )
            db.commit()
            print(f"✓ Deleted {result.rowcount} user(s) with invalid roles")
            
        elif choice == "2":
            # Update user role to participant
            result = db.execute(
                "UPDATE users SET role = 'participant' WHERE role = 'user'"
            )
            db.commit()
            print(f"✓ Updated {result.rowcount} user(s) from 'user' to 'participant' role")
            
        else:
            print("Skipping cleanup")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*50)
    print("SPMS Admin User Setup")
    print("="*50)
    
    try:
        create_admin_user()
        create_sample_users()
        cleanup_invalid_users()
        verify_database()
        
        print("\n" + "="*50)
        print("✅ Setup completed successfully!")
        print("="*50)
        print("\n📝 Available Roles in Your System:")
        print("   • admin       - Full system access")
        print("   • staff       - Staff member access")
        print("   • participant - Participant access")
        print("\n💡 Password Requirements:")
        print("   • At least 8 characters")
        print("   • At least one uppercase letter")
        print("   • At least one lowercase letter")
        print("   • At least one number")
        print("\n🔐 Test Credentials Created:")
        print("   Admin:       admin / Admin123!")
        print("   Staff:       john_staff / Staff123!")
        print("   Participant: jane_participant / Participant123!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)