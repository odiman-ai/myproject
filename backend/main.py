# spms_db/backend/main.py
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text

# Add parent directory to path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ===== CONFIGURATION - MUST BE FIRST =====
SPMS_ENV = os.getenv("SPMS_ENV", "development").lower()
DEBUG_MODE = SPMS_ENV in ("development", "dev", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG_MODE else "DEBUG")
PORT = int(os.getenv("PORT", 8000))

# Logging configuration
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("spms_backend")

# Security: Ensure SECRET_KEY is set in production
if not DEBUG_MODE:
    if not os.getenv("SECRET_KEY"):
        logger.error("SECRET_KEY environment variable must be set in production!")
        sys.exit(1)
    if not os.getenv("DATABASE_URL"):
        logger.error("DATABASE_URL environment variable must be set in production!")
        sys.exit(1)

# ===== NOW IMPORT BACKEND MODULES =====
from backend.database import Base, engine, SessionLocal
from backend.models import User
from backend.auth.utils import hash_password
from backend.auth.routes_simple import router as auth_router

# App metadata
APP_TITLE = "Smart Participants Management System (SPMS)"
APP_DESCRIPTION = """
## Humanitarian Social Protection Management API

A comprehensive system for managing humanitarian programs, participants, and activities.

### Features:
* 🔐 **Authentication & Authorization** - Secure JWT-based auth with role-based access
* 👥 **Household Management** - Track families and individual members
* 📊 **Programme & Project Management** - Organize humanitarian interventions
* 📅 **Activity & Attendance Tracking** - Monitor participation and engagement
* 📋 **Survey & M&E** - Data collection and impact measurement
* 🔍 **Case Management** - Track and resolve participant issues
* 📈 **Reporting** - Generate comprehensive reports

### Support Contact:
**Engineer Simon Akalees Odiman**
- 📧 Email: oakalees@yahoo.com
- 📱 Phone: +256 773 965 088 / +256 755 002 896
- 📍 Location: Kampala, Uganda
"""
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# CORS origins configuration
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",  # Allow all for development testing
]

allow_origins = os.getenv("SPMS_CORS_ORIGINS")
if allow_origins:
    origins = [o.strip() for o in allow_origins.split(",") if o.strip()]
else:
    origins = DEFAULT_ORIGINS
    if not DEBUG_MODE:
        logger.warning("Using default CORS origins in production. Set SPMS_CORS_ORIGINS environment variable.")


# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application."""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting SPMS Backend")
    logger.info(f"Environment: {SPMS_ENV}")
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info(f"API Version: {APP_VERSION}")
    logger.info("=" * 60)
    
    # Create database tables in development
    if DEBUG_MODE:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✓ Database tables created/verified")
            
            # Create default admin user if doesn't exist
            db = SessionLocal()
            try:
                admin = db.query(User).filter(User.username == "admin").first()
                if not admin:
                    # Use the hash_password function from auth.utils
                    admin = User(
                        username="admin",
                        password_hash=hash_password("admin123", validate_policy=False),
                        full_name="System Administrator",
                        email="admin@spms.local",
                        phone="+256773965088",
                        role="admin",
                        status="active"
                    )
                    db.add(admin)
                    db.commit()
                    logger.info("✓ Default admin user created")
                    logger.info("  Username: admin")
                    logger.info("  Password: admin123")
                else:
                    logger.info("✓ Admin user exists")
                    logger.info("  Username: admin")
                    logger.info("  Password: admin123")
            except Exception as e:
                logger.error(f"Error creating admin user: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as exc:
            logger.exception("✗ Error during startup: %s", exc)
            if not DEBUG_MODE:
                raise
    else:
        logger.info("Production mode: Skipping automatic table creation")
    
    # Verify database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection verified")
    except Exception as exc:
        logger.error("✗ Database connection failed: %s", exc)
        if not DEBUG_MODE:
            raise
    
    logger.info("✓ SPMS Backend started successfully")
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down SPMS Backend...")
    logger.info("✓ SPMS Backend shutdown complete")


# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    openapi_url="/openapi.json" if DEBUG_MODE else None,
)


# -------------------------
# Middleware Configuration
# -------------------------

# CORS Middleware - ALLOW ALL FOR TESTING
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Total-Count"],
)

# GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# -------------------------
# Static Files
# -------------------------
try:
    frontend_path = Path(__file__).resolve().parent.parent / "frontend" / "src" / "images"
    if frontend_path.exists():
        app.mount("/images", StaticFiles(directory=str(frontend_path)), name="images")
        logger.info("✓ Static files mounted from: %s", frontend_path)
    else:
        logger.debug("Frontend images path not found: %s", frontend_path)
except Exception as exc:
    logger.warning("Could not mount static files: %s", exc)


# -------------------------
# Exception Handlers
# -------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent JSON response"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed information"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })
    
    logger.warning("Validation error on %s: %s", request.url.path, errors)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
    
    detail = str(exc) if DEBUG_MODE else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "status_code": 500,
            "path": str(request.url),
        },
    )


# -------------------------
# Middleware - Request Logging
# -------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring and debugging"""
    import time
    
    start_time = time.time()
    logger.debug(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.debug(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] {process_time:.3f}s"
    )
    
    return response


# -------------------------
# Router Registration
# -------------------------

# Register auth router
app.include_router(auth_router, tags=["Authentication"])
logger.info(f"✓ Router registered: /api/v1/auth (Authentication)")


# -------------------------
# Root Endpoints
# -------------------------

@app.get("/", tags=["Root"], summary="API Root")
def root() -> Dict[str, Any]:
    """API root endpoint providing basic information and links."""
    return {
        "message": APP_TITLE,
        "version": APP_VERSION,
        "environment": SPMS_ENV,
        "status": "running",
        "endpoints": {
            "docs": "/docs" if DEBUG_MODE else "Documentation disabled in production",
            "redoc": "/redoc" if DEBUG_MODE else "ReDoc disabled in production",
            "health": "/health",
            "api": API_PREFIX,
        },
        "api_version": "v1",
        "support": {
            "contact": "Engineer Simon Akalees Odiman",
            "email": "oakalees@yahoo.com",
            "phone": ["+256773965088", "+256755002896"],
            "location": "Kampala, Uganda"
        }
    }


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "version": APP_VERSION,
        "environment": SPMS_ENV,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        health_status["checks"]["database"] = {
            "status": "connected",
            "type": str(engine.url).split("://")[0],
        }
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = {
            "status": "disconnected",
            "error": str(exc) if DEBUG_MODE else "Connection failed",
        }
    
    # Application checks
    health_status["checks"]["application"] = {
        "status": "running",
        "debug_mode": DEBUG_MODE,
    }
    
    return health_status


# Add API-prefixed health endpoint for compatibility
@app.get(f"{API_PREFIX}/health", tags=["Health"], summary="Health Check (API Prefix)")
def health_check_api() -> Dict[str, Any]:
    """Alias health endpoint under the API prefix."""
    return health_check()


@app.get(f"{API_PREFIX}/info", tags=["Root"], summary="API Information")
def api_info() -> Dict[str, Any]:
    """Get detailed API information.""" 
    return {
        "title": APP_TITLE,
        "version": APP_VERSION,
        "api_prefix": API_PREFIX,
        "environment": SPMS_ENV,
        "modules": [
            {"name": "Authentication", "prefix": f"{API_PREFIX}/auth", "status": "active"}
        ],
        "features": [
            "JWT Authentication",
            "Role-based Access Control",
            "Account Security (lockout, password policy)",
            "Token Management",
        ],
    }


# -------------------------
# Development Endpoints
# -------------------------

if DEBUG_MODE:
    @app.get("/debug/routes", tags=["Debug"], summary="List All Routes")
    def debug_routes():
        """List all registered routes (development only)"""
        routes = []
        for route in app.routes:
            if hasattr(route, "methods"):
                routes.append({
                    "path": route.path,
                    "name": route.name,
                    "methods": list(route.methods),
                })
        return {"routes": routes, "count": len(routes)}
    
    
    @app.get("/debug/config", tags=["Debug"], summary="Show Configuration")
    def debug_config():
        """Show current configuration (development only)"""
        return {
            "environment": SPMS_ENV,
            "debug_mode": DEBUG_MODE,
            "log_level": LOG_LEVEL,
            "cors_origins": origins,
            "api_prefix": API_PREFIX,
            "database_url": str(engine.url).split("@")[-1] if "@" in str(engine.url) else str(engine.url),
        }


# -------------------------
# Startup Message
# -------------------------

logger.info("=" * 60)
logger.info("SPMS Backend Configuration Complete")
logger.info(f"Environment: {SPMS_ENV}")
logger.info(f"API Prefix: {API_PREFIX}")
logger.info(f"Debug Mode: {DEBUG_MODE}")
logger.info("=" * 60)
logger.info("Start server with:")
logger.info("  python -m uvicorn backend.main:app --reload --port 8000")
logger.info("=" * 60)

# For running with uvicorn directly (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG_MODE,
        log_level=LOG_LEVEL.lower(),
    )