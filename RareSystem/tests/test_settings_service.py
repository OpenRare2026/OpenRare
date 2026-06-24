"""
Tests for Settings Service - LLM configuration management.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.case_models import LLMSettings
from services.settings_service import (
    SettingsService, create_settings_service,
    SettingsNotFoundError, InvalidProviderError,
    VALID_PROVIDERS, PROVIDER_NAMES
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def settings_service(db_session):
    """Create a SettingsService instance for testing."""
    return create_settings_service(db_session)


class TestSettingsService:
    """Test cases for SettingsService."""

    def test_create_llm_settings_openai(self, settings_service):
        """Test creating OpenAI LLM settings."""
        settings = settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test-key',
            model='gpt-4o-mini',
            temperature=0.7,
            max_tokens=1024
        )

        assert settings.id is not None
        assert settings.patient_id == 1
        assert settings.provider == 'openai'
        assert settings.provider_name == 'OpenAI'
        assert settings.model == 'gpt-4o-mini'
        assert settings.temperature == 0.7
        assert settings.max_tokens == 1024
        assert settings.is_active == 1

    def test_create_llm_settings_anthropic(self, settings_service):
        """Test creating Anthropic LLM settings."""
        settings = settings_service.create_llm_settings(
            patient_id=1,
            provider='anthropic',
            api_key='sk-ant-test',
            model='claude-3-haiku-20240307',
            temperature=0.5,
            max_tokens=2048
        )

        assert settings.provider == 'anthropic'
        assert settings.provider_name == 'Anthropic'
        assert settings.model == 'claude-3-haiku-20240307'

    def test_create_llm_settings_ollama(self, settings_service):
        """Test creating Ollama LLM settings."""
        settings = settings_service.create_llm_settings(
            patient_id=1,
            provider='ollama',
            api_key='not-needed',
            model='llama3',
            base_url='http://localhost:11434'
        )

        assert settings.provider == 'ollama'
        assert settings.provider_name == 'Ollama (本地)'
        assert settings.base_url == 'http://localhost:11434'

    def test_create_llm_settings_invalid_provider(self, settings_service):
        """Test that invalid provider raises error."""
        with pytest.raises(InvalidProviderError):
            settings_service.create_llm_settings(
                patient_id=1,
                provider='invalid_provider',
                api_key='test',
                model='test-model'
            )

    def test_get_llm_settings(self, settings_service):
        """Test retrieving LLM settings."""
        created = settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test',
            model='gpt-4o-mini'
        )

        retrieved = settings_service.get_llm_settings(patient_id=1)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.provider == 'openai'

    def test_get_llm_settings_not_found(self, settings_service):
        """Test retrieving settings for non-existent patient."""
        retrieved = settings_service.get_llm_settings(patient_id=999)

        assert retrieved is None

    def test_update_llm_settings(self, settings_service):
        """Test updating LLM settings."""
        created = settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test',
            model='gpt-4o-mini'
        )

        updated = settings_service.update_llm_settings(
            settings_id=created.id,
            model='gpt-4o',
            temperature=0.5
        )

        assert updated.model == 'gpt-4o'
        assert updated.temperature == 0.5

    def test_update_llm_settings_not_found(self, settings_service):
        """Test updating non-existent settings."""
        with pytest.raises(SettingsNotFoundError):
            settings_service.update_llm_settings(
                settings_id=999,
                model='gpt-4o'
            )

    def test_delete_llm_settings(self, settings_service):
        """Test deleting LLM settings."""
        created = settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test',
            model='gpt-4o-mini'
        )

        result = settings_service.delete_llm_settings(created.id)

        assert result is True
        assert settings_service.get_llm_settings(patient_id=1) is None

    def test_delete_llm_settings_not_found(self, settings_service):
        """Test deleting non-existent settings."""
        result = settings_service.delete_llm_settings(999)

        assert result is False

    def test_activate_settings(self, settings_service):
        """Test activating settings."""
        settings1 = settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test-1',
            model='gpt-4o-mini'
        )

        settings2 = settings_service.create_llm_settings(
            patient_id=1,
            provider='anthropic',
            api_key='sk-ant-test',
            model='claude-3-haiku-20240307'
        )

        assert settings1.is_active == 0
        assert settings2.is_active == 1

        settings_service.activate_settings(settings1.id)

        db = settings_service._db
        db.refresh(settings1)
        db.refresh(settings2)

        assert settings1.is_active == 1
        assert settings2.is_active == 0

    def test_get_all_settings(self, settings_service):
        """Test retrieving all settings for a patient."""
        settings_service.create_llm_settings(
            patient_id=1,
            provider='openai',
            api_key='sk-test-1',
            model='gpt-4o-mini'
        )

        settings_service.create_llm_settings(
            patient_id=1,
            provider='anthropic',
            api_key='sk-ant-test',
            model='claude-3-haiku-20240307'
        )

        all_settings = settings_service.get_all_settings(patient_id=1)

        assert len(all_settings) == 2

    def test_get_provider_models(self, settings_service):
        """Test retrieving provider models."""
        openai_models = settings_service.get_provider_models('openai')
        assert 'gpt-4o-mini' in openai_models
        assert 'gpt-4o' in openai_models

        anthropic_models = settings_service.get_provider_models('anthropic')
        assert 'claude-3-haiku-20240307' in anthropic_models

    def test_get_all_providers(self, settings_service):
        """Test retrieving all providers."""
        providers = settings_service.get_all_providers()

        assert 'openai' in providers
        assert 'anthropic' in providers
        assert 'ollama' in providers
        assert 'custom' in providers
        assert providers['openai'] == 'OpenAI'


class TestValidProviders:
    """Test provider constants."""

    def test_valid_providers_list(self):
        """Test that valid providers are defined."""
        assert 'openai' in VALID_PROVIDERS
        assert 'anthropic' in VALID_PROVIDERS
        assert 'ollama' in VALID_PROVIDERS
        assert 'custom' in VALID_PROVIDERS

    def test_provider_names_mapping(self):
        """Test provider names mapping."""
        assert PROVIDER_NAMES['openai'] == 'OpenAI'
        assert PROVIDER_NAMES['anthropic'] == 'Anthropic'
        assert PROVIDER_NAMES['ollama'] == 'Ollama (本地)'
