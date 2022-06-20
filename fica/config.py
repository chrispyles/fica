"""Configuration objects"""

from typing import Any, Dict, List


class Config:
    """
    A class defining the structure of configurations expected by an application.

    Configuration keys are represented as fields declared in a subclass of this class, whose default
    values are instances of :py:class:`fica.Key`:

    .. code-block:: python

        class MyConfig(fica.Config):

            foo = fica.Key(description="a value for foo")

    Args:
        user_config (``dict[str, object]``): a dictionary containing the configurations specified
            by the user
    """

    def _validate_user_config(self, user_config: Dict[str, Any]) -> None:
        """
        Validate that a dictionary containing user-specified configuration values has the correct
        format.

        Args:
            user_config (``dict[str, object]``): a dictionary of new configuration values

        Raises:
            ``TypeError``: if ``user_config`` is of the wrong type or structure
        """
        if not isinstance(user_config, dict):
            raise TypeError("The user-specified configurations must be passed as a dictionary")

        if not all(isinstance(k, str) for k in user_config):
            raise TypeError(
                "Some keys of the user-specified configurations dictionary are not strings")

    def __init__(self, user_config: Dict[str, Any] = {}) -> None:
        self._validate_user_config(user_config)

        cls, all_keys = type(self), self._get_keys_()
        for k, v in user_config.items():
            if k in all_keys:
                try:
                    value = getattr(cls, k).get_value(v)
                except Exception as e:
                    # wrap the error message with one containing the key name
                    raise type(e)(f"An error occurred while processing key '{k}': {e}")

                setattr(self, k, value)

        # set values for unspecified keys
        seen_keys = user_config.keys()
        for k in all_keys:
            if k not in seen_keys:
                setattr(self, k, getattr(cls, k).get_value())

    def update_(self, user_config: Dict[str, Any]):
        """
        Recursively update the values for keys of this configuration in-place.

        Args:
            user_config (``dict[str, object]``): a dictionary of new configuration values

        Raises:
            ``TypeError``: if ``user_config`` is of the wrong type or structure
            ``Exception``: if an error occurs while parsing the specified value for a key
        """
        self._validate_user_config(user_config)

        cls, all_keys = type(self), self._get_keys_()
        for k, v in user_config.items():
            if k in all_keys:
                if isinstance(getattr(self, k), Config) and isinstance(v, dict):
                    getattr(self, k).update_(v)

                else:
                    try:
                        value = getattr(cls, k).get_value(v)
                    except Exception as e:
                        # wrap the error message with one containing the key name
                        raise type(e)(f"An error occurred while processing key '{k}': {e}")

                    setattr(self, k, value)

    def _get_keys_(self) -> List[str]:
        """
        Get a ``list`` containing the attribute names corresponding to all keys of this config.

        The list is constructed using ``dir``, so its elements should be sorted in ascending order.

        Returns:
            ``list[str]``: the attribute names of all keys
        """
        cls = type(self)
        return [a for a in dir(cls) if isinstance(getattr(cls, a), Key)]

    def __eq__(self, other: Any) -> bool:
        """
        Determine whether another object is equal to this config. An object is equal to a config iff
        it is also a config of the same type and has the same key values.
        """
        if not isinstance(other, type(self)):
            return False

        return all(getattr(self, k) == getattr(other, k) for k in self._get_keys_())

    def __getitem__(self, key) -> Any:
        """
        Redirect indexing with ``[]`` to ``getattr``.
        """
        return getattr(self, key)

    def __repr__(self) -> str:
        ret = f"{type(self).__name__}("
        for k in self._get_keys_():
            ret += f"{k}={getattr(self, k)}, "
        ret = ret[:-2] + ")"
        return ret


from .key import Key
