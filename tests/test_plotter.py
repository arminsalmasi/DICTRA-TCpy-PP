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

    @patch('dictra_analyzr.plotter.plt')
    @patch.object(Path, 'exists', return_value=True)
    def test_process_plots_all_actions(self, mock_exists, mock_plt):
        # Setup plotter with mocked methods
        self.plotter.del_pngs_pdf = MagicMock()
        self.plotter.single_plotter = MagicMock()
        self.plotter.ol_plotter = MagicMock()
        self.plotter.all_GMX_plotter = MagicMock()

        # Setup config with all actions True
        config = MagicMock()
        config.dirList = ["dir1", "dir2"]
        config.actions.delPNGs = True
        config.actions.plot = True
        config.actions.plotoverlaid = True
        config.actions.plotMG = True
        config.actions.showPlot = False
        config.tc_setting.mobFlag = True

        self.plotter.process_plots(config)

        # Verify calls for dir1 and dir2
        self.assertEqual(self.plotter.del_pngs_pdf.call_count, 2)
        self.plotter.del_pngs_pdf.assert_any_call(Path("dummy_path/dir1"))
        self.plotter.del_pngs_pdf.assert_any_call(Path("dummy_path/dir2"))

        self.assertEqual(self.plotter.single_plotter.call_count, 2)
        self.plotter.single_plotter.assert_any_call(Path("dummy_path/dir1"), config)

        self.assertEqual(self.plotter.ol_plotter.call_count, 2)
        self.plotter.ol_plotter.assert_any_call(Path("dummy_path/dir1"), config)

        # Verify all_GMX_plotter called once
        self.plotter.all_GMX_plotter.assert_called_once_with(Path("dummy_path"), config)

        # Verify plt.close('all') called since showPlot is False
        mock_plt.close.assert_called_once_with('all')
        mock_plt.show.assert_not_called()

    @patch('dictra_analyzr.plotter.plt')
    @patch.object(Path, 'exists')
    def test_process_plots_missing_directory(self, mock_exists, mock_plt):
        # Setup plotter
        self.plotter.del_pngs_pdf = MagicMock()
        self.plotter.single_plotter = MagicMock()

        # Setup config
        config = MagicMock()
        config.dirList = ["dir1", "dir2"]
        config.actions.delPNGs = True
        config.actions.plot = True
        config.actions.plotoverlaid = False
        config.actions.plotMG = False
        config.actions.showPlot = True

        # Mock Path.exists to return False for dir1, True for dir2
        def fake_exists(self_path):
            return self_path.name == 'dir2'
        # Can't use side_effect with self_path directly for property mock.
        # Just use simple list of returns corresponding to the calls
        mock_exists.side_effect = [False, True]

        self.plotter.process_plots(config)

        # Since dir1 doesn't exist, actions should only be called for dir2
        self.plotter.del_pngs_pdf.assert_called_once_with(Path("dummy_path/dir2"))
        self.plotter.single_plotter.assert_called_once_with(Path("dummy_path/dir2"), config)

        # Verify plt.show() called since showPlot is True
        mock_plt.show.assert_called_once()
        mock_plt.close.assert_not_called()

if __name__ == '__main__':
    unittest.main()
