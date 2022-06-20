"""pytest configurations for fica's tests"""

import pytest

from fica import Config, Key


@pytest.fixture
def sample_config() -> Config:
    """
    A pytest fixture for generating a sample ``Config`` object.
    """
    class SampleConfig(Config):
        
        foo = Key(description="foo")
        
        class BarValue(Config):
            baz = Key(default=1, description="baz")

            quux = Key()

            _expected_attrs = {
                "baz": 1,
                "quux": None,
            }

        bar = Key(subkey_container=BarValue, description="bar")

        class QuuzValue(Config):

            corge = Key(default=True)

            _expected_attrs = {
                "corge": True,
            }

        quuz = Key(default=1, subkey_container=QuuzValue)

        grault = Key(default=2, type_=(int, float), allow_none=True)

        garply = Key(default=3, type_=(int, float))

        _expected_attrs = {
            "foo": None,
            "bar": BarValue(),
            "quuz": 1,
            "grault": 2,
            "garply": 3,
        }

    return SampleConfig
