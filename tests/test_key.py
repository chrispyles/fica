"""Tests for ``fica.key``"""

import pytest

from unittest import mock

from fica import EMPTY, Key, SUBKEYS
from fica.key import KeyValuePair

from .utils import assert_object_attrs


@pytest.fixture
def default_key_attrs():
    """
    A pytest fixture returning the default attribute values for a ``Key``.
    """
    return {
        "description": None,
        "default": EMPTY,
        "subkeys": None,
        "type_": None,
        "allow_none": False,
    }


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

    def test_constructor_and_getters(self, default_key_attrs):
        """
        Tests for the ``Key`` constructor and attribute getters.
        """
        name = "foo"
        key = Key(name)
        assert_object_attrs(key, {**default_key_attrs, "name": name})
        assert key.get_name() == name

        type_ = int
        key = Key(name, type_=type_)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "type_": type_})

        type_ = int, float
        key = Key(name, type_=type_)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "type_": type_})

        default = 1
        key = Key(name, default=default)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "default": default})

        key = Key(name, default=default, allow_none=True)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "default": default, "allow_none": True})

        descr = "bar"
        key = Key(name, description=descr)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "description": descr})
        assert key.get_description() == descr

        subkeys = [Key("bar")]
        key = Key(name, subkeys=subkeys)
        assert_object_attrs(key, {**default_key_attrs, "name": name, "subkeys": subkeys, "default": SUBKEYS})

        # test errors
        with pytest.raises(TypeError):
            Key(name, type_=[int])

        with pytest.raises(TypeError):
            Key(name, type_=int, default=1.3)

        with pytest.raises(TypeError):
            Key(name, default={"bar": 1})

        with pytest.raises(ValueError):
            Key(name, default=SUBKEYS)

    def test_from_dict(self, default_key_attrs):
        """
        Test for the ``from_dict`` method.
        """
        key_dict = {
            "name": "foo",
            "description": "bar",
            "default": 1,
        }
        key = Key.from_dict(key_dict)
        assert_object_attrs(key, {**default_key_attrs, **key_dict})

        key_dict = {
            "name": "foo",
            "subkeys": [
                {
                    "name": "bar",
                    "default": 2,
                },
                Key("baz"),
            ],
        }
        key = Key.from_dict(key_dict)
        expected_attrs = {
            **default_key_attrs,
            "name": key_dict["name"],
            "default": SUBKEYS,
            "subkeys__len": 2,
        }
        expected_attrs.pop("subkeys")
        assert_object_attrs(key, expected_attrs)

        assert len(key.subkeys) == 2
        assert_object_attrs(key.subkeys[0], {
            **default_key_attrs,
            "name": key_dict["subkeys"][0]["name"],
            "default": key_dict["subkeys"][0]["default"],
        })
        assert_object_attrs(key.subkeys[1], {
            **default_key_attrs,
            "name": key_dict["subkeys"][1].name,
        })

    # test errors
    with pytest.raises(TypeError):
        Key.from_dict({"subkeys": 1})

    @mock.patch("fica.key.Config")
    def test_get_subkeys_as_config(self, mocked_config):
        """
        Test for the ``get_subkeys_as_config`` method.
        """
        key = Key("foo")
        assert key.get_subkeys_as_config() is None
        mocked_config.assert_not_called()

        key = Key("foo", subkeys=[Key("bar")])
        subkeys = key.get_subkeys_as_config()
        mocked_config.assert_called_with(key.subkeys)

    def test_to_pair(self):
        """
        Test for the ``to_pair`` method.
        """
        name = "foo"
        pair = Key(name).to_pair()
        assert pair is None

        pair = Key(name).to_pair(include_empty=True)
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value is None

        pair = Key(name, default=None).to_pair()
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value is None

        pair = Key(name, default=None).to_pair(True)
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value is True

        pair = Key(name, default=1).to_pair()
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == 1

        pair = Key(name, default=1).to_pair(2)
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == 2

        pair = pair = Key(name, default=1, type_=(int, float), allow_none=True).to_pair(None)
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value is None

        pair = Key(name, subkeys=[Key("bar", default=1), Key("baz")]).to_pair()
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == {"bar": 1}

        pair = Key(name, default=1.2, subkeys=[Key("bar", default=1), Key("baz")]).to_pair()
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == 1.2

        pair = Key(name, subkeys=[Key("bar", default=1), Key("baz")]).to_pair(2)
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == 2

        pair = Key(name, subkeys=[Key("bar", default=1), Key("baz")]).to_pair({"bar": 2})
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == {"bar": 2}

        pair = Key(name, subkeys=[Key("bar", default=1), Key("baz")]).to_pair({"bar": 2, "baz": 3})
        assert isinstance(pair, KeyValuePair)
        assert pair.key == name
        assert pair.value == {"bar": 2, "baz": 3}

        # test errors
        with pytest.raises(TypeError):
            pair = Key(name, default=1, type_=(int, float)).to_pair("quux")

        with pytest.raises(TypeError):
            pair = Key(name, default=1, type_=(int, float)).to_pair(None)
