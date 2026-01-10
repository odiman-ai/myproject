import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any
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

# ===== CONFIGURATION =====
SPMS_ENV = os.getenv("SPMS_ENV", "development").lower()
DEBUG_MODE = SPMS_ENV in ("development", "dev", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG_MODE else "DEBUG")
PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("spms_backend")

# Security checks for production
if not DEBUG_MODE:
    if not os.getenv("SECRET_KEY"):
        logger.error("SECRET_KEY environment variable must be set in production!")
        sys.exit(1)
    if not os.getenv("DATABASE_URL"):
        logger.error("DATABASE_URL environment variable must be set in production!")
        sys.exit(1)

# ===== IMPORT BACKEND MODULES =====
from backend.database import Base, engine, SessionLocal
from backend.models import User
from backend.auth.routes_simple import router as auth_router

# Import feature routers directly
from backend.households.routes import router as households_router
from backend.programmes.routes import router as programmes_router
from backend.activities.routes import router as activities_router
from backend.attendance.routes import router as attendance_router
from backend.surveys.routes import router as surveys_router
from backend.cases.routes import router as cases_router
from backend.reports.routes import router as reports_router

APP_TITLE = "Smart Participants Management System (SPMS)"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# ===== FASTAPI APP =====
app = FastAPI(
    title=APP_TITLE,
    description="Humanitarian Social Protection Management API",
    version=APP_VERSION,
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    openapi_url="/openapi.json" if DEBUG_MODE else None,
)

# ===== MIDDLEWARE =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Total-Count"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ===== ROUTER REGISTRATION =====
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(households_router, prefix=f"{API_PREFIX}/households", tags=["Households"])
app.include_router(programmes_router, prefix=f"{API_PREFIX}/programmes", tags=["Programmes"])
app.include_router(activities_router, prefix=f"{API_PREFIX}/activities", tags=["Activities"])
app.include_router(attendance_router, prefix=f"{API_PREFIX}/attendance", tags=["Attendance"])
app.include_router(surveys_router, prefix=f"{API_PREFIX}/surveys", tags=["Surveys"])
app.include_router(cases_router, prefix=f"{API_PREFIX}/cases", tags=["Cases"])
app.include_router(reports_router, prefix=f"{API_PREFIX}/reports", tags=["Reports"])

logger.info("✓ Routers registered successfully")

# ===== STATIC FILES =====
try:
    frontend_path = Path(__file__).resolve().parent.parent / "frontend" / "src" / "images"
    if frontend_path.exists():
        app.mount("/images", StaticFiles(directory=str(frontend_path)), name="images")
        logger.info("✓ Static files mounted from: %s", frontend_path)
except Exception as exc:
    logger.warning("Could not mount static files: %s", exc)

# ===== EXCEPTION HANDLERS =====
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code, "path": str(request.url)},
        headers=exc.headers,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    logger.warning("Validation error on %s: %s", request.url.path, errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors, "path": str(request.url)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
    detail = str(exc) if DEBUG_MODE else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "status_code": 500, "path": str(request.url)},
    )

# ===== ROOT ENDPOINTS =====
@app.get("/", tags=["Root"])
def root() -> Dict[str, Any]:
    return {
        "message": APP_TITLE,
        "version": APP_VERSION,
        "environment": SPMS_ENV,
        "status": "running",
        "endpoints": {
            "docs": "/docs" if DEBUG_MODE else "disabled",
            "redoc": "/redoc" if DEBUG_MODE else "disabled",
            "health": "/health",
            "api": API_PREFIX,
            "login": "/login",
            "info": f"{API_PREFIX}/info"
        }
    }

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": APP_VERSION,
        "environment": SPMS_ENV,
        "database": db_status,
    }
