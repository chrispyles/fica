"""Tests for ``fica.validators``"""

import pytest

from fica.validators import choice, validator


def test_choice():
    """
    Tests the ``choice`` validator.
    """
    choices = [1, 2, 3, 'a', 'b', 'c']
    validator = choice(choices)

    for c in choices:
        assert validator.validate(c) is None

    as_str = lambda v: "'" + v + "'" if isinstance(v, str) else str(v)
    choices_str = '{' + ', '.join(as_str(c) for c in choices) + '}'

    for c in [4, 'd', False, 1.2, None]:
        ret = validator.validate(c)
        value = as_str(c)
        assert ret == f"{value} is not one of {choices_str}"

    # test errors
    with pytest.raises(TypeError):
        choice({1, 2, 3})

    with pytest.raises(TypeError):
        choice(1)


def test_validator():
    """
    Tests the ``validator`` decorator for validation functions.
    """
    fn = lambda x: x % 2 == 0
    message = "bad value"

    @validator
    def validator_fn(x):
        return None if fn(x) else message

    for i in range(10):
        ret = validator_fn.validate(i)
        if fn(i):
            assert ret is None
        else:
            assert ret == message

    # test errors
    with pytest.raises(TypeError):
        vdtr = validator(lambda x: 1)
        vdtr.validate(2)
