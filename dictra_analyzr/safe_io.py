import json

def _numpy_encoder(obj):
    import numpy as np
    if isinstance(obj, np.ndarray):
        return {
            "__ndarray__": obj.tolist(),
            "dtype": str(obj.dtype),
            "shape": obj.shape
        }
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, complex):
        return {"__complex__": True, "real": obj.real, "imag": obj.imag}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def _numpy_decoder(dct):
    if "__ndarray__" in dct:
        import numpy as np
        return np.array(dct["__ndarray__"], dtype=dct["dtype"]).reshape(dct["shape"])
    if "__complex__" in dct:
        return complex(dct["real"], dct["imag"])
    return dct

def save_data(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, default=_numpy_encoder)

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f, object_hook=_numpy_decoder)
