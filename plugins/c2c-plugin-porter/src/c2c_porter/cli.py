from __future__ import annotations

import json
from pathlib import Path

import typer

from c2c_porter.porter import (
    assess_inventory,
    convert_plugin,
    load_plugin_inventory,
)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Port Claude plugins into Codex plugins.",
)


@app.command()
def scan(source: Path) -> None:
    """Scan and summarize a Claude plugin."""
    inventory = load_plugin_inventory(source.resolve())
    typer.echo(json.dumps(assess_inventory(inventory), indent=2))


@app.command()
def plan(source: Path) -> None:
    """Assess portability and print a plan payload."""
    inventory = load_plugin_inventory(source.resolve())
    payload = assess_inventory(inventory)
    payload["next_step"] = "convert" if payload["summary"]["worth_porting"] else "extract-guidance-only"
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def convert(source: Path, destination: Path) -> None:
    """Generate a Codex plugin from a Claude plugin."""
    output_root = convert_plugin(source.resolve(), destination.resolve())
    typer.echo(str(output_root))


def main() -> None:
    app()
