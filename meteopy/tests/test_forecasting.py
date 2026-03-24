from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from meteopy.forecasting.imgw_simple_forecaster import IMGWSimpleForecaster


class TestIMGWSimpleForecaster(unittest.TestCase):
    @patch("meteopy.eda.imgw_eda_visualizer.IMGWDataVisualizer")
    @patch("meteopy.data_fetchers.imgw_fetecher.IMGWDataFetcher")
    @patch("meteopy.preprocessing.imgw_handler.IMGWDataHandler")
    def test_linear_regresion_forecast(self, MockDataHandler, MockDataFetcher, MockDataVisualizer) -> None:
        mock_visualizer = MagicMock()
        mock_fetcher = MagicMock()
        mock_handler = MagicMock()
        MockDataVisualizer.return_value = mock_visualizer
        MockDataFetcher.return_value = mock_fetcher
        MockDataHandler.return_value = mock_handler

        forecaster = IMGWSimpleForecaster()

        mock_visualizer.data = {
            "BABIMOST": pd.DataFrame({
                "Data": pd.date_range(start="01.01.2015", periods=10, freq="D"),
                "Maksymalna temperatura dobowa [°C]": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            })
        }

        stations = ["BABIMOST"]
        data_type = "klimat"
        target = "Maksymalna temperatura dobowa [°C]"
        start_date = "02.01.2017"
        use_t_files = False
        predictions = forecaster.linear_regresion_forecast(stations, data_type, target, start_date, use_t_files)

        self.assertIn("BABIMOST", predictions)
        self.assertEqual(predictions["BABIMOST"].shape[0], 7)


if __name__ == "__main__":
    unittest.main()
