import sys
import unittest.mock

class DummyNDArray:
    def __init__(self, lst, dtype_str):
        self._lst = lst
        self.dtype = dtype_str
        self.shape = (len(lst),)
    def tolist(self):
        return self._lst
    def reshape(self, shape):
        self.shape = shape
        return self

class DummyGeneric:
    def __init__(self, val):
        self._val = val
    def item(self):
        return self._val

def dummy_array(lst, dtype=None):
    return DummyNDArray(lst, str(dtype) if dtype else "float64")

np_mock = unittest.mock.MagicMock()
np_mock.ndarray = DummyNDArray
np_mock.generic = DummyGeneric
np_mock.array = dummy_array
sys.modules['numpy'] = np_mock

import unittest
import numpy as np
import io
import os
from dictra_analyzr.safe_io import safe_dump, safe_load
from dictra_analyzr.config import TCSetting

class TestSafeIO(unittest.TestCase):
    def test_numpy_array_serialization(self):
        arr = DummyNDArray([1, 2, 3], "int32")
        data = {"arr": arr}
        f = io.StringIO()
        safe_dump(data, f)

        f.seek(0)
        loaded_data = safe_load(f)

        self.assertIn("arr", loaded_data)
        # Because we mocked numpy and the hook recreates using np.array() which maps to DummyNDArray
        self.assertEqual(loaded_data["arr"].tolist(), [1, 2, 3])
        self.assertEqual(loaded_data["arr"].dtype, "int32")

    def test_numpy_generic_serialization(self):
        class float64(DummyGeneric): pass
        val = float64(42.5)
        data = {"val": val}
        f = io.StringIO()
        safe_dump(data, f)

        f.seek(0)
        loaded_data = safe_load(f)

        self.assertIn("val", loaded_data)
        self.assertEqual(loaded_data["val"], 42.5)

    def test_dataclass_serialization(self):
        tc = TCSetting(database=["DB1"], acRefs=[], phsToSus=[], p3flag=True, mobFlag=False)
        data = {"tc_setting": tc}

        f = io.StringIO()
        safe_dump(data, f)

        f.seek(0)
        loaded_data = safe_load(f)

        self.assertIn("tc_setting", loaded_data)
        loaded_tc = loaded_data["tc_setting"]
        self.assertIsInstance(loaded_tc, TCSetting)
        self.assertEqual(loaded_tc.database, ["DB1"])
        self.assertEqual(loaded_tc.p3flag, True)

    def test_int_keys_restoration(self):
        data = {"tS_TC_phnames": {0: ["BCC_A2"], 1: ["FCC_A1"]}}

        f = io.StringIO()
        safe_dump(data, f)

        f.seek(0)
        loaded_data = safe_load(f)

        self.assertIn("tS_TC_phnames", loaded_data)
        self.assertIn(0, loaded_data["tS_TC_phnames"])
        self.assertEqual(loaded_data["tS_TC_phnames"][0], ["BCC_A2"])

if __name__ == '__main__':
    unittest.main()
