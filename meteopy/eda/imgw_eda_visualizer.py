from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import calendar

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

MAX_STATIONS = 10
MAX_MONTH = 12
from meteopy.consts.dirs import DATA_DIR
from meteopy.utils.logging import get_logger


class IMGWDataVisualizer:
    def __init__(self) -> None:
        self.input_directory = DATA_DIR / "sorted"
        self.output_dir = DATA_DIR / "plot"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}
        self.logger = get_logger("DataVisualizer")

    def find_file(self, year: int, month: int, directory: str, use_t_files: bool = False) -> None:
        file_suffix = "_t" if use_t_files else ""
        file_name = f"{year}_{str(month).zfill(2)}{file_suffix}.csv"
        file_path = Path(directory) / file_name
        if file_path.exists():
            return file_path
        self.logger.warning(f"Plik {file_name} nie został znaleziony w katalogu {directory}.")
        return None

    def get_ready(
        self, stations: list, data_type: str, start_date: str, end_date: str, use_t_files: bool = False
    ) -> None:
        try:
            start_day, start_month, start_year = map(int, start_date.split("."))
            end_day, end_month, end_year = map(int, end_date.split("."))
        except ValueError:
            raise ValueError("Data musi mieć format dzień.miesiąc.rok")

        type_path = Path(self.input_directory) / data_type
        for i in range(0, len(stations), MAX_STATIONS):
            batch = stations[i : i + MAX_STATIONS]
            for station in batch:
                station_data = []
                station_path = Path(type_path) / station

                if station_path.exists():
                    years, months, day_ranges = self._get_months_in_range( start_month, start_year, end_month, end_year, start_day, end_day)
                    self.logger.info("Pliki do załadowania dla stacji %s: %s", station, (years, months, day_ranges))
                    for year, month, day_range in zip(years, months, day_ranges, strict=False):
                        file_path = self.find_file(year, month, station_path, use_t_files)
                        if file_path:
                            try:
                                df_1 = pd.read_csv(file_path, header=0, encoding="utf-8", index_col=False)
                                df_1["Dzień"] = pd.to_numeric(df_1["Dzień"], errors="coerce")

                                df_1 = df_1.dropna(subset=["Dzień"])
                                df_1["Dzień"] = df_1["Dzień"].astype(int)
                                df_1["Data"] = pd.to_datetime({"year": year, "month": month, "day": df_1["Dzień"]})
                                df_1 = df_1[["Data"] + [col for col in df_1.columns if col != "Data"]]

                                if day_range == "all":
                                    df_filtered = df_1
                                else:
                                    df_filtered = df_1[
                                        (df_1["Dzień"] >= day_range[0]) & (df_1["Dzień"] <= day_range[1])
                                    ]
                                if not df_filtered.empty:
                                    station_data.append(df_filtered)
                            except Exception as e:
                                self.logger.exception("Nie udało się wczytać pliku %s: {%s}", file_path, e)
                                raise

                if station_data:
                    self.data[station] = pd.concat(station_data, ignore_index=True)

    def _get_months_in_range(
        self, start_month: int, start_year: int, end_month: int, end_year: int, start_day=None, end_day=None
    ) -> None:
        years = []
        months = []
        day_ranges = []
        current_year = start_year
        current_month = start_month

        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            years.append(current_year)
            months.append(current_month)

            if current_year == start_year and current_month == start_month:
                day_ranges.append((start_day, self._days_in_month(current_year, current_month)))
            elif current_year == end_year and current_month == end_month:
                day_ranges.append((1, end_day))
            else:
                day_ranges.append("all")

            current_month += 1
            if current_month > MAX_MONTH:
                current_month = 1
                current_year += 1

        return years, months, day_ranges

    def _days_in_month(self, year: int, month: int) -> None:
        return calendar.monthrange(year, month)[1]

    def plot_time_series(
        self, parameter: str, stations: list, data_type: str, start_date: str, end_date: str, use_t_files: bool = False
    ) -> None:
        if not stations:
            directory = self.input_directory / data_type
            stations = [kat.name for kat in directory.iterdir()]

        self.get_ready(stations, data_type, start_date, end_date, use_t_files)
        for station in stations:
            if station not in self.data:
                self.logger.info("Brak danych dla stacji {%s}", station)
                continue

            df_1 = self.data[station]
            df_1.columns = df_1.columns.str.strip()

            if (
                parameter not in df_1.columns
            ):  # zostawiamy printy, bo wyświetlaja w terminalu użytkownikowi dostepne kolumny
                print(f"Brak kolumny '{parameter}' w danych dla stacji {station}")
                print(f"Dostępne kolumny: {df_1.columns.tolist()}")
                continue

            plt.figure(figsize=(12, 6))

            plt.xlim(pd.to_datetime(start_date, format="%d.%m.%Y"), pd.to_datetime(end_date, format="%d.%m.%Y"))
            plt.grid(True, which="major", axis="x", linestyle="--", linewidth=0.5)
            sns.lineplot(data=df_1, x="Data", y=parameter, label=station, marker="o")
            plt.xlabel("Data")
            plt.ylabel(parameter)
            plt.title(f"{parameter} - Stacja {station}")
            plt.legend()
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
            plt.grid(True, which="minor", axis="x", linestyle=":", linewidth=0.3)

            plt.xticks(rotation=45, ha="right", fontsize=8)
            output = self.output_dir / data_type / station
            output.mkdir(parents=True, exist_ok=True)
            name_of_file = f"{start_date}-{end_date}_{parameter}.png"
            plt.savefig(output / f"{name_of_file}", dpi=300, bbox_inches="tight")
            plt.close()


if __name__ == "__main__":
    visualizer = IMGWDataVisualizer()
    visualizer.plot_time_series(
        "Suma dobowa opadów [mm]", ["ADAMOWICE"], "opad", "02.01.1996", "12.04.1996", use_t_files=False
    )
