import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Provide mocks only for modules that cannot be imported
import importlib

def safe_import(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        sys.modules[module_name] = MagicMock()

safe_import('matplotlib')
safe_import('matplotlib.pyplot')
safe_import('tc_python')
safe_import('numpy')
safe_import('pandas')

from dictra_analyzr.plotter import Plotter

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = Plotter(Path("dummy_path"))

    @patch('dictra_analyzr.plotter.plt')
    @patch('builtins.print')
    def test_save_fig_exception_handled(self, mock_print, mock_plt):
        """Test that _save_fig handles exceptions gracefully without crashing."""
        # Set up the mock to raise an Exception when savefig is called
        mock_plt.savefig.side_effect = Exception("Mocked save error")

        filename = "test_plot"
        xlims = [0, 10]

        # Call _save_fig, which should catch the Exception
        try:
            self.plotter._save_fig(filename, xlims)
        except Exception as e:
            self.fail(f"_save_fig raised an exception unexpectedly: {e}")

        # Verify that savefig was called correctly
        suffix = f"_{xlims[0]}_{xlims[1]}"
        mock_plt.savefig.assert_called_once_with(f"{filename}{suffix}.png", dpi=400, bbox_inches='tight')

        # Verify that the exception was caught and printed
        mock_print.assert_called_once_with(f"Error saving figure {filename}: Mocked save error")

    def test_get_xlims_valid(self):
        """Test get_xlims with valid iterable of arrays."""
        import numpy as np
        data = [
            np.array([[10, 1], [20, 2], [30, 3]]),
            np.array([[5, 1], [15, 2], [25, 3]])
        ]
        xlims = self.plotter.get_xlims(data)
        self.assertEqual(xlims, [5, 30])

    def test_get_xlims_empty(self):
        """Test get_xlims with empty data list."""
        data = []
        with self.assertRaises(ValueError):
            self.plotter.get_xlims(data)

    @patch('dictra_analyzr.plotter.plt')
    @patch.object(Plotter, '_decorate_ax')
    @patch.object(Plotter, '_save_fig')
    def test_plot_generic_empty_data(self, mock_save_fig, mock_decorate_ax, mock_plt):
        """Test that plot_generic handles an empty list of data without crashing."""
        # Setup mocks
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Setup mock settings
        mock_settings = MagicMock()
        mock_settings.figsize = (8, 6)
        mock_settings.lineW = 1.0
        mock_settings.legF = 10
        mock_settings.xlab = "X Label"

        # Test inputs
        x_empty = []
        y_empty = []
        legend = ["legend"]
        title = "title"
        filename = "file"
        ylab = "ylab"
        xlims = [0, 1]

        # Call the method
        try:
            self.plotter.plot_generic(x_empty, y_empty, legend, title, filename, ylab, xlims, mock_settings)
        except Exception as e:
            self.fail(f"plot_generic crashed with empty data: {e}")

        # Assertions
        # Just verify that the plotting functions were called to indicate it didn't return early or crash
        mock_plt.subplots.assert_called()
        mock_ax.plot.assert_called()
        mock_save_fig.assert_called()

if __name__ == '__main__':
    unittest.main()
