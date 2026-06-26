"""
Database Session Configuration
"""
import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Generator

from .base import Base

logger = logging.getLogger(__name__)

# Database configuration - use absolute path to avoid working directory issues
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_DB_PATH = _BACKEND_DIR / "rare_disease_diagnosis.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{_DEFAULT_DB_PATH}"
)

# Create engine
# For SQLite: check_same_thread=False allows multiple threads
# For PostgreSQL/MySQL: pool_size and max_overflow control connection pooling
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 3600

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread-safe access
db_session = scoped_session(SessionLocal)


def get_db() -> Generator:
    """
    Dependency for FastAPI to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def verify_tables(eng=None) -> bool:
    """
    Verify that all expected database tables exist.
    Returns True if all tables are present, False otherwise.
    """
    if eng is None:
        eng = engine
    from sqlalchemy import inspect as sa_inspect
    insp = sa_inspect(eng)
    existing = set(insp.get_table_names())
    expected = set(Base.metadata.tables.keys())
    missing = expected - existing
    if missing:
        logger.error(f"Missing database tables: {sorted(missing)}")
        return False
    logger.info(f"Database initialized: {len(existing)} tables verified")
    return True


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in Base.metadata.
    
    Import model modules to register all tables with Base.metadata
    before calling create_all(). Without these imports, Base.metadata
    would be empty and create_all() would be a no-op.
    
    This method is idempotent - it only creates tables that don't exist.
    Safe to call multiple times (e.g., on every startup).
    """
    logger.info(f"Database URL: {DATABASE_URL}")

    import database.models  # noqa: F401
    import database.case_models  # noqa: F401
    
    from sqlalchemy import inspect as sa_insp
    
    insp = sa_insp(engine)
    existing_tables = set(insp.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())
    missing_tables = expected_tables - existing_tables
    
    if missing_tables:
        logger.info(f"Creating missing database tables: {sorted(missing_tables)}")
        Base.metadata.create_all(bind=engine)
        
        if not verify_tables():
            logger.warning("Table verification failed after create_all(), retrying...")
            Base.metadata.create_all(bind=engine)
            if not verify_tables():
                logger.error("Database initialization failed after retry")
            else:
                logger.info(f"Database tables created on retry. Total tables: {len(expected_tables)}")
        else:
            logger.info(f"Database tables created successfully. Total tables: {len(expected_tables)}")
    else:
        logger.info(f"All {len(expected_tables)} database tables already exist, no migration needed")


def close_db() -> None:
    """
    Close database session on application shutdown.
    """
    db_session.remove()
