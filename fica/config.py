"""Configuration objects"""

from typing import Any, Dict, Set


class Config:
    """
    A class defining the structure of configurations expected by an application.

    Configurations are represented as key-value pairs, where the application defines the structure
    of the expected configurations and the user provides some subset of the key-value pairs, which
    are processed and populated by this class.

    Args:
        user_config (``dict[str, object]``): a dictionary containing the configurations specified
            by the user
    """

    def __init__(self, user_config: Dict[str, Any] = {}) -> None:
        if not isinstance(user_config, dict):
            raise TypeError("The user-specified configurations must be passed as a dictionary")

        if not all(isinstance(k, str) for k in user_config):
            raise TypeError(
                "Some keys of the user-specified configurations dictionary are not strings")

        cls = type(self)
        all_keys = self._get_keys_()
        seen_keys = set()
        for k, v in user_config.items():
            if k in all_keys:
                try:
                    value = getattr(cls, k).get_value(v)
                except Exception as e:
                    raise RuntimeError(f"An error occurred while processing key '{k}': {e}")

                setattr(self, k, value)
                seen_keys.add(k)

        # set values for unspecified keys
        for k in all_keys:
            if k not in seen_keys:
                setattr(self, k, getattr(cls, k).get_value())

    def _get_keys_(self) -> Set[str]:
        """
        Get a ``set`` containing the attribute names corresponding to all keys of this config.

        Returns:
            ``set[str]``: the attribute names of all keys
        """
        cls = type(self)
        keys = set()
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), Key):
                keys.add(attr)
        return keys

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
        """
        return getattr(self, key)


from .key import Key
