"""Command-line interface for the code review bot."""

from __future__ import annotations

import sys

import click
from dotenv import load_dotenv

from .llm import make_provider
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
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai", "fake"]),
    default="anthropic",
    help="Review provider to use.",
)
@click.option(
    "--model",
    default=None,
    help="Model override (defaults to the provider's default).",
)
def main(
    diff_file: str | None,
    stdin: bool,
    fmt: str,
    provider: str,
    model: str | None,
) -> None:
    """Review a git diff and print findings."""
    load_dotenv()
    if diff_file and stdin:
        raise click.UsageError("Use only one of --diff-file or --stdin.")
    if not diff_file and not stdin:
        raise click.UsageError("Provide a diff via --diff-file or --stdin.")

    if stdin:
        diff_text = sys.stdin.read()
    else:
        with open(diff_file, encoding="utf-8") as handle:
            diff_text = handle.read()

    review_provider = make_provider(provider, model)

    findings = review_diff(diff_text, review_provider)
    click.echo(render(findings, fmt))  # type: ignore[arg-type]
