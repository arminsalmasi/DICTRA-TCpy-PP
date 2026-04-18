import unittest
from dictra_analyzr.serializer import _encode_dict_keys

class TestSerializer(unittest.TestCase):
    def test_encode_dict_keys_nested_structure(self):
        """Test encoding nested structures including dicts with int keys, lists, and tuples."""
        obj = {1: (2, [3, {4: 5}])}
        encoded = _encode_dict_keys(obj)
        expected = {'__int_key_1': {'__tuple__': True, 'data': [2, [3, {'__int_key_4': 5}]]}}
        self.assertEqual(encoded, expected)

if __name__ == '__main__':
    unittest.main()
