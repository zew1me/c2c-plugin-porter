#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$ROOT/tests/fixtures/sample-claude-plugin"
TMP_DIR="$ROOT/evals/tmp"
PROMPT_FILE="$ROOT/evals/prompts/smoke-eval.txt"

mkdir -p "$TMP_DIR"

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found; skipping local eval"
  exit 0
fi

cat <<EOF >"$PROMPT_FILE"
Use the local c2c-plugin-porter repo as guidance and assess the Claude plugin fixture at:
$FIXTURE

Summarize:
1. whether it is worth porting
2. which references need rewriting
3. which components port directly vs need flattening
EOF

echo "Running deterministic smoke checks first..."
uv run c2c-porter scan "$FIXTURE" >"$TMP_DIR/scan.json"

echo "Attempting headless Codex smoke eval..."
set +e
codex exec --skip-git-repo-check -C "$ROOT" "$(cat "$PROMPT_FILE")" \
  -o "$TMP_DIR/codex-last-message.txt" \
  >"$TMP_DIR/codex-stdout.log" \
  2>"$TMP_DIR/codex-stderr.log" &
PID=$!
TIMEOUT_SECONDS="${C2C_EVAL_TIMEOUT_SECONDS:-30}"
START_TIME=$(date +%s)

while kill -0 "$PID" >/dev/null 2>&1; do
  NOW=$(date +%s)
  if (( NOW - START_TIME >= TIMEOUT_SECONDS )); then
    kill "$PID" >/dev/null 2>&1 || true
    wait "$PID" >/dev/null 2>&1 || true
    STATUS=124
    break
  fi
  sleep 1
done

if [[ -z "${STATUS:-}" ]]; then
  wait "$PID"
  STATUS=$?
fi
set -e

if [[ $STATUS -ne 0 ]]; then
  echo "codex exec returned status $STATUS"
  if [[ $STATUS -eq 124 ]]; then
    echo "codex exec timed out after ${TIMEOUT_SECONDS}s"
  fi
  echo "The attempted prompt is saved at $PROMPT_FILE"
  echo "Stdout and stderr were captured to:"
  echo "- $TMP_DIR/codex-stdout.log"
  echo "- $TMP_DIR/codex-stderr.log"
  exit 0
fi

echo "Smoke eval completed. Outputs:"
echo "- $TMP_DIR/scan.json"
echo "- $TMP_DIR/codex-last-message.txt"
echo "- $TMP_DIR/codex-stdout.log"
echo "- $TMP_DIR/codex-stderr.log"
