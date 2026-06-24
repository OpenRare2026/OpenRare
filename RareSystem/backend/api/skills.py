"""Skills API endpoints for skill management and execution."""
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from database.case_models import SkillConfig
from services.skill_base import SkillRegistry, create_skill_registry, SkillContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skills", tags=["skills"])


class SkillResponse(BaseModel):
    name: str
    description: str
    skill_type: str
    icon: str
    input_schema: dict
    config_schema: dict = {}
    is_enabled: bool = True
    config: dict = {}


class SkillConfigUpdateRequest(BaseModel):
    is_enabled: Optional[bool] = None
    config: Optional[dict] = None


class SkillExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1)
    patient_id: int
    context: Optional[dict] = None


class SkillExecuteResponse(BaseModel):
    content: str
    references: list = []
    confidence: float = 0.0
    metadata: dict = {}


def get_skill_registry() -> SkillRegistry:
    return create_skill_registry()


@router.get("", response_model=List[SkillResponse])
async def list_skills(db: Session = Depends(get_db)):
    registry = get_skill_registry()
    skills = registry.list()
    result = []
    for skill in skills:
        config_record = db.query(SkillConfig).filter(
            SkillConfig.skill_name == skill.name
        ).first()
        result.append(SkillResponse(
            name=skill.name,
            description=skill.description,
            skill_type=skill.skill_type,
            icon=skill.icon,
            input_schema=skill.input_schema,
            config_schema=getattr(skill, 'config_schema', {}),
            is_enabled=bool(config_record.is_enabled) if config_record else True,
            config=config_record.config if config_record else {}
        ))
    return result


@router.get("/config")
async def get_skill_configs(db: Session = Depends(get_db)):
    configs = db.query(SkillConfig).all()
    return [
        {
            "id": c.id,
            "skill_name": c.skill_name,
            "is_enabled": bool(c.is_enabled),
            "config": c.config,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in configs
    ]


@router.put("/config/{skill_name}")
async def update_skill_config(
    skill_name: str,
    request: SkillConfigUpdateRequest,
    db: Session = Depends(get_db)
):
    config_record = db.query(SkillConfig).filter(
        SkillConfig.skill_name == skill_name
    ).first()

    if not config_record:
        config_record = SkillConfig(
            skill_name=skill_name,
            is_enabled=1 if (request.is_enabled if request.is_enabled is not None else True) else 0,
            config=request.config or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(config_record)
    else:
        if request.is_enabled is not None:
            config_record.is_enabled = 1 if request.is_enabled else 0
        if request.config is not None:
            config_record.config = request.config
        config_record.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(config_record)

    return {
        "id": config_record.id,
        "skill_name": config_record.skill_name,
        "is_enabled": bool(config_record.is_enabled),
        "config": config_record.config,
        "updated_at": config_record.updated_at.isoformat()
    }


@router.post("/{skill_name}/execute", response_model=SkillExecuteResponse)
async def execute_skill(
    skill_name: str,
    request: SkillExecuteRequest,
    db: Session = Depends(get_db)
):
    registry = get_skill_registry()
    skill = registry.get(skill_name)

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_name}")

    context = SkillContext(
        query=request.query,
        patient_id=request.patient_id,
        db_session=db,
        llm_client=None,
        case_context=None
    )

    try:
        result = skill.execute(context)
        return SkillExecuteResponse(
            content=result.content,
            references=[
                {"id": r.reference_id, "type": r.reference_type, "label": r.label}
                for r in result.references
            ],
            confidence=result.confidence,
            metadata=result.metadata
        )
    except Exception as e:
        logger.error(f"Skill execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
