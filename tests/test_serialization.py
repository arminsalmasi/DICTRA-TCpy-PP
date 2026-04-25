import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

# Provide standard mocks inside the test scope or cleanly if numpy missing
import builtins

try:
    import numpy as np
except ImportError:
    class DummyNdarray(list):
        def __init__(self, data, dtype="float64"):
            super().__init__(data)
            self.data = data
            self.dtype = dtype
            self.shape = (len(data),) if isinstance(data, list) else (1,)
        def tolist(self):
            return self.data

    class DummyInteger(int):
        def __new__(cls, value=0):
            return super().__new__(cls, value)

    class DummyFloating(float):
        def __new__(cls, value=0.0):
            return super().__new__(cls, value)

    class DummyBool:
        def __new__(cls, value=False):
            return True if value else False

    np = MagicMock()
    np.ndarray = DummyNdarray
    np.array = lambda data, dtype=None: DummyNdarray(data, dtype)
    np.integer = DummyInteger
    np.floating = DummyFloating
    np.bool_ = DummyBool

    sys.modules['numpy'] = np
from dictra_analyzr.serialization import save_data, load_data
from dictra_analyzr.config import TCSetting

class TestSerialization(unittest.TestCase):
    def test_save_and_load_data(self):
        # Create test data including basic types, numpy types, and dataclass
        tc_setting = TCSetting(
            database=["TCFE9"],
            acRefs=[],
            phsToSus=[],
            p3flag=False,
            mobFlag=True
        )

        test_data = {
            "integer": 42,
            "float": 3.14,
            "string": "test",
            "list": [1, 2, 3],
            "dict": {"a": 1, "b": 2},
            "bool": True,
            "numpy_int": np.integer(10),
            "numpy_float": np.floating(5.5),
            "numpy_bool": np.bool_(True),
            "numpy_array": np.array([1.0, 2.0, 3.0]),
            "tc_setting": tc_setting
        }

        fd, temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)

        try:
            # Save data
            save_data(test_data, temp_path)

            # Load data
            loaded_data = load_data(temp_path)

            # Assert basic types
            self.assertEqual(loaded_data["integer"], 42)
            self.assertEqual(loaded_data["float"], 3.14)
            self.assertEqual(loaded_data["string"], "test")
            self.assertEqual(loaded_data["list"], [1, 2, 3])
            self.assertEqual(loaded_data["dict"], {"a": 1, "b": 2})
            self.assertEqual(loaded_data["bool"], True)

            # Assert numpy scalar types (they get converted to built-in types during serialization)
            self.assertEqual(loaded_data["numpy_int"], 10)
            self.assertEqual(loaded_data["numpy_float"], 5.5)
            self.assertEqual(loaded_data["numpy_bool"], True)

            # Assert numpy array
            # If using DummyNdarray, type(loaded_data["numpy_array"]) will be the object itself,
            # or dict if not fully decoded, or DummyNdarray if json_obj_hook properly intercepted it.
            # wait, json_obj_hook calls np.array(...) which returns a DummyNdarray
            # Let's just check the data attribute or tolist() method.
            if hasattr(loaded_data["numpy_array"], 'tolist'):
                self.assertEqual(loaded_data["numpy_array"].tolist(), [1.0, 2.0, 3.0])
            else:
                self.assertEqual(loaded_data["numpy_array"], [1.0, 2.0, 3.0])

            # Assert dataclass
            self.assertTrue(isinstance(loaded_data["tc_setting"], TCSetting))
            self.assertEqual(loaded_data["tc_setting"].database, ["TCFE9"])
            self.assertEqual(loaded_data["tc_setting"].mobFlag, True)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
