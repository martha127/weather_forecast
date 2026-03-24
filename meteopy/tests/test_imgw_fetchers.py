from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from meteopy.data_fetchers.imgw_fetecher import IMGWDataFetcher


class TestIMGWDataFetcher(unittest.TestCase):
    def test_parse_years_single_year(self):
        fetcher = IMGWDataFetcher()
        years = fetcher.parse_years(("2017",))
        self.assertEqual(years, [2017])

    def test_parse_years_range(self):
        fetcher = IMGWDataFetcher()
        years = fetcher.parse_years(("2017-2019",))
        self.assertEqual(years, [2017, 2018])

    def test_parse_years_invalid_format(self) -> None:
        fetcher = IMGWDataFetcher()
        with self.assertRaises(ValueError):
            fetcher.parse_years(("2017-2015",))

    def test_download_file_existing(self):
        fetcher = IMGWDataFetcher()
        with patch("pathlib.Path.exists", return_value=True):
            result = fetcher.download_file(["https://example.com/2017.zip"], "klimat")
            self.assertIsNone(result)

    @patch("meteopy.data_fetchers.imgw_fetecher.get_logger")
    def test_logging_for_fetch(self, mock_logger):
        fetcher = IMGWDataFetcher()
        mock_logger.return_value = MagicMock()
        mock_logger_instance = mock_logger.return_value

        year_range = (2017,)
        data_type = "klimat/"

        fetcher.fetch(data_type, year_range)
        mock_logger_instance.error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
