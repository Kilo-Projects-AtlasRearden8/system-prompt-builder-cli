"""Endpoint client for live testing against OpenAI-compatible APIs (default Ollama).

No API keys are required by default. Ollama runs locally and accepts empty
bearer tokens, which is why this tool is local-first and secret-free.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"


@dataclass
class EndpointConfig:
    """Configuration for the OpenAI-compatible chat endpoint."""

    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    api_key: str = ""
    timeout: float = 30.0


@dataclass
class ChatMessage:
    """A single chat message."""

    role: str
    content: str


@dataclass
class ChatResponse:
    """A chat completion response."""

    content: str
    model: str
    raw: Dict[str, Any] = field(default_factory=dict)


class EndpointError(Exception):
    """Raised when the endpoint cannot be reached or returns an error."""


class EndpointClient:
    """Talks to an OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(self, config: EndpointConfig | None = None) -> None:
        self.config = config or EndpointConfig()

    def chat(self, messages: List[ChatMessage]) -> ChatResponse:
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            body = exc.read()
            raise EndpointError(
                f"HTTP {exc.code}: {body.decode('utf-8', 'replace')}"
            ) from exc
        except urllib.error.URLError as exc:
            raise EndpointError(f"Cannot reach {self.config.base_url}: {exc}") from exc

        parsed = json.loads(body.decode("utf-8"))
        choices = parsed.get("choices", [])
        content = ""
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
        return ChatResponse(
            content=content,
            model=parsed.get("model", self.config.model),
            raw=parsed,
        )


class MockEndpoint:
    """In-memory fake endpoint for tests and demos (no network, no keys)."""

    def __init__(self, responses: Optional[Dict[str, str]] = None) -> None:
        self.responses = responses or {}
        self.calls: List[List[ChatMessage]] = []

    def chat(self, messages: List[ChatMessage]) -> ChatResponse:
        self.calls.append([ChatMessage(m.role, m.content) for m in messages])
        joined = "\n".join(m.content for m in messages)
        for pattern, response in self.responses.items():
            if pattern in joined:
                return ChatResponse(
                    content=response, model="mock-model", raw={"matched": pattern}
                )
        return ChatResponse(
            content=f"mock reply to: {joined[:80]}", model="mock-model", raw={}
        )
