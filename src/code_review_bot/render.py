"""Render findings in different output formats."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Literal

from .models import Finding


def render(findings: list[Finding], fmt: Literal["summary", "inline", "json"]) -> str:
    """Render findings as a summary, inline list, or JSON string."""
    if fmt == "json":
        return json.dumps([asdict(f) for f in findings], indent=2)

    if fmt == "inline":
        return "\n".join(
            f"{f.file}:{f.line} [{f.severity}] {f.category} — {f.message}"
            for f in findings
        )

    if fmt == "summary":
        if not findings:
            return "No findings."
        by_file: dict[str, list[Finding]] = {}
        for f in findings:
            by_file.setdefault(f.file, []).append(f)
        lines: list[str] = []
        for path in sorted(by_file):
            file_findings = by_file[path]
            lines.append(f"{path} ({len(file_findings)} finding(s)):")
            for f in file_findings:
                lines.append(
                    f"  line {f.line} [{f.severity}] {f.category} — {f.message}"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    raise ValueError(f"unknown format: {fmt}")
