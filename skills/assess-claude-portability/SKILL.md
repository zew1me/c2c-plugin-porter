---
name: assess-claude-portability
description: Use when deciding whether a Claude plugin is worth porting to Codex, or when you need a component-by-component portability summary first.
---

# Assess Claude Portability

Run the scanner before doing any manual rewrite work.

## Commands

```bash
uv run c2c-porter scan <source-plugin>
uv run c2c-porter plan <source-plugin>
```

## Heuristics

- `skills/` usually port directly with light rewrites.
- `commands/` usually become Codex skills or plugin docs.
- `agents/` usually need flattening into sequential workflows.
- Claude built-ins like `Task`, `Teammate`, `AskUserQuestion`, `update-config`, or `claude code guide` should be rewritten into explicit behavior.

Reject the port if most of the source value is Claude runtime semantics and the generated Codex result would mostly be caveats.
