"""
    test_current_conditions_heatmap.py

    This is a unit test for the current_conditions_heatmap.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.location_map import render_location_map

# pylint: disable=C0413

class TestCurrentConditionsHeatMap(unittest.TestCase):
    """Unit test class"""

    def test_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        api_result = render_location_map("test_user", "test_domain")
        self.assertEqual("usa", api_result.get("layout").get("geo").get("scope"))

if __name__ == "__main__":
    unittest.main()
