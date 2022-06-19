"""Configuration keys"""

from typing import Any, List, Optional, Tuple, Type, Union

from .config import Config
from .validators import _Validator


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
        description (``str | None``): a description of the configuration for documentation
        default (``object``): the default value of the key
        type (``type | tuple[type]``): valid type(s) for the value of this configuration
        allow_none (``bool``): whether ``None`` is a valid value for the configuration
        validator (validator or ``None``): a validator for validating user-specified values
        subkey_container (subclass of :py:class:`fica.Config`): an (uninstantiated) config class
            containing the subkeys of this key
    """

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

    validator: Optional[_Validator]
    """a validator for user-specified values"""

    subkey_container: Optional[Type[Config]]
    """a config class containing the subkeys of this key"""

    def __init__(
        self,
        description: Optional[str] = None,
        default: Any = EMPTY,
        type_: Optional[Union[Type, Tuple[Type]]] = None,
        allow_none: bool = False,
        validator: Optional[_Validator] = None,
        subkey_container: Optional[Type[Config]] = None
    ) -> None:
        if type_ is not None:
            if not (isinstance(type_, Type) or (isinstance(type_, tuple) and \
                    all(isinstance(e, Type) for e in type_))):
                raise TypeError("type_ must be a single type or tuple of types")

            if default is not EMPTY and default is not SUBKEYS and \
                    not (isinstance(default, type_) or (allow_none and default is None)):
                raise TypeError("The default value is not of the specified type(s)")

        if isinstance(default, dict):
            raise TypeError("The default value cannot be a dictionary; use subkeys instead")

        if validator is not None and not isinstance(validator, _Validator):
            raise TypeError("validator is not a valid validator")

        if subkey_container is not None and not issubclass(subkey_container, Config):
            raise TypeError("The provided subkey_container is not a subclass of fica.Config")

        if default is EMPTY and subkey_container is not None:
            default = SUBKEYS

        if default is SUBKEYS and subkey_container is None:
            raise ValueError("Cannot default to subkeys when no subkey_container is provided")

        self.description = description
        self.default = default
        self.type_ = type_
        self.allow_none = allow_none
        self.validator = validator
        self.subkey_container = subkey_container

    def get_description(self) -> Optional[str]:
        """
        Get the description of the key.

        Returns:
            ``str | None``: the description of the key
        """
        return self.description

    def get_subkey_container(self) -> Optional[Type[Config]]:
        """
        Get the subkey container class.

        Returns:
            subclass of :py:class:`fica.Config`: the uninstantiated subkey container class
        """
        return self.subkey_container

    def get_value(self, user_value: Any = EMPTY) -> Any:
        """
        Convert this key to a :py:class:`KeyValuePair` with the provided user-specified value.

        Args:
            user_value (``object``): the value specified by the user
            include_empty (``bool``): whether to return a pair with the value ``None`` if no user
                value is provided and the default is :py:obj:`fica.EMPTY`

        Returns:
            ``object``: the value of the key, taking into account the user-specified value

        Raises:
            ``TypeError``: if the user-specified value is not of the correct type
            ``ValueError``: if the user-specified value fails validation
        """
        value = user_value
        if value is EMPTY:
            if self.default is SUBKEYS:
                value = self.subkey_container()
            elif self.default is EMPTY:
                return None
            else:
                value = self.default
        else:
            if not ((self.type_ is None or isinstance(value, self.type_)) or \
                    (self.allow_none and value is None)):
                raise TypeError("User-specified value is not of the correct type")

            # validate the value
            if self.validator is not None:
                err = self.validator.validate(value)
                if err is not None:
                    raise ValueError(f"User-specified value failed validation: {err}")

            # TODO: add a way to enforce that some keys can _only_ map to subkey dicts?
            # handle user-inputted dict w/ missing subkeys
            if self.subkey_container is not None and isinstance(value, dict):
                value = self.subkey_container(value)

        return value

    def should_document_subkeys(self) -> bool:
        """
        Determine whether this key has subkeys that should be documented.

        Returns:
            ``bool``: whether this class has subkeys that should be documented
        """
        return self.subkey_container is not None
