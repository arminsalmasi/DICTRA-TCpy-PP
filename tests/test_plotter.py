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

    @patch('dictra_analyzr.plotter.serializer.load_data')
    @patch('pathlib.Path.exists')
    @patch('builtins.print')
    def test_single_plotter(self, mock_print, mock_exists, mock_load_data):
        """Test single_plotter function covering logic of setting plotting limits and labels."""
        # Setup mocks
        mock_exists.return_value = True

        # Mock data with required keys
        mock_data = {
            'tS_pts': [0, 1, 2],
            'nearestTime': 100,
            'tS_DICT_ufs': [0.1, 0.2, 0.3],
            'tS_DICT_mfs': [0.2, 0.3, 0.4],
            'elnames': ['A', 'B'],
            'tS_TC_ws': {'PhaseA': [0.5, 0.6, 0.7]},
            'nameChanged_CQT_tS_TC_NEAT_npms': {'PhaseB': [0.8, 0.9, 1.0]},
            'tS_TC_acSER': {'PhaseC': [1.1, 1.2, 1.3]}
        }
        mock_load_data.return_value = mock_data

        # Create a dummy config
        mock_config = MagicMock()
        mock_config.timeflags = ['t1']
        mock_config.plot_settings = MagicMock()
        mock_config.plot_settings.xlims = [0, 10]
        mock_config.plot_settings.acSERleg = ['LegendA']

        # Patch plotter methods that would try to create plots
        with patch.object(self.plotter, 'plot_generic') as mock_plot_generic, \
             patch.object(self.plotter, 'plot_dict_generic') as mock_plot_dict_generic, \
             patch.object(self.plotter, 'plot_ylog_dict') as mock_plot_ylog_dict:

            # Execute
            self.plotter.single_plotter(Path("dummy_path"), mock_config)

            # Verify load_data was called
            mock_load_data.assert_called_once()

            # Verify plot_generic was called twice (for tS_DICT_ufs and tS_DICT_mfs)
            self.assertEqual(mock_plot_generic.call_count, 2)

            # Verify specific arguments to plot_generic, including xlims and ylab
            from unittest.mock import call

            mock_plot_generic.assert_any_call(
                x=[0, 1, 2],
                y=[0.1, 0.2, 0.3],
                legend=['A', 'B'],
                title='dummy_path',
                filename=Path('dummy_path/tS_DICT_ufs_100'),
                ylab=r'$U \: fraction$',
                xlims=[0, 10],
                settings=mock_config.plot_settings
            )

            mock_plot_generic.assert_any_call(
                x=[0, 1, 2],
                y=[0.2, 0.3, 0.4],
                legend=['A', 'B'],
                title='dummy_path',
                filename=Path('dummy_path/tS_DICT_mfs_100'),
                ylab=r'$Mole \: Fraction$',
                xlims=[0, 10],
                settings=mock_config.plot_settings
            )

            # Verify plot_dict_generic was called twice (for tS_TC_ws and nameChanged_CQT_tS_TC_NEAT_npms)
            self.assertEqual(mock_plot_dict_generic.call_count, 2)

            mock_plot_dict_generic.assert_any_call(
                x=[0, 1, 2],
                y_dict={'PhaseA': [0.5, 0.6, 0.7]},
                title='dummy_path',
                filename=Path('dummy_path/tS_TC_ws_100'),
                ylab=r'$Mass \:Fraction$',
                xlims=[0, 10],
                settings=mock_config.plot_settings
            )

            mock_plot_dict_generic.assert_any_call(
                x=[0, 1, 2],
                y_dict={'PhaseB': [0.8, 0.9, 1.0]},
                title='dummy_path',
                filename=Path('dummy_path/nameChanged_CQT_tS_TC_NEAT_npms_100'),
                ylab=r'$Phase \: Fraction$',
                xlims=[0, 10],
                settings=mock_config.plot_settings
            )

            # Verify plot_ylog_dict was called once (for tS_TC_acSER)
            self.assertEqual(mock_plot_ylog_dict.call_count, 1)

            mock_plot_ylog_dict.assert_any_call(
                x=[0, 1, 2],
                y_dict={'PhaseC': [1.1, 1.2, 1.3]},
                legend=['LegendA'],
                title='dummy_path',
                filename=Path('dummy_path/tS_TC_acSER_100'),
                ylab=r"$Log_{10}(Activity) \: (SER)$",
                xlims=[0, 10],
                settings=mock_config.plot_settings
            )

if __name__ == '__main__':
    unittest.main()
