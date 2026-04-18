import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()

# Only mock matplotlib, numpy, pandas if they are not actually available
try:
    import matplotlib
except ImportError:
    sys.modules['matplotlib'] = MagicMock()
    sys.modules['matplotlib.pyplot'] = MagicMock()

try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()

try:
    import pandas
except ImportError:
    sys.modules['pandas'] = MagicMock()

from dictra_analyzr.plotter import Plotter
from dictra_analyzr.config import PlotSettings

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = Plotter(Path("dummy_path"))
        self.settings = PlotSettings(
            legend='', lineW=2, legF=12, xlims=[0, 100], title='test title',
            ylab='y', xlab='x', labF=12, tickS=12, bins=5, figsize=[10, 8]
        )

    def test_plot_dict(self):
        # Use simple lists instead of numpy arrays to avoid global numpy mock
        x = [1, 2, 3]
        y_dict = {'A': [4, 5, 6], 'B': [7, 8, 9]}
        title = "Test Title"
        filename = "test_file"
        ylab = "Y Label"
        xlims = [0, 4]

        # Patch plot_dict_generic
        with patch.object(self.plotter, 'plot_dict_generic') as mock_plot_dict_generic:
            self.plotter.plot_dict(x, y_dict, title, filename, ylab, xlims, self.settings)

            # Assert that plot_dict_generic was called with the correct arguments
            mock_plot_dict_generic.assert_called_once_with(
                x, y_dict, title, filename, ylab, xlims, self.settings
            )

if __name__ == '__main__':
    unittest.main()
