from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from meteopy.eda.imgw_eda_visualizer import IMGWDataVisualizer


class TestIMGWDataVisualizer(unittest.TestCase):
    @patch("os.path.exists")
    def test_find_file_found(self, mock_exists):
        mock_exists.return_value = True
        visualizer = IMGWDataVisualizer()
        file_path = visualizer.find_file(2022, 3, "some_directory", use_t_files=False)
        expected_path = "some_directory\\2022_03.csv"
        self.assertEqual(file_path, expected_path)

    @patch("os.path.exists")
    def test_find_file_not_found(self, mock_exists):
        mock_exists.return_value = False

        visualizer = IMGWDataVisualizer()
        file_path = visualizer.find_file(2022, 3, "some_directory", use_t_files=False)

        self.assertIsNone(file_path)

    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_get_ready(self, mock_read_csv, mock_exists):
        mock_exists.return_value = True
        mock_df = pd.DataFrame({
            "Dzień": [1, 2],
            "Temperatura": [5.5, 6.0],
        })
        mock_read_csv.return_value = mock_df

        visualizer = IMGWDataVisualizer()
        stations = ["station1"]
        visualizer.get_ready(stations, "opad", "01.01.2020", "31.12.2020", use_t_files=False)

        self.assertIn("station1", visualizer.data)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.close")
    @patch("seaborn.lineplot")
    def test_plot_time_series(self, mock_lineplot, mock_close, mock_figure, mock_savefig):
        mock_figure.return_value = MagicMock()
        mock_savefig.return_value = None
        mock_lineplot.return_value = MagicMock()

        visualizer = IMGWDataVisualizer()

        visualizer.data = {
            "station1": pd.DataFrame({
                "Data": pd.date_range("2020-01-01", periods=5, freq="D"),
                "Suma dobowa opadów [mm]": [0.0, 0.2, 0.5, 1.0, 0.0],
            })
        }

        visualizer.plot_time_series(
            "Suma dobowa opadów [mm]", ["station1"], "opad", "01.01.2020", "05.01.2020", use_t_files=False
        )
        mock_savefig.assert_called_once()


if __name__ == "__main__":
    unittest.main()
