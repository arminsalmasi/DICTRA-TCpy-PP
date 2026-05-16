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

    @unittest.skipIf(isinstance(sys.modules.get('numpy'), MagicMock), 'NumPy not installed')
    def test_get_xlims_valid(self):
        """Test get_xlims with valid iterable of arrays."""
        import numpy as np
        data = [
            np.array([[10, 1], [20, 2], [30, 3]]),
            np.array([[5, 1], [15, 2], [25, 3]])
        ]
        xlims = self.plotter.get_xlims(data)
        self.assertEqual(xlims, [5, 30])

    @unittest.skipIf(isinstance(sys.modules.get('numpy'), MagicMock), 'NumPy not installed')
    def test_get_xlims_empty(self):
        """Test get_xlims with empty data list."""
        data = []
        with self.assertRaises(ValueError):
            self.plotter.get_xlims(data)

    @patch('dictra_analyzr.plotter.Plotter.single_plotter')
    def test_process_plots_path_traversal(self, mock_single):
        from dictra_analyzr.config import Config, Actions, PlotSettings
        from dictra_analyzr.plotter import Plotter
        from unittest.mock import MagicMock

        mock_config = MagicMock()
        # Set dirList with normal and traversal directories
        mock_config.dirList = ["normal_dir", "../outside_dir", "/etc/passwd"]
        mock_config.actions.plot = True
        mock_config.actions.plotoverlaid = False
        mock_config.actions.plotMG = False
        mock_config.actions.delPNGs = False
        mock_config.actions.showPlot = False
        mock_config.timeflags = []
        mock_config.plot_settings = MagicMock()

        # Mock the Path object behavior for exists
        with patch('pathlib.Path.exists', return_value=True):
            self.plotter.process_plots(mock_config)

        # Expected single_plotter call ONLY for "normal_dir", since others fail the relative path check
        # dummy_path / normal_dir is relative to dummy_path
        # dummy_path / ../outside_dir is not relative to dummy_path
        # /etc/passwd is not relative to dummy_path

        # Verify it was only called once, for the normal dir
        self.assertEqual(mock_single.call_count, 1)
        args, kwargs = mock_single.call_args
        self.assertTrue(args[0].name == "normal_dir")

    @patch('dictra_analyzr.plotter.Plotter._plot_elements_for_dir')
    @patch('dictra_analyzr.plotter.serializer.load_data')
    @patch('dictra_analyzr.plotter.plt.subplots')
    @patch('dictra_analyzr.plotter.plt.close')
    def test_plot_overlay_for_k_path_traversal(self, mock_close, mock_subplots, mock_load, mock_plot_elements):
        from dictra_analyzr.config import Config, PlotSettings
        from dictra_analyzr.plotter import Plotter
        from unittest.mock import MagicMock

        # Basic setup
        mock_subplots.return_value = (MagicMock(), MagicMock())
        mock_plot_elements.return_value = ["dummy"]
        mock_load.return_value = {}

        mock_config = MagicMock()
        mock_config.dirList = ["normal_dir", "../outside_dir", "/etc/passwd"]

        settings = MagicMock()
        settings.MPlotlegs = ["A"]
        settings.MPlotPhase = "Phase"
        settings.figsize = (1,1)

        base_path = Path("/tmp/dummy_base").resolve()

        # We need exists to be True so it proceeds, but it will skip due to path traversal
        with patch('pathlib.Path.exists', return_value=True):
            with patch('dictra_analyzr.plotter.Plotter._save_fig'):
                self.plotter._plot_overlay_for_k(base_path, mock_config, "k_key", "k_ylab", settings)

        # load_data should only be called for the valid path "normal_dir"
        self.assertEqual(mock_load.call_count, 1)
        args, kwargs = mock_load.call_args
        self.assertTrue("normal_dir" in str(args[0]))

if __name__ == '__main__':
    unittest.main()
