import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path

# Mock tc_python because it is a proprietary SDK unavailable in this environment
sys.modules['tc_python'] = MagicMock()

from dictra_analyzr.calculator import ThermodynamicCalculator

class TestThermodynamicCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = ThermodynamicCalculator(Path("dummy_path"))

    def test_tccalc_missing_key(self):
        """Test that missing keys in the input dictionary are caught and the dictionary is returned unmodified."""
        input_dict = {}

        # tccalc catches KeyError and returns the dict
        result = self.calculator.tccalc(input_dict)

        # Assert that the dictionary returned is the same as the input dictionary
        self.assertEqual(result, input_dict)

if __name__ == '__main__':
    unittest.main()
