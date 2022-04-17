"""pytest configurations for fica's tests"""

import pytest

from typing import List

from fica import Config, Key


@pytest.fixture
def sample_keys() -> List[Key]:
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


@pytest.fixture
def sample_config(sample_keys: List[Key]) -> Config:
    """
    A pytest fixture for generating a sample ``Config`` object.
    """
    return Config(sample_keys)
