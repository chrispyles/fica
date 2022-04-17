"""Testing utilities"""

import numpy as np

from typing import Any, Dict, List


def assert_object_attrs(obj: Any, attrs: Dict[str, Any]) -> None:
    """
    Assert that an object has specific attributes.

    For each ``key`` in ``attrs``, checks that ``getattr(obj, key)`` is equal to ``attrs[key]``. If
    an attribute is sized, the length of the attribute can be checked by adding ``__len`` to the end
    of the key name (e.g. ``{"lst__len": 3}``).

    Args:
        obj (``object``): the object to check
        attrs (``dict[str, object]``): the expected attribute values

    Raises:
        ``AssertionError``: if one of the attributes does not have the correct value
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
    A custom iterable for lists.

    This class wraps a list and iterates over its elements. An instance may be used multiple times
    for iterating over the sample list as long as it is exhausted each time.

    Args:
        lst (``list[object]``): the list to iterative over
    """

    lst: List[Any]
    """the list being iterated over"""

    idx: int
    """the index of the last element yielded in the iteration"""

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
