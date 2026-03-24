from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.append(str(Path(__file__).resolve().parent.parent))
from meteopy.forecasting.imgw_simple_forecaster import IMGWSimpleForecaster
from meteopy.imgw_statistics.imgw_statistics import IMGWStatistics


@click.command()
@click.option("--parameter", required=True, help="Wybarnay parameter do analizy")
@click.option(
    "--stations",
    multiple=True,
    required=True,
    help="Lista stacji lub jedna stacja (jeśli parameter jest pusty to funkcja bierze wszsytkie stacje)",
)
@click.option("--data-type", required=True, help="Typ danych (np. klimat, synop, opad)")
@click.option("--start-date", required=True, help="Data początkowa (DD.MM.YYYY)")
@click.option("--end-date", required=True, help="Data końcowa (DD.MM.YYYY)")
@click.option(
    "--use-t-files", is_flag=True, help="Czy użyć plików z dopiskiem _t (zawieraja one inne dane niż pliki podstawowe)"
)
def basic_summary(
    parameter: str, stations: list, data_type: str, start_date: str, end_date: str, use_t_files: bool = False
) -> None:
    start_year = int(start_date.split(".")[-1])
    end_year = int(end_date.split(".")[-1])
    if start_year != end_year:
        year_range = tuple(range(min(start_year, end_year), max(start_year, end_year) + 1))
    else:
        year_range = start_year, ""
    statistics = IMGWSimpleForecaster()
    year_check = list(year_range)
    station_check = ", ".join(stations)
    statistics.check_existing_years(station_check, data_type, year_check)
    statistics_1 = IMGWStatistics()
    statistics_1.calculate_basic_stats(parameter, stations, data_type, start_date, end_date, use_t_files)
