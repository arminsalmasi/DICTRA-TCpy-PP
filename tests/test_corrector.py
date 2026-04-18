import unittest
import sys
from unittest.mock import MagicMock
from pathlib import Path

# Mock numpy before importing dictra_analyzr
try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()

from dictra_analyzr.corrector import ResultCorrector

class MockArray:
    def __init__(self, vals):
        self.vals = vals
    def __add__(self, other):
        return MockArray([a + b for a, b in zip(self.vals, other.vals)])
    def __eq__(self, other):
        return self.vals == other.vals

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
                'PhaseA': MockArray([1, 2, 3]),
                'PhaseB': MockArray([4, 5, 6])
            }
        }

        result = self.corrector.phnameChange(dict_in)

        new_dict = result['nameChanged_CQT_tS_TC_NEAT_npms']
        self.assertNotIn('PhaseA', new_dict)
        self.assertIn('PhaseB', new_dict)

        # 4. Values are summed if target exists
        self.assertEqual(new_dict['PhaseB'].vals, [5, 7, 9])

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

if __name__ == '__main__':
    unittest.main()
