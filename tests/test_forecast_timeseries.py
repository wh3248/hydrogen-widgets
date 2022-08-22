"""
    test_forecast_timeseries.py

    This is a unit test for the forecast_timeseries.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.forecast_timeseries import render_forecast_timeseries

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
        api_result = render_forecast_timeseries("test_user", "test_domain", test_query_parameters)
        self.assertEqual(2, len(api_result.get("subplots")));


if __name__ == "__main__":
    unittest.main()
