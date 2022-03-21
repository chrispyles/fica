"""Module for configuration keys"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from .config import Config


class _Empty:
    """
    A singleton object representing an empty default value.
    """

    def __repr__(self) -> str:
        return "fica.EMPTY"


class _Subkeys():
    """
    A singleton object representing that a key's subkeys should be its default value.
    """

    def __repr__(self) -> str:
        return "fica.SUBKEYS"


EMPTY = _Empty()
SUBKEYS = _Subkeys()


@dataclass
class KeyValuePair:
    """
    A dataclass representing a processed key-value pair.
    """

    key: str
    """the configuration key"""

    value: Any
    """the configuration value"""


class Key:
    """
    A class representing a key in a configuration.

    Keys have a default value, specified with the ``default`` argument.

    - If ``default`` is :py:data:`fica.EMPTY`, then the key is not included in the resulting
      configuration unless the user specifies a value.
    - If ``default`` is :py:data:`fica.SUBKEYS`, then the key is defaulted to a dictionary
      containing each subkey with its default unless the user specifies
      a value.
    - Otherwise, the key is mapped to the value of ``default``.

    If ``default`` is :py:data:`fica.EMPTY` and subkeys are provided, ``default`` is
    automatically set to :py:data:`fica.SUBKEYS`.

    Args:
        name (``str``): the name of the key
        description (``str | None``): a description of the configuration for documentation
        default (``object``): the default value of the key
        subkeys (``list[Key]``): subkeys of this configuration
        type (``type | tuple[type]``): valid type(s) for the value of this configuration
        allow_none (``bool``): whether ``None`` is a valid value for the configuration
    """

    name: str
    """the name of the key"""

    description: Optional[str]
    """a description of the configuration for documentation"""

    default: Any
    """the default value of the key"""

    subkeys: Optional[List["Key"]]
    """subkeys of this configuration"""

    type_: Optional[Union[Type, Tuple[Type]]]
    """valid type(s) for the value of this configuration"""

    allow_none: bool
    """whether ``None`` is a valid value for the configuration"""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        default: Any = EMPTY,
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

        if default is EMPTY and subkeys is not None:
            default = SUBKEYS

        if default is SUBKEYS and subkeys is None:
            raise ValueError("Cannot default to subkeys when there are no subkeys specified")

        self.name = name
        self.description = description
        self.default = default
        self.subkeys = subkeys
        self.type_ = type
        self.allow_none = allow_none

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "Key":
        """
        Create a :py:class:`Key` from a dictionary whose keys match constructor argument names.

        Args:
            dct (``dict[str, object]``): the dictionary of constructor arguments

        Returns:
            :py:class:`Key`: the key object
        """
        subkeys = dct.pop("subkeys", None)
        if subkeys:
            if not isinstance(subkeys, list):
                raise TypeError("'subkeys' provided to Key.from_dict is not a list")

            subkeys = [Key.from_dict(s) if not isinstance(s, Key) else s for s in subkeys]

        return cls(**dct, subkeys=subkeys)

    def get_name(self) -> str:
        """
        Get the name of the key.

        Returns:
            ``str``: the name of the key
        """
        return self.name

    def get_description(self) -> Optional[str]:
        """
        Get the description of the key.

        Returns:
            ``str | None``: the description of the key
        """
        return self.description

    def get_subkeys_as_config(self) -> Optional[Config]:
        """
        """
        return Config(self.subkeys) if self.default is SUBKEYS else None

    def to_pair(self, user_value: Any = EMPTY, include_empty=False) -> Optional[KeyValuePair]:
        """
        Convert this key to a :py:class:`KeyValuePair` with the provided user-specified value.

        Args:
            user_value (``object``): the value specified by the user
            include_empty (``bool``): whether to return a pair with the value ``None`` if no user
                value is provided and the default is :py:obj:`fica.EMPTY`

        Returns:
            :py:class:`KeyValuePair`: the key-value pair if the key should be present,
            otherwise ``None``
        """
        value = user_value
        if value is EMPTY:
            if self.default is SUBKEYS:
                value = Config(self.subkeys).to_dict()
            elif self.default is EMPTY:
                if include_empty:
                    return KeyValuePair(self.name, None)
                return None
            else:
                value = self.default
        else:
            if not (isinstance(value, self.type_) or (self.allow_none and value is None)):
                raise TypeError(
                    f"User-specified value for key '{self.key}' is not of the correct type")

            # handle user-inputted dict w/ missing subkeys
            if self.subkeys is not None and isinstance(value, dict):
                conf = Config(self.subkeys).to_dict(value)
                conf.update(value)
                value = conf

        return KeyValuePair(self.name, value)
