#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

uv run --project "$ROOT" ruff check "$ROOT"
uv run --project "$ROOT" ty check "$ROOT/src" "$ROOT/tests"
uv run --project "$ROOT" pytest "$ROOT/tests"
"$ROOT/scripts/run_porter.sh" scan "$ROOT/tests/fixtures/sample-claude-plugin" >/dev/null
