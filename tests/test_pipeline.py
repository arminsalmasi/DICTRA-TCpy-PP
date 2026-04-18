import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()

from dictra_analyzr.pipeline import DictraPipeline

class TestDictraPipeline(unittest.TestCase):
    @patch('dictra_analyzr.pipeline.DataLoader')
    @patch('dictra_analyzr.pipeline.Config.from_json')
    def test_run_exception_propagation(self, mock_from_json, mock_data_loader_class):
        # Setup the mock config
        mock_config = MagicMock()
        mock_config.actions.read = True
        mock_config.actions.calc = False
        mock_config.actions.value_correction = False
        mock_config.actions.plot = False
        mock_config.actions.plotoverlaid = False
        mock_config.actions.plotMG = False
        mock_from_json.return_value = mock_config

        # Setup the mock DataLoader to raise an exception
        mock_loader_instance = mock_data_loader_class.return_value
        mock_loader_instance.process_directories.side_effect = Exception("Test DataLoader failed")

        # Initialize the pipeline
        pipeline = DictraPipeline("dummy_config_path")

        # Call pipeline.run() and assert it raises the exception
        with self.assertRaisesRegex(Exception, "Test DataLoader failed"):
            pipeline.run()

        # Verify that the sub-component was called correctly before raising
        mock_loader_instance.process_directories.assert_called_once_with(mock_config)

if __name__ == '__main__':
    unittest.main()
