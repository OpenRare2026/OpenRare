"""
Tests for LLM Client Factory.
"""
import pytest
from unittest.mock import patch, MagicMock

from services.llm_client import (
    LLMClient, LLMResponse, LLMClientError,
    OpenAIClient, AnthropicClient, OllamaClient, CustomClient,
    create_llm_client
)


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating LLM response."""
        response = LLMResponse(
            content="Test response",
            model="gpt-4o-mini",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            finish_reason="stop"
        )

        assert response.content == "Test response"
        assert response.model == "gpt-4o-mini"
        assert response.usage["prompt_tokens"] == 10
        assert response.finish_reason == "stop"

    def test_llm_response_minimal(self):
        """Test creating minimal LLM response."""
        response = LLMResponse(
            content="Test",
            model="test-model"
        )

        assert response.content == "Test"
        assert response.model == "test-model"
        assert response.usage is None
        assert response.finish_reason is None


class TestCreateLLMClient:
    """Test LLM client factory function."""

    def test_create_openai_client(self):
        """Test creating OpenAI client."""
        client = create_llm_client(
            provider='openai',
            api_key='sk-test',
            model='gpt-4o-mini'
        )

        assert isinstance(client, OpenAIClient)
        assert client._model == 'gpt-4o-mini'
        assert client._api_key == 'sk-test'

    def test_create_anthropic_client(self):
        """Test creating Anthropic client."""
        client = create_llm_client(
            provider='anthropic',
            api_key='sk-ant-test',
            model='claude-3-haiku-20240307'
        )

        assert isinstance(client, AnthropicClient)
        assert client._model == 'claude-3-haiku-20240307'

    def test_create_ollama_client(self):
        """Test creating Ollama client."""
        client = create_llm_client(
            provider='ollama',
            api_key='not-needed',
            model='llama3',
            base_url='http://localhost:11434'
        )

        assert isinstance(client, OllamaClient)
        assert client._model == 'llama3'
        assert client._base_url == 'http://localhost:11434'

    def test_create_custom_client(self):
        """Test creating custom client."""
        client = create_llm_client(
            provider='custom',
            api_key='custom-key',
            model='custom-model',
            base_url='https://custom.api.com/v1'
        )

        assert isinstance(client, CustomClient)
        assert client._base_url == 'https://custom.api.com/v1'

    def test_create_custom_client_missing_url(self):
        """Test that custom client requires base_url."""
        with pytest.raises(LLMClientError):
            create_llm_client(
                provider='custom',
                api_key='custom-key',
                model='custom-model'
            )

    def test_create_unknown_provider(self):
        """Test that unknown provider raises error."""
        with pytest.raises(LLMClientError):
            create_llm_client(
                provider='unknown',
                api_key='test',
                model='test-model'
            )


class TestOpenAIClient:
    """Test OpenAI client methods."""

    def test_openai_client_init(self):
        """Test OpenAI client initialization."""
        client = OpenAIClient(
            api_key='sk-test',
            model='gpt-4o-mini',
            base_url='https://api.openai.com/v1'
        )

        assert client._api_key == 'sk-test'
        assert client._model == 'gpt-4o-mini'
        assert client._base_url == 'https://api.openai.com/v1'
        assert 'Authorization' in client._headers
        assert 'Bearer sk-test' in client._headers['Authorization']

    def test_openai_client_custom_base_url(self):
        """Test OpenAI client with custom base URL."""
        client = OpenAIClient(
            api_key='sk-test',
            model='gpt-4o-mini',
            base_url='https://custom.openai.com/v1'
        )

        assert client._base_url == 'https://custom.openai.com/v1'


class TestAnthropicClient:
    """Test Anthropic client methods."""

    def test_anthropic_client_init(self):
        """Test Anthropic client initialization."""
        client = AnthropicClient(
            api_key='sk-ant-test',
            model='claude-3-haiku-20240307'
        )

        assert client._api_key == 'sk-ant-test'
        assert client._model == 'claude-3-haiku-20240307'
        assert 'x-api-key' in client._headers
        assert 'anthropic-version' in client._headers


class TestOllamaClient:
    """Test Ollama client methods."""

    def test_ollama_client_init(self):
        """Test Ollama client initialization."""
        client = OllamaClient(
            model='llama3',
            base_url='http://localhost:11434'
        )

        assert client._model == 'llama3'
        assert client._base_url == 'http://localhost:11434'

    def test_ollama_client_default_base_url(self):
        """Test Ollama client default base URL."""
        client = OllamaClient(model='llama3')

        assert client._base_url == 'http://localhost:11434'


class TestCustomClient:
    """Test Custom client methods."""

    def test_custom_client_init(self):
        """Test Custom client initialization."""
        client = CustomClient(
            api_key='custom-key',
            model='custom-model',
            base_url='https://custom.api.com/v1'
        )

        assert client._api_key == 'custom-key'
        assert client._model == 'custom-model'
        assert client._base_url == 'https://custom.api.com/v1'
