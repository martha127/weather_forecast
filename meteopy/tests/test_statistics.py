from __future__ import annotations

import unittest

import pandas as pd

from meteopy.imgw_statistics.imgw_statistics import IMGWStatistics


class TestIMGWStatistics(unittest.TestCase):
    def test_calculate_basic_stats(self):
        statistics = IMGWStatistics()

        mock_data = {
            "BIELSKO-BIAŁA": pd.DataFrame({
                "Suma dobowa opadu [mm]": [1.2, 3.4, 2.1],
                "Wysokość pokrywy śnieżnej [cm]": [5, 4, 3],
            })
        }
        statistics.data = mock_data
        result = statistics.calculate_basic_stats(
            "Suma dobowa opadu [mm]", "BIELSKO-BIAŁA", "synop", "02.02.2000", "12.04.2000", use_t_files=False
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("Średnia", result.columns)
        self.assertAlmostEqual(result["Średnia"].iloc[0], 2.23, places=2)


if __name__ == "__main__":
    unittest.main()
