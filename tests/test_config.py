"""Tests for ``fica.key``"""

import pytest

from unittest import mock

from fica import Config, Key, validators
from fica.utils import ConfigProcessingException


class TestConfig:
    """
    Tests for ``fica.config.Config``.
    """

    def test_constructor_and_update(self, sample_config):
        """
        Tests for the ``Config`` constructor and the ``update`` method.
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

        config.update({"foo": 2, "bar": {"quux": 4}})
        expected_attrs = {
            **sample_config._expected_attrs,
            "foo": 2,
            "bar": sample_config.BarValue({"baz": 2, "quux": 4}),
            "quuz": sample_config.QuuzValue({"corge": False}),
        }
        for k, v in expected_attrs.items():
            assert getattr(config, k) == v

        config = sample_config({"foo": 1}, require_valid_keys=True)
        expected_attrs = {
            **sample_config._expected_attrs,
            "foo": 1,
        }
        for k, v in expected_attrs.items():
            assert getattr(config, k) == v

        config.update({"foo": 2})
        expected_attrs = {
            **sample_config._expected_attrs,
            "foo": 2,
        }
        for k, v in expected_attrs.items():
            assert getattr(config, k) == v

        # test errors
        with pytest.raises(TypeError):
            sample_config(1)

        with pytest.raises(TypeError):
            sample_config({1: 2})

        sample_config.foo = mock.MagicMock(spec=Key)
        sample_config.foo.get_name.return_value = "foo"
        sample_config.foo.get_value.side_effect = TypeError("bad value")
        with pytest.raises(ConfigProcessingException, match=r".*foo: bad value"):
            sample_config({"foo": 1})

        sample_config.foo.get_value.side_effect = ValueError("bad value")
        with pytest.raises(ConfigProcessingException, match=r".*foo: bad value"):
            sample_config({"foo": 1})

        with pytest.raises(ConfigProcessingException, match=r".*foo: bad value"):
            config.update({"foo": 1})

        sample_config.foo.get_value.side_effect = None

        with pytest.raises(ValueError, match="Unexpected key found in config: 'doesnotexist'"):
            sample_config({"foo": 1, "doesnotexist": True}, require_valid_keys=True)

        with pytest.raises(
            ConfigProcessingException,
            match="An error occured while processing quuz: Unexpected key found in config: 'doesnotexist'",
        ):
            sample_config({"quuz": {"doesnotexist": True}}, require_valid_keys=True)

        config = sample_config({"foo": 1}, require_valid_keys=True)
        with pytest.raises(ValueError, match="Unexpected key found in config: 'doesnotexist'"):
            config.update({"foo": 1, "doesnotexist": True})

        with pytest.raises(
            ConfigProcessingException,
            match="An error occured while processing quuz: Unexpected key found in config: 'doesnotexist'",
        ):
            config.update({"quuz": {"doesnotexist": True}})

        class DeeplyNestConfig(Config):
            class AValue(Config):
                class BValue(Config):
                    c = Key(validator=validators.choice([1, 2]))
                
                b = Key(subkey_container=BValue)
            
            a = Key(subkey_container=AValue)
        
        with pytest.raises(
            ConfigProcessingException,
            match=r"An error occured while processing a\.b\.c: User-specified value failed validation: 3 is not one of \{1, 2\}",
        ):
            DeeplyNestConfig({"a": {"b": {"c": 3}}})
        
        c = DeeplyNestConfig({"a": {"b": {"c": 1}}})
        with pytest.raises(
            ConfigProcessingException,
            match=r"An error occured while processing a\.b\.c: User-specified value failed validation: 3 is not one of \{1, 2\}",
        ):
            c.update({"a": {"b": {"c": 3}}})

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

    def test___repr__(self, sample_config):
        """
        Tests for the ``__repr__`` method.
        """
        config = sample_config()
        assert repr(config) == \
            "SampleConfig(foo=None, bar=BarValue(baz=1, quux=None), quuz=1, grault=2, garply=3)"

    def test_get_user_config(self, sample_config):
        """
        Tests for the ``get_user_config`` method.
        """
        def test_with_user_config(user_config):
            config = sample_config(user_config)
            assert config.get_user_config() == user_config

            config = sample_config()
            config.update(user_config)
            assert config.get_user_config() == user_config

        test_with_user_config({})
        test_with_user_config({"foo": True, "bar": {"baz": 2}})
        test_with_user_config({"quuz": {"corge": False}, "bar": 3})
        test_with_user_config({"grault": None})

    # Used in test_get_user_config_with_factories
    counter = 0

    def test_get_user_config_with_factories(self):
        """
        Tests for the ``get_user_config`` method with factories.
        """
        def bar_factory():
            self.counter += 1
            return self.counter

        class SampleConfig(Config):
            foo = Key(factory=lambda: [])
            bar = Key(factory=bar_factory)

        def test_with_user_config(user_config):
            config = SampleConfig(user_config)
            assert config.get_user_config() == user_config

            config = SampleConfig()
            config.update(user_config)
            assert config.get_user_config() == user_config

        test_with_user_config({})
        test_with_user_config({"foo": [1], "bar": 10})
        test_with_user_config({"foo": [], "bar": 3})

        c = SampleConfig()
        c.update({"foo": []})
        assert c.get_user_config() == {"foo": []}

    def test_get_user_config_with_defaults(self):
        """
        Tests for the ``get_user_config`` method.
        """
        class C(Config):
            foo = Key(default=2)
            bar = Key(name="baz", default=3)

        c = C()
        assert c.get_user_config() == {}

        c.foo = 3
        assert c.get_user_config() == {"foo": 3}

        c.bar = 4
        assert c.get_user_config() == {"foo": 3, "baz": 4}

    def test_inheritance(self):
        """
        Tests for ``Config`` inheritance.
        """
        class BValue(Config):
            b1 = Key(default=1)

        class A(Config):
            a = Key()
            b = Key()

        class B(A):
            b = Key(subkey_container=BValue)
            c = Key()
            d = Key(default=2)
            e = Key()

        class C(B):
            c = Key()
            d = Key()
            e = Key(default=3)
            f = Key()

        default_attrs = {
            "A": {
                "a": None,
                "b": None,
            },
            "B": {
                "a": None,
                "b": BValue(),
                "c": None,
                "d": 2,
                "e": None,
            },
            "C": {
                "a": None,
                "b": BValue(),
                "c": None,
                "d": None,
                "e": 3,
                "f": None,
            },
        }

        for c, attrs in [
            (A(), default_attrs["A"]),
            (B(), default_attrs["B"]),
            (C(), default_attrs["C"]),
        ]:
            for a, v in attrs.items():
                assert getattr(c, a) == v

        for uc, cc, attrs in [
            ({"a": -3, "b": {"b1": "b1"}, "c": 1}, B, default_attrs["B"]),
            ({"a": -3, "c": 1, "d": -1, "e": -2}, C, default_attrs["C"]),
        ]:
            c = cc(uc)
            attrs = {**attrs, **uc}
            for a, v in attrs.items():
                if a == "b" and isinstance(v, dict):
                    v = BValue(v)
                assert getattr(c, a) == v

            c.update({"a": -10, "b": {"b1": "b2"}})
            attrs = {**attrs, "a": -10, "b": BValue({"b1": "b2"})}
            for a, v in attrs.items():
                if a == "b" and isinstance(v, dict):
                    v = BValue(v)
                assert getattr(c, a) == v
