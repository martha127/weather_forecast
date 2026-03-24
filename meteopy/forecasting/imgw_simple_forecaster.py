from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timedelta

import pandas as pd
from sklearn.linear_model import LinearRegression

from meteopy.consts.dirs import DATA_DIR
from meteopy.data_fetchers.imgw_fetecher import IMGWDataFetcher
from meteopy.eda.imgw_eda_visualizer import IMGWDataVisualizer
from meteopy.preprocessing.imgw_handler import IMGWDataHandler
from meteopy.utils.logging import get_logger


class IMGWSimpleForecaster:
    def __init__(self) -> None:
        self.input_directory = DATA_DIR / "sorted"
        self.output_dir = DATA_DIR / "forecast"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}
        self.logger = get_logger("DataForecaster")

    def linear_regresion_forecast(
        self, stations: list, data_type: str, target: str, date_of_start: str, use_t_files: bool = False
    ) -> None:
        if not stations:
            directory = self.input_directory / data_type
            stations = [kat.name for kat in directory.iterdir()]

        date_format = "%d.%m.%Y"
        date_obj = datetime.strptime(date_of_start, date_format)
        new_date = date_obj.replace(year=date_obj.year - 3)
        new_date_str = new_date.strftime(date_format)

        start_year = new_date.year
        end_year = date_obj.year
        years = list(range(start_year, end_year + 1))
        print(years)

        for station in stations:
            self.check_existing_years(station, data_type, years)

        forecast = IMGWDataVisualizer()
        forecast.get_ready(stations, data_type, new_date_str, date_of_start, use_t_files)

        self.data = forecast.data
        predictions = {}

        for station in stations:
            if station not in self.data:
                self.logger.warning("Brak danych dla stacji %s", station)
                continue

            df_2 = self.data[station]
            df_2.columns = df_2.columns.str.strip()

            if target not in df_2.columns:
                self.logger.warning("Brak kolumny '%s' w danych dla stacji %s", target, station)
                print(f"Dostępne kolumny: {df_2.columns.tolist()}")
                continue
            df_2["Data"] = pd.to_datetime(df_2["Data"])
            df_2["Days"] = (df_2["Data"] - df_2["Data"].min()).dt.days

            x_1 = df_2[["Days"]]
            y_1 = df_2[target]

            model = LinearRegression()
            model.fit(x_1, y_1)

            future_dates = [date_obj + timedelta(days=i) for i in range(1, 8)]
            future_days = [(d - df_2["Data"].min()).days for d in future_dates]
            predictions[station] = pd.DataFrame({
                "Data": future_dates,
                target: model.predict(pd.DataFrame(future_days)),
            })
            file_path = self.output_dir / data_type
            file_path.mkdir(exist_ok=True, parents=True)
            file_name = file_path / f"{date_of_start}_{station}_{target}.csv"

            predictions[station].to_csv(file_name, index=False)

        return predictions

    def check_existing_years(self, station: str, data_type: str, years: list[int]) -> tuple[int, ...]:
        station_path = Path(self.input_directory) / data_type / station
        years = {int(year) for year in years if year}
        if not station_path.exists():
            missing_years = sorted(years)
        else:
            existing_years = {int(file[:4]) for file in os.listdir(station_path) if file[:4].isdigit()}
            missing_years = sorted(years - existing_years)

        if not missing_years:
            self.logger.info("Wszystkie dane dla {%s} ({%s}) są już dostępne.", station, data_type)
            return ()

        self.logger.info("Brakujące lata dla {%s}: {%s}", station, missing_years)

        fetcher = IMGWDataFetcher()

        year_range = tuple(missing_years) if len(missing_years) > 1 else (missing_years[0], "")

        result = fetcher.fetch(f"{data_type}/", year_range)
        fetcher.download_file(result, data_type)
        handler = IMGWDataHandler(data_type)
        handler.divide_downloaded(data_type)

        return tuple(missing_years)


if __name__ == "__main__":
    forecaster = IMGWSimpleForecaster()
    forecaster.linear_regresion_forecast(
        ["BABIMOST"], "klimat", "Maksymalna temperatura dobowa [°C]", "02.01.2017", use_t_files=False
    )
