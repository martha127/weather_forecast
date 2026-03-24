from __future__ import annotations
from urllib.parse import urlparse
from urllib.parse import urljoin
import os
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import zipfile

import requests
from bs4 import BeautifulSoup

from meteopy.consts.dirs import DATA_DIR
from meteopy.consts.linki import ROOT_URL, START_SEARCH
from meteopy.utils.logging import get_logger


class IMGWDataFetcher:
    def __init__(self) -> None:
        self.base_url = ROOT_URL
        self.start_url = START_SEARCH
        self.download_dir = DATA_DIR / "downloaded"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("DataFetcher")

    def parse_years(self, data: tuple) -> list:
        years = []
        for item in data:
            clean_item = str(item).strip()  # traktujemy elementy jako ciągi znaków
            if "-" in clean_item:
                try:
                    start_year, end_year = map(int, item.split("-"))
                    if start_year > end_year:
                        raise_value_error(f"Startowy rok przedziału {start_year} jest większy niż końcowy {end_year}.")
                    years.extend(range(start_year, end_year))
                except ValueError:
                    raise_value_error(f"Nieprawidłowy format przedziału: {item}")
            else:
                try:
                    if item:
                        year = int(item)
                        years.append(year)
                except ValueError:
                    raise_value_error(f"Nieprawidłowy format roku: {item}")
        return years

    def fetch(self, data_type: str, year_range: tuple) -> list:
        url = os.path.join(self.start_url, data_type)
        self.logger.info(f"URL do szukania: {url}")
        response = requests.get(url)
        response.raise_for_status()
        item = str(year_range).strip()
        if "-" in item:
            years = self.parse_years(year_range)
            less_than_threshold = [year for year in years if year < 2001]
            greater_threshold = [year for year in years if year >= 2001]
        else:
            years = year_range
            if years[0] >= 2001:
                greater_threshold = years
                less_than_threshold = 0
            else:
                less_than_threshold = years

        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if not a["href"].startswith("..")]
        matched_links = []  # Przechowuje pasujące linki

        if data_type == "synop/":  # Dla typu synop, lata poniżej 2001 są nierozdzielone
            if less_than_threshold:
                self.logger.info("Dostępne linki:", links)
                for link in links:
                    if re.match(r"^19", link):
                        try:
                            start, end = map(int, link.strip("/").split("_"))
                            for year in less_than_threshold:
                                if start <= year <= end:
                                    if link not in matched_links:
                                        matched_links.append(link)
                        except ValueError:
                            print(f"Nieprawidłowy format linku: {link}")
                            continue
            elif greater_threshold:
                for year in greater_threshold:
                    for link in links:
                        if re.match(r"^20", link):
                            if year == int(link.strip("/")):
                                if link not in matched_links:
                                    matched_links.append(link)
        else:
            for link in links:
                if link.endswith("/"):
                    try:
                        if less_than_threshold and "_" in link:
                            start, end = map(int, link.strip("/").split("_"))
                            for year in years:
                                if start <= year <= end:
                                    # Dopasowanie linku przy użyciu wyrażenia regularnego
                                    pattern = rf"{start}_{end}/{year}_{data_type[0]}.zip"
                                    final_link = os.path.join(pattern)
                                    matched_links.append(final_link)

                        else:
                            for year in years:
                                if int(link.strip("/")) == year:
                                    matched_links.append(link)
                    except ValueError:
                        continue

        full_links = [os.path.join(url, link) for link in matched_links]
        return full_links

    def download_file(self, full_links: list, data_type: str):
        type_dir = self.download_dir / data_type
        type_dir.mkdir(parents=True, exist_ok=True)

        for link in full_links:
            file_name = os.path.basename(link.strip("/"))
            file_path = type_dir / file_name
            if file_path.exists():
                continue

            if link.endswith("/"):
                response = requests.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                zip_links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".zip")]

                for zip_link in zip_links:
                    zip_url = urljoin(link, zip_link)  # POPRAWIONE!
                    self._download_and_extract_zip(zip_url, unzip=True, type_dir=type_dir)
            elif link.endswith(".zip"):
                self._download_and_extract_zip(link, unzip=True, type_dir=type_dir)
    def _download_and_extract_zip(self, zip_url: str, unzip: bool, type_dir: Path) -> None:
        response = requests.get(zip_url, timeout=10)
        response.raise_for_status()

        zip_file_name = Path(urlparse(zip_url).path).name
        zip_file_path = type_dir / zip_file_name

        zip_file_path.write_bytes(response.content)
        if unzip:
            self._extract_zip(zip_file_path, type_dir)


    def _extract_zip(self, zip_file_path: Path, type_dir: Path) -> None:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(type_dir)
        zip_file_path.unlink()  # usuwanie pliku zip po rozpakowaniu


def raise_value_error(message: str):
    raise ValueError(message)


if __name__ == "__main__":  # testowanie dla przykładowych danych
    fetcher = IMGWDataFetcher()
    result = fetcher.fetch("klimat/", ("2017-2018", ""))
    fetcher.download_file(result, "klimat")
