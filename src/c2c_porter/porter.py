from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

TOOL_PATTERN = re.compile(
    r"\b(Read|Glob|Grep|Bash|WebFetch|WebSearch|Task|TaskCreate|TaskList|"
    r"AskUserQuestion|EnterPlanMode|Teammate|TodoRead|TodoWrite)\b"
)
SKILL_CALL_PATTERN = re.compile(r"Skill\(([^)]+)\)")
CLAUDE_GUIDE_PATTERN = re.compile(r"\bclaude code guide\b", re.IGNORECASE)
USE_SKILL_PATTERN = re.compile(r"\buse (?:the )?([a-z0-9-]+) skill\b", re.IGNORECASE)

REFERENCE_MAPPINGS = {
    "Read": "inspect or read specific files",
    "Glob": "enumerate matching files",
    "Grep": "search text patterns across files",
    "Bash": "run shell commands",
    "WebFetch": "open a primary source URL directly",
    "WebSearch": "search the web for current information",
    "AskUserQuestion": "ask the user a focused decision question",
    "EnterPlanMode": "switch into explicit planning before mutation",
    "Task": "delegate a bounded subtask or run the pass sequentially",
    "TaskCreate": "track a planned subtask explicitly",
    "TaskList": "inspect task progress explicitly",
    "Teammate": "coordinate multiple agents or flatten the workflow sequentially",
    "TodoRead": "read a working checklist",
    "TodoWrite": "update a working checklist",
    "update-config": "inspect and modify the relevant config files directly",
    "claude code guide": "extract the needed guidance and rewrite it in product-neutral terms",
}

NON_DIRECT_REFERENCE_NAMES = {
    "AskUserQuestion",
    "EnterPlanMode",
    "Task",
    "TaskCreate",
    "TaskList",
    "Teammate",
    "TodoRead",
    "TodoWrite",
    "update-config",
    "claude code guide",
}


@dataclass(frozen=True)
class Reference:
    name: str
    category: str
    meaning: str


@dataclass(frozen=True)
class PluginInventory:
    root: Path
    plugin_name: str
    manifest_path: Path
    component_counts: dict[str, int]
    references: list[Reference]


def normalize_plugin_name(plugin_name: str) -> str:
    normalized = plugin_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def extract_references(text: str) -> list[Reference]:
    seen: set[tuple[str, str]] = set()
    references: list[Reference] = []

    def add(name: str, category: str) -> None:
        key = (name, category)
        if key in seen:
            return
        seen.add(key)
        references.append(
            Reference(
                name=name,
                category=category,
                meaning=REFERENCE_MAPPINGS.get(name, "expand this named reference into explicit behavior"),
            )
        )

    for match in TOOL_PATTERN.finditer(text):
        add(match.group(1), "tool")

    for match in SKILL_CALL_PATTERN.finditer(text):
        add(match.group(1).strip(), "built-in-skill")

    for match in USE_SKILL_PATTERN.finditer(text):
        add(match.group(1).strip(), "skill-reference")

    if CLAUDE_GUIDE_PATTERN.search(text):
        add("claude code guide", "built-in-skill")

    return references


def _iter_component_files(root: Path, folder: str) -> list[Path]:
    base = root / folder
    if not base.exists():
        return []
    if folder == "skills":
        return sorted(base.glob("*/SKILL.md"))
    return sorted(base.glob("*.md"))


def load_plugin_inventory(plugin_root: Path) -> PluginInventory:
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing Claude plugin manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text())

    references: list[Reference] = []
    for component_path in (
        _iter_component_files(plugin_root, "skills")
        + _iter_component_files(plugin_root, "commands")
        + _iter_component_files(plugin_root, "agents")
    ):
        references.extend(extract_references(component_path.read_text()))

    readme_path = plugin_root / "README.md"
    doc_count = 1 if readme_path.exists() else 0
    if readme_path.exists():
        references.extend(extract_references(readme_path.read_text()))

    deduped: list[Reference] = []
    seen: set[tuple[str, str]] = set()
    for reference in references:
        key = (reference.name, reference.category)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(reference)

    return PluginInventory(
        root=plugin_root,
        plugin_name=normalize_plugin_name(manifest["name"]),
        manifest_path=manifest_path,
        component_counts={
            "skills": len(_iter_component_files(plugin_root, "skills")),
            "commands": len(_iter_component_files(plugin_root, "commands")),
            "agents": len(_iter_component_files(plugin_root, "agents")),
            "docs": doc_count,
        },
        references=deduped,
    )


def assess_inventory(inventory: PluginInventory) -> dict:
    components = {
        "skills": {"count": inventory.component_counts["skills"], "strategy": "direct"},
        "commands": {"count": inventory.component_counts["commands"], "strategy": "rewrite"},
        "agents": {"count": inventory.component_counts["agents"], "strategy": "flatten"},
        "docs": {"count": inventory.component_counts["docs"], "strategy": "carry"},
    }

    total_weight = sum(inventory.component_counts.values()) or 1
    loss_weight = inventory.component_counts["commands"] + inventory.component_counts["agents"]
    worth_porting = (loss_weight / total_weight) < 0.75

    return {
        "plugin_name": inventory.plugin_name,
        "components": components,
        "summary": {
            "worth_porting": worth_porting,
            "references_detected": len(inventory.references),
            "lossy_component_ratio": round(loss_weight / total_weight, 3),
        },
        "references": [asdict(reference) for reference in inventory.references],
    }


def _rewrite_reference_name(name: str) -> str:
    meaning = REFERENCE_MAPPINGS.get(name)
    if not meaning:
        return name
    return f"{name} ({meaning})"


def _rewrite_skill_markdown(text: str) -> str:
    rewritten = text
    for name, _meaning in REFERENCE_MAPPINGS.items():
        if name == "claude code guide":
            rewritten = re.sub(
                CLAUDE_GUIDE_PATTERN,
                _rewrite_reference_name("claude code guide"),
                rewritten,
            )
            continue
        rewritten = re.sub(rf"\b{re.escape(name)}\b", _rewrite_reference_name(name), rewritten)
    return rewritten


def _build_plugin_manifest(plugin_name: str, repository_url: str | None = None) -> dict:
    repo_url = repository_url or "https://github.com/zew1me/c2c-plugin-porter"
    return {
        "name": plugin_name,
        "version": "0.1.0",
        "description": "Port Claude plugins into Codex plugins with explicit mapping and caveats.",
        "author": {
            "name": "zew1me",
            "url": "https://github.com/zew1me",
        },
        "homepage": repo_url,
        "repository": repo_url,
        "license": "MIT",
        "keywords": ["codex", "claude", "plugins", "migration"],
        "skills": "./skills/",
        "interface": {
            "displayName": plugin_name,
            "shortDescription": "Convert Claude plugins into Codex plugins.",
            "longDescription": (
                "Scans Claude plugin structure, resolves Claude-specific references, "
                "and generates Codex plugin output with caveats."
            ),
            "developerName": "zew1me",
            "category": "Productivity",
            "capabilities": ["Interactive", "Write"],
            "websiteURL": repo_url,
            "privacyPolicyURL": repo_url,
            "termsOfServiceURL": repo_url,
            "defaultPrompt": [
                "Assess this Claude plugin for Codex portability.",
                "Convert this Claude skill into a Codex plugin skill.",
                "Explain which Claude runtime references need rewrites.",
            ],
            "brandColor": "#1F6FEB",
        },
    }


def convert_plugin(source_root: Path, destination_root: Path) -> Path:
    inventory = load_plugin_inventory(source_root)
    output_name = f"{inventory.plugin_name}-codex"
    output_root = destination_root / output_name

    (output_root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (output_root / "skills").mkdir(parents=True, exist_ok=True)
    (output_root / "docs").mkdir(parents=True, exist_ok=True)

    manifest = _build_plugin_manifest(output_name)
    (output_root / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    for source_skill in _iter_component_files(source_root, "skills"):
        skill_dir = output_root / "skills" / source_skill.parent.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        original = source_skill.read_text()
        rewritten = _rewrite_skill_markdown(original)
        skill_dir.joinpath("SKILL.md").write_text(
            "<!-- Converted from a Claude plugin skill. Named Claude references were expanded or rewritten. -->\n"
            + rewritten
        )

    assessment = assess_inventory(inventory)
    rewritten_reference_names = sorted(
        reference.name
        for reference in inventory.references
        if reference.name in NON_DIRECT_REFERENCE_NAMES
    )
    report_json = {
        "source_plugin": inventory.plugin_name,
        "output_plugin": output_name,
        "component_counts": inventory.component_counts,
        "assessment": assessment["summary"],
        "unresolved_or_rewritten_references": rewritten_reference_names,
    }
    (output_root / "docs" / "porting-report.json").write_text(
        json.dumps(report_json, indent=2) + "\n"
    )
    (output_root / "docs" / "PORTING_REPORT.md").write_text(
        "\n".join(
            [
                f"# Porting Report: {inventory.plugin_name}",
                "",
                f"- Output plugin: `{output_name}`",
                f"- Worth porting: `{assessment['summary']['worth_porting']}`",
                f"- Skills: `{inventory.component_counts['skills']}` direct",
                f"- Commands: `{inventory.component_counts['commands']}` rewrite",
                f"- Agents: `{inventory.component_counts['agents']}` flatten",
                "",
                "## References Rewritten Or Flagged",
                "",
                *[f"- `{name}`" for name in rewritten_reference_names],
            ]
        )
        + "\n"
    )

    return output_root
