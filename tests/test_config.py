"""Tests for ``fica.key``"""

import pytest

from unittest import mock

from fica import Config, Key

from .utils import assert_object_attrs, CustomIterable


@pytest.fixture
def sample_keys():
    """
    A pytest fixture for generating a list of sample ``Key`` objects.
    """
    return [
        Key("foo"),
        Key("bar", subkeys=[Key("baz", default=1), Key("quux")]),
        Key("quuz", default=1, subkeys=[Key("corge", default=True)]),
        Key("grault", default=2, type_=(int, float), allow_none=True),
        Key("garply", default=3, type_=(int, float)),
    ]


class TestConfig:
    """
    Tests for ``fica.config.Config``.
    """

    def test_constructor_and_getters(self, sample_keys):
        """
        Tests for the ``Config`` constructor and attribute getters.
        """
        config = Config(sample_keys)
        assert_object_attrs(config, {"keys": sample_keys})

        for key in sample_keys:
            assert config.get_key(key.name) is key

        # test iterable conversion
        config = Config(CustomIterable(sample_keys))
        assert config.keys == sample_keys

        # test errors
        with pytest.raises(TypeError):
            Config(1)

        with pytest.raises(TypeError):
            Config([Key("foo"), 2])

    def test_from_list_and___eq__(self, sample_keys):
        """
        Tests for the ``from_list`` and ``__eq__`` methods.
        """
        config = Config.from_list([
            {
                "name": "foo"
            },
            {
                "name": "bar",
                "subkeys": [
                    {
                        "name": "baz",
                        "default": 1,
                    },
                    {
                        "name": "quux",
                    },
                ],
            },
            {
                "name": "quuz",
                "default": 1,
                "subkeys": [
                    Key("corge", default=True),
                ],
            },
            *sample_keys[3:],
        ])
        assert config == Config(sample_keys)

    def test_to_dict(self, sample_keys):
        """
        Test for the ``to_dict`` method.
        """
        default_result = {
            "bar": {
                "baz": 1,
            },
            "quuz": 1,
            "grault": 2,
            "garply": 3,
        }
        result = Config(sample_keys).to_dict()
        assert result == default_result

        result = Config(sample_keys).to_dict({"foo": False})
        assert result == {**default_result, "foo": False}

        result = Config(sample_keys).to_dict({"waldo": False})
        assert result == {**default_result, "waldo": False}

        result = Config(sample_keys).to_dict({"bar": {"quux": True}})
        assert result == {**default_result, "bar": {**default_result["bar"], "quux": True}}

        result = Config(sample_keys).to_dict({"grault": 3.14})
        assert result == {**default_result, "grault": 3.14}

        result = Config(sample_keys).to_dict({"grault": None})
        assert result == {**default_result, "grault": None}

        result = Config(sample_keys).to_dict({"garply": 3.14})
        assert result == {**default_result, "garply": 3.14}

        # test errors
        with pytest.raises(TypeError):
            Config(sample_keys).to_dict({"grault": "bazly"})

        with pytest.raises(TypeError):
            Config(sample_keys).to_dict({"garply": None})
