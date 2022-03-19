"""Tests for ``fica.key``"""

import pytest

from fica import EMPTY, Key, SUBKEYS

from .utils import assert_object_attrs


class TestKey:
    """
    Tests for ``fica.key.Key``.
    """

    def test_constructor(self):
        """
        """
        default_attrs = {
            "description": None,
            "default": EMPTY,
            "subkeys": None,
            "type_": None,
            "allow_none": False,
        }

        name = "foo"
        key = Key(name)
        assert_object_attrs(key, {**default_attrs, "name": name})
