import sys
import unittest
from unittest.mock import MagicMock

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()

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

    def test_get_timestamp_invalid_timeflag(self):
        """Test that get_timestamp falls back to the last element when given an invalid timeflag."""
        times = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        timeflag = "invalid"

        tS, nearestTime = self.loader.get_timestamp(times, timeflag)

        self.assertEqual(tS, 4)
        self.assertEqual(nearestTime, 4.0)

if __name__ == '__main__':
    unittest.main()
