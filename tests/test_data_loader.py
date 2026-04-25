import sys
if 'numpy' in sys.modules and type(sys.modules['numpy']).__name__ == 'MagicMock':
    del sys.modules['numpy']
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock tc_python because it is a proprietary SDK unavailable in this environment
if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()
# Prevent numpy mock conflicts from test_corrector
if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
    del sys.modules['numpy']

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    if 'numpy' not in sys.modules:
        sys.modules['numpy'] = MagicMock()
    np = sys.modules['numpy']
    HAVE_NUMPY = False

from dictra_analyzr.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader("dummy_path")

    @unittest.skipIf(not HAVE_NUMPY, "Requires real numpy")
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

    @unittest.skipIf(not HAVE_NUMPY, "Requires real numpy")
    def test_categorize_elements_mixed(self):
        """Test _categorize_elements with a mix of AC and substitutionals."""
        elnames = np.array(['FE', 'AC1', 'CR', 'AC2'])
        acs, subs = self.loader._categorize_elements(elnames)

        # ACs: ['AC1', 'AC2'] at indices [1, 3]
        np.testing.assert_array_equal(acs[0], np.array(['AC1', 'AC2']))
        self.assertEqual(acs[1], [1, 3])

        # Substitutionals: ['FE', 'CR'] at indices [0, 2]
        np.testing.assert_array_equal(subs[0], np.array(['FE', 'CR']))
        self.assertEqual(subs[1], [0, 2])

    @unittest.skipIf(not HAVE_NUMPY, "Requires real numpy")
    def test_categorize_elements_only_sub(self):
        """Test _categorize_elements with only substitutional elements."""
        elnames = np.array(['FE', 'CR', 'NI'])
        acs, subs = self.loader._categorize_elements(elnames)

        # ACs: empty
        np.testing.assert_array_equal(acs[0], np.array([]))
        self.assertEqual(acs[1], [])

        # Substitutionals: ['FE', 'CR', 'NI'] at indices [0, 1, 2]
        np.testing.assert_array_equal(subs[0], np.array(['FE', 'CR', 'NI']))
        self.assertEqual(subs[1], [0, 1, 2])

    @unittest.skipIf(not HAVE_NUMPY, "Requires real numpy")
    def test_categorize_elements_only_ac(self):
        """Test _categorize_elements with only AC elements."""
        elnames = np.array(['AC_AL', 'AC_NI'])
        acs, subs = self.loader._categorize_elements(elnames)

        # ACs: ['AC_AL', 'AC_NI'] at indices [0, 1]
        np.testing.assert_array_equal(acs[0], np.array(['AC_AL', 'AC_NI']))
        self.assertEqual(acs[1], [0, 1])

        # Substitutionals: empty
        np.testing.assert_array_equal(subs[0], np.array([]))
        self.assertEqual(subs[1], [])

    @unittest.skipIf(not HAVE_NUMPY, "Requires real numpy")
    def test_categorize_elements_empty(self):
        """Test _categorize_elements with an empty element array."""
        elnames = np.array([])
        acs, subs = self.loader._categorize_elements(elnames)

        # ACs: empty
        np.testing.assert_array_equal(acs[0], np.array([]))
        self.assertEqual(acs[1], [])

        # Substitutionals: empty
        np.testing.assert_array_equal(subs[0], np.array([]))
        self.assertEqual(subs[1], [])

    @patch('builtins.print')
    def test_get_values_from_textfiles_error_path(self, mock_print):
        """Test that get_values_from_textfiles correctly catches and re-raises exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create an unreadable file to specifically trigger a read error in np.loadtxt
            test_file = path / 'MOLE_FRACTIONS.TXT'
            test_file.touch()
            # Set permissions so the file is unreadable
            test_file.chmod(0o000)

            if isinstance(np, MagicMock):
                # If numpy is mocked, we need to make the mock raise an exception
                with patch('numpy.loadtxt', side_effect=Exception("Mocked read error")):
                    with self.assertRaises(Exception):
                        self.loader.get_values_from_textfiles(path)

                    called_args = mock_print.call_args[0][0]
                    self.assertTrue(called_args.startswith(f"Error reading text files in {path}:"))
            else:
                with self.assertRaises(Exception):
                    self.loader.get_values_from_textfiles(path)

                called_args = mock_print.call_args[0][0]
                self.assertTrue(called_args.startswith(f"Error reading text files in {path}:"))

            # Reset permissions so tempfile can cleanup
            test_file.chmod(0o666)

if __name__ == '__main__':
    unittest.main()
