from __future__ import annotations

from pydantic import BaseModel, Field


class ReportStreamRequest(BaseModel):
    wide_path: str = Field(
        default="fixtures/wide_table.csv",
        description="Path to ranked wide table CSV.",
    )
    phenotype_path: str = Field(
        default="fixtures/phenotype.csv",
        description="Path to phenotype CSV (ID + Phenotype).",
    )
    hpo_path: str = Field(
        default="fixtures/hpo_terms.txt",
        description="Path to HPO terms text file.",
    )
    ppi_path: str = Field(
        default="",
        description="Path to PPI data file (reserved; not used in report pipeline yet).",
    )
    top_n: int = Field(default=5, ge=1, le=50, description="Number of top genes to include.")


class HealthResponse(BaseModel):
    status: str = "ok"
