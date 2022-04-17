"""Testing utilities"""

import numpy as np

from typing import Any, List


# TODO: docstring, type annotations
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


class CustomIterable:
    """
    """

    def __init__(self, lst: List[Any]) -> None:
        self.lst = lst
        self.idx = -1

    def __iter__(self) -> "CustomIterable":
        return self

    def __next__(self) -> Any:
        self.idx += 1
        if self.idx >= len(self.lst):
            self.idx = -1
            raise StopIteration
        return self.lst[self.idx]
