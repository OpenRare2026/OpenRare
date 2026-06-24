"""Pydantic models for RAG-HPO FastAPI service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class NoteItem(BaseModel):
    """A single clinical note to process."""

    patient_id: str = Field(..., description="Unique patient identifier")
    clinical_note: str = Field(..., description="Free-text clinical note")


class ExtractRequest(BaseModel):
    """Request body for the extract endpoint."""

    notes: list[NoteItem] = Field(..., min_length=1, max_length=500)

    # Optional metadata
    input_filename: Optional[str] = None


class ResultItem(BaseModel):
    """A single mapped HPO term result."""

    patient_id: str
    phrase: str
    category: str
    hpo_id: Optional[str] = None


class RunOptions(BaseModel):
    """Processing options for the current run (future expansion)."""

    pass  # reserved for future flags like --no-stage2, etc.


class RunResponse(BaseModel):
    """Response returned immediately after submitting an extraction job.

    Mirrors the VEP /runs response shape.
    """

    job_id: str
    status: str = "queued"
    created_at: str
    updated_at: str
    input_filename: Optional[str] = None
    input_bytes: int = 0
    options: dict = Field(default_factory=dict)
    status_url: str
    result_url: str
    log_url: str
    rows: Optional[int] = None
    error: Optional[str] = None


class JobStatus(BaseModel):
    """Status and (when finished) results of an extraction job."""

    job_id: str
    status: str  # "queued" | "completed" | "failure"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    input_filename: Optional[str] = None
    input_bytes: int = 0
    options: dict = Field(default_factory=dict)
    status_url: Optional[str] = None
    result_url: Optional[str] = None
    log_url: Optional[str] = None
    notes_count: int = 0
    rows: Optional[int] = None
    results: Optional[list[ResultItem]] = None
    elapsed_seconds: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    model_loaded: bool
    queue_size: int


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
