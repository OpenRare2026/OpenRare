"""
ACMG Classification API endpoints.

Variant data is read from VEP Parquet files. The variant_id format is
"{vcf_file_id}_{row_index}" — e.g., "3_0" means VCF file 3, row 0.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pathlib import Path

from database import get_db, VEPJob
from services.parquet_service import ParquetService
from services.acmg_classifier import ACMGClassifier, ClassificationResult, ClassificationCategory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/acmg", tags=["acmg"])


class CriterionResultResponse(BaseModel):
    criterion_code: str
    criterion_name: str
    is_met: bool
    evidence_strength: str
    direction: str
    score: float
    description: str
    evidence_sources: List[str] = []
    confidence: float = 1.0


class ACMGClassificationResponse(BaseModel):
    id: str
    variant_id: str
    classification: str
    confidence_score: float
    classification_date: str
    classifier_version: str
    notes: Optional[str] = None
    evidence_chain: List[dict] = []
    pathogenic_criteria: List[CriterionResultResponse] = []
    benign_criteria: List[CriterionResultResponse] = []
    total_pathogenic_score: float = 0.0
    total_benign_score: float = 0.0
    warnings: List[str] = []


def _parse_variant_id(variant_id: str):
    parts = variant_id.split("_", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail=f"Invalid variant_id format: {variant_id}")
    try:
        vcf_file_id = int(parts[0])
        row_index = int(parts[1])
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid variant_id format: {variant_id}")
    return vcf_file_id, row_index


def _get_variant_row(vcf_file_id: int, row_index: int, db: Session):
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_file_id,
        VEPJob.parquet_path.isnot(None)
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.parquet_path:
        raise HTTPException(status_code=404, detail="VEP annotation not available")

    if not Path(vep_job.parquet_path).exists():
        raise HTTPException(status_code=404, detail="VEP Parquet file not found")

    service = ParquetService()
    row = service.read_row(vep_job.parquet_path, row_index)
    if not row:
        raise HTTPException(status_code=404, detail=f"Row {row_index} not found")

    return row


def _map_row_to_variant_data(row: dict) -> dict:
    """Map VEP Parquet row to variant_data dict for ACMGClassifier."""
    chrom_col = next((c for c in row if c in ("chrom", "Chromosome", "#CHROM")), None)
    pos_col = next((c for c in row if c in ("pos", "POS", "Position")), None)
    ref_col = next((c for c in row if c in ("ref", "REF", "Reference")), None)
    alt_col = next((c for c in row if c in ("alt", "ALT", "Alternate", "Allele")), None)
    consequence_col = next((c for c in row if c in ("consequence", "Consequence")), None)
    impact_col = next((c for c in row if c in ("impact", "IMPACT")), None)
    qual_col = next((c for c in row if c in ("quality", "QUAL", "vcf_info_QD")), None)

    chromosome = row.get(chrom_col, "") if chrom_col else ""
    position = 0
    if pos_col:
        try:
            position = int(row.get(pos_col, 0))
        except (ValueError, TypeError):
            pass

    ref = row.get(ref_col, "") if ref_col else ""
    alt = row.get(alt_col, "") if alt_col else ""

    consequence = row.get(consequence_col, "") if consequence_col else ""
    impact = row.get(impact_col, "") if impact_col else ""
    variant_type = "SNV"
    if ref and alt and len(ref) != len(alt):
        variant_type = "INDEL"
    elif "insertion" in consequence.lower() or "deletion" in consequence.lower():
        variant_type = "INDEL"

    quality = None
    if qual_col:
        try:
            quality = float(row.get(qual_col, 0) or 0)
        except (ValueError, TypeError):
            pass

    skip_cols = {chrom_col, pos_col, ref_col, alt_col, consequence_col, impact_col, qual_col} - {None}
    return {
        "chromosome": chromosome,
        "position": position,
        "ref": ref or "-",
        "alt": alt or "-",
        "variant_type": variant_type,
        "quality": quality,
        "info": {k: v for k, v in row.items() if v and k not in skip_cols},
    }


@router.get("/{variant_id}", response_model=ACMGClassificationResponse)
async def get_acmg_classification(
    variant_id: str,
    db: Session = Depends(get_db)
):
    """
    Get existing ACMG classification for a variant.

    Since we no longer persist classifications to the Variant FK chain,
    this endpoint suggests running analyze first.
    """
    try:
        vcf_file_id, row_index = _parse_variant_id(variant_id)
    except HTTPException:
        raise

    row = _get_variant_row(vcf_file_id, row_index, db)

    classifier = ACMGClassifier()
    variant_data = _map_row_to_variant_data(row)
    result = classifier.classify(variant_data)

    classification_value = result.classification.value if isinstance(result.classification, ClassificationCategory) else str(result.classification)

    pathogenic_criteria = [
        CriterionResultResponse(
            criterion_code=str(c.criterion_code),
            criterion_name=str(c.criterion_name),
            is_met=bool(c.is_met),
            evidence_strength=str(c.evidence_strength.value) if hasattr(c.evidence_strength, 'value') else str(c.evidence_strength),
            direction="pathogenic",
            score=float(c.score),
            description=str(c.description),
            evidence_sources=list(c.evidence_sources) if hasattr(c, 'evidence_sources') else [],
            confidence=float(c.confidence) if hasattr(c, 'confidence') else 1.0
        )
        for c in (result.pathogenic_criteria or [])
    ]

    benign_criteria = [
        CriterionResultResponse(
            criterion_code=str(c.criterion_code),
            criterion_name=str(c.criterion_name),
            is_met=bool(c.is_met),
            evidence_strength=str(c.evidence_strength.value) if hasattr(c.evidence_strength, 'value') else str(c.evidence_strength),
            direction="benign",
            score=float(c.score),
            description=str(c.description),
            evidence_sources=list(c.evidence_sources) if hasattr(c, 'evidence_sources') else [],
            confidence=float(c.confidence) if hasattr(c, 'confidence') else 1.0
        )
        for c in (result.benign_criteria or [])
    ]

    return ACMGClassificationResponse(
        id=f"acmg_{variant_id}",
        variant_id=variant_id,
        classification=classification_value,
        confidence_score=float(result.confidence_score),
        classification_date="",
        classifier_version="1.0",
        evidence_chain=list(result.evidence_chain) if result.evidence_chain else [],
        pathogenic_criteria=pathogenic_criteria,
        benign_criteria=benign_criteria,
        total_pathogenic_score=float(result.total_pathogenic_score),
        total_benign_score=float(result.total_benign_score),
        warnings=list(result.warnings) if result.warnings else []
    )


@router.post("/{variant_id}/analyze", response_model=ACMGClassificationResponse)
async def analyze_variant_acmg(
    variant_id: str,
    db: Session = Depends(get_db)
):
    """
    Run ACMG classification for a variant from VEP Parquet data.
    variant_id format: "{vcf_file_id}_{row_index}"
    """
    try:
        vcf_file_id, row_index = _parse_variant_id(variant_id)
    except HTTPException:
        raise

    row = _get_variant_row(vcf_file_id, row_index, db)

    classifier = ACMGClassifier()
    variant_data = _map_row_to_variant_data(row)

    try:
        result: ClassificationResult = classifier.classify(variant_data)
    except Exception as e:
        logger.error(f"ACMG classification error: {e}")
        result = ClassificationResult(
            variant_id=variant_id,
            classification=ClassificationCategory.UNCERTAIN_SIGNIFICANCE,
            confidence_score=0.5,
            total_pathogenic_score=0.0,
            total_benign_score=0.0,
            pathogenic_criteria=[],
            benign_criteria=[],
            evidence_chain=[],
            warnings=[f"Classification error: {str(e)}"]
        )

    classification_value = result.classification.value if isinstance(result.classification, ClassificationCategory) else str(result.classification)

    pathogenic_criteria = [
        CriterionResultResponse(
            criterion_code=str(c.criterion_code),
            criterion_name=str(c.criterion_name),
            is_met=bool(c.is_met),
            evidence_strength=str(c.evidence_strength.value) if hasattr(c.evidence_strength, 'value') else str(c.evidence_strength),
            direction="pathogenic",
            score=float(c.score),
            description=str(c.description),
            evidence_sources=list(c.evidence_sources) if hasattr(c, 'evidence_sources') else [],
            confidence=float(c.confidence) if hasattr(c, 'confidence') else 1.0
        )
        for c in (result.pathogenic_criteria or [])
    ]

    benign_criteria = [
        CriterionResultResponse(
            criterion_code=str(c.criterion_code),
            criterion_name=str(c.criterion_name),
            is_met=bool(c.is_met),
            evidence_strength=str(c.evidence_strength.value) if hasattr(c.evidence_strength, 'value') else str(c.evidence_strength),
            direction="benign",
            score=float(c.score),
            description=str(c.description),
            evidence_sources=list(c.evidence_sources) if hasattr(c, 'evidence_sources') else [],
            confidence=float(c.confidence) if hasattr(c, 'confidence') else 1.0
        )
        for c in (result.benign_criteria or [])
    ]

    return ACMGClassificationResponse(
        id=f"acmg_{variant_id}",
        variant_id=variant_id,
        classification=classification_value,
        confidence_score=float(result.confidence_score),
        classification_date="",
        classifier_version="1.0",
        evidence_chain=list(result.evidence_chain) if result.evidence_chain else [],
        pathogenic_criteria=pathogenic_criteria,
        benign_criteria=benign_criteria,
        total_pathogenic_score=float(result.total_pathogenic_score),
        total_benign_score=float(result.total_benign_score),
        warnings=list(result.warnings) if result.warnings else []
    )
