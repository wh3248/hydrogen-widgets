"""
    test_terrain_obs_points.py

    This is a unit test for the terrain_obs_points.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.terrain_obs_points import render_terrain_obs_points

# pylint: disable=C0413

class TestTerrainObsPoints(unittest.TestCase):
    """Unit test class"""

    def test_streamflow_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        query_parameters = {
            "site_id": "06713500",
            "site_name": "test",
            "site_type" : "streamflow"
        }
        api_result = render_terrain_obs_points("test_user", "test_domain", query_parameters)
        self.assertEqual(5403, len(api_result.get("traces")[0].get("x")))

    def test_groundwater_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        query_parameters = {
            "site_id": "403536111545001",
            "site_name": "test",
            "site_type" : "groundwater"
        }
        api_result = render_terrain_obs_points("test_user", "test_domain", query_parameters)
        self.assertEqual(559, len(api_result.get("traces")[0].get("x")))

    def test_no_site(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        query_parameters = {
        }
        api_result = render_terrain_obs_points("test_user", "test_domain", query_parameters)
        self.assertEqual(0, len(api_result.get("traces")))

if __name__ == "__main__":
    unittest.main()
