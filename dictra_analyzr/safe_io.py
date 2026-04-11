import json
import numpy as np
from dataclasses import is_dataclass
from .config import TCSetting

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        # We handle Mock objects for test environment (no numpy) gracefully
        if hasattr(obj, 'tolist') and hasattr(obj, 'dtype') and hasattr(obj, 'shape'):
            # Duck-typing numpy array
            return {
                "__ndarray__": obj.tolist(),
                "dtype": str(obj.dtype),
                "shape": obj.shape
            }
        elif type(obj).__name__ in ('float64', 'int64', 'int32', 'float32', 'bool_') and hasattr(obj, 'item'):
            # Duck-typing numpy generic scalar
            return obj.item()

        try:
            if isinstance(obj, np.ndarray):
                return {
                    "__ndarray__": obj.tolist(),
                    "dtype": str(obj.dtype),
                    "shape": obj.shape
                }
            if isinstance(obj, np.generic):
                return obj.item()
        except TypeError:
            pass # Ignore if np is a mock causing TypeError

        if is_dataclass(obj):
            return {
                "__dataclass__": obj.__class__.__name__,
                "data": obj.__dict__
            }
        return super().default(obj)

def safe_object_hook(dct):
    if "__ndarray__" in dct:
        return np.array(dct["__ndarray__"], dtype=dct["dtype"]).reshape(dct["shape"])
    if "__dataclass__" in dct:
        cls_name = dct["__dataclass__"]
        if cls_name == "TCSetting":
            return TCSetting(**dct["data"])
    # Handle int keys for dictionary which get turned into strings by JSON
    # dictra_analyzr uses int points as keys like '0', '1', etc? Actually it uses f'{pt}, {ph}' or pt.
    # In TC dict 'tS_TC_phnames': tc_phnames[pt] = stablePhs. Here pt is int!
    # JSON converts int keys to strings.
    # We should probably convert keys back to int if they represent integers?
    # Actually it's safer to leave keys as strings if not explicitly requested,
    # but the codebase might expect int keys for 'tS_TC_phnames'.
    # Let's handle it later if needed or try to be generic.
    return dct

def safe_dump(obj, f):
    json.dump(obj, f, cls=SafeEncoder)

def safe_load(f):
    data = json.load(f, object_hook=safe_object_hook)

    # Restore integer keys for specific dictionaries if they exist
    # dictra_analyzr calculator.py uses int keys for tS_TC_phnames: tc_phnames[pt] = stablePhs
    if 'tS_TC_phnames' in data and isinstance(data['tS_TC_phnames'], dict):
        new_phnames = {}
        for k, v in data['tS_TC_phnames'].items():
            try:
                new_phnames[int(k)] = v
            except ValueError:
                new_phnames[k] = v
        data['tS_TC_phnames'] = new_phnames

    return data
