from __future__ import annotations

import json
import tempfile
from pathlib import Path

from c2c_porter.porter import (
    assess_inventory,
    convert_plugin,
    extract_references,
    load_plugin_inventory,
    normalize_plugin_name,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_references_detects_tools_and_built_in_skills() -> None:
    text = """
Use the Task tool to run parallel review work.
Use WebFetch for docs and AskUserQuestion at checkpoints.
If needed, call Skill(update-config) and the claude code guide.
"""
    refs = extract_references(text)
    names = {ref.name for ref in refs}

    assert "Task" in names
    assert "WebFetch" in names
    assert "AskUserQuestion" in names
    assert "update-config" in names
    assert "claude code guide" in names


def test_load_plugin_inventory_classifies_components() -> None:
    inventory = load_plugin_inventory(FIXTURES / "sample-claude-plugin")

    assert inventory.plugin_name == "sample-review"
    assert inventory.manifest_path.name == "plugin.json"
    assert inventory.component_counts == {
        "skills": 1,
        "commands": 1,
        "agents": 1,
        "docs": 1,
    }
    assert any(ref.name == "Task" for ref in inventory.references)
    assert any(ref.name == "update-config" for ref in inventory.references)


def test_assess_inventory_marks_agent_heavy_plugins_as_lossy() -> None:
    inventory = load_plugin_inventory(FIXTURES / "sample-claude-plugin")
    assessment = assess_inventory(inventory)

    assert assessment["summary"]["worth_porting"] is True
    assert assessment["components"]["agents"]["strategy"] == "flatten"
    assert assessment["components"]["commands"]["strategy"] == "rewrite"


def test_convert_plugin_generates_codex_plugin_output() -> None:
    source = FIXTURES / "sample-claude-plugin"
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = Path(tmp_dir)
        output_root = convert_plugin(source, destination)

        manifest = json.loads((output_root / ".codex-plugin" / "plugin.json").read_text())
        assert manifest["name"] == "sample-review-codex"
        assert (output_root / "skills" / "review-checklist" / "SKILL.md").exists()
        assert (output_root / "docs" / "PORTING_REPORT.md").exists()
        report = json.loads((output_root / "docs" / "porting-report.json").read_text())
        assert report["source_plugin"] == "sample-review"
        assert "Task" in report["unresolved_or_rewritten_references"]


def test_normalize_plugin_name_collapses_punctuation() -> None:
    assert normalize_plugin_name(" Claude To Codex Porter!! ") == "claude-to-codex-porter"
