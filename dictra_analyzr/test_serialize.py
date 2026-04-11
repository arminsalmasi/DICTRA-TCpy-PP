import numpy as np
import json

def encode_item(obj):
    if isinstance(obj, np.ndarray):
        return {"__type__": "ndarray", "data": obj.tolist(), "dtype": str(obj.dtype)}
    elif isinstance(obj, np.integer):
        return {"__type__": "npint", "data": int(obj), "dtype": str(obj.dtype)}
    elif isinstance(obj, np.floating):
        return {"__type__": "npfloat", "data": float(obj), "dtype": str(obj.dtype)}
    elif isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, int):
                new_dict[f"__int_key_{k}"] = encode_item(v)
            else:
                new_dict[k] = encode_item(v)
        return {"__type__": "dict", "data": new_dict}
    elif isinstance(obj, list):
        return [encode_item(v) for v in obj]
    elif isinstance(obj, tuple):
        return {"__type__": "tuple", "data": [encode_item(v) for v in obj]}
    else:
        return obj

def decode_item(obj):
    if isinstance(obj, dict) and "__type__" in obj:
        t = obj["__type__"]
        data = obj["data"]
        if t == "ndarray":
            return np.array(data, dtype=obj["dtype"])
        elif t == "npint":
            return np.dtype(obj["dtype"]).type(data)
        elif t == "npfloat":
            return np.dtype(obj["dtype"]).type(data)
        elif t == "tuple":
            return tuple(decode_item(v) for v in data)
        elif t == "dict":
            new_dict = {}
            for k, v in data.items():
                if k.startswith("__int_key_"):
                    new_dict[int(k[10:])] = decode_item(v)
                else:
                    new_dict[k] = decode_item(v)
            return new_dict
    elif isinstance(obj, dict):
        return {k: decode_item(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decode_item(v) for v in obj]
    else:
        return obj

# Test
d = {
    "test_int": 5,
    "test_arr": np.array([1, 2, 3], dtype=np.float32),
    "test_dict": {1: "a", 2: "b"},
    "test_tuple": (1, 2, np.array([4, 5])),
    "test_nested": [{"a": np.float64(5.5)}],
}

j = json.dumps(encode_item(d))
d2 = decode_item(json.loads(j))

assert isinstance(d2["test_arr"], np.ndarray)
assert d2["test_arr"].dtype == np.float32
assert d2["test_dict"][1] == "a"
assert isinstance(d2["test_tuple"], tuple)
assert d2["test_nested"][0]["a"] == 5.5

print("Test passed!")
