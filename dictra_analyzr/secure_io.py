import json
import numpy as np

def to_dict(obj):
    if isinstance(obj, dict):
        return {"_type": "dict", "items": [[to_dict(k), to_dict(v)] for k, v in obj.items()]}
    elif isinstance(obj, list):
        return [to_dict(v) for v in obj]
    elif isinstance(obj, tuple):
        return {"_type": "tuple", "items": [to_dict(v) for v in obj]}
    elif isinstance(obj, np.ndarray):
        return {"_type": "ndarray", "data": obj.tolist(), "dtype": str(obj.dtype)}
    elif isinstance(obj, np.generic):
        return {"_type": "npscalar", "data": obj.item(), "dtype": str(obj.dtype)}
    else:
        return obj

def from_dict(obj):
    if isinstance(obj, dict):
        if "_type" in obj:
            if obj["_type"] == "dict":
                return {from_dict(k): from_dict(v) for k, v in obj["items"]}
            elif obj["_type"] == "tuple":
                return tuple(from_dict(v) for v in obj["items"])
            elif obj["_type"] == "ndarray":
                return np.array(obj["data"], dtype=obj["dtype"])
            elif obj["_type"] == "npscalar":
                return np.dtype(obj["dtype"]).type(obj["data"])
        return {k: from_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [from_dict(v) for v in obj]
    else:
        return obj

def secure_save(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(to_dict(data), f)

def secure_load(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return from_dict(data)
