"""
Tests for database initialization - verifies init_db() creates all expected tables.
"""
import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect

from database.base import Base


EXPECTED_TABLES = [
    "patients",
    "vcf_files",
    "variants",
    "acmg_evidence",
    "acmg_classifications",
    "clinical_reports",
    "research_reports",
    "case_documents",
    "case_embeddings",
    "chat_sessions",
    "chat_messages",
    "llm_settings",
    "skill_configs",
]


def test_init_db_creates_all_tables():
    """Verify that init_db() creates all 13 expected database tables."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        test_url = f"sqlite:///{db_path}"
        test_engine = create_engine(test_url, connect_args={"check_same_thread": False})

        import database.session as session_module
        original_engine = session_module.engine
        session_module.engine = test_engine

        try:
            from database.session import init_db
            init_db()

            inspector = inspect(test_engine)
            tables = inspector.get_table_names()

            for table in EXPECTED_TABLES:
                assert table in tables, f"Missing table: {table}. Found: {tables}"

            assert len(tables) == len(EXPECTED_TABLES), (
                f"Expected {len(EXPECTED_TABLES)} tables, found {len(tables)}: {tables}"
            )
        finally:
            session_module.engine = original_engine
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_db_idempotent():
    """Verify that calling init_db() twice does not raise errors."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        test_url = f"sqlite:///{db_path}"
        test_engine = create_engine(test_url, connect_args={"check_same_thread": False})

        import database.session as session_module
        original_engine = session_module.engine
        session_module.engine = test_engine

        try:
            from database.session import init_db
            init_db()
            init_db()

            inspector = inspect(test_engine)
            tables = inspector.get_table_names()
            assert len(tables) == len(EXPECTED_TABLES)
        finally:
            session_module.engine = original_engine
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
