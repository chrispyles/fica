"""Tests for ``fica.key``"""

import pytest

from unittest import mock

from fica import Config, Key


class TestConfig:
    """
    Tests for ``fica.config.Config``.
    """

    def test_constructor_and_getters(self, sample_config):
        """
        Tests for the ``Config`` constructor and attribute getters.
        """
        config = sample_config()
        for k, v in sample_config._expected_attrs.items():
            assert getattr(config, k) == v

        config = sample_config({"foo": 1, "bar": {"baz": 2}, "quuz": {"corge": False}})
        expected_attrs = {
            **sample_config._expected_attrs,
            "foo": 1,
            "bar": sample_config.BarValue({"baz": 2}),
            "quuz": sample_config.QuuzValue({"corge": False}),
        }
        for k, v in expected_attrs.items():
            assert getattr(config, k) == v 

        # test errors
        with pytest.raises(TypeError):
            sample_config(1)

        with pytest.raises(TypeError):
            sample_config({1: 2})

        sample_config.foo = mock.MagicMock(spec=Key)
        sample_config.foo.get_value.side_effect = TypeError("bad value")
        with pytest.raises(TypeError, match=r".*key 'foo': bad value"):
            sample_config({"foo": 1})

        sample_config.foo.get_value.side_effect = ValueError("bad value")
        with pytest.raises(ValueError, match=r".*key 'foo': bad value"):
            sample_config({"foo": 1})

    def test___eq__(self, sample_config):
        """
        Tests for the ``__eq__`` method.
        """
        assert sample_config() == sample_config()
        assert sample_config({"bar": {"quux": 2}}) == sample_config({"bar": {"quux": 2}})
        assert sample_config({"bar": {"quux": 2}}) != sample_config({"bar": {"quux": 3}})
        
        class OtherConfig(Config):
            pass

        assert sample_config() != OtherConfig()

    def test___getitem__(self, sample_config):
        """
        Tests for the ``__getitem__`` method.
        """
        config = sample_config()
        with mock.patch("fica.config.getattr") as mocked_getattr:
            config["foo"]
            mocked_getattr.assert_called_with(config, "foo")
