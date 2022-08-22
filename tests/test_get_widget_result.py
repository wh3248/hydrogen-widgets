"""
    test_get_widget_result.py

    This is a unit test for the get_widget_result.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.utilities.get_widget_result import get_widget_result

# pylint: disable=C0413

class TestGetWidgetResult(unittest.TestCase):
    """Unit test class"""

    def test_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        api_result = get_widget_result("current_conditions_heatmap", "test_user", "test_domain")
        self.assertEqual("Y [km]", api_result.get("layout").get("yaxis").get("title"))
        api_result = get_widget_result("location_map", "test_user", "test_domain")
        self.assertEqual("usa", api_result.get("layout").get("geo").get("scope"))

    def test_nomatch(self):
        api_result = get_widget_result("dummy", "test_user", "test_domain")
        self.assertEqual(None, api_result)

if __name__ == "__main__":
    unittest.main()
