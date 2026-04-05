# c2c-plugin-porter

`c2c-plugin-porter` is a Codex plugin that creates **Codex plugins from Claude plugins**.

It is intentionally narrow:

- scan a Claude plugin
- decide whether it is worth porting
- rewrite Claude-specific runtime references into explicit behavior
- generate a Codex plugin scaffold plus caveats and reports

The repo is only the utility and the Codex plugin itself. It is not a marketplace repo.

## What it handles

- direct skill ports from `skills/**/SKILL.md`
- metadata and plugin manifest conversion
- command-to-skill rewrite guidance
- flattening of agent/subagent-heavy workflows into sequential Codex workflows
- caveats for loosened tool restrictions when no exact Codex mapping exists

## What it does not pretend to support

- native Claude Agent Teams parity
- direct execution of Claude-only runtime primitives
- perfect one-to-one translation of Claude commands or agent orchestration

## Project layout

```text
.codex-plugin/plugin.json   # Codex plugin manifest
skills/                     # Agent-facing skills for using the porter
scripts/port_to_codex.py    # CLI entrypoint
src/c2c_porter/            # Deterministic porter logic
tests/                     # pytest suite
evals/                     # headless Codex smoke-eval inputs
.githooks/                 # pre-commit and pre-push hooks
```

## Quick start

```bash
uv sync --dev
./scripts/install_git_hooks.sh
uv run pytest
uv run ruff check .
uv run ty check src tests
```

Scan a Claude plugin:

```bash
uv run c2c-porter scan /path/to/source-plugin
```

Convert a Claude plugin:

```bash
uv run c2c-porter convert /path/to/source-plugin ./generated
```

## Local Codex evals

Smoke evals are scriptable through `codex exec`:

```bash
./scripts/run_local_eval.sh
```

The eval script is intentionally best-effort. It verifies that:

- `codex exec` is available locally
- the sample Claude plugin fixture can be scanned
- a headless Codex run can be pointed at the local plugin repo and sample materials

If your local Codex installation requires login or different plugin loading behavior, the script will explain the exact command it attempted.

## GitHub repo creation

This repo is meant to live at:

- `https://github.com/zew1me/c2c-plugin-porter`

If `gh auth status` shows an invalid token locally, the code can still be prepared here first and the repo can be created once GitHub auth is refreshed.
