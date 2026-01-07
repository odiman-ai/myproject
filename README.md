# SPMS Backend

## Overview
This repository contains the SPMS backend (FastAPI + SQLAlchemy).  
Key files:
- `backend/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, and `get_db`.
- `backend/models.py` — ORM models (already present).
- `backend/main.py` — FastAPI application entrypoint.

## Environment
Set environment variables as needed. Example (development):

```bash
# Windows PowerShell
$env:DATABASE_URL = "sqlite:///./spms_dev.db"
$env:SECRET_KEY = "change-this-in-production"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"
$env:SPMS_ENV = "development"
