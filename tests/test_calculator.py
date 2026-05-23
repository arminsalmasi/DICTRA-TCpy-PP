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

    @patch('builtins.print')
    @patch('dictra_analyzr.calculator.TCPython')
    def test_tccalc_input_exception_handling(self, mock_tcpython, mock_print):
        """Test that an exception during input parsing is caught and printed."""

        # We need an object that acts like a dict but raises a specific Exception when accessed
        class FaultyDict(dict):
            def __getitem__(self, key):
                if key == 'tS_DICT_mfs':
                    raise Exception("Test Generic Exception")
                return super().__getitem__(key)

        # We also need to patch deepcopy to return our faulty dict
        dict_input = {'T': 1000.0}

        with patch('copy.deepcopy', return_value=FaultyDict(dict_input)):
            # This should trigger the exception when 'tS_DICT_mfs' is accessed
            self.calc.tccalc(dict_input)

        # Verify that print was called with the exact exception
        # We can assert that print was called with an Exception whose string match our message
        found = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], Exception) and str(args[0]) == "Test Generic Exception":
                found = True
                break
        self.assertTrue(found, "print() was not called with the expected Exception")

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

        from dictra_analyzr.calculator import TCPythonException
        with patch.object(self.calc, '_setup_system') as mock_setup:
            mock_poly = MagicMock()
            # Force calculate() to raise a TCPythonException
            mock_poly.calculate.side_effect = TCPythonException("Test Calculation Error")
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


    def test_calculate_point_equilibrium_basic(self):
        """Test basic point equilibrium calculation without C and McalcFlag=False."""
        # Mock inputs
        mock_poly = MagicMock()
        mock_pntEq = MagicMock()
        mock_poly.calculate.return_value = mock_pntEq

        mock_pntEq.get_stable_phases.return_value = ['FCC_A1', 'BCC_A2']

        # Helper to simulate get_value_of
        def mock_get_value_of(query):
            if query.startswith('ac('):
                return 0.5
            elif query.startswith('mu('):
                return -1000.0
            elif query.startswith('w('):
                return 0.1
            elif query.startswith('npm('):
                return 1.0
            elif query.startswith('vpv('):
                return 0.2
            elif query.startswith('X('):
                return 0.3
            return 0.0

        mock_pntEq.get_value_of.side_effect = mock_get_value_of

        elnames = ['FE', 'NI']
        acsRef = []
        McalcFlag = False

        # To avoid problems with mocked numpy inside calculator.py which might not have array implemented nicely
        with patch('dictra_analyzr.calculator.np') as mock_np:
            mock_np.array.side_effect = lambda x: list(x) # Just use list for simplicity in test

            results = self.calc._calculate_point_equilibrium(mock_poly, elnames, acsRef, McalcFlag)

        self.assertEqual(results['stablePhs'], ['FCC_A1', 'BCC_A2'])
        self.assertEqual(results['acRefs'], {})
        self.assertEqual(results['acSER']['FE'], 0.5)
        self.assertEqual(results['mus']['NI'], -1000.0)
        self.assertEqual(results['ws']['FE'], 0.1)

        self.assertIn('FCC_A1', results['phases'])
        self.assertEqual(results['phases']['FCC_A1']['npm'], 1.0)
        self.assertEqual(results['phases']['FCC_A1']['vpv'], 0.2)
        self.assertEqual(results['phases']['FCC_A1']['X'], [0.3, 0.3]) # FE, NI
        self.assertNotIn('M', results['phases']['FCC_A1'])
        self.assertNotIn('G', results['phases']['FCC_A1'])


    def test_calculate_point_equilibrium_with_c_and_mcalc(self):
        """Test point equilibrium calculation with C in elnames and McalcFlag=True."""
        # Mock inputs
        mock_poly = MagicMock()
        mock_pntEq = MagicMock()
        mock_poly.calculate.return_value = mock_pntEq

        mock_pntEq.get_stable_phases.return_value = ['LIQUID']

        # Helper to simulate get_value_of
        def mock_get_value_of(query):
            if query.startswith('ac(C,'):
                return 0.8
            elif query.startswith('ac('):
                return 0.5
            elif query.startswith('mu('):
                return -1000.0
            elif query.startswith('w('):
                return 0.1
            elif query.startswith('npm('):
                return 1.0
            elif query.startswith('vpv('):
                return 0.2
            elif query.startswith('X('):
                return 0.3
            elif query.startswith('M('):
                return 0.4
            return 0.0

        mock_pntEq.get_value_of.side_effect = mock_get_value_of

        elnames = ['FE', 'C']
        acsRef = ['GRAPHITE']
        McalcFlag = True

        with patch('dictra_analyzr.calculator.np') as mock_np:
            mock_np.array.side_effect = lambda x: list(x)

            results = self.calc._calculate_point_equilibrium(mock_poly, elnames, acsRef, McalcFlag)

        self.assertIn('ac(C, GRAPHITE)', results['acRefs'])
        self.assertEqual(results['acRefs']['ac(C, GRAPHITE)'], 0.8)

        self.assertIn('LIQUID', results['phases'])
        self.assertEqual(results['phases']['LIQUID']['X'], [0.3, 0.3])
        self.assertEqual(results['phases']['LIQUID']['M'], [0.4, 0.4])
        # G is M * X = 0.4 * 0.3 = 0.12 (simulated by mocked value retrieval logic in _calculate_point_equilibrium)
        # Wait, the code does: m_val = get_value_of(M), x_val = get_value_of(X), temp3.append(m_val * x_val)
        # So temp3 = [0.4 * 0.3, 0.4 * 0.3] = [0.12, 0.12]
        self.assertAlmostEqual(results['phases']['LIQUID']['G'][0], 0.12)
        self.assertAlmostEqual(results['phases']['LIQUID']['G'][1], 0.12)

if __name__ == '__main__':
    unittest.main()
