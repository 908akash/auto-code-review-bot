"""Command-line interface for the code review bot."""

from __future__ import annotations

import sys

import click

from .llm import FakeProvider
from .render import render
from .review import review_diff


@click.command()
@click.option(
    "--diff-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Read a diff from a file.",
)
@click.option("--stdin", is_flag=True, help="Read a diff from standard input.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["summary", "inline", "json"]),
    default="summary",
    help="Output format.",
)
def main(diff_file: str | None, stdin: bool, fmt: str) -> None:
    """Review a git diff and print findings."""
    if diff_file and stdin:
        raise click.UsageError("Use only one of --diff-file or --stdin.")
    if not diff_file and not stdin:
        raise click.UsageError("Provide a diff via --diff-file or --stdin.")

    if stdin:
        diff_text = sys.stdin.read()
    else:
        with open(diff_file, encoding="utf-8") as handle:
            diff_text = handle.read()

    # TODO: swap FakeProvider for a real LLM-backed ReviewProvider here
    # (e.g. AnthropicProvider / OpenAIProvider) in the next iteration.
    provider = FakeProvider()

    findings = review_diff(diff_text, provider)
    click.echo(render(findings, fmt))  # type: ignore[arg-type]
