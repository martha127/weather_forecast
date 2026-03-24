from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from meteopy.consts.dirs import DATA_DIR
from meteopy.utils.logging import get_logger


class IMGWDataHandler:
    def __init__(self, data_type: str) -> None:
        self.input_directory = DATA_DIR / "downloaded" / data_type
        self.output_dir = DATA_DIR / "sorted"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("DataHandler")

        self.files = [f for f in os.listdir(self.input_directory) if f.endswith(".csv")]
        self.data = {}

        for file in self.files:
            is_t_file = "_t" in file
            file_path = Path(self.input_directory) / file

            try:
                df_5 = pd.read_csv(file_path, encoding="ANSI")  # Kodowanie obsługujące polskie znaki zawarte w plikach
                self.data[file, is_t_file] = df_5
            except Exception as e:
                self.logger.warning("Nie udało się wczytać pliku %s: %s", file, e)

    def divide_downloaded(self, data_type: str) -> None:
        type_folder = Path(self.output_dir) / data_type
        Path.mkdir(type_folder, exist_ok=True)

        for (filename, is_t_file), df in self.data.items():
            unique_stations = df.iloc[:, 0].unique()
            for station in unique_stations:
                station_data = df[df.iloc[:, 0] == station]
                station_name = station_data.iloc[0, 1]

                station_folder = Path(type_folder) / station_name
                Path.mkdir(station_folder, exist_ok=True)

                unique_year_month = station_data.iloc[:, [2, 3]].drop_duplicates()
                for _, row in unique_year_month.iterrows():
                    year, month = str(row.iloc[0]).zfill(4), str(row.iloc[1]).zfill(2)
                    file_suffix = "_t.csv" if is_t_file else ".csv"
                    file_name = f"{year}_{month}{file_suffix}"
                    file_path = Path(station_folder) / file_name

                    month_data = station_data[
                        (station_data.iloc[:, 2] == int(year)) & (station_data.iloc[:, 3] == int(month))
                    ]
                    month_data = month_data.iloc[:, 4:]
                    month_data = self.apply_headers(month_data, data_type, use_t_files=is_t_file)

                    month_data = month_data.dropna(axis=1, how="all")
                    cols_to_keep = [col for col in month_data.columns if month_data[col][1:].nunique() > 1]
                    month_data = month_data[cols_to_keep]

                    month_data.to_csv(file_path, index=False, header=True, encoding="utf-8")

    def apply_headers(
        self, df: pd.DataFrame, parameter: str, use_t_files: bool
    ) -> None:  # Dodaje nagłówki do DataFrame w zależności od parametru i typu danych.
        headers_map = {
            "synop": {
                True: [
                    "Dzień",
                    "Średnie dobowe zachmurzenie ogólne [oktanty]",
                    "Status pomiaru NOS",
                    "Średnia dobowa prędkość wiatru [m/s]",
                    "Status pomiaru FWS",
                    "Średnia dobowa temperatura [°C]",
                    "Status pomiaru TEMP",
                    "Średnia dobowe ciśnienie pary wodnej [hPa]",
                    "Status pomiaru CPW",
                    "Średnia dobowa wilgotność względna [%]",
                    "Status pomiaru WLGS",
                    "Średnia dobowe ciśnienie na poziomie stacji [hPa]",
                    "Status pomiaru PPPS",
                    "Średnie dobowe ciśnienie na poziomie morza [hPa]",
                    "Status pomiaru PPPM",
                    "Suma opadu dzień [mm]",
                    "Status pomiaru WODZ",
                    "Suma opadu noc [mm]",
                    "Status pomiaru WONO",
                ],
                False: [
                    "Dzień",
                    "Maksymalna temperatura dobowa [°C]",
                    "Status pomiaru TMAX",
                    "Minimalna temperatura dobowa [°C]",
                    "Status pomiaru TMIN",
                    "Średnia temperatura dobowa [°C]",
                    "Status pomiaru STD",
                    "Temperatura minimalna przy gruncie [°C]",
                    "Status pomiaru TMNG",
                    "Suma dobowa opadu [mm]",
                    "Status pomiaru SMDB",
                    "Rodzaj opadu [S/W/ ]",
                    "Wysokość pokrywy śnieżnej [cm]",
                    "Status pomiaru PKSN",
                    "Równoważnik wodny śniegu [mm/cm]",
                    "Status pomiaru RWSN",
                    "Usłonecznienie [godziny]",
                    "Status pomiaru USL",
                    "Czas trwania opadu deszczu [godziny]",
                    "Status pomiaru DESZ",
                    "Czas trwania opadu śniegu [godziny]",
                    "Status pomiaru SNEG",
                    "Czas trwania opadu deszczu ze śniegiem [godziny]",
                    "Status pomiaru DISN",
                    "Czas trwania gradu [godziny]",
                    "Status pomiaru GRAD",
                    "Czas trwania mgły [godziny]",
                    "Status pomiaru MGLA",
                    "Czas trwania zamglenia [godziny]",
                    "Status pomiaru ZMGL",
                    "Czas trwania sadzi [godziny]",
                    "Status pomiaru SADZ",
                    "Czas trwania gołoledzi [godziny]",
                    "Status pomiaru GOLO",
                    "Czas trwania zamieci śnieżnej niskiej [godziny]",
                    "Status pomiaru ZMNI",
                    "Czas trwania zamieci śnieżnej wysokiej [godziny]",
                    "Status pomiaru ZMWS",
                    "Czas trwania zmętnienia [godziny]",
                    "Status pomiaru ZMET",
                    "Czas trwania wiatru >=10m/s [godziny]",
                    "Status pomiaru FF10",
                    "Czas trwania wiatru >15m/s [godziny]",
                    "Status pomiaru FF15",
                    "Czas trwania burzy [godziny]",
                    "Status pomiaru BRZA",
                    "Czas trwania rosy [godziny]",
                    "Status pomiaru ROSA",
                    "Czas trwania szronu [godziny]",
                    "Status pomiaru SZRO",
                    "Wystąpienie pokrywy śnieżnej [0/1]",
                    "Status pomiaru DZPS",
                    "Wystąpienie błyskawicy [0/1]",
                    "Status pomiaru DZBL",
                    "Stan gruntu [Z/R]",
                    "Izoterma dolna [cm]",
                    "Status pomiaru IZD",
                    "Izoterma górna [cm]",
                    "Status pomiaru IZG",
                    "Aktynometria [J/cm2]",
                    "Status pomiaru AKTN",
                ],
            },
            "klimat": {
                True: [
                    "Dzień",
                    "Średnia dobowa temperatura [°C]",
                    "Status pomiaru TEMP",
                    "Średnia dobowa wilgotność względna [%]",
                    "Status pomiaru WLGS",
                    "Średnia dobowa prędkość wiatru [m/s]",
                    "Status pomiaru FWS",
                    "Średnie dobowe zachmurzenie ogólne [oktanty]",
                    "Status pomiaru NOS",
                ],
                False: [
                    "Dzień",
                    "Maksymalna temperatura dobowa [°C]",
                    "Status pomiaru TMAX",
                    "Minimalna temperatura dobowa [°C]",
                    "Status pomiaru TMIN",
                    "Średnia temperatura dobowa [°C]",
                    "Status pomiaru STD",
                    "Temperatura minimalna przy gruncie [°C]",
                    "Status pomiaru TMNG",
                    "Suma dobowa opadów [mm]",
                    "Status pomiaru SMDB",
                    "Rodzaj opadu [S/W/ ]",
                    "Wysokość pokrywy śnieżnej [cm]",
                    "Status pomiaru PKSN",
                ],
            },
            "opad": {
                True: None,  # Nie istnieje wersja 'opad' z '_t'
                False: [
                    "Dzień",
                    "Suma dobowa opadów [mm]",
                    "Status pomiaru SMDB",
                    "Rodzaj opadu [S/W/ ]",
                    "Wysokość pokrywy śnieżnej [cm]",
                    "Status pomiaru PKSN",
                    "Wysokość świeżospałego śniegu [cm]",
                    "Status pomiaru HSS",
                    "Gatunek śniegu [kod]",
                    "Status pomiaru GATS",
                    "Rodzaj pokrywy śnieżnej [kod]",
                    "Status pomiaru RPSN",
                ],
            },
        }
        headers = headers_map.get(parameter, {}).get(use_t_files)
        if len(df.columns) != len(headers):
            raise ValueError(
                f"Liczba kolumn w DataFrame ({len(df.columns)}) nie zgadza się z liczbą nagłówków ({len(headers)})."
            )
        if headers:
            df.columns = headers
        else:
            raise ValueError(f"Brak nagłówków dla parametru '{parameter}' i use_t_files={use_t_files}")

        return df


if __name__ == "__main__":
    handler = IMGWDataHandler("synop")
    handler.divide_downloaded("synop")
