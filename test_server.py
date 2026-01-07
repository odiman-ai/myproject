# test_server.py (in spms_db folder)
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import User
from backend.auth.utils import verify_password, create_access_token, hash_password

app = FastAPI(title="SPMS Test API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SPMS Backend Test", "status": "running", "docs": "/docs"}

@app.get("/api/v1/health")
def health():
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": "1.0.0",
        "database": db_status
    }

@app.post("/api/v1/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Test login endpoint"""
    print(f"Login attempt: {form_data.username}")
    
    user = db.query(User).filter(User.username == form_data.username.lower()).first()
    
    if not user:
        print(f"User not found: {form_data.username}")
        return {"detail": "Invalid username or password"}
    
    if not verify_password(form_data.password, user.password_hash):
        print(f"Invalid password for: {form_data.username}")
        return {"detail": "Invalid username or password"}
    
    if user.status != "active":
        print(f"User not active: {form_data.username}")
        return {"detail": f"Account is {user.status}"}
    
    print(f"Login successful: {form_data.username}")
    token = create_access_token({"sub": user.username, "role": user.role, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.on_event("startup")
def startup():
    print("=" * 60)
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")
        
        # Create test user if doesn't exist
        with get_db().__next__() as db:
            existing = db.query(User).filter(User.username == "admin").first()
            if not existing:
                test_user = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    full_name="Test Admin",
                    email="admin@test.com",
                    role="admin",
                    status="active"
                )
                db.add(test_user)
                db.commit()
                print("✓ Test user created: admin / admin123")
            else:
                print("✓ Test user already exists: admin / admin123")
    except Exception as e:
        print(f"✗ Error during startup: {e}")
    
    print("=" * 60)
    print("✓ SPMS Test Backend Started")
    print("✓ Login at: http://127.0.0.1:8000/docs")
    print("✓ Health: http://127.0.0.1:8000/api/v1/health")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)