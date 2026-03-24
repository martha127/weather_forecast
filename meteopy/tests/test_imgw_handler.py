from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from meteopy.preprocessing.imgw_handler import IMGWDataHandler


class TestIMGWDataHandler(unittest.TestCase):
    @patch("meteopy.utils.logging.get_logger")
    def test_initialization(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        handler = IMGWDataHandler("synop")

    def test_apply_headers(self):
        df = pd.DataFrame({"column1": [1, 2], "column2": [3, 4]})
        handler = IMGWDataHandler("synop")
        with self.assertRaises(ValueError):
            handler.apply_headers(df, "synop", use_t_files=True)

    @patch("pandas.read_csv")
    @patch("meteopy.utils.logging.get_logger")
    def test_file_reading_error_handling(self, mock_get_logger, mock_read_csv):
        mock_read_csv.side_effect = Exception("Błąd odczytu")
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        handler = IMGWDataHandler("synop")
        try:
            handler.divide_downloaded("synop")
        except Exception as e:
            self.assertEqual(str(e), "Błąd odczytu")


if __name__ == "__main__":
    unittest.main()
