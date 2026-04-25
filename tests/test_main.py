import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure tc_python is mocked before any imports from the package
if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()

# Since numpy is not available in the testing environment, mock it as well conditionally
try:
    import numpy
except ImportError:
    if 'numpy' not in sys.modules:
        sys.modules['numpy'] = MagicMock()

# Mock other external dependencies unavailable in the test environment
try:
    import matplotlib
except ImportError:
    if 'matplotlib' not in sys.modules:
        sys.modules['matplotlib'] = MagicMock()
        sys.modules['matplotlib.pyplot'] = MagicMock()

try:
    import pandas
except ImportError:
    if 'pandas' not in sys.modules:
        sys.modules['pandas'] = MagicMock()

try:
    import scipy
except ImportError:
    if 'scipy' not in sys.modules:
        sys.modules['scipy'] = MagicMock()
        sys.modules['scipy.interpolate'] = MagicMock()

import main

class TestMain(unittest.TestCase):

    @patch('main.Path')
    @patch('main.DictraPipeline')
    @patch('sys.argv', ['main.py'])
    def test_main_default_args(self, mock_pipeline, mock_path_class):
        mock_base_path = MagicMock()
        mock_config_path = MagicMock()

        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.resolve.return_value = mock_base_path

        mock_base_path.__truediv__.return_value = mock_config_path

        mock_base_path.exists.return_value = True
        mock_config_path.exists.return_value = True

        mock_base_path.__str__.return_value = '/mock/base_path'
        mock_config_path.__str__.return_value = '/mock/base_path/settings.json'

        main.main()

        mock_pipeline.assert_called_once_with('/mock/base_path/settings.json', '/mock/base_path')
        mock_pipeline.return_value.run.assert_called_once()

    @patch('main.Path')
    @patch('main.DictraPipeline')
    @patch('sys.argv', ['main.py', '/custom/path', '--config', 'custom.json'])
    def test_main_custom_args(self, mock_pipeline, mock_path_class):
        mock_base_path = MagicMock()
        mock_config_path = MagicMock()

        mock_path_class.return_value.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path

        mock_base_path.exists.return_value = True
        mock_config_path.exists.return_value = True

        mock_base_path.__str__.return_value = '/custom/path'
        mock_config_path.__str__.return_value = '/custom/path/custom.json'

        main.main()

        mock_pipeline.assert_called_once_with('/custom/path/custom.json', '/custom/path')
        mock_pipeline.return_value.run.assert_called_once()

    @patch('sys.exit')
    @patch('main.Path')
    @patch('sys.argv', ['main.py'])
    def test_main_base_path_not_exists(self, mock_path_class, mock_exit):
        # We must prevent sys.exit from raising SystemExit, but we also want to stop
        # execution of main() after sys.exit(1) is called, so we raise an exception
        # we can catch, or we can just mock sys.exit to raise an exception.
        mock_exit.side_effect = Exception("SystemExit mocked")
        mock_base_path = MagicMock()
        mock_path_class.return_value.resolve.return_value = mock_base_path

        mock_base_path.exists.return_value = False

        try:
            main.main()
        except Exception as e:
            if str(e) != "SystemExit mocked":
                raise

        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('main.Path')
    @patch('sys.argv', ['main.py'])
    def test_main_config_path_not_exists(self, mock_path_class, mock_exit):
        mock_exit.side_effect = Exception("SystemExit mocked")
        mock_base_path = MagicMock()
        mock_config_path = MagicMock()

        mock_path_class.return_value.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path

        mock_base_path.exists.return_value = True
        mock_config_path.exists.return_value = False

        try:
            main.main()
        except Exception as e:
            if str(e) != "SystemExit mocked":
                raise

        mock_exit.assert_called_once_with(1)

    @patch('traceback.print_exc')
    @patch('sys.exit')
    @patch('main.DictraPipeline')
    @patch('main.Path')
    @patch('sys.argv', ['main.py'])
    def test_main_pipeline_exception(self, mock_path_class, mock_pipeline, mock_exit, mock_print_exc):
        mock_base_path = MagicMock()
        mock_config_path = MagicMock()

        mock_path_class.return_value.resolve.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_config_path

        mock_base_path.exists.return_value = True
        mock_config_path.exists.return_value = True

        mock_base_path.__str__.return_value = '/mock/base_path'
        mock_config_path.__str__.return_value = '/mock/base_path/settings.json'

        mock_pipeline.return_value.run.side_effect = Exception("Test exception")

        main.main()

        mock_print_exc.assert_called_once()
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
