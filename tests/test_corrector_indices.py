import unittest
import sys
from unittest.mock import MagicMock
from pathlib import Path
import numpy as np

# Mock numpy before importing dictra_analyzr

from dictra_analyzr.corrector import ResultCorrector

class TestResultCorrectorIndices(unittest.TestCase):
    def setUp(self):
        self.corrector = ResultCorrector(Path('dummy_path'))

    def test_correct_phase_indices(self):
        dict_in = {
            'tS_pts': [0, 1],
            'elnames': np.array(['Fe', 'Cr']),
            'tS_TC_NEAT_npms': {
                'BCC': np.array([1.0, 1.0])
            },
            'tS_TC_NEAT_phXs': {
                'BCC': np.array([
                    [0.8, 0.2], # point 0
                    [0.2, 0.8]  # point 1
                ])
            },
            'tS_TC_NEAT_phnames': ['BCC'],
            'phase_changes': [
                ('BCC', 'Cr', 0.5) # Splitting BCC when Cr > 0.5
            ]
        }

        result = self.corrector.correct_phase_indices(dict_in)

        self.assertIn('CQT_tS_TC_NEAT_npms', result)
        npms = result['CQT_tS_TC_NEAT_npms']

        # Original BCC should have zero at point 1 (since it was moved to new phase)
        self.assertIn('BCC', npms)
        self.assertEqual(npms['BCC'][0], 1.0)
        self.assertEqual(npms['BCC'][1], 0.0)

        # New phase BCC-CrFe or BCC-FeCr?
        # Cr = 0.8, Fe = 0.2, sorted: Cr, Fe
        # cutoff > 0 and < 1: phase_to_change + '-' + "".join(sorted_elnames[:2]) -> 'BCC-CrFe'
        self.assertIn('BCC-CrFe', npms)
        self.assertEqual(npms['BCC-CrFe'][0], 0.0)
        self.assertEqual(npms['BCC-CrFe'][1], 1.0)

    def test_correct_phase_indices_cutoff_1(self):
        dict_in = {
            'tS_pts': [0, 1, 2],
            'elnames': np.array(['Fe', 'Cr', 'Ni']),
            'tS_TC_NEAT_npms': {
                'FCC': np.array([1.0, 1.0, 1.0])
            },
            'tS_TC_NEAT_phXs': {
                'FCC': np.array([
                    [0.7, 0.2, 0.1], # Fe major
                    [0.2, 0.7, 0.1], # Cr major
                    [0.1, 0.1, 0.8]  # Ni major
                ])
            },
            'tS_TC_NEAT_phnames': ['FCC'],
            'phase_changes': [
                ('FCC', 'Cr', 1) # Splitting FCC when Cr is largest
            ]
        }

        result = self.corrector.correct_phase_indices(dict_in)

        npms = result['CQT_tS_TC_NEAT_npms']

        self.assertIn('FCC', npms)
        self.assertEqual(npms['FCC'][0], 1.0)
        self.assertEqual(npms['FCC'][1], 0.0)
        self.assertEqual(npms['FCC'][2], 1.0)

        # cutoff == 1 uses top 1 element
        self.assertIn('FCC-Cr', npms)
        self.assertEqual(npms['FCC-Cr'][0], 0.0)
        self.assertEqual(npms['FCC-Cr'][1], 1.0)
        self.assertEqual(npms['FCC-Cr'][2], 0.0)

if __name__ == '__main__':
    unittest.main()
