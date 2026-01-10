# cleanup_users.py
"""
Clean up users with invalid roles
Run this to fix the 'user' role issue

Usage:
    python cleanup_users.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from sqlalchemy import text


def cleanup_invalid_users():
    """Fix users with invalid 'user' role"""
    db = SessionLocal()
    
    try:
        print("="*50)
        print("Database Cleanup - Invalid User Roles")
        print("="*50)
        
        # Check for invalid users
        result = db.execute(text(
            "SELECT id, username, email, role FROM users WHERE role NOT IN ('admin', 'staff', 'participant')"
        ))
        invalid_users = result.fetchall()
        
        if not invalid_users:
            print("\n✓ No invalid users found. Database is clean!")
            return
        
        print(f"\nFound {len(invalid_users)} user(s) with invalid roles:")
        print("-" * 70)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Current Role':<15}")
        print("-" * 70)
        
        for user in invalid_users:
            print(f"{user[0]:<5} {user[1]:<20} {user[2]:<30} {user[3]:<15}")
        
        print("-" * 70)
        print("\nOptions:")
        print("1. Update role 'user' → 'participant'")
        print("2. Delete these users")
        print("3. Cancel")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            # Update users
            db.execute(text(
                "UPDATE users SET role = 'participant' WHERE role = 'user'"
            ))
            db.execute(text(
                "UPDATE users SET role = 'participant' WHERE role NOT IN ('admin', 'staff', 'participant')"
            ))
            db.commit()
            
            print("\n✅ Updated all invalid roles to 'participant'")
            
            # Verify
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE role = 'participant'"))
            count = result.scalar()
            print(f"✓ Total participants now: {count}")
            
        elif choice == "2":
            # Delete users
            confirm = input("\n⚠️  Are you sure? This cannot be undone! (yes/no): ")
            if confirm.lower() == 'yes':
                db.execute(text(
                    "DELETE FROM users WHERE role NOT IN ('admin', 'staff', 'participant')"
                ))
                db.commit()
                print("\n✅ Deleted users with invalid roles")
        else:
            print("\n❌ Cancelled")
            return
        
        # Show final state
        print("\n" + "="*50)
        print("Final User Count by Role:")
        print("="*50)
        
        result = db.execute(text(
            "SELECT role, COUNT(*) FROM users GROUP BY role"
        ))
        
        for row in result:
            print(f"  {row[0]:<15}: {row[1]} users")
        
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        cleanup_invalid_users()
        print("\n✅ Cleanup completed!")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Failed: {e}")