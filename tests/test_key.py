"""Tests for ``fica.key``"""

import pytest

from unittest import mock

from fica import Config, EMPTY, Key, SUBKEYS, validators
from fica.validators import _Validator

from .utils import assert_object_attrs


@pytest.fixture
def default_key_attrs():
    """
    A pytest fixture returning the default attribute values for a ``Key``.
    """
    return {
        "description": None,
        "default": EMPTY,
        "type_": None,
        "allow_none": False,
        "validator": None,
        "subkey_container": None,
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
        key = Key()
        assert_object_attrs(key, {**default_key_attrs})
        assert key.get_subkey_container() is None

        type_ = int
        key = Key(type_=type_)
        assert_object_attrs(key, {**default_key_attrs, "type_": type_})

        type_ = int, float
        key = Key(type_=type_)
        assert_object_attrs(key, {**default_key_attrs, "type_": type_})

        default = 1
        key = Key(default=default)
        assert_object_attrs(key, {**default_key_attrs, "default": default})

        key = Key(default=default, allow_none=True)
        assert_object_attrs(key, {**default_key_attrs, "default": default, "allow_none": True})

        descr = "bar"
        key = Key(description=descr)
        assert_object_attrs(key, {**default_key_attrs, "description": descr})
        assert key.get_description() == descr

        validator = validators.choice([1, 2, 3])
        key = Key(validator=validator)
        assert_object_attrs(key, {**default_key_attrs, "validator": validator})

        class SubkeyValue(Config):

            bar = Key()

        key = Key(subkey_container=SubkeyValue)
        assert_object_attrs(
            key, {**default_key_attrs, "subkey_container": SubkeyValue, "default": SUBKEYS})
        assert key.get_subkey_container() is SubkeyValue

        # test errors
        with pytest.raises(TypeError):
            Key(type_=[int])

        with pytest.raises(TypeError):
            Key(type_=int, default=1.3)

        with pytest.raises(TypeError):
            Key(type_=int, default=None)

        with pytest.raises(TypeError):
            Key(default={"bar": 1})

        with pytest.raises(ValueError):
            Key(default=SUBKEYS)

        with pytest.raises(TypeError):
            Key(validator=lambda x: x % 2 == 0)

        class BadSubkeyValue:
            pass

        with pytest.raises(TypeError):
            Key(subkey_container=BadSubkeyValue)

    def test_get_value(self):
        """
        Test for the ``get_value`` method.
        """
        value = Key().get_value()
        assert value is None

        value = Key(default=None).get_value()
        assert value is None

        value = Key(default=None).get_value(True)
        assert value is True

        value = Key(default=1).get_value()
        assert value == 1

        value = Key(default=1).get_value(2)
        assert value == 2

        value = value = Key(default=1, type_=(int, float), allow_none=True).get_value(None)
        assert value is None

        class SubkeyValue(Config):
            
            bar = Key(default=1)
            baz = Key()

        value = Key(subkey_container=SubkeyValue).get_value()
        assert value == SubkeyValue({"bar": 1})

        value = Key(default=1.2, subkey_container=SubkeyValue).get_value()
        assert value == 1.2

        value = Key(subkey_container=SubkeyValue).get_value(2)
        assert value == 2

        value = Key(subkey_container=SubkeyValue).get_value({"bar": 2})
        assert value == SubkeyValue({"bar": 2})

        value = Key(subkey_container=SubkeyValue).get_value({"bar": 2, "baz": 3})
        assert value == SubkeyValue({"bar": 2, "baz": 3})

        mocked_validator = mock.Mock(spec=_Validator)
        validator_key = Key(validator=mocked_validator)
        validator_key.get_value()
        mocked_validator.validate.assert_not_called()

        mocked_validator.validate.return_value = None
        validator_key.get_value(1)
        mocked_validator.validate.assert_called_with(1)

        mocked_validator.validate.return_value = "bad value"
        with pytest.raises(ValueError, match=fr".*{mocked_validator.validate.return_value}.*"):
            validator_key.get_value(1)
            mocked_validator.validate.assert_called_with(1)

        # test errors
        with pytest.raises(TypeError):
            value = Key(default=1, type_=(int, float)).get_value("quux")

        with pytest.raises(TypeError):
            value = Key(default=1, type_=(int, float)).get_value(None)

    def test_should_document_subkeys(self):
        """
        Test for the ``should_document_subkeys`` method.
        """
        class SubkeyValue(Config):

            bar = Key()

        key = Key(subkey_container=SubkeyValue)
        assert key.should_document_subkeys() is True

        key = Key(subkey_container=SubkeyValue, default=1)
        assert key.should_document_subkeys() is False

        key = Key()
        assert key.should_document_subkeys() is False
