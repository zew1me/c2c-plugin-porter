---
name: resolve-claude-references
description: Use when a Claude plugin mentions built-in tools, built-in skills, or plugin-local names that must be converted into explicit Codex-facing behavior.
---

# Resolve Claude References

The porter utility extracts named references, but the final output must explain behavior rather than rely on product-specific names.

## Mapping rules

- `Read`, `Glob`, `Grep`, `Bash`, `WebFetch`, `WebSearch`: map directly to capabilities.
- `Task`, `TaskCreate`, `TaskList`, `Teammate`: convert to delegation guidance or sequential fallbacks.
- `AskUserQuestion`: rewrite to an explicit decision point.
- `update-config`: rewrite to “inspect and update the relevant config file(s) directly”.
- `claude code guide`: replace with the actual guidance the source was invoking.

If you cannot map a reference confidently, document it in the generated report instead of guessing silently.
