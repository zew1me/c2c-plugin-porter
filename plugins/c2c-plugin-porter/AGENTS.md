# AGENTS.md

## Purpose

This directory is the `c2c-plugin-porter` Codex plugin and its deterministic helper utility. Keep work focused on porting Claude plugins into Codex plugins.

## Working rules

- Prefer `uv` for Python workflows.
- Use `uv run --project . pytest` for tests when working inside this directory.
- Use `uv run --project . ruff check .` for linting when the current directory is not the plugin root.
- Use `uv run --project . ty check src tests` for type analysis when the current directory is not the plugin root.
- Do not preserve raw Claude runtime names in generated Codex output when behavior can be spelled out explicitly.
- If a Claude tool restriction cannot be mapped cleanly, document the caveat rather than silently dropping it.

## Important paths

- `.codex-plugin/plugin.json`: plugin manifest
- `skills/`: Codex plugin skills
- `src/c2c_porter/cli.py`: packaged CLI entrypoint
- `scripts/run_porter.sh`: shipped launcher that resolves the plugin root and runs the packaged CLI
- `src/c2c_porter/`: Python conversion engine
- `tests/fixtures/`: Claude plugin fixtures
- `evals/`: local headless Codex smoke-eval materials

## Verification

Before finishing work:

```bash
./scripts/check.sh
```

Run the local eval smoke test when touching plugin behavior or conversion workflows:

```bash
./scripts/run_local_eval.sh
```
