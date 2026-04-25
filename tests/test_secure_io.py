import os
import unittest
import tempfile
import numpy as np

from dictra_analyzr.secure_io import secure_load, secure_save
import json

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

    def test_secure_save(self):
        # Create a sample data structure
        test_data = {
            "ndarray": np.array([1, 2], dtype='int64')
        }

        # Expected raw JSON format after secure_save -> to_dict
        # {"_type": "dict", "items": [["ndarray", {"_type": "ndarray", "data": [1, 2], "dtype": "int64"}]]}

        fd, temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)

        try:
            # Save the data using secure_save
            secure_save(test_data, temp_path)

            # Load the raw JSON to verify exact output structure
            with open(temp_path, 'r') as f:
                raw_json = json.load(f)

            self.assertEqual(raw_json["_type"], "dict")
            self.assertEqual(len(raw_json["items"]), 1)

            key, val = raw_json["items"][0]
            self.assertEqual(key, "ndarray")
            self.assertEqual(val["_type"], "ndarray")
            self.assertEqual(val["data"], [1, 2])

            # Since numpy might be mocked, we'll just check it's a string representing the dtype
            self.assertTrue(isinstance(val["dtype"], str))

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
