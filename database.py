# spms_db/backend/database.py
import os
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, pool, Engine, text  # Add text here
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError

# Logging
logger = logging.getLogger("spms_database")

# -------------------------
# Configuration
# -------------------------

# Load database URL from environment, default to a local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spms_dev.db")

# Database connection pool settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

# Echo SQL queries (useful for debugging)
ECHO_SQL = os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes")

# Environment
SPMS_ENV = os.getenv("SPMS_ENV", "development").lower()
IS_PRODUCTION = SPMS_ENV in ("production", "prod")


# -------------------------
# Database-specific Configuration
# -------------------------

def get_engine_config(database_url: str) -> dict:
    """
    Get database-specific engine configuration.
    
    Args:
        database_url: Database connection URL
    
    Returns:
        dict: Engine configuration parameters
    """
    config = {
        "echo": ECHO_SQL,
        "future": True,
    }
    
    # SQLite-specific settings
    if database_url.startswith("sqlite"):
        config["connect_args"] = {
            "check_same_thread": False,
            "timeout": 20,  # Increase timeout for busy databases
        }
        # SQLite doesn't support connection pooling well
        config["poolclass"] = pool.StaticPool if not IS_PRODUCTION else pool.NullPool
        logger.info("Using SQLite database")
    
    # PostgreSQL-specific settings
    elif database_url.startswith("postgresql"):
        config["pool_size"] = POOL_SIZE
        config["max_overflow"] = MAX_OVERFLOW
        config["pool_timeout"] = POOL_TIMEOUT
        config["pool_recycle"] = POOL_RECYCLE
        config["pool_pre_ping"] = True  # Verify connections before using
        config["connect_args"] = {
            "connect_timeout": 10,
            "options": "-c timezone=utc",  # Set timezone
        }
        logger.info("Using PostgreSQL database")
    
    # MySQL-specific settings
    elif database_url.startswith("mysql"):
        config["pool_size"] = POOL_SIZE
        config["max_overflow"] = MAX_OVERFLOW
        config["pool_timeout"] = POOL_TIMEOUT
        config["pool_recycle"] = POOL_RECYCLE
        config["pool_pre_ping"] = True
        config["connect_args"] = {
            "connect_timeout": 10,
        }
        logger.info("Using MySQL database")
    
    else:
        logger.warning(f"Unknown database type: {database_url.split('://')[0]}")
    
    return config


# -------------------------
# Engine Creation
# -------------------------

# Get configuration
engine_config = get_engine_config(DATABASE_URL)

# Create engine with appropriate configuration
try:
    engine = create_engine(DATABASE_URL, **engine_config)
    logger.info("Database engine created successfully")
except Exception as exc:
    logger.error(f"Failed to create database engine: {exc}")
    raise


# -------------------------
# Event Listeners
# -------------------------

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable foreign keys for SQLite connections.
    SQLite has foreign keys disabled by default.
    """
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.close()
        logger.debug("SQLite pragmas set: foreign_keys=ON, journal_mode=WAL")


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool (debug only)"""
    if ECHO_SQL:
        logger.debug("Connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to the pool (debug only)"""
    if ECHO_SQL:
        logger.debug("Connection returned to pool")


# -------------------------
# Session Factory
# -------------------------

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
    expire_on_commit=False,  # Prevent lazy loading issues after commit
)

# Base class for models
Base = declarative_base()


# -------------------------
# Database Dependency
# -------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes.
    Yields a SQLAlchemy Session and ensures it is closed after use.
    
    Usage:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        logger.error(f"Database error in request: {exc}")
        db.rollback()
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in request: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


# -------------------------
# Context Manager
# -------------------------

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Useful for scripts and background tasks outside of FastAPI.
    
    Usage:
        ```python
        from backend.database import get_db_context
        
        with get_db_context() as db:
            users = db.query(User).all()
            # Session is automatically closed
        ```
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as exc:
        logger.error(f"Error in database context: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


# -------------------------
# Database Utilities
# -------------------------

def create_all_tables():
    """
    Create all database tables.
    Should only be used in development or with migrations in production.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables created successfully")
    except Exception as exc:
        logger.error(f"Failed to create tables: {exc}")
        raise


def drop_all_tables():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    Should only be used in development.
    """
    if IS_PRODUCTION:
        raise RuntimeError("Cannot drop tables in production environment")
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as exc:
        logger.error(f"Failed to drop tables: {exc}")
        raise


def reset_database():
    """
    Drop and recreate all database tables.
    WARNING: This will delete all data!
    Should only be used in development.
    """
    if IS_PRODUCTION:
        raise RuntimeError("Cannot reset database in production environment")
    
    logger.warning("Resetting database...")
    drop_all_tables()
    create_all_tables()
    logger.info("Database reset complete")


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        from sqlalchemy import text  # ensure text is imported at the top
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection check: OK")
        return True
    except Exception as exc:
        logger.error(f"Database connection check failed: {exc}")
        return False


def get_database_info() -> dict:
    """
    Get information about the database connection.
    
    Returns:
        dict: Database information
    """
    info = {
        "url": str(engine.url),
        "driver": engine.url.drivername,
        "database": engine.url.database,
        "pool_size": getattr(engine.pool, "size", lambda: None)(),
        "pool_timeout": getattr(engine.pool, "timeout", lambda: None)(),
        "echo_sql": ECHO_SQL,
    }
    
    # Hide sensitive information
    if "@" in info["url"]:
        info["url"] = info["url"].split("@")[-1]
    
    return info


# -------------------------
# Transaction Utilities
# -------------------------

class TransactionManager:
    """
    Context manager for explicit transaction management.
    
    Usage:
        ```python
        with TransactionManager(db) as tm:
            user = User(username="test")
            tm.add(user)
            # Automatically commits or rolls back
        ```
    """
    
    def __init__(self, session: Session, auto_commit: bool = True):
        self.session = session
        self.auto_commit = auto_commit
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Transaction failed: {exc_val}")
            self.session.rollback()
            return False
        
        if self.auto_commit:
            try:
                self.session.commit()
            except Exception as exc:
                logger.error(f"Commit failed: {exc}")
                self.session.rollback()
                raise


# -------------------------
# Bulk Operations
# -------------------------

def bulk_insert(session: Session, model_class, data: list[dict]) -> int:
    """
    Perform bulk insert operation.
    
    Args:
        session: Database session
        model_class: SQLAlchemy model class
        data: List of dictionaries to insert
    
    Returns:
        int: Number of records inserted
    """
    try:
        session.bulk_insert_mappings(model_class, data)
        session.commit()
        logger.info(f"Bulk inserted {len(data)} {model_class.__name__} records")
        return len(data)
    except Exception as exc:
        logger.error(f"Bulk insert failed: {exc}")
        session.rollback()
        raise


def bulk_update(session: Session, model_class, data: list[dict]) -> int:
    """
    Perform bulk update operation.
    
    Args:
        session: Database session
        model_class: SQLAlchemy model class
        data: List of dictionaries to update (must include primary key)
    
    Returns:
        int: Number of records updated
    """
    try:
        session.bulk_update_mappings(model_class, data)
        session.commit()
        logger.info(f"Bulk updated {len(data)} {model_class.__name__} records")
        return len(data)
    except Exception as exc:
        logger.error(f"Bulk update failed: {exc}")
        session.rollback()
        raise


# -------------------------
# Session Utilities
# -------------------------

def refresh_session(session: Session):
    """
    Refresh session by expiring all objects.
    Useful after bulk operations or external changes.
    """
    session.expire_all()
    logger.debug("Session refreshed")


def clear_session(session: Session):
    """
    Clear session and remove all objects.
    """
    session.expunge_all()
    logger.debug("Session cleared")


# -------------------------
# Startup Check
# -------------------------

# Verify database connection on module import
if __name__ != "__main__":
    try:
        check_database_connection()
    except Exception as exc:
        logger.warning(f"Initial database connection check failed: {exc}")
        logger.warning("Application may have database connectivity issues")


# -------------------------
# Export Public API
# -------------------------

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_db_context",
    "create_all_tables",
    "drop_all_tables",
    "reset_database",
    "check_database_connection",
    "get_database_info",
    "TransactionManager",
    "bulk_insert",
    "bulk_update",
    "refresh_session",
    "clear_session",
]