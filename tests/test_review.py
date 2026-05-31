from __future__ import annotations

import pytest

from code_review_bot.llm import (
    AnthropicProvider,
    FakeProvider,
    OpenAIProvider,
    make_provider,
)
from code_review_bot.models import Finding
from code_review_bot.review import review_diff

SINGLE_FILE_DIFF = """\
diff --git a/example.py b/example.py
index 1234567..89abcde 100644
--- a/example.py
+++ b/example.py
@@ -1,4 +1,5 @@
 import os
-x = 1
+x = 2
+y = 3
 print(x)
"""


FENCED_RESPONSE = """\
```json
[
  {"file": "a.py", "line": 1, "category": "style", "severity": "low", "message": "Tabs."}
]
```"""


class FencedProvider:
    def review(self, prompt: str) -> str:
        return FENCED_RESPONSE


class MalformedProvider:
    def review(self, prompt: str) -> str:
        return "this is not json"


class EmptyArrayProvider:
    def review(self, prompt: str) -> str:
        return "[]"


def test_fake_provider_returns_parsed_findings() -> None:
    findings = review_diff(SINGLE_FILE_DIFF, FakeProvider())
    assert len(findings) == 3
    assert all(isinstance(f, Finding) for f in findings)
    assert findings[0].category == "naming"
    assert findings[2].severity == "high"


def test_malformed_json_is_skipped(capsys) -> None:
    findings = review_diff(SINGLE_FILE_DIFF, MalformedProvider())
    assert findings == []
    captured = capsys.readouterr()
    assert "malformed JSON" in captured.out


def test_empty_diff_means_no_provider_calls() -> None:
    findings = review_diff("", FakeProvider())
    assert findings == []


def test_empty_array_response() -> None:
    findings = review_diff(SINGLE_FILE_DIFF, EmptyArrayProvider())
    assert findings == []


def test_fenced_json_response_is_stripped() -> None:
    findings = review_diff(SINGLE_FILE_DIFF, FencedProvider())
    assert len(findings) == 1
    assert findings[0].file == "a.py"
    assert findings[0].message == "Tabs."


def test_make_provider_fake() -> None:
    assert isinstance(make_provider("fake", None), FakeProvider)


def test_make_provider_anthropic_no_api_call(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    provider = make_provider("anthropic", None)
    assert isinstance(provider, AnthropicProvider)
    assert provider.model == "claude-sonnet-4-6"


def test_make_provider_openai_no_api_call(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    provider = make_provider("openai", None)
    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-4o"


def test_make_provider_model_override() -> None:
    provider = make_provider("anthropic", "claude-custom")
    assert isinstance(provider, AnthropicProvider)
    assert provider.model == "claude-custom"


def test_make_provider_unknown_raises() -> None:
    with pytest.raises(ValueError):
        make_provider("bogus", None)
