import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

# Mock numpy and tc_python if missing in test environment
try:
    import numpy as np
except ImportError:
    if 'numpy' not in sys.modules:
        mock_np = MagicMock()
        mock_np.ndarray = type('ndarray', (), {})
        mock_np.integer = type('integer', (), {})
        mock_np.floating = type('floating', (), {})
        sys.modules['numpy'] = mock_np
        np = mock_np

if 'tc_python' not in sys.modules:
    sys.modules['tc_python'] = MagicMock()

from dictra_analyzr.serializer import _encode_dict_keys, save_data, load_data

class TestSerializer(unittest.TestCase):
    def test_encode_dict_keys_nested_structure(self):
        """Test encoding nested structures including dicts with int keys, lists, and tuples."""
        obj = {1: (2, [3, {4: 5}])}
        encoded = _encode_dict_keys(obj)
        expected = {'__int_key_1': {'__tuple__': True, 'data': [2, [3, {'__int_key_4': 5}]]}}
        self.assertEqual(encoded, expected)

    def test_save_load_data(self):
        """Test that data is correctly saved and loaded, preserving types."""
        test_data = {
            1: (2, 3),
            "string_key": [4, 5, 6],
            (7, 8): {"nested": 9},
            "numpy_float": 10.5,
            "set_key": {11, 12}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_data.json")

            # Save data
            save_data(test_data, filepath)

            # Verify file exists
            self.assertTrue(os.path.exists(filepath))

            # Load data
            loaded_data = load_data(filepath)

            # Verify data matches (sets are converted back from list format)
            # Depending on numpy mock we may not get np.float/ndarray tests fully
            # here, but we verify standard python types and mock fallbacks
            self.assertEqual(test_data, loaded_data)

if __name__ == '__main__':
    unittest.main()
