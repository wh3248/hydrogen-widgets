"""
    test_terrain_map.py

    This is a unit test for the terrain_map.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.terrain_map import render_terrain_map

# pylint: disable=C0413

class TestTerrainMap(unittest.TestCase):
    """Unit test class"""

    def test_widget(self):
        """Test the widget."""

        env_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.environ["CLIENT_HYDRO_DATA_PATH"] = env_data_path
        api_result = render_terrain_map("test_user", "test_domain")
        self.assertEqual("zoom", api_result.get("layout").get("dragmode"))

if __name__ == "__main__":
    unittest.main()
