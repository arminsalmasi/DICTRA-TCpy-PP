import sys
import unittest
from unittest.mock import MagicMock

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()
# Prevent numpy mock conflicts from test_corrector
if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
    del sys.modules['numpy']

import numpy as np
from dictra_analyzr.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader("dummy_path")

    def test_calculate_u_fractions_zero_division_protection(self):
        """Test that division by zero is avoided when calculating u-fractions.
        Verifies behavior with actual numpy evaluation."""

        # We supply an array where the sum of indices 0 and 1 for the second row is 0.0
        mf = np.array([
            [1.0, 1.0, 0.5], # sum of idx [0, 1] is 2.0
            [0.0, 0.0, 0.5], # sum of idx [0, 1] is 0.0 -> protected to 1.0
            [2.0, 0.0, 1.0]  # sum of idx [0, 1] is 2.0
        ])
        sub_idx = [0, 1]
        elnames = ['Element1', 'Element2', 'Element3']

        result = self.loader.calculate_u_fractions(mf, sub_idx, elnames)

        # Expected calculations:
        # row 0 sum: 2.0 -> fractions: [1.0/2.0, 1.0/2.0, 0.5/2.0] = [0.5, 0.5, 0.25]
        # row 1 sum: 0.0 -> protected to 1.0 -> fractions: [0.0/1.0, 0.0/1.0, 0.5/1.0] = [0.0, 0.0, 0.5]
        # row 2 sum: 2.0 -> fractions: [2.0/2.0, 0.0/2.0, 1.0/2.0] = [1.0, 0.0, 0.5]

        # result is formatted as columns per element, so we verify by row-columns:
        # Element 1: [0.5, 0.0, 1.0]
        # Element 2: [0.5, 0.0, 0.0]
        # Element 3: [0.25, 0.5, 0.5]

        expected_element1 = np.array([0.5, 0.0, 1.0])
        expected_element2 = np.array([0.5, 0.0, 0.0])
        expected_element3 = np.array([0.25, 0.5, 0.5])

        np.testing.assert_allclose(result[0], expected_element1)
        np.testing.assert_allclose(result[1], expected_element2)
        np.testing.assert_allclose(result[2], expected_element3)

    def test_get_tS_VLUs_out_of_bounds_tS(self):
        """Test get_tS_VLUs handles out-of-bounds tS values (tS=0 and large tS)."""
        dict_input = {
            'n_pts': np.array([2, 3]), # 2 timesteps: 1st has 2 pts, 2nd has 3 pts (total 5 pts)
            'all_pts': np.array([0.1, 0.2, 0.1, 0.2, 0.3]),
            'DICT_phnames': np.array(['FCC_A1', 'BCC_A2']),
            'DICT_all_npms': np.zeros((5 * 2)), # 5 pts * 2 phases = 10 elements
            'elnames': np.array(['FE', 'NI']),
            'all_mfs': np.zeros((5 * 2)), # 5 pts * 2 elements = 10 elements
            'DICT_all_mus': np.zeros((5 * 2)), # 5 pts * 2 elements = 10 elements
            'substitutionals': [np.array(['FE', 'NI']), [0, 1]], # List of elements, list of indices
            'times': np.array([0.0, 1.0])
        }

        # Test under-bound tS
        res_under = self.loader.get_tS_VLUs(dict_input, 0, 0.0)
        self.assertEqual(res_under['tS'], 1)

        # Test over-bound tS
        res_over = self.loader.get_tS_VLUs(dict_input, 999, 1.0)
        self.assertEqual(res_over['tS'], len(dict_input['n_pts']))

if __name__ == '__main__':
    unittest.main()
