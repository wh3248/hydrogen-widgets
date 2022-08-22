"""
    test_scenaries_timeseries.py

    This is a unit test for the scenaries_timeseries.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.scenarios_timeseries import render_scenario_timeseries

# pylint: disable=C0413

class TestScenariesTimeseries(unittest.TestCase):
    """Unit test class"""

    def test_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        test_query_parameters = {
            "scenario_id": "test_average",
        }
        api_result = render_scenario_timeseries("test_user", "test_domain", test_query_parameters)
        self.assertEqual(5, len(api_result.get("layout").get("updatemenus")[0].get("buttons")))

if __name__ == "__main__":
    unittest.main()
