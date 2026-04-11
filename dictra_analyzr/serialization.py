import json
import numpy as np
from dataclasses import is_dataclass, asdict
from .config import TCSetting

class SecureEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return {"__dataclass__": type(obj).__name__, "data": asdict(obj)}
        if isinstance(obj, np.ndarray):
            return {"__ndarray__": obj.tolist(), "dtype": str(obj.dtype), "shape": obj.shape}
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(SecureEncoder, self).default(obj)

def json_obj_hook(dct):
    if "__ndarray__" in dct:
        return np.array(dct["__ndarray__"], dtype=dct["dtype"])
    if "__dataclass__" in dct:
        class_name = dct["__dataclass__"]
        if class_name == "TCSetting":
            return TCSetting(**dct["data"])
    return dct

def save_data(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, cls=SecureEncoder)

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f, object_hook=json_obj_hook)
