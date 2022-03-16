""""""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union


class _Empty:
    """
    """


EMPTY = _Empty()
""""""


class _Subkeys():
    """
    """


SUBKEYS = _Subkeys()
""""""


@dataclass
class KeyValuePair:
    """
    """

    key: str
    """"""

    value: Any
    """"""


class Key:
    """
    """

    name: str
    """"""

    description: Optional[str]
    """"""

    default: Any
    """"""

    subkeys: List["Key"]
    """"""

    type_: Optional[Union[Type, Tuple[Type]]]
    """"""

    allow_none: bool
    """"""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        default: Any = SUBKEYS,
        subkeys: Optional[List["Key"]] = None,
        type: Optional[Union[Type, Tuple[Type]]] = None,
        allow_none: bool = False
    ) -> None:
        if type is not None:
            if not isinstance(type, Type) or (isinstance(type, tuple) and \
                    all(isinstance(e, Type) for e in type)):
                raise TypeError("type must be a single type or tuple of types")

            if default is not EMPTY and default is not SUBKEYS and \
                    not (isinstance(default, type) or (allow_none and default is None)):
                raise TypeError("The default value is not of the specified type(s)")

        if default is SUBKEYS and subkeys is None:
            raise ValueError("Subkeys must be specified when they are the default value")

        self.name = name
        self.description = description
        self.default = default
        self.subkeys = subkeys if subkeys is not None else []
        self.type_ = type
        self.allow_none = allow_none

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "Key":
        """
        """
        return cls(**dct)

    def get_name(self) -> str:
        """
        """
        return self.name

    def to_pair(self, user_value: Any = EMPTY) -> Optional[KeyValuePair]:
        """
        """
        value = user_value
        if value is EMPTY:
            if self.default is SUBKEYS:
                value = Config(self.subkeys).to_dict()
            elif self.default is EMPTY:
                return None
            else:
                value = self.default
        else:
            if not (isinstance(value, self.type_) or (self.allow_none and value is None)):
                raise TypeError(
                    f"User-specified value for key '{self.key}' is not of the correct type")

            # handle user-inputted dict w/ missing subkeys
            if self.subkeys is not None and isinstance(value, dict):
                conf = Config(self.subkeys).to_dict()
                conf.update(value)
                value = conf

        return KeyValuePair(self.key, value)


from .config import Config
