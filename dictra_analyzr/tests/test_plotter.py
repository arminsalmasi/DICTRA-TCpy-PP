import sys
from unittest.mock import MagicMock

# Mock external dependencies
sys.modules['numpy'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['tc_python'] = MagicMock()

import unittest
from pathlib import Path
from dictra_analyzr.plotter import Plotter

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = Plotter(Path('.'))

    def test_get_xlims_with_valid_data(self):
        data = {'tS_pts': [10.5, 20.0, 30.5]}
        self.assertEqual(self.plotter.get_xlims(data), [10.5, 30.5])

    def test_get_xlims_with_empty_pts(self):
        data = {'tS_pts': []}
        self.assertEqual(self.plotter.get_xlims(data), [0, 100])

    def test_get_xlims_without_pts(self):
        data = {'other_key': [1, 2, 3]}
        self.assertEqual(self.plotter.get_xlims(data), [0, 100])

if __name__ == '__main__':
    unittest.main()
