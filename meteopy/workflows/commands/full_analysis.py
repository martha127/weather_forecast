from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.append(str(Path(__file__).resolve().parent.parent))
from meteopy.eda.imgw_eda_visualizer import IMGWDataVisualizer
from meteopy.forecasting.imgw_simple_forecaster import IMGWSimpleForecaster
from meteopy.imgw_statistics.imgw_statistics import IMGWStatistics


@click.command()
@click.option("--parameter", required=True, help="Wybarany parameter do analizy")
@click.option("--parameter1", required=False, help="Pierwszy parameter korelacji")
@click.option("--parameter2", required=False, help="Drugi parameter korelacji")
@click.option("--target", required=False, help="Prognozowany parameter w regresji liniowej")
@click.option(
    "--stations",
    multiple=True,
    required=True,
    help="Lista stacji lub jedna stacja (jeśli parameter jest pusty to funkcja bierze wszsytkie stacje)",
)
@click.option("--data-type", required=True, help="Typ danych (np. klimat, synop, opad)")
@click.option("--start-date", required=True, help="Data początkowa (DD.MM.YYYY)")
@click.option("--end-date", required=True, help="Data końcowa (DD.MM.YYYY)")
@click.option("--forecast-date", required=False, help="Data początkowa prognozy (DD.MM.YYYY)")
@click.option(
    "--use-t-files", is_flag=True, help="Czy użyć plików z dopiskiem _t (zawieraja one inne dane niż pliki podstawowe)"
)
def full_analysis(
    parameter: str,
    parameter1: str,
    parameter2: str,
    target: str,
    stations: list,
    data_type: str,
    start_date: str,
    end_date: str,
    forecast_date: str,
    use_t_files: bool = False,
) -> None:
    forecast_date = forecast_date or end_date
    parameter2 = parameter2 or parameter
    target = target or parameter

    start_year = int(start_date.split(".")[-1])
    end_year = int(end_date.split(".")[-1])
    if start_year != end_year:
        year_range = tuple(range(min(start_year, end_year), max(start_year, end_year) + 1))
    else:
        year_range = start_year

    full_forecast = IMGWSimpleForecaster()
    full_forecast.linear_regresion_forecast(stations, data_type, target, forecast_date, use_t_files)

    station_check = ", ".join(stations)
    full = IMGWStatistics()
    full.calculate_basic_stats(parameter, stations, data_type, start_date, end_date, use_t_files)
    full.calculate_correlation(parameter1, parameter2)

    full_visualize = IMGWDataVisualizer()

    full_visualize.plot_time_series(parameter, stations, data_type, start_date, end_date, use_t_files)
