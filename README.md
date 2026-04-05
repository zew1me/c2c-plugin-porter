# c2c-plugin-porter Marketplace

This repo is now a **Codex marketplace-style repo** whose only shipped plugin is `c2c-plugin-porter`.

The plugin itself lives at [plugins/c2c-plugin-porter](/Users/nigelstuke/Documents/repos/zew1me/c2c-plugin-porter/plugins/c2c-plugin-porter), and the marketplace registry entry that points Codex at it lives at [.agents/plugins/marketplace.json](/Users/nigelstuke/Documents/repos/zew1me/c2c-plugin-porter/.agents/plugins/marketplace.json).

## Layout

```text
.agents/plugins/marketplace.json     # Marketplace registry for Codex
plugins/c2c-plugin-porter/           # The only plugin in this repo
.githooks/                           # Shared repo hooks
.github/workflows/                   # PR automation
```

Inside the plugin:

```text
plugins/c2c-plugin-porter/
├── .codex-plugin/plugin.json
├── skills/
├── scripts/
├── src/c2c_porter/
├── tests/
├── evals/
└── pyproject.toml
```

## Local development

```bash
uv sync --dev --project plugins/c2c-plugin-porter
./plugins/c2c-plugin-porter/scripts/install_git_hooks.sh
./plugins/c2c-plugin-porter/scripts/check.sh
```

Useful commands:

```bash
./plugins/c2c-plugin-porter/scripts/run_porter.sh scan /path/to/source-plugin
./plugins/c2c-plugin-porter/scripts/run_porter.sh convert /path/to/source-plugin ./generated
./plugins/c2c-plugin-porter/scripts/run_local_eval.sh
```

## Why the repo is a marketplace

Local Codex plugin installs appear to expect a marketplace-style layout with:

- `.agents/plugins/marketplace.json`
- `plugins/<plugin-name>/.codex-plugin/plugin.json`

This repo now matches that shape directly so it can act as both:

- the source repo for the utility
- the installable local marketplace wrapper for Codex
