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

if __name__ == '__main__':
    unittest.main()
