"""Drive a diff through a review provider and collect findings."""

from __future__ import annotations

import json

from .diff import parse_diff
from .llm import ReviewProvider
from .models import Finding
from .prompts import build_review_prompt


def _strip_code_fence(text: str) -> str:
    """Strip surrounding whitespace and a ```json / ``` code fence if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Drop the opening fence line (e.g. ``` or ```json).
        lines = lines[1:]
        # Drop the closing fence line if present.
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def review_diff(diff_text: str, provider: ReviewProvider) -> list[Finding]:
    """Parse a diff, review each file, and collect findings.

    Malformed JSON from the provider is skipped with a warning rather than
    crashing the whole run.
    """
    findings: list[Finding] = []

    for file_diff in parse_diff(diff_text):
        prompt = build_review_prompt(file_diff)
        raw = provider.review(prompt)
        try:
            items = json.loads(_strip_code_fence(raw))
        except json.JSONDecodeError:
            print(f"warning: skipping malformed JSON for {file_diff.path}")
            continue

        if not isinstance(items, list):
            print(f"warning: expected a JSON array for {file_diff.path}")
            continue

        for item in items:
            try:
                findings.append(
                    Finding(
                        file=item["file"],
                        line=item["line"],
                        category=item["category"],
                        severity=item["severity"],
                        message=item["message"],
                    )
                )
            except (KeyError, TypeError):
                print(f"warning: skipping malformed finding for {file_diff.path}")
                continue

    return findings
