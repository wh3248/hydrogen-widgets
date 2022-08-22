"""
    test_get_widget_layout.py

    This is a unit test for the get_widget_layout.py
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hydrogen_widgets.utilities.get_widget_layout import get_widget_layout

# pylint: disable=C0413

class TestGetWidgetLayout(unittest.TestCase):
    """Unit test class"""

    def test_widget_layout(self):
        """Test the widget."""

        api_result = get_widget_layout()
        self.assertEqual(4, len(api_result))


if __name__ == "__main__":
    unittest.main()
