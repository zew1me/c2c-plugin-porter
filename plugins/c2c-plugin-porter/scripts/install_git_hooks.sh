#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

git config core.hooksPath "$REPO_ROOT/.githooks"
echo "Configured git hooks to use .githooks/"
