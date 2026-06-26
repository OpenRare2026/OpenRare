"""
LLM Client Factory - Unified interface for multiple LLM providers.

Supports: OpenAI, Anthropic, Ollama, and custom endpoints.
"""
import logging
import os
import json
from typing import Optional, Dict, Any, List, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class LLMClientError(Exception):
    pass


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        pass

    @abstractmethod
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Iterator[str]:
        pass


class OpenAIClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url or "https://api.openai.com/v1"
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"OpenAI API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", self._model),
            usage=data.get("usage"),
            finish_reason=data["choices"][0].get("finish_reason")
        )

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Iterator[str]:
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, stream=True, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"OpenAI API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue


class AnthropicClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        base_url: Optional[str] = None
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url or "https://api.anthropic.com/v1"
        self._headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        url = f"{self._base_url}/messages"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"Anthropic API error: {response.status_code} - {response.text}")

        data = response.json()
        content = data["content"][0]["text"] if data.get("content") else ""
        return LLMResponse(
            content=content,
            model=data.get("model", self._model),
            usage=data.get("usage"),
            finish_reason=data.get("stop_reason")
        )

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Iterator[str]:
        url = f"{self._base_url}/messages"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, stream=True, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"Anthropic API error: {response.status_code} - {response.text}")

        current_event = None
        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if line.startswith("event: "):
                current_event = line[7:].strip()
            elif line.startswith("data: "):
                data_str = line[6:]
                if current_event == "content_block_delta":
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            yield text
                    except json.JSONDecodeError:
                        continue


class OllamaClient(LLMClient):
    def __init__(
        self,
        model: str = "llama3",
        base_url: Optional[str] = None
    ):
        self._model = model
        self._base_url = base_url or "http://localhost:11434"

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        url = f"{self._base_url}/api/generate"
        payload = {
            "model": self._model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        payload.update(kwargs)

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code != 200:
            raise LLMClientError(f"Ollama API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data.get("response", ""),
            model=data.get("model", self._model),
            usage={"prompt_tokens": data.get("prompt_eval_count", 0), "completion_tokens": data.get("eval_count", 0)},
            finish_reason="stop"
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        payload.update(kwargs)

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code != 200:
            raise LLMClientError(f"Ollama API error: {response.status_code} - {response.text}")

        data = response.json()
        content = data.get("message", {}).get("content", "")
        return LLMResponse(
            content=content,
            model=data.get("model", self._model),
            usage={"prompt_tokens": data.get("prompt_eval_count", 0), "completion_tokens": data.get("eval_count", 0)},
            finish_reason="stop"
        )

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Iterator[str]:
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": True
        }
        payload.update(kwargs)

        response = requests.post(url, json=payload, stream=True, timeout=120)

        if response.status_code != 200:
            raise LLMClientError(f"Ollama API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            try:
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
                if chunk.get("done", False):
                    break
            except json.JSONDecodeError:
                continue


class CustomClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"Custom API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", self._model),
            usage=data.get("usage"),
            finish_reason=data["choices"][0].get("finish_reason")
        )

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Iterator[str]:
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        payload.update(kwargs)

        response = requests.post(url, headers=self._headers, json=payload, stream=True, timeout=60)

        if response.status_code != 200:
            raise LLMClientError(f"Custom API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue


def create_llm_client(
    provider: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None
) -> LLMClient:
    provider = provider.lower()

    if provider == "openai":
        return OpenAIClient(api_key=api_key, model=model, base_url=base_url)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=model, base_url=base_url)
    elif provider == "ollama":
        return OllamaClient(model=model, base_url=base_url)
    elif provider == "custom":
        if not base_url:
            raise LLMClientError("base_url is required for custom provider")
        return CustomClient(api_key=api_key, model=model, base_url=base_url)
    else:
        raise LLMClientError(f"Unknown provider: {provider}")
