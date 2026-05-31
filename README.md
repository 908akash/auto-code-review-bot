# auto-code-review-bot

An automated code review bot. It parses a `git diff`, sends each file to a review
provider, and prints findings. This is the foundation skeleton: it runs
end-to-end offline using a fake provider. Real LLM support is coming next.

## Install

```sh
pip install -e .
```

## Usage

Review a diff stored in a file:

```sh
review-bot --diff-file benchmarks/samples/single_file.diff
```

Review a diff piped from `git`:

```sh
git diff | review-bot --stdin
```

Choose an output format with `--format` (`summary` is the default):

```sh
git diff | review-bot --stdin --format inline
```

## Finding categories

- **style** — formatting and stylistic issues
- **bug_risk** — likely bugs or risky logic
- **security** — security concerns
- **naming** — unclear or misleading names

Each finding also has a severity: `low`, `medium`, or `high`.

## Example output

```
$ review-bot --diff-file benchmarks/samples/single_file.diff
example.py (3 finding(s)):
  line 2 [low] naming — Variable name 'x' is not descriptive.
  line 3 [medium] bug_risk — Possible off-by-one error in loop bound.
  line 5 [high] security — User input is used without validation.
```

## Status

The findings above come from a built-in `FakeProvider` so the pipeline runs
without any API keys. Real LLM-backed providers (Anthropic, OpenAI) land in the
next iteration; see `.env.example` for the keys they will use.

## Development

```sh
pip install -e ".[dev]"
pytest
```
