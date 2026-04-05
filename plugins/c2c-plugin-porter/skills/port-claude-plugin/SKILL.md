---
name: port-claude-plugin
description: Use when converting a Claude plugin into a Codex plugin. Run the deterministic porter utility first, then refine the generated output and caveats.
---

# Port Claude Plugin

This skill ports a Claude plugin into a Codex plugin with explicit caveats for unsupported runtime behavior.

## Workflow

1. Run `./plugins/c2c-plugin-porter/scripts/run_porter.sh scan <source-plugin>` from the marketplace repo root, or `./scripts/run_porter.sh scan <source-plugin>` from the plugin root.
2. Review the portability summary and named-reference inventory.
3. If the plugin is worth porting, run `./plugins/c2c-plugin-porter/scripts/run_porter.sh convert <source-plugin> <output-dir>` from the marketplace repo root, or `./scripts/run_porter.sh convert <source-plugin> <output-dir>` from the plugin root.
4. Inspect the generated `PORTING_REPORT.md` and expand any remaining Claude-only references into explicit behavior.
5. If the source relies on Claude subagents or Agent Teams, flatten that logic into sequential Codex skill steps unless the target environment clearly supports delegation.

## Guardrails

- Do not leave raw Claude runtime names as unexplained required steps.
- If tool restrictions cannot be mapped cleanly, loosen them only with a visible caveat.
- Prefer porting reusable skills and checklists over commands or agents when fidelity is low.
