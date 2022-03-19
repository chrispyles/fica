"""Testing utilities"""

import numpy as np


def assert_object_attrs(obj, attrs):
    """
    """
    for k, v in attrs.items():
        if k.endswith("__len"):
            assert len(getattr(obj, k[:-5])) == v, \
                f"Attr '{k}' length is wrong: expected {v} but got {len(getattr(obj, k[:-5]))}"
        else:
            attr = getattr(obj, k)
            if isinstance(attr, (np.ndarray, float, np.generic, int)):
                is_eq = np.allclose(attr, v)
            else:
                is_eq = attr == v
            if isinstance(is_eq, np.ndarray):
                assert is_eq.all(), f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"
            else:
                assert is_eq, f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"
