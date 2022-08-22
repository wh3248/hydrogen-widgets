"""
    test_forecast_waterdepth_heatmap.py

    This is a unit test for the forecast_waterdepth_heatmap.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.forecast_waterdepth_heatmap import render_forecast_waterdepth_heatmap

# pylint: disable=C0413

class TestForecastWaterDepthHeatmap(unittest.TestCase):
    """Unit test class"""

    def test_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        test_query_parameters = {
            "scenario_id": "test_average",
        }
        api_result = render_forecast_waterdepth_heatmap("test_user", "test_domain", test_query_parameters)
        self.assertEqual(5, len(api_result.get("layout").get("updatemenus")[0].get("buttons")))

        z_values = api_result.get("traces")[0].get("z")
        self.assertEqual(20, len(z_values))
        self.assertEqual(14399.588696, round(sum([sum(x) for x in z_values]), 6))

if __name__ == "__main__":
    unittest.main()
