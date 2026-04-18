import json
import dataclasses
import numpy as np
from pathlib import Path

class DataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {
                "__ndarray__": True,
                "data": obj.tolist(),
                "dtype": str(obj.dtype),
                "shape": obj.shape
            }
        if isinstance(obj, np.integer):
            return {"__npint__": True, "data": int(obj), "dtype": str(obj.dtype)}
        if isinstance(obj, np.floating):
            return {"__npfloat__": True, "data": float(obj), "dtype": str(obj.dtype)}
        if isinstance(obj, set):
            return {"__set__": True, "data": list(obj)}
        if dataclasses.is_dataclass(obj):
            return {"__dataclass__": obj.__class__.__name__, "data": dataclasses.asdict(obj)}
        return super().default(obj)

def data_decoder(dct):
    if "__ndarray__" in dct:
        # We need to reshape when it's just a 1D list from tolist() but originally a multi-dimensional array
        # actually, tolist() preserves nested structure, so we just pass it to np.array
        # which handles multi-dimensional arrays naturally
        return np.array(dct["data"], dtype=dct["dtype"])
    if "__npint__" in dct:
        return np.dtype(dct["dtype"]).type(dct["data"])
    if "__npfloat__" in dct:
        return np.dtype(dct["dtype"]).type(dct["data"])
    if "__set__" in dct:
        return set(dct["data"])
    if "__int_dict__" in dct:
        # We need a way to preserve dict int keys.
        # Standard json converts dict keys to strings.
        pass

    # Notice: we don't handle dataclass decoding here automatically as we don't have the class refs,
    # and they are usually passed around. However, in our code, the `tc_setting` is attached.
    # It might be easier to rebuild it when we need it, or pass the class reference.
    # Let's import config to have access to dataclasses if needed.
    if "__dataclass__" in dct:
        import dictra_analyzr.config as cfg
        cls_name = dct["__dataclass__"]
        if hasattr(cfg, cls_name):
            cls = getattr(cfg, cls_name)
            return cls(**dct["data"])

    return dct

def _encode_dict_keys(obj):
    """Recursively converts dict keys to string if they are integers or tuples, keeping track of them."""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, (int, np.integer)):
                new_dict[f"__int_key_{int(k)}"] = _encode_dict_keys(v)
            elif isinstance(k, tuple):
                new_dict[f"__tuple_key_{json.dumps(k)}"] = _encode_dict_keys(v)
            else:
                new_dict[k] = _encode_dict_keys(v)
        return new_dict
    elif isinstance(obj, list):
        return [_encode_dict_keys(v) for v in obj]
    elif isinstance(obj, tuple):
        # JSON standard converts tuples to lists, we must track tuples
        return {"__tuple__": True, "data": [_encode_dict_keys(v) for v in obj]}
    elif dataclasses.is_dataclass(obj):
        # Recurse into dataclasses to ensure inner dicts are also encoded
        return dataclasses.replace(obj, **{f.name: _encode_dict_keys(getattr(obj, f.name)) for f in dataclasses.fields(obj)})
    return obj

def _decode_dict_keys(obj):
    """Recursively restores dict keys to integer or tuple if they start with tracking prefixes."""
    if isinstance(obj, dict):
        if "__tuple__" in obj:
            return tuple(_decode_dict_keys(v) for v in obj["data"])

        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.startswith("__int_key_"):
                new_dict[int(k[10:])] = _decode_dict_keys(v)
            elif isinstance(k, str) and k.startswith("__tuple_key_"):
                tup_list = json.loads(k[12:])
                new_dict[tuple(tup_list)] = _decode_dict_keys(v)
            else:
                new_dict[k] = _decode_dict_keys(v)
        return new_dict
    elif isinstance(obj, list):
        return [_decode_dict_keys(v) for v in obj]
    return obj

def save_data(data, filepath):
    with open(filepath, 'w') as f:
        # Encode dict keys to preserve integers before json dumping
        encoded_data = _encode_dict_keys(data)
        json.dump(encoded_data, f, cls=DataEncoder)

def load_data(filepath):
    with open(filepath, 'r') as f:
        loaded = json.load(f, object_hook=data_decoder)
        # Decode dict keys back to integers after json loading
        return _decode_dict_keys(loaded)
