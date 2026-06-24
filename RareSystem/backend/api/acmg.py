"""
ACMG Classification API endpoints.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, Variant, ACMGClassification, ACMGEvidence
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


@router.get("/{variant_id}", response_model=ACMGClassificationResponse)
async def get_acmg_classification(
    variant_id: int,
    db: Session = Depends(get_db)
):
    classification = db.query(ACMGClassification).filter(
        ACMGClassification.variant_id == variant_id
    ).first()
    
    if not classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    
    evidence_records = db.query(ACMGEvidence).filter(
        ACMGEvidence.variant_id == variant_id
    ).all()
    
    evidence_chain = [
        {
            "criterion": e.criterion,
            "description": e.description,
            "score": 0.0
        }
        for e in evidence_records
    ]
    
    return ACMGClassificationResponse(
        id=str(classification.id),
        variant_id=str(classification.variant_id),
        classification=str(classification.classification),
        confidence_score=float(classification.confidence_score) if classification.confidence_score else 0.0,
        classification_date=str(classification.classification_date) if classification.classification_date else "",
        classifier_version=str(classification.classifier_version) if classification.classifier_version else "1.0",
        notes=str(classification.notes) if classification.notes else None,
        evidence_chain=evidence_chain,
        pathogenic_criteria=[],
        benign_criteria=[],
        total_pathogenic_score=0.0,
        total_benign_score=0.0,
        warnings=[]
    )


@router.post("/{variant_id}/analyze", response_model=ACMGClassificationResponse)
async def analyze_variant_acmg(
    variant_id: int,
    db: Session = Depends(get_db)
):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    classifier = ACMGClassifier()
    
    variant_data = {
        "chromosome": str(variant.chromosome),
        "position": int(variant.position),
        "ref": str(variant.ref),
        "alt": str(variant.alt),
        "variant_type": str(variant.variant_type),
        "quality": float(variant.quality) if variant.quality else None,
        "info": dict(variant.info_field) if variant.info_field else {}
    }
    
    try:
        result: ClassificationResult = classifier.classify(variant_data)
    except Exception as e:
        logger.error(f"ACMG classification error: {e}")
        result = ClassificationResult(
            variant_id=str(variant_id),
            classification=ClassificationCategory.UNCERTAIN_SIGNIFICANCE,
            confidence_score=0.5,
            total_pathogenic_score=0.0,
            total_benign_score=0.0,
            pathogenic_criteria=[],
            benign_criteria=[],
            evidence_chain=[],
            warnings=[f"Classification error: {str(e)}"]
        )
    
    existing = db.query(ACMGClassification).filter(
        ACMGClassification.variant_id == variant_id
    ).first()
    
    classification_value = result.classification.value if isinstance(result.classification, ClassificationCategory) else str(result.classification)
    
    if existing:
        existing.classification = classification_value
        existing.confidence_score = result.confidence_score
        existing.classifier_version = "1.0"
        db.commit()
        db.refresh(existing)
        classification_id = existing.id
    else:
        new_classification = ACMGClassification(
            variant_id=variant_id,
            classification=classification_value,
            confidence_score=result.confidence_score,
            classifier_version="1.0"
        )
        db.add(new_classification)
        db.commit()
        db.refresh(new_classification)
        classification_id = new_classification.id
    
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
        id=str(classification_id),
        variant_id=str(variant_id),
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
