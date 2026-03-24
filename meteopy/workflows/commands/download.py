from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.append(str(Path(__file__).resolve().parent.parent))
from meteopy.data_fetchers.imgw_fetecher import IMGWDataFetcher
from meteopy.preprocessing.imgw_handler import IMGWDataHandler


@click.command()
@click.option("--data-type", required=True, help="Folder, z którego mają zostać pobrane dane (np. klimat, synop, opad)")
@click.option(
    "--years", required=True, help="Rok lub lata (może być przedział lat rozdzielony myślnikiem lub przecinkami)"
)
def download(data_type: str, years: str) -> None:
    year_range = tuple(years.split(",")) + ("",) if "-" in years or "," in years else (int(years), "")
    # year_range= (*tuple(years.split(",")), "") if "-" in years or "," in years else (int(years), "") # opcja alternatywna
    fetcher = IMGWDataFetcher()
    result = fetcher.fetch(f"{data_type}/", year_range)
    fetcher.download_file(result, data_type)
    handler = IMGWDataHandler(data_type)
    handler.divide_downloaded(data_type)
