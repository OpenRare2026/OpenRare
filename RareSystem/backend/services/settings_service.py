"""
Settings Service - LLM configuration management for Case Q&A.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.case_models import LLMSettings

logger = logging.getLogger(__name__)


class SettingsServiceError(Exception):
    pass


class SettingsNotFoundError(SettingsServiceError):
    pass


class InvalidProviderError(SettingsServiceError):
    pass


VALID_PROVIDERS = ["openai", "anthropic", "ollama", "custom"]

PROVIDER_MODELS = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
    "ollama": ["llama3", "llama3:8b", "mistral", "qwen2", "deepseek-coder"],
    "custom": []
}

PROVIDER_NAMES = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "ollama": "Ollama (本地)",
    "custom": "自定义"
}


class SettingsService:
    def __init__(self, db: Session):
        self._db = db

    def get_llm_settings(self, patient_id: int) -> Optional[LLMSettings]:
        settings = self._db.query(LLMSettings).filter(
            and_(
                LLMSettings.patient_id == patient_id,
                LLMSettings.is_active == 1
            )
        ).first()
        return settings

    def get_all_settings(self, patient_id: int) -> list:
        settings = self._db.query(LLMSettings).filter(
            LLMSettings.patient_id == patient_id
        ).order_by(LLMSettings.updated_at.desc()).all()
        return settings

    def create_llm_settings(
        self,
        patient_id: int,
        provider: str,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> LLMSettings:
        if provider not in VALID_PROVIDERS:
            raise InvalidProviderError(f"Invalid provider: {provider}. Valid providers: {VALID_PROVIDERS}")

        self._deactivate_other_settings(patient_id)

        settings = LLMSettings(
            patient_id=patient_id,
            provider=provider,
            provider_name=PROVIDER_NAMES.get(provider, provider),
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            is_active=1
        )
        self._db.add(settings)
        self._db.commit()
        self._db.refresh(settings)

        logger.info(f"Created LLM settings for patient {patient_id}: provider={provider}, model={model}")
        return settings

    def update_llm_settings(
        self,
        settings_id: int,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMSettings:
        settings = self._db.query(LLMSettings).filter(LLMSettings.id == settings_id).first()

        if not settings:
            raise SettingsNotFoundError(f"Settings not found: {settings_id}")

        if provider is not None:
            if provider not in VALID_PROVIDERS:
                raise InvalidProviderError(f"Invalid provider: {provider}")
            settings.provider = provider
            settings.provider_name = PROVIDER_NAMES.get(provider, provider)

        if api_key is not None:
            settings.api_key = api_key
        if model is not None:
            settings.model = model
        if base_url is not None:
            settings.base_url = base_url
        if temperature is not None:
            settings.temperature = temperature
        if max_tokens is not None:
            settings.max_tokens = max_tokens

        settings.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(settings)

        logger.info(f"Updated LLM settings {settings_id}")
        return settings

    def delete_llm_settings(self, settings_id: int) -> bool:
        settings = self._db.query(LLMSettings).filter(LLMSettings.id == settings_id).first()

        if not settings:
            return False

        self._db.delete(settings)
        self._db.commit()

        logger.info(f"Deleted LLM settings {settings_id}")
        return True

    def activate_settings(self, settings_id: int) -> LLMSettings:
        settings = self._db.query(LLMSettings).filter(LLMSettings.id == settings_id).first()

        if not settings:
            raise SettingsNotFoundError(f"Settings not found: {settings_id}")

        self._deactivate_other_settings(settings.patient_id)

        settings.is_active = 1
        settings.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(settings)

        logger.info(f"Activated LLM settings {settings_id}")
        return settings

    def _deactivate_other_settings(self, patient_id: int):
        self._db.query(LLMSettings).filter(
            LLMSettings.patient_id == patient_id
        ).update({"is_active": 0})

    def get_provider_models(self, provider: str) -> list:
        return PROVIDER_MODELS.get(provider, [])

    def get_all_providers(self) -> Dict[str, str]:
        return PROVIDER_NAMES


def create_settings_service(db: Session) -> SettingsService:
    return SettingsService(db=db)
