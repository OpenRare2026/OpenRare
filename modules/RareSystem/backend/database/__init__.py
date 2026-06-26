"""
Database models and connections package
"""
from .base import Base
from .session import engine, SessionLocal, db_session, get_db, init_db, close_db
from .models import (
    Patient,
    VCFFile,
    Variant,
    ACMGEvidence,
    ACMGClassification,
    ClinicalReport,
    ResearchReport,
    VEPJob,
)
from .case_models import (
    CaseDocument,
    CaseEmbedding,
    ChatSession,
    ChatMessageRecord,
    LLMSettings,
)

__all__ = [
    # Base
    "Base",
    # Session
    "engine",
    "SessionLocal",
    "db_session",
    "get_db",
    "init_db",
    "close_db",
    # Models
    "Patient",
    "VCFFile",
    "Variant",
    "ACMGEvidence",
    "ACMGClassification",
    "ClinicalReport",
    "ResearchReport",
    "VEPJob",
    # Case/QA Models
    "CaseDocument",
    "CaseEmbedding",
    "ChatSession",
    "ChatMessageRecord",
    "LLMSettings",
]
