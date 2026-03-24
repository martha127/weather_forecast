from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.append(str(Path(__file__).resolve().parent.parent))
from meteopy.workflows.commands.basic_summary import basic_summary
from meteopy.workflows.commands.download import download
from meteopy.workflows.commands.full_analysis import full_analysis


@click.group()
def cli() -> None:
    pass


cli.add_command(download, name="download")
cli.add_command(basic_summary, name="basic_summary")
cli.add_command(full_analysis, name="full_analysis")
if __name__ == "__main__":
    cli()
