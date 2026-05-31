"""Review provider protocol, an offline fake, and real LLM providers."""

from __future__ import annotations

import json
import os
from typing import Protocol


class ReviewProvider(Protocol):
    def review(self, prompt: str) -> str:
        """Return raw model text for the given prompt."""
        ...


class FakeProvider:
    """Offline provider returning fixed findings so the pipeline runs without an LLM."""

    def review(self, prompt: str) -> str:
        findings = [
            {
                "file": "example.py",
                "line": 2,
                "category": "naming",
                "severity": "low",
                "message": "Variable name 'x' is not descriptive.",
            },
            {
                "file": "example.py",
                "line": 3,
                "category": "bug_risk",
                "severity": "medium",
                "message": "Possible off-by-one error in loop bound.",
            },
            {
                "file": "example.py",
                "line": 5,
                "category": "security",
                "severity": "high",
                "message": "User input is used without validation.",
            },
        ]
        return json.dumps(findings)


def _require_key(env_var: str) -> str:
    value = os.environ.get(env_var)
    if not value:
        raise RuntimeError(
            f"Missing {env_var}. Set it in your environment or in a .env file "
            f"(see .env.example)."
        )
    return value


class AnthropicProvider:
    """Review provider backed by the Anthropic Messages API."""

    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic

            _require_key("ANTHROPIC_API_KEY")
            self._client = anthropic.Anthropic()
        return self._client

    def review(self, prompt: str) -> str:
        client = self._get_client()
        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in message.content if block.type == "text"
        )


class OpenAIProvider:
    """Review provider backed by the OpenAI Chat Completions API."""

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import openai

            _require_key("OPENAI_API_KEY")
            self._client = openai.OpenAI()
        return self._client

    def review(self, prompt: str) -> str:
        client = self._get_client()
        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content or ""


def make_provider(name: str, model: str | None) -> ReviewProvider:
    """Build a ReviewProvider by name. The single place provider selection lives."""
    if name == "fake":
        return FakeProvider()
    if name == "anthropic":
        return AnthropicProvider(model) if model else AnthropicProvider()
    if name == "openai":
        return OpenAIProvider(model) if model else OpenAIProvider()
    raise ValueError(f"unknown provider: {name!r}")
