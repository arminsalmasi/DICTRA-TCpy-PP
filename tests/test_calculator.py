import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock proprietary and missing dependencies
sys.modules['tc_python'] = MagicMock()

from dictra_analyzr.calculator import ThermodynamicCalculator

class TestThermodynamicCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = ThermodynamicCalculator(Path("dummy_path"))

    @patch('dictra_analyzr.calculator.logger')
    @patch('dictra_analyzr.calculator.TCPython')
    def test_tccalc_point_iteration_exception(self, mock_tcpython, mock_logger):
        """Test that an exception during point calculation is logged and iteration continues."""
        mock_tc_setting = MagicMock()
        mock_tc_setting.database = ['DB1']
        mock_tc_setting.phsToSus = []
        mock_tc_setting.acRefs = []
        mock_tc_setting.p3flag = False
        mock_tc_setting.mobFlag = False

        # Mock mfs for X condition setting
        mock_mfs = MagicMock()
        mock_mfs.__getitem__.return_value = 0.5

        # Create a dictionary input with n_pts = 2
        dict_input = {
            'tS_DICT_mfs': mock_mfs,
            'tS_pts': [0, 1], # 2 points
            'tc_setting': mock_tc_setting,
            'T': 1000.0,
            'elnames': ['A', 'B'],
            'path': 'dummy_pth'
        }

        with patch.object(self.calc, '_setup_system') as mock_setup:
            mock_poly = MagicMock()
            # Force calculate() to raise an exception
            mock_poly.calculate.side_effect = Exception("Test Calculation Error")
            mock_setup.return_value = mock_poly

            # Suppress print statements in tests
            with patch('builtins.print'):
                result = self.calc.tccalc(dict_input)

            # Verify that calculate() was called twice (once for each point)
            self.assertEqual(mock_poly.calculate.call_count, 2)

            # Verify that warning was called twice with expected message
            self.assertEqual(mock_logger.warning.call_count, 2)
            mock_logger.warning.assert_any_call("Calculation failed at point 0: Test Calculation Error")
            mock_logger.warning.assert_any_call("Calculation failed at point 1: Test Calculation Error")

            # Verify the result still contains empty data structures initialized in tccalc
            self.assertIn('tS_TC_phnames', result)
            self.assertEqual(result['tS_TC_phnames'], {})

if __name__ == '__main__':
    unittest.main()
