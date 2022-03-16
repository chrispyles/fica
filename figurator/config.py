""""""

from collections.abc import Iterable
from typing import Any, Dict, List, Union

from .key import Key


class Config:
    """
    """

    keys: List[Key]
    """"""

    def __init__(self, keys: List[Key]) -> None:
        if not isinstance(keys, Iterable) or not all(isinstance(e, Key) for e in keys):
            raise TypeError("'keys' must be a list (or other iterable) of keys")

        if not isinstance(keys, list):
            keys = list(keys)

        self.keys = keys

    @classmethod
    def from_list(cls, lst: List[Union[Key, Dict[str, Any]]]) -> "Config":
        """
        """
        keys = [e if isinstance(e, Key) else Key.from_dict(e) for e in lst]
        return cls(keys)

    def _get_keys_dict(self) -> Dict[str, Key]:
        """
        """
        return {k.name: k for k in self.keys}

    def to_dict(self, user_config: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        """
        config = {}
        keys_dict = self._get_keys_dict()
        for k, v in user_config.items():
            if k not in keys_dict:
                config[k] = v
            else:
                pair = keys_dict[k].to_pair(v)
                if pair is not None:
                    config[pair.key] = pair.value

        for k, v in keys_dict.items():
            if k not in config:
                pair = v.to_pair()
                if pair is not None:
                    config[pair.key] = pair.value

        return config
