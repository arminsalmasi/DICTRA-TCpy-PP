import os
import sys
import unittest
import tempfile
from unittest.mock import MagicMock

if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
    del sys.modules['numpy']

import numpy as np

from dictra_analyzr.secure_io import secure_load, secure_save

class TestSecureIO(unittest.TestCase):
    def test_secure_load_save(self):
        # Create a sample complex data structure
        test_data = {
            "integer": 42,
            "float": 3.14159,
            "string": "hello world",
            "list": [1, 2, 3, {"nested": "dict"}],
            "tuple": (4, 5, 6),
            "ndarray": np.array([[1.0, 2.0], [3.0, 4.0]]),
            "npscalar": np.float64(42.5),
        }

        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)

        try:
            # Save the data
            secure_save(test_data, temp_path)

            # Load the data
            loaded_data = secure_load(temp_path)

            # Assert basic types and dict structure
            self.assertEqual(loaded_data["integer"], test_data["integer"])
            self.assertEqual(loaded_data["float"], test_data["float"])
            self.assertEqual(loaded_data["string"], test_data["string"])
            self.assertEqual(loaded_data["list"], test_data["list"])
            self.assertEqual(loaded_data["tuple"], test_data["tuple"])

            # Assert numpy array
            np.testing.assert_array_equal(loaded_data["ndarray"], test_data["ndarray"])
            self.assertEqual(loaded_data["ndarray"].dtype, test_data["ndarray"].dtype)

            # Assert numpy scalar
            self.assertEqual(loaded_data["npscalar"], test_data["npscalar"])
            self.assertEqual(type(loaded_data["npscalar"]), type(test_data["npscalar"]))

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_secure_load_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            secure_load("non_existent_file_path_12345.json")

if __name__ == '__main__':
    unittest.main()
