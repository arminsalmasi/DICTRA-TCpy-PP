import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module we are testing
import main

class TestMain(unittest.TestCase):

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.Path')
    @patch('main.DictraPipeline')
    def test_main_success(self, mock_pipeline_class, mock_path_class, mock_parse_args):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.path = '.'
        mock_args.config = 'settings.json'
        mock_parse_args.return_value = mock_args

        mock_base_path = MagicMock()
        mock_base_path.__str__.return_value = '/test/base'
        mock_base_path.exists.return_value = True

        mock_config_path = MagicMock()
        mock_config_path.__str__.return_value = '/test/base/settings.json'
        mock_config_path.exists.return_value = True

        mock_base_path.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path

        mock_path_class.return_value = mock_base_path

        mock_pipeline_instance = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline_instance

        # Execute
        main.main()

        # Assertions
        mock_pipeline_class.assert_called_once_with('/test/base/settings.json', '/test/base')
        mock_pipeline_instance.run.assert_called_once()

    @patch('main.sys.exit')
    @patch('builtins.print')
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.Path')
    def test_main_missing_base_path(self, mock_path_class, mock_parse_args, mock_print, mock_exit):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.path = 'invalid_path'
        mock_args.config = 'settings.json'
        mock_parse_args.return_value = mock_args

        mock_base_path = MagicMock()
        mock_base_path.__str__.return_value = '/test/invalid_path'
        mock_base_path.exists.return_value = False

        mock_base_path.resolve.return_value = mock_base_path
        mock_path_class.return_value = mock_base_path

        mock_exit.side_effect = Exception('SystemExit mocked')

        # Execute
        with self.assertRaisesRegex(Exception, 'SystemExit mocked'):
            main.main()

        # Assertions
        mock_print.assert_called_once_with('Error: Path /test/invalid_path does not exist.')
        mock_exit.assert_called_once_with(1)

    @patch('main.sys.exit')
    @patch('builtins.print')
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.Path')
    def test_main_missing_config_path(self, mock_path_class, mock_parse_args, mock_print, mock_exit):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.path = '.'
        mock_args.config = 'missing_settings.json'
        mock_parse_args.return_value = mock_args

        mock_base_path = MagicMock()
        mock_base_path.__str__.return_value = '/test/base'
        mock_base_path.exists.return_value = True

        mock_config_path = MagicMock()
        mock_config_path.__str__.return_value = '/test/base/missing_settings.json'
        mock_config_path.exists.return_value = False

        mock_base_path.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path
        mock_path_class.return_value = mock_base_path

        mock_exit.side_effect = Exception('SystemExit mocked')

        # Execute
        with self.assertRaisesRegex(Exception, 'SystemExit mocked'):
            main.main()

        # Assertions
        mock_print.assert_any_call('Error: Configuration file /test/base/missing_settings.json not found.')
        mock_print.assert_any_call('Please ensure settings.json exists in the target directory.')
        mock_exit.assert_called_once_with(1)

    @patch('main.sys.exit')
    @patch('traceback.print_exc')
    @patch('builtins.print')
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.Path')
    @patch('main.DictraPipeline')
    def test_main_pipeline_exception(self, mock_pipeline_class, mock_path_class, mock_parse_args, mock_print, mock_print_exc, mock_exit):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.path = '.'
        mock_args.config = 'settings.json'
        mock_parse_args.return_value = mock_args

        mock_base_path = MagicMock()
        mock_base_path.__str__.return_value = '/test/base'
        mock_base_path.exists.return_value = True

        mock_config_path = MagicMock()
        mock_config_path.__str__.return_value = '/test/base/settings.json'
        mock_config_path.exists.return_value = True

        mock_base_path.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path
        mock_path_class.return_value = mock_base_path

        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.run.side_effect = Exception("Test Pipeline Error")
        mock_pipeline_class.return_value = mock_pipeline_instance

        mock_exit.side_effect = Exception('SystemExit mocked')

        # Execute
        with self.assertRaisesRegex(Exception, 'SystemExit mocked'):
            main.main()

        # Assertions
        mock_print.assert_called_once_with('Pipeline failed: Test Pipeline Error')
        mock_print_exc.assert_called_once()
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
