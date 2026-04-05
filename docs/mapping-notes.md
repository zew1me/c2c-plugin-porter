# Mapping Notes

The porter focuses on behavior-level rewrites rather than literal name preservation.

## Starter mappings

- `Read` -> inspect or read specific files
- `Glob` -> enumerate matching files
- `Grep` -> search text patterns across files
- `Bash` -> run shell commands
- `WebFetch` -> open a primary source URL directly
- `WebSearch` -> search the web for current information
- `AskUserQuestion` -> ask the user a focused decision question
- `Task` -> delegate a bounded subtask or perform that pass sequentially
- `Teammate` -> coordinate multiple agents or flatten the workflow sequentially
- `update-config` -> inspect and update the relevant configuration files directly
- `claude code guide` -> extract the needed guidance and rewrite it in product-neutral terms

## Caveat policy

If a source plugin relies on explicit tool restrictions that do not map cleanly to Codex, the generated output may loosen the restriction, but the conversion report must call that out explicitly.
