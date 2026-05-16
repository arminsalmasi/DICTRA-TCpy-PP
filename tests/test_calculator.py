import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock proprietary and missing dependencies
if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()

# Global cleanup for previously established mocks that break things
if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
    del sys.modules['numpy']

if 'numpy' not in sys.modules:
    try:
        import numpy
    except ImportError:
        sys.modules['numpy'] = MagicMock()

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
            self.assertEqual(result['tS_TC_npms'], {})
            self.assertEqual(result['tS_TC_vpvs'], {})
            self.assertEqual(result['tS_TC_phXs'], {})
            self.assertEqual(result['tS_TC_acRef'], {})
            self.assertEqual(result['tS_TC_acSER'], {})
            self.assertEqual(result['tS_TC_mus'], {})
            self.assertEqual(result['tS_TC_ws'], {})
            self.assertEqual(result['tS_TC_NEAT_phnames'], [])
            self.assertEqual(result['tS_TC_NEAT_npms'], {})
            self.assertEqual(result['tS_TC_NEAT_vpvs'], {})
            self.assertEqual(result['tS_TC_NEAT_phXs'], {})

    @patch('builtins.print')
    def test_tccalc_key_error(self, mock_print):
        """Test that missing keys in input trigger a KeyError and return original input."""
        dict_input = {
            'T': 1000.0,
            # Missing other required keys like 'tS_DICT_mfs', 'tc_setting', etc.
        }

        # Deep copy to simulate what tccalc will return on failure
        import copy
        expected_result = copy.deepcopy(dict_input)

        result = self.calc.tccalc(dict_input)

        # Check that an error message was printed containing "Missing key"
        mock_print.assert_called()
        self.assertTrue(any("Missing key" in str(call) for call in mock_print.call_args_list))

        # Check that it returned a copy of the input dictionary
        self.assertEqual(result, expected_result)


    @patch('dictra_analyzr.calculator.TCPython')
    def test_tccalc_success(self, mock_tcpython):
        """Test happy path calculation using mocked _calculate_point_equilibrium data."""
        mock_tc_setting = MagicMock()
        mock_tc_setting.database = ['DB1']
        mock_tc_setting.phsToSus = []
        mock_tc_setting.acRefs = ['GRAPHITE']
        mock_tc_setting.p3flag = False
        mock_tc_setting.mobFlag = True

        import numpy as np

        # Create input dict for 1 point, 2 elements
        mock_mfs = np.array([[0.5, 0.5]])
        dict_input = {
            'tS_DICT_mfs': mock_mfs,
            'tS_pts': [0],
            'tc_setting': mock_tc_setting,
            'T': 1000.0,
            'elnames': ['A', 'C'], # include 'C' to trigger carbon reference block
            'path': 'dummy_pth'
        }

        mock_pnt_results = {
            'stablePhs': ['BCC'],
            'acRefs': {'ac(C, GRAPHITE)': 1.5},
            'acSER': {'A': 1.0, 'C': 2.0},
            'mus': {'A': -100, 'C': -200},
            'ws': {'A': 0.1, 'C': 0.2},
            'phases': {
                'BCC': {
                    'npm': 1.0,
                    'vpv': 1.0,
                    'X': np.array([0.5, 0.5]),
                    'M': np.array([1e-10, 2e-10]),
                    'G': np.array([5e-11, 1e-10])
                }
            }
        }

        with patch.object(self.calc, '_setup_system') as mock_setup, \
             patch.object(self.calc, '_calculate_point_equilibrium') as mock_calc_pnt:

            mock_poly = MagicMock()
            mock_setup.return_value = mock_poly
            mock_calc_pnt.return_value = mock_pnt_results

            with patch('builtins.print'):
                result = self.calc.tccalc(dict_input)

            # Assert correct population of dictionary
            self.assertEqual(result['tS_TC_phnames'][0], ['BCC'])
            self.assertEqual(result['tS_TC_npms']['0, BCC'], 1.0)
            self.assertEqual(result['tS_TC_vpvs']['0, BCC'], 1.0)
            np.testing.assert_array_equal(result['tS_TC_phXs']['0, BCC'], np.array([0.5, 0.5]))
            self.assertEqual(result['tS_TC_acRef']['ac(C, GRAPHITE)'], [1.5])
            self.assertEqual(result['tS_TC_acSER']['A'], [1.0])
            self.assertEqual(result['tS_TC_mus']['A'], [-100])
            self.assertEqual(result['tS_TC_ws']['A'], [0.1])

            # McalcFlag=True checks
            np.testing.assert_array_equal(result['tS_TC_M']['0, BCC'], np.array([1e-10, 2e-10]))
            np.testing.assert_array_equal(result['tS_TC_G']['0, BCC'], np.array([5e-11, 1e-10]))

            # Check NEAT structures from _trim_results
            self.assertEqual(result['tS_TC_NEAT_phnames'], ['BCC'])
            np.testing.assert_array_equal(result['tS_TC_NEAT_npms']['BCC'], np.array([1.0]))
            np.testing.assert_array_equal(result['tS_TC_NEAT_vpvs']['BCC'], np.array([1.0]))
            np.testing.assert_array_equal(result['tS_TC_NEAT_phXs']['BCC'][0], np.array([0.5, 0.5]))


if __name__ == '__main__':
    unittest.main()
