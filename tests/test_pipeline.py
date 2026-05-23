import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()

from dictra_analyzr.pipeline import DictraPipeline

class TestDictraPipeline(unittest.TestCase):
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_init_with_base_path(self, mock_from_json):
        mock_config = MagicMock()
        mock_from_json.return_value = mock_config

        pipeline = DictraPipeline('dummy_config.json', base_path='/custom/path')

        mock_from_json.assert_called_once_with('dummy_config.json')
        self.assertEqual(pipeline.config, mock_config)
        self.assertEqual(pipeline.base_path, Path('/custom/path'))
        self.assertEqual(pipeline.loader.base_path, Path('/custom/path'))
        self.assertEqual(pipeline.calculator.base_path, Path('/custom/path'))
        self.assertEqual(pipeline.corrector.base_path, Path('/custom/path'))
        self.assertEqual(pipeline.plotter.base_path, Path('/custom/path'))

    @patch('dictra_analyzr.pipeline.Path.cwd')
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_init_without_base_path(self, mock_from_json, mock_cwd):
        mock_config = MagicMock()
        mock_from_json.return_value = mock_config
        mock_cwd.return_value = Path('/current/working/dir')

        pipeline = DictraPipeline('dummy_config.json')

        mock_from_json.assert_called_once_with('dummy_config.json')
        self.assertEqual(pipeline.config, mock_config)
        self.assertEqual(pipeline.base_path, Path('/current/working/dir'))
        self.assertEqual(pipeline.loader.base_path, Path('/current/working/dir'))
        self.assertEqual(pipeline.calculator.base_path, Path('/current/working/dir'))
        self.assertEqual(pipeline.corrector.base_path, Path('/current/working/dir'))
        self.assertEqual(pipeline.plotter.base_path, Path('/current/working/dir'))

    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_all_actions(self, mock_from_json):
        mock_config = MagicMock()
        mock_config.actions.read = True
        mock_config.actions.calc = True
        mock_config.actions.value_correction = True
        mock_config.actions.plot = True
        mock_from_json.return_value = mock_config

        mock_loader = MagicMock()
        mock_calc = MagicMock()
        mock_corr = MagicMock()
        mock_plotter = MagicMock()

        pipeline = DictraPipeline(
            'dummy_config.json',
            base_path='/custom/path',
            loader=mock_loader,
            calculator=mock_calc,
            corrector=mock_corr,
            plotter=mock_plotter
        )
        pipeline.run()

        mock_loader.process_directories.assert_called_once_with(mock_config)
        mock_calc.process_calculations.assert_called_once_with(mock_config)
        mock_corr.process_corrections.assert_called_once_with(mock_config)
        mock_plotter.process_plots.assert_called_once_with(mock_config)

    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_no_actions(self, mock_from_json):
        mock_config = MagicMock()
        mock_config.actions.read = False
        mock_config.actions.calc = False
        mock_config.actions.value_correction = False
        mock_config.actions.plot = False
        mock_config.actions.plotoverlaid = False
        mock_config.actions.plotMG = False
        mock_from_json.return_value = mock_config

        mock_loader = MagicMock()
        mock_calc = MagicMock()
        mock_corr = MagicMock()
        mock_plotter = MagicMock()

        pipeline = DictraPipeline(
            'dummy_config.json',
            base_path='/custom/path',
            loader=mock_loader,
            calculator=mock_calc,
            corrector=mock_corr,
            plotter=mock_plotter
        )
        pipeline.run()

        mock_loader.process_directories.assert_not_called()
        mock_calc.process_calculations.assert_not_called()
        mock_corr.process_corrections.assert_not_called()
        mock_plotter.process_plots.assert_not_called()

    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_partial_actions(self, mock_from_json):
        mock_config = MagicMock()
        mock_config.actions.read = True
        mock_config.actions.calc = False
        mock_config.actions.value_correction = False
        mock_config.actions.plot = False
        mock_config.actions.plotoverlaid = True # This should trigger plotting
        mock_config.actions.plotMG = False
        mock_from_json.return_value = mock_config

        mock_loader = MagicMock()
        mock_calc = MagicMock()
        mock_corr = MagicMock()
        mock_plotter = MagicMock()

        pipeline = DictraPipeline(
            'dummy_config.json',
            base_path='/custom/path',
            loader=mock_loader,
            calculator=mock_calc,
            corrector=mock_corr,
            plotter=mock_plotter
        )
        pipeline.run()

        mock_loader.process_directories.assert_called_once_with(mock_config)
        mock_calc.process_calculations.assert_not_called()
        mock_corr.process_corrections.assert_not_called()
        mock_plotter.process_plots.assert_called_once_with(mock_config)

if __name__ == '__main__':
    unittest.main()
