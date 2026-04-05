#!/usr/bin/env bash
set -euo pipefail

uv run ruff check .
uv run ty check src tests
uv run pytest
./scripts/run_porter.sh scan tests/fixtures/sample-claude-plugin >/dev/null
