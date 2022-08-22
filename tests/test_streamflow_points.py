"""
    test_streamflow_points.py

    This is a unit test for the streamflow_points.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.streamflow_points import render_streamflow_points

# pylint: disable=C0413

class TestStreamFlowPoints(unittest.TestCase):
    """Unit test class"""

    def test_streamflow_points(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        api_result = render_streamflow_points("test_user", "test_domain")
        self.assertEqual(5, len(api_result.get("layout").get("updatemenus")[0].get("buttons")))

if __name__ == "__main__":
    unittest.main()
