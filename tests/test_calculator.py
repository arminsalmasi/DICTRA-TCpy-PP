import sys
import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# Only mock tc_python globally. We should NOT mock numpy.
sys.modules['tc_python'] = MagicMock()

import numpy as np
from dictra_analyzr.calculator import ThermodynamicCalculator
from dictra_analyzr.config import TCSetting

class TestThermodynamicCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = ThermodynamicCalculator(Path("dummy_path"))

    def test_tccalc_missing_key(self):
        dict_input = {'T': 1000}
        result = self.calc.tccalc(dict_input)
        self.assertEqual(result, dict_input)

    @patch('dictra_analyzr.calculator.TCPython')
    def test_tccalc_success(self, mock_tc_class):
        tc_setting = TCSetting(
            database=['TCFE9'],
            acRefs=['GRAPHITE'],
            phsToSus=['CEMENTITE'],
            p3flag=False,
            mobFlag=True
        )

        dict_input = {
            'tS_DICT_mfs': np.array([[0.1, 0.9], [0.2, 0.8]]),
            'tc_setting': tc_setting,
            'tS_pts': [0, 1],
            'T': 1000.0,
            'elnames': ['C', 'Fe'],
            'path': 'dummy_path'
        }

        # Mock the TCPython return values
        mock_tc_instance = MagicMock()
        mock_tc_class.return_value.__enter__.return_value = mock_tc_instance

        mock_poly = MagicMock()
        # mock _setup_system return value indirectly by mocking what it calls
        mock_tc_instance.set_cache_folder.return_value.select_thermodynamic_and_kinetic_databases_with_elements.return_value.get_system.return_value.with_single_equilibrium_calculation.return_value = mock_poly
        mock_tc_instance.set_cache_folder.return_value.select_thermodynamic_and_kinetic_databases_with_elements.return_value.deselect_phase.return_value.get_system.return_value.with_single_equilibrium_calculation.return_value = mock_poly

        mock_pntEq = MagicMock()
        mock_poly.calculate.return_value = mock_pntEq

        mock_pntEq.get_stable_phases.return_value = ['FCC_A1', 'BCC_A2']
        mock_pntEq.get_value_of.side_effect = lambda x: 0.5 # just return a dummy value for all get_value_of calls

        result = self.calc.tccalc(dict_input)

        # verify the calls
        self.assertIn('tS_TC_NEAT_phnames', result)
        self.assertEqual(result['tS_TC_NEAT_phnames'], ['FCC_A1', 'BCC_A2'])

        # 2 points
        self.assertEqual(len(result['tS_TC_phnames']), 2)

        self.assertIn('tS_TC_M', result)
        self.assertIn('tS_TC_G', result)

        self.assertEqual(len(result['tS_TC_npms']), 4) # 2 pts * 2 phases

    @patch('dictra_analyzr.calculator.TCPython')
    def test_tccalc_poly3_and_no_mob(self, mock_tc_class):
        tc_setting = TCSetting(
            database=['TCFE9'],
            acRefs=['GRAPHITE'],
            phsToSus=[],
            p3flag=True,
            mobFlag=False
        )

        dict_input = {
            'tS_DICT_mfs': np.array([[0.1, 0.9]]),
            'tc_setting': tc_setting,
            'tS_pts': [0],
            'T': 1000.0,
            'elnames': ['C', 'Fe'],
            'path': 'dummy_path'
        }

        # Mock the TCPython return values
        mock_tc_instance = MagicMock()
        mock_tc_class.return_value.__enter__.return_value = mock_tc_instance

        mock_poly = MagicMock()
        mock_tc_instance.select_database_and_elements.return_value.get_system.return_value.with_single_equilibrium_calculation.return_value = mock_poly

        mock_pntEq = MagicMock()
        mock_poly.calculate.return_value = mock_pntEq

        mock_pntEq.get_stable_phases.return_value = ['FCC_A1']
        mock_pntEq.get_value_of.side_effect = lambda x: 0.5

        with patch('os.path.isfile', return_value=True):
            result = self.calc.tccalc(dict_input)

        # verify poly3 commands were called
        mock_poly.run_poly_command.assert_called_with('read dummy_path/p.POLY3')

        # Verify result contains the expected data
        self.assertIn('tS_TC_NEAT_phnames', result)
        self.assertEqual(result['tS_TC_NEAT_phnames'], ['FCC_A1'])

        self.assertNotIn('tS_TC_M', result)
        self.assertNotIn('tS_TC_G', result)

if __name__ == '__main__':
    unittest.main()
