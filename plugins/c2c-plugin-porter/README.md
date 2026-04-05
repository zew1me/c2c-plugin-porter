# c2c-plugin-porter

`c2c-plugin-porter` is a Codex plugin that creates **Codex plugins from Claude plugins**.

It is intentionally narrow:

- scan a Claude plugin
- decide whether it is worth porting
- rewrite Claude-specific runtime references into explicit behavior
- generate a Codex plugin scaffold plus caveats and reports

This plugin now lives inside a marketplace-style repo. The plugin root is `plugins/c2c-plugin-porter/`.

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

## Plugin layout

```text
.codex-plugin/plugin.json   # Codex plugin manifest
skills/                     # Agent-facing skills for using the porter
scripts/run_porter.sh       # Shipped launcher for the packaged CLI
src/c2c_porter/             # Deterministic porter logic
tests/                      # pytest suite
evals/                      # headless Codex smoke-eval inputs
```

## Quick start

From the repo root:

```bash
uv sync --dev --project plugins/c2c-plugin-porter
./plugins/c2c-plugin-porter/scripts/install_git_hooks.sh
./plugins/c2c-plugin-porter/scripts/check.sh
```

Scan a Claude plugin:

```bash
./plugins/c2c-plugin-porter/scripts/run_porter.sh scan /path/to/source-plugin
```

Convert a Claude plugin:

```bash
./plugins/c2c-plugin-porter/scripts/run_porter.sh convert /path/to/source-plugin ./generated
```

## Why this is plugin-shippable

The Python package lives in `src/c2c_porter`, but it is shipped together with the plugin.
The plugin skills call the shipped launcher in `scripts/run_porter.sh`, not a bare ambient command.
That launcher always runs:

```bash
uv run --project <plugin-root> c2c-porter ...
```

So the package is resolved from the plugin itself, even if Codex invokes it from another working directory.

## Local Codex evals

Smoke evals are scriptable through `codex exec`:

```bash
./plugins/c2c-plugin-porter/scripts/run_local_eval.sh
```

The eval script is intentionally best-effort. It verifies that:

- `codex exec` is available locally
- the sample Claude plugin fixture can be scanned
- a headless Codex run can be pointed at the local plugin and marketplace materials
