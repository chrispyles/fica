"""Tests for ``fica.key``"""

import pytest

from fica import EMPTY, Key, SUBKEYS

from .utils import assert_object_attrs


def test_singletons():
    """
    Tests for the singletons exported by ``fica.key``.
    """
    assert repr(EMPTY) == "fica.EMPTY"
    assert repr(SUBKEYS) == "fica.SUBKEYS"


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

        type_ = int
        key = Key(name, type_=type_)
        assert_object_attrs(key, {**default_attrs, "name": name, "type_": type_})

        type_ = int, float
        key = Key(name, type_=type_)
        assert_object_attrs(key, {**default_attrs, "name": name, "type_": type_})

        default = 1
        key = Key(name, default=default)
        assert_object_attrs(key, {**default_attrs, "name": name, "default": default})

        key = Key(name, default=default, allow_none=True)
        assert_object_attrs(key, {**default_attrs, "name": name, "default": default, "allow_none": True})

        descr = "bar"
        key = Key(name, description=descr)
        assert_object_attrs(key, {**default_attrs, "name": name, "description": descr})

        subkeys = [Key("bar")]
        key = Key(name, subkeys=subkeys)
        assert_object_attrs(key, {**default_attrs, "name": name, "subkeys": subkeys, "default": SUBKEYS})

        # test errors
        with pytest.raises(TypeError):
            Key(name, type_=[int])

        with pytest.raises(TypeError):
            Key(name, type_=int, default=1.3)

        with pytest.raises(TypeError):
            Key(name, default={"bar": 1})

        with pytest.raises(ValueError):
            Key(name, default=SUBKEYS)

    def test_from_dict(self):
        """
        """
        
