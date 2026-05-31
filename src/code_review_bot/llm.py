"""Review provider protocol and an offline fake implementation."""

from __future__ import annotations

import json
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
