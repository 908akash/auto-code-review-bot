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

## API keys

Copy `.env.example` to `.env` and fill in the key for the provider you want:

```sh
cp .env.example .env
# then edit .env:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
```

The CLI loads `.env` automatically at startup.

## Providers and models

- `--provider anthropic|openai|fake` (default `anthropic`)
- `--model NAME` overrides the model (defaults: `claude-sonnet-4-6` for
  anthropic, `gpt-4o` for openai)

Real run against a live model:

```sh
git diff | review-bot --stdin --provider anthropic
git diff | review-bot --stdin --provider openai --model gpt-4o
```

Use `--provider fake` to run the offline fixture without any API key.

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

## Continuous integration & automated review

Two GitHub Actions workflows live in `.github/workflows/`:

- **`ci.yml`** — runs on every push and pull request. It installs the package
  and runs the full test suite (`python -m pytest -v`) on Python 3.11. It needs
  no secrets, so it works out of the box for anyone who forks the repo.
- **`pr-review.yml`** — runs on pull requests. It builds a diff of only the
  PR's own changes (merge-base/triple-dot against the base branch), runs the
  review bot over it, and posts the findings as a PR comment. If the bot finds
  nothing, it posts a short "No issues found" note instead.

One-time setup: running the AI review on your own repo requires an Anthropic
key. Add it under **Settings > Secrets and variables > Actions** as
`ANTHROPIC_API_KEY`. If the secret is absent, `pr-review.yml` skips the review
and comment steps and passes cleanly.

## Status

The example above uses `--provider fake`, a built-in fixture that runs without
any API keys. Anthropic and OpenAI providers are now wired in — see the API
keys and providers sections above.

## Development

```sh
pip install -e ".[dev]"
pytest
```
