import sys
import unittest
import tempfile
import os
import json

# Handle potential numpy mock pollution from other test files
if 'numpy' in sys.modules and type(sys.modules['numpy']).__name__ == 'MagicMock':
    class NpIntegerType(int): pass
    class NpFloatingType(float): pass
    sys.modules['numpy'].integer = NpIntegerType
    sys.modules['numpy'].floating = NpFloatingType

from dictra_analyzr.serializer import save_data, load_data

class TestSerializer(unittest.TestCase):
    def test_save_data(self):
        data = {"test": {1: "one", "two": 2}}
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as f:
            filepath = f.name

        try:
            save_data(data, filepath)
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, 'r') as f:
                loaded_raw = json.load(f)

            self.assertEqual(loaded_raw, {"test": {"__int_key_1": "one", "two": 2}})

            loaded = load_data(filepath)
            self.assertEqual(loaded, data)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
