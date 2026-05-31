from __future__ import annotations

from code_review_bot.llm import FakeProvider
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
