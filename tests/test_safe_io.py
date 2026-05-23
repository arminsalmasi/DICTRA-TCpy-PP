import unittest
import os
import tempfile
import json
from unittest.mock import patch

from dictra_analyzr.safe_io import load_data

class TestSafeIO(unittest.TestCase):
    def test_load_data_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_data("non_existent_file_path_12345.json")

    def test_load_data_json_decode_error(self):
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write("invalid json string")

            with self.assertRaises(json.JSONDecodeError):
                load_data(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_data_permission_error(self):
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                load_data("some_file.json")

if __name__ == '__main__':
    unittest.main()
