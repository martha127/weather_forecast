from __future__ import annotations
import re
import sys
from pathlib import Path
CONST = 2
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
from scipy.stats import pearsonr

from meteopy.consts.dirs import DATA_DIR
from meteopy.eda.imgw_eda_visualizer import IMGWDataVisualizer
from meteopy.utils.logging import get_logger


class IMGWStatistics:
    def __init__(self) -> None:
        self.input_directory = DATA_DIR / "sorted"
        self.output_dir = DATA_DIR / "stats"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.outdir = ""
        self.start_date = ""
        self.end_date = ""
        self.data = {}
        self.logger = get_logger("DataStatistics")

    def calculate_basic_stats(
        self, parameter: str, stations: list, data_type: str, start_date: str, end_date: str, use_t_files: bool = False
    ) -> None:
        if not stations:
            directory = self.input_directory / data_type
            stations = [kat.name for kat in directory.iterdir()]
        print(f"Dostępne stacje: {stations}")
        statistic = IMGWDataVisualizer()
        statistic.get_ready(stations, data_type, start_date, end_date, use_t_files)
        if not statistic.data:
            self.logger.warning(f"Brak danych po wywołaniu get_ready dla stacji {stations}")
        self.data = statistic.data
        stats_dict = {}

        for station in stations:
            if station not in statistic.data:
                self.logger.warning("Brak danych dla stacji {%s}", station)
                continue

            df_3 = self.data[station]
            df_3.columns = df_3.columns.str.strip()
            if parameter not in df_3.columns:
                print(f"Błąd: Kolumna {parameter} nie istnieje w danych dla {station}")
                print(f"Dostępne kolumny: {df_3.columns.tolist()}")
                continue

            if parameter not in df_3.columns:
                self.logger.warning("Brak kolumny %s w danych dla stacji %s", parameter, station)
                print(f"Dostępne kolumny: {df_3.columns.tolist()}")
                continue

            stats_df = df_3[parameter].describe().to_frame().T
            stats_df = stats_df.round(2)
            stats_df.insert(0, "Stacja", station)

            stats_df = stats_df.rename(
                columns={
                    "count": "Liczba obserwacji",
                    "mean": "Średnia",
                    "std": "Odchylenie standardowe",
                    "min": "Min",
                    "25%": "Pierwszy kwartyl (25%)",
                    "50%": "Mediana",
                    "75%": "Trzeci kwartyl (75%)",
                    "max": "Max",
                }
            )
            stats_dict[station] = stats_df

        self.data = pd.concat(list(stats_dict.values()), ignore_index=True)
        self.outdir = self.output_dir / data_type
        outdir_end = self.outdir / "basic_stats"
        outdir_end.mkdir(parents=True, exist_ok=True)
        self.start_date = start_date
        self.end_date = end_date
        safe_parameter = re.sub(r'[<>:"/\\|?*]', "", parameter)
        file_path = outdir_end / f"{start_date}-{end_date}_{safe_parameter}.csv"
        self.data.to_csv(file_path, index=False, sep=",")
        self.data = statistic.data
        return self.data, self.outdir, self.start_date, self.end_date

    def calculate_correlation(self, parameter1: str, parameter2: str) -> None:
        correlation_results = []

        for station, df_4 in self.data.items():
            df_4 = df_4.copy()
            if parameter1 not in df_4.columns or parameter2 not in df_4.columns:
                self.logger.warning("Stacja %s: brak kolumn ({%s}, {%s})", station, parameter1, parameter2)
                continue
            if df_4[parameter1].nunique() < CONST or df_4[parameter2].nunique() < CONST:
                self.logger.warning(
                    "Stacja %s - jedna z kolumn (%s,%s) ma tylko jedną wartość.", station, parameter1, parameter2
                )
            else:
                if parameter1 == "Rodzaj opadu [S/W/ ]" or parameter2 == "Rodzaj opadu [S/W/ ]":
                    df_4["Rodzaj opadu [S/W/ ]"] = df_4["Rodzaj opadu [S/W/ ]"].map({"S": 0, "W": 1}).astype(float)

                if parameter1 == "Stan gruntu [Z/R]" or parameter2 == "Stan gruntu [Z/R]":
                    df_4["Stan gruntu [Z/R]"] = df_4["Stan gruntu [Z/R]"].map({"Z": 0, "R": 1}).astype(float)

                df_4 = df_4[[parameter1, parameter2]].dropna()
                if not df_4.empty:
                    correlation, _ = pearsonr(df_4[parameter1], df_4[parameter2])
                    correlation_results.append({
                        "Stacja": station,
                        "Korelacja": correlation,
                        "Przedział czasowy": self.start_date + "-" + self.end_date,
                    })

        correlation_df = pd.DataFrame(correlation_results)

        outdir_end = self.outdir / "correlations"
        outdir_end.mkdir(parents=True, exist_ok=True)
        name_1 = re.sub(r'[<>:"/\\|?*[\]]', "_", parameter1)
        name_2 = re.sub(r'[<>:"/\\|?*[\]]', "_", parameter2)
        file_path = outdir_end / f"{name_1}-{name_2}.csv"
        if file_path.exists():
            correlation_df.to_csv(file_path, mode="a", index=False, header=False)
        else:
            correlation_df.to_csv(file_path, index=False)


if __name__ == "__main__":
    statistics = IMGWStatistics()
    statistics.calculate_basic_stats(
        "Suma dobowa opadu [mm]", ["BIELSKO-BIAŁA"], "synop", "02.02.2017", "12.04.2017", use_t_files=False
    )
    statistics.calculate_correlation("Suma dobowa opadu [mm]", "Wysokość pokrywy śnieżnej [cm]")
