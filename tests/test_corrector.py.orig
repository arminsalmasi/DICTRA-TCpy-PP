import unittest
import sys
from unittest.mock import MagicMock
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()

import numpy as np
from dictra_analyzr.corrector import ResultCorrector

class TestResultCorrector(unittest.TestCase):
    def setUp(self):
        self.corrector = ResultCorrector(Path('dummy_path'))

    def test_phnameChange(self):
        dict_in = {
            'name_pairs': [('PhaseA', 'PhaseB'), ('PhaseC', 'PhaseD')],
            'CQT_tS_TC_NEAT_npms': {
                'PhaseA': [1, 2, 3],
                'PhaseC': [4, 5, 6],
                'PhaseE': [7, 8, 9]
            }
        }

        result = self.corrector.phnameChange(dict_in)

        # 1. Original dictionary is not modified
        self.assertIn('PhaseA', dict_in['CQT_tS_TC_NEAT_npms'])
        self.assertIn('PhaseC', dict_in['CQT_tS_TC_NEAT_npms'])
        self.assertNotIn('nameChanged_CQT_tS_TC_NEAT_npms', dict_in)

        # 2. Result dictionary has new keys mapped correctly
        new_dict = result['nameChanged_CQT_tS_TC_NEAT_npms']
        self.assertNotIn('PhaseA', new_dict)
        self.assertIn('PhaseB', new_dict)
        self.assertNotIn('PhaseC', new_dict)
        self.assertIn('PhaseD', new_dict)
        self.assertIn('PhaseE', new_dict)

        # 3. Basic values are preserved
        self.assertEqual(new_dict['PhaseB'], [1, 2, 3])
        self.assertEqual(new_dict['PhaseD'], [4, 5, 6])
        self.assertEqual(new_dict['PhaseE'], [7, 8, 9])

    def test_phnameChange_existing_target(self):
        dict_in = {
            'name_pairs': [('PhaseA', 'PhaseB')],
            'CQT_tS_TC_NEAT_npms': {
                'PhaseA': np.array([1, 2, 3]),
                'PhaseB': np.array([4, 5, 6])
            }
        }

        result = self.corrector.phnameChange(dict_in)

        new_dict = result['nameChanged_CQT_tS_TC_NEAT_npms']
        self.assertNotIn('PhaseA', new_dict)
        self.assertIn('PhaseB', new_dict)

        # 4. Values are summed if target exists
        np.testing.assert_array_equal(new_dict['PhaseB'], np.array([5, 7, 9]))

    def test_phnameChange_missing_source(self):
        dict_in = {
            'name_pairs': [('PhaseA', 'PhaseB'), ('MissingPhase', 'AnotherPhase')],
            'CQT_tS_TC_NEAT_npms': {
                'PhaseA': [1, 2, 3]
            }
        }

        result = self.corrector.phnameChange(dict_in)

        new_dict = result['nameChanged_CQT_tS_TC_NEAT_npms']
        self.assertNotIn('PhaseA', new_dict)
        self.assertIn('PhaseB', new_dict)

        # 5. Missing sources in name_pairs are ignored gracefully
        self.assertNotIn('MissingPhase', new_dict)
        self.assertNotIn('AnotherPhase', new_dict)

        self.assertEqual(new_dict['PhaseB'], [1, 2, 3])

    def test_correct_phase_indices_missing_keys(self):
        dict_in = {}
        result = self.corrector.correct_phase_indices(dict_in)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
