"""
Settings API endpoints for LLM configuration management.
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from services.settings_service import (
    SettingsService, create_settings_service,
    SettingsNotFoundError, InvalidProviderError
)
from api.middleware import APIException, ErrorCode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


class LLMSettingsRequest(BaseModel):
    provider: str = Field(..., min_length=1, max_length=50)
    api_key: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1, max_length=100)
    base_url: Optional[str] = Field(None, max_length=500)
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(1024, ge=1, le=32768)


class LLMSettingsResponse(BaseModel):
    id: int
    patient_id: int
    is_active: bool
    provider: str
    provider_name: Optional[str]
    model: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    created_at: str
    updated_at: str


class ProviderInfo(BaseModel):
    code: str
    name: str
    models: List[str]


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    return create_settings_service(db)


@router.get("/patient/{patient_id}", response_model=LLMSettingsResponse)
async def get_patient_settings(
    patient_id: int,
    service: SettingsService = Depends(get_settings_service)
):
    settings = service.get_llm_settings(patient_id)
    if not settings:
        raise HTTPException(status_code=404, detail="No active settings found for this patient")

    return LLMSettingsResponse(
        id=settings.id,
        patient_id=settings.patient_id,
        is_active=bool(settings.is_active),
        provider=settings.provider,
        provider_name=settings.provider_name,
        model=settings.model,
        base_url=settings.base_url,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        created_at=settings.created_at.isoformat(),
        updated_at=settings.updated_at.isoformat()
    )


@router.get("/patient/{patient_id}/all", response_model=List[LLMSettingsResponse])
async def get_all_patient_settings(
    patient_id: int,
    service: SettingsService = Depends(get_settings_service)
):
    settings_list = service.get_all_settings(patient_id)
    return [
        LLMSettingsResponse(
            id=s.id,
            patient_id=s.patient_id,
            is_active=bool(s.is_active),
            provider=s.provider,
            provider_name=s.provider_name,
            model=s.model,
            base_url=s.base_url,
            temperature=s.temperature,
            max_tokens=s.max_tokens,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        )
        for s in settings_list
    ]


@router.post("/patient/{patient_id}", response_model=LLMSettingsResponse)
async def create_settings(
    patient_id: int,
    request: LLMSettingsRequest,
    service: SettingsService = Depends(get_settings_service)
):
    try:
        settings = service.create_llm_settings(
            patient_id=patient_id,
            provider=request.provider,
            api_key=request.api_key,
            model=request.model,
            base_url=request.base_url,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        logger.info(f"Created LLM settings for patient {patient_id}: {request.provider}/{request.model}")

        return LLMSettingsResponse(
            id=settings.id,
            patient_id=settings.patient_id,
            is_active=bool(settings.is_active),
            provider=settings.provider,
            provider_name=settings.provider_name,
            model=settings.model,
            base_url=settings.base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )

    except InvalidProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{settings_id}", response_model=LLMSettingsResponse)
async def update_settings(
    settings_id: int,
    request: LLMSettingsRequest,
    service: SettingsService = Depends(get_settings_service)
):
    try:
        settings = service.update_llm_settings(
            settings_id=settings_id,
            provider=request.provider,
            api_key=request.api_key,
            model=request.model,
            base_url=request.base_url,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        logger.info(f"Updated LLM settings {settings_id}")

        return LLMSettingsResponse(
            id=settings.id,
            patient_id=settings.patient_id,
            is_active=bool(settings.is_active),
            provider=settings.provider,
            provider_name=settings.provider_name,
            model=settings.model,
            base_url=settings.base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )

    except SettingsNotFoundError:
        raise HTTPException(status_code=404, detail="Settings not found")
    except InvalidProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{settings_id}")
async def delete_settings(
    settings_id: int,
    service: SettingsService = Depends(get_settings_service)
):
    success = service.delete_llm_settings(settings_id)
    if not success:
        raise HTTPException(status_code=404, detail="Settings not found")

    logger.info(f"Deleted LLM settings {settings_id}")
    return {"message": "Settings deleted", "settings_id": settings_id}


@router.post("/{settings_id}/activate", response_model=LLMSettingsResponse)
async def activate_settings(
    settings_id: int,
    service: SettingsService = Depends(get_settings_service)
):
    try:
        settings = service.activate_settings(settings_id)

        logger.info(f"Activated LLM settings {settings_id}")

        return LLMSettingsResponse(
            id=settings.id,
            patient_id=settings.patient_id,
            is_active=bool(settings.is_active),
            provider=settings.provider,
            provider_name=settings.provider_name,
            model=settings.model,
            base_url=settings.base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )

    except SettingsNotFoundError:
        raise HTTPException(status_code=404, detail="Settings not found")


@router.get("/providers", response_model=List[ProviderInfo])
async def get_providers(
    service: SettingsService = Depends(get_settings_service)
):
    providers = service.get_all_providers()
    result = []
    for code, name in providers.items():
        result.append(ProviderInfo(
            code=code,
            name=name,
            models=service.get_provider_models(code)
        ))
    return result


@router.get("/providers/{provider}/models", response_model=List[str])
async def get_provider_models(
    provider: str,
    service: SettingsService = Depends(get_settings_service)
):
    models = service.get_provider_models(provider)
    if not models and provider not in service.get_all_providers():
        raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
    return models
