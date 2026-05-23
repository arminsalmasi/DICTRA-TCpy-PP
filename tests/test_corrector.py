import unittest
import sys
from unittest.mock import MagicMock
if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
    del sys.modules['numpy']

from unittest.mock import MagicMock
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()

try:
    import numpy as np
except ImportError:
    sys.modules['numpy'] = MagicMock()
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

    def test_add_compSets_numbered_duplicates(self):
        dict_in = {
            'elnames': ['A', 'B'],
            'tS_TC_NEAT_phXs': {
                'PhaseA#1': np.array([[0.5, 0.5]]),
                'PhaseA#2': np.array([[0.4, 0.6]])
            },
            'CQT_tS_TC_NEAT_npms': {
                'PhaseA#1': np.array([1, 2, 3]),
                'PhaseA#2': np.array([4, 5, 6]),
                'PhaseA#3': np.array([1, 1, 1]),
                'PhaseB': np.array([0, 0, 0])
            }
        }
        result = self.corrector.add_compSets(dict_in)

        # 1. Original dictionary should remain untouched
        self.assertIn('PhaseA#2', dict_in['CQT_tS_TC_NEAT_npms'])

        # 2. Result dictionary should contain the correct merged sum
        new_dict = result['sum_CQT_tS_TC_NEAT_npms']
        self.assertIn('PhaseA#1', new_dict)
        self.assertNotIn('PhaseA#2', new_dict)
        self.assertNotIn('PhaseA#3', new_dict)
        self.assertIn('PhaseB', new_dict)

        np.testing.assert_array_equal(new_dict['PhaseA#1'], np.array([6, 8, 10]))
        np.testing.assert_array_equal(new_dict['PhaseB'], np.array([0, 0, 0]))

    def test_add_compSets_anagrams(self):
        dict_in = {
            'elnames': ['A', 'B', 'C'],
            'tS_TC_NEAT_phXs': {
                'ABC': np.array([[0.3, 0.3, 0.4]]),
                'CBA': np.array([[0.4, 0.3, 0.3]])
            },
            'CQT_tS_TC_NEAT_npms': {
                'ABC': np.array([1, 2, 3]),
                'CBA': np.array([4, 5, 6]),
                'BCA': np.array([1, 1, 1]),
                'DEF': np.array([2, 2, 2])
            }
        }
        result = self.corrector.add_compSets(dict_in)

        # Original shouldn't be touched
        self.assertIn('CBA', dict_in['CQT_tS_TC_NEAT_npms'])

        new_dict = result['sum_CQT_tS_TC_NEAT_npms']

        # We don't necessarily know which one comes first in standard dict,
        # but the logic preserves the first encountered anagram
        keys = list(new_dict.keys())
        self.assertEqual(len(keys), 2) # Only 2 unique groups (ABC group and DEF group)

        # Check that sum is correct for the ABC anagrams
        anagram_key = [k for k in keys if sorted(k) == sorted('ABC')][0]
        np.testing.assert_array_equal(new_dict[anagram_key], np.array([6, 8, 10]))

        self.assertIn('DEF', new_dict)
        np.testing.assert_array_equal(new_dict['DEF'], np.array([2, 2, 2]))

    def test_add_compSets_no_merge(self):
        dict_in = {
            'elnames': ['X', 'Y'],
            'tS_TC_NEAT_phXs': {
                'Phase1': np.array([[0.1, 0.9]]),
                'Phase2': np.array([[0.9, 0.1]])
            },
            'CQT_tS_TC_NEAT_npms': {
                'Phase1': np.array([1, 2]),
                'Phase2': np.array([3, 4]),
                'DifferentName': np.array([5, 6])
            }
        }
        result = self.corrector.add_compSets(dict_in)

        new_dict = result['sum_CQT_tS_TC_NEAT_npms']

        self.assertIn('Phase1', new_dict)
        self.assertIn('Phase2', new_dict)
        self.assertIn('DifferentName', new_dict)
        self.assertEqual(len(new_dict), 3)

if __name__ == '__main__':
    unittest.main()
