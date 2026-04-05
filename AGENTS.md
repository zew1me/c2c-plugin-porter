# AGENTS.md

## Purpose

This repo is a marketplace-style Codex plugin repo. It currently ships exactly one plugin:

- `plugins/c2c-plugin-porter`

Keep work focused on the Claude-to-Codex porting utility and the marketplace wrapper needed for Codex to discover it.

## Working rules

- Treat the repo root as the marketplace root, not the plugin root.
- Treat `plugins/c2c-plugin-porter/` as the Python project root for `uv` commands.
- Prefer `uv` for Python workflows.
- Use `uv sync --dev --project plugins/c2c-plugin-porter` to prepare the environment.
- Use `./plugins/c2c-plugin-porter/scripts/check.sh` for the shared verification path.
- Do not preserve raw Claude runtime names in generated Codex output when behavior can be spelled out explicitly.
- If a Claude tool restriction cannot be mapped cleanly, document the caveat rather than silently dropping it.

## Important paths

- `.agents/plugins/marketplace.json`: marketplace registry for Codex
- `plugins/c2c-plugin-porter/.codex-plugin/plugin.json`: plugin manifest
- `plugins/c2c-plugin-porter/skills/`: Codex plugin skills
- `plugins/c2c-plugin-porter/src/c2c_porter/`: Python conversion engine
- `plugins/c2c-plugin-porter/scripts/run_porter.sh`: shipped launcher for the packaged CLI
- `plugins/c2c-plugin-porter/tests/fixtures/`: Claude plugin fixtures
- `plugins/c2c-plugin-porter/evals/`: local headless Codex smoke-eval materials

## Verification

Before finishing work:

```bash
uv sync --dev --project plugins/c2c-plugin-porter
./plugins/c2c-plugin-porter/scripts/check.sh
```

Run the local eval smoke test when touching plugin behavior or conversion workflows:

```bash
./plugins/c2c-plugin-porter/scripts/run_local_eval.sh
```
