import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
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

    @patch('dictra_analyzr.pipeline.Plotter')
    @patch('dictra_analyzr.pipeline.ResultCorrector')
    @patch('dictra_analyzr.pipeline.ThermodynamicCalculator')
    @patch('dictra_analyzr.pipeline.DataLoader')
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_all_actions(self, mock_from_json, mock_loader, mock_calc, mock_corr, mock_plotter):
        mock_config = MagicMock()
        mock_config.actions.read = True
        mock_config.actions.calc = True
        mock_config.actions.value_correction = True
        mock_config.actions.plot = True
        mock_from_json.return_value = mock_config

        pipeline = DictraPipeline('dummy_config.json', base_path='/custom/path')
        pipeline.run()

        mock_loader.assert_called_once_with(Path('/custom/path'))
        mock_loader.return_value.process_directories.assert_called_once_with(mock_config)

        mock_calc.assert_called_once_with(Path('/custom/path'))
        mock_calc.return_value.process_calculations.assert_called_once_with(mock_config)

        mock_corr.assert_called_once_with(Path('/custom/path'))
        mock_corr.return_value.process_corrections.assert_called_once_with(mock_config)

        mock_plotter.assert_called_once_with(Path('/custom/path'))
        mock_plotter.return_value.process_plots.assert_called_once_with(mock_config)

    @patch('dictra_analyzr.pipeline.Plotter')
    @patch('dictra_analyzr.pipeline.ResultCorrector')
    @patch('dictra_analyzr.pipeline.ThermodynamicCalculator')
    @patch('dictra_analyzr.pipeline.DataLoader')
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_no_actions(self, mock_from_json, mock_loader, mock_calc, mock_corr, mock_plotter):
        mock_config = MagicMock()
        mock_config.actions.read = False
        mock_config.actions.calc = False
        mock_config.actions.value_correction = False
        mock_config.actions.plot = False
        mock_config.actions.plotoverlaid = False
        mock_config.actions.plotMG = False
        mock_from_json.return_value = mock_config

        pipeline = DictraPipeline('dummy_config.json', base_path='/custom/path')
        pipeline.run()

        mock_loader.assert_not_called()
        mock_calc.assert_not_called()
        mock_corr.assert_not_called()
        mock_plotter.assert_not_called()

    @patch('dictra_analyzr.pipeline.Plotter')
    @patch('dictra_analyzr.pipeline.ResultCorrector')
    @patch('dictra_analyzr.pipeline.ThermodynamicCalculator')
    @patch('dictra_analyzr.pipeline.DataLoader')
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_partial_actions(self, mock_from_json, mock_loader, mock_calc, mock_corr, mock_plotter):
        mock_config = MagicMock()
        mock_config.actions.read = True
        mock_config.actions.calc = False
        mock_config.actions.value_correction = False
        mock_config.actions.plot = False
        mock_config.actions.plotoverlaid = True # This should trigger plotting
        mock_config.actions.plotMG = False
        mock_from_json.return_value = mock_config

        pipeline = DictraPipeline('dummy_config.json', base_path='/custom/path')
        pipeline.run()

        mock_loader.assert_called_once_with(Path('/custom/path'))
        mock_loader.return_value.process_directories.assert_called_once_with(mock_config)

        mock_calc.assert_not_called()
        mock_corr.assert_not_called()

        mock_plotter.assert_called_once_with(Path('/custom/path'))
        mock_plotter.return_value.process_plots.assert_called_once_with(mock_config)

if __name__ == '__main__':
    unittest.main()
