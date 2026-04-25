import unittest
import sys
from unittest.mock import MagicMock

try:
    import numpy as np
except ImportError:
    np = MagicMock()
    if 'numpy' not in sys.modules:
        sys.modules['numpy'] = np
    # Add fake types for np.integer and np.floating so isinstance checks pass if needed
    np.integer = type('NpIntegerType', (int,), {})
    np.floating = type('NpFloatingType', (float,), {})

from dictra_analyzr.serializer import _encode_dict_keys, data_decoder
from dictra_analyzr.config import TCSetting

class TestSerializer(unittest.TestCase):
    def test_encode_dict_keys_nested_structure(self):
        """Test encoding nested structures including dicts with int keys, lists, and tuples."""
        obj = {1: (2, [3, {4: 5}])}
        encoded = _encode_dict_keys(obj)
        expected = {'__int_key_1': {'__tuple__': True, 'data': [2, [3, {'__int_key_4': 5}]]}}
        self.assertEqual(encoded, expected)

    def test_data_decoder_ndarray(self):
        dct = {"__ndarray__": True, "data": [[1, 2], [3, 4]], "dtype": "int64"}
        result = data_decoder(dct)
        # If numpy is mocked, np.array will return a mock object.
        # We can check that np.array was called correctly if it's a mock.
        if isinstance(np, MagicMock):
            np.array.assert_called_with([[1, 2], [3, 4]], dtype="int64")
        else:
            np.testing.assert_array_equal(result, np.array([[1, 2], [3, 4]], dtype=np.int64))

    def test_data_decoder_npint(self):
        dct = {"__npint__": True, "data": 42, "dtype": "int64"}
        result = data_decoder(dct)
        if isinstance(np, MagicMock):
            np.dtype.assert_called_with("int64")
        else:
            self.assertEqual(result, np.int64(42))
            self.assertTrue(isinstance(result, np.integer))

    def test_data_decoder_npfloat(self):
        dct = {"__npfloat__": True, "data": 3.14, "dtype": "float64"}
        result = data_decoder(dct)
        if isinstance(np, MagicMock):
            np.dtype.assert_called_with("float64")
        else:
            self.assertEqual(result, np.float64(3.14))
            self.assertTrue(isinstance(result, np.floating))

    def test_data_decoder_set(self):
        dct = {"__set__": True, "data": [1, 2, 3]}
        result = data_decoder(dct)
        self.assertEqual(result, {1, 2, 3})

    def test_data_decoder_dataclass(self):
        dct = {
            "__dataclass__": "TCSetting",
            "data": {
                "database": ["TCFE9"],
                "acRefs": [],
                "phsToSus": [],
                "p3flag": False,
                "mobFlag": False
            }
        }
        result = data_decoder(dct)
        self.assertTrue(isinstance(result, TCSetting))
        self.assertEqual(result.database, ["TCFE9"])
        self.assertEqual(result.p3flag, False)

    def test_data_decoder_default(self):
        dct = {"some_key": "some_value"}
        result = data_decoder(dct)
        self.assertEqual(result, dct)

if __name__ == '__main__':
    unittest.main()
