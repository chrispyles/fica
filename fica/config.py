"""Configuration objects"""

from typing import Any, Dict, Set

from .utils import ConfigProcessingException


class Config:
    """
    A class defining the structure of configurations expected by an application.

    Configuration keys are represented as fields declared in a subclass of this class, whose default
    values are instances of :py:class:`fica.Key`:

    .. code-block:: python

        class MyConfig(fica.Config):

            foo = fica.Key(description="a value for foo")

    When ``fica`` creates an instance of your config to document it, it will set
    ``documentation_mode`` to ``True``; this can be useful for disabling any validations in your
    subclass's constructor when fica documents it.

    Args:
        user_config (``dict[str, object]``): a dictionary containing the configurations specified
            by the user
        documentation_mode (``bool``): indicates that ``fica`` is creating an instance with an empty
            user config to generate the documentation.
        require_valid_keys (``bool``): whether to require that all keys in the user config are valid
    """

    _defaulted: Set[str]
    """the names of keys that were not specified by the user"""

    _require_valid_keys: bool
    """whether to require that all keys in the user config are valid"""

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

    def __init__(
            self,
            user_config: Dict[str, Any] = {},
            documentation_mode: bool = False,
            require_valid_keys: bool = False,
        ) -> None:
        self._validate_user_config(user_config)

        self._defaulted = set()
        self._require_valid_keys = require_valid_keys
        self._populate(user_config, True, documentation_mode)

    def __setattr__(self, attr: str, value: Any) -> None:
        super().__setattr__(attr, value)
        name = self._get_attrs_to_names().get(attr)
        if name in self._defaulted:
            self._defaulted.remove(name)

    def update(self, user_config: Dict[str, Any]):
        """
        Recursively update the values for keys of this configuration in-place.

        Args:
            user_config (``dict[str, object]``): a dictionary of new configuration values

        Raises:
            ``TypeError``: if ``user_config`` is of the wrong type or structure
            ``Exception``: if an error occurs while parsing the specified value for a key
        """
        self._validate_user_config(user_config)
        self._populate(user_config, False)

    def _populate(
        self,
        user_config: Dict[str, Any],
        populate_defaults: bool,
        documentation_mode: bool = False,
    ):
        """
        """
        cls, names_to_attrs, seen_attrs = type(self), self._get_names_to_attrs(), set()

        # go through attributes on this class and every Config subclass it inherits from to find all
        # keys
        for name, v in user_config.items():
            if name not in names_to_attrs:
                if self._require_valid_keys:
                    raise ValueError(f"Unexpected key found in config: '{name}'")
                else:
                    continue

            attr  = names_to_attrs[name]
            try:
                key = getattr(cls, attr)
                if isinstance(getattr(self, attr), Config) and \
                        isinstance(v, dict):
                    getattr(self, names_to_attrs[name]).update(v)

                else:
                    value = key.get_value(v, require_valid_keys=self._require_valid_keys)
                    setattr(self, attr, value)

                if key.use_default(v):
                    self._defaulted.add(name)
                elif name in self._defaulted:
                    self._defaulted.remove(name)

            except Exception as e:
                # wrap the error message with one containing the key name
                if isinstance(e, ConfigProcessingException):
                    raise ConfigProcessingException.from_child(name, e)
                else:
                    raise ConfigProcessingException(name, e)

            seen_attrs.add(attr)

        if not populate_defaults:
            return

        # set values for unspecified keys
        for name, attr in names_to_attrs.items():
            if attr in seen_attrs:
                continue

            key = getattr(cls, attr)
            if documentation_mode:
                value = key.get_default()
            else:
                value = key.get_value()
            setattr(self, attr, value)
            self._defaulted.add(name)

    @property
    def _config_classes(self):
        """"""
        return tuple(c for c in type(self).__mro__ if issubclass(c, Config) and c is not Config)

    def _get_attrs_to_names(self) -> Dict[str, str]:
        """
        Get a dictionary mapping class attribute names to key names in the user config.
        """
        res = {}
        # iterate over config classes in reverse order so that attr collisions are resolved in favor
        # of the lower class in the MRO
        for cls in self._config_classes[::-1]:
            # iterate through cls.__dict__ because dicts maintain insertion order, and will
            # therefore be ordered in the same order as the fields were declared
            res.update({
                a: getattr(cls, a).get_name(a)
                for a
                in cls.__dict__
                if isinstance(getattr(cls, a), Key)
            })

        return res

    def _get_names_to_attrs(self) -> Dict[str, str]:
        """
        Get a dictionary mapping key names in the user config to class attribute names.
        """
        return {v: k for k, v in self._get_attrs_to_names().items()}

    def __eq__(self, other: Any) -> bool:
        """
        Determine whether another object is equal to this config. An object is equal to a config iff
        it is also a config of the same type and has the same key values.
        """
        if not isinstance(other, type(self)):
            return False

        return all(getattr(self, k) == getattr(other, k) for k in self._get_attrs_to_names())

    def __getitem__(self, key) -> Any:
        """
        Redirect indexing with ``[]`` to ``getattr``.
        """
        return getattr(self, key)

    def __repr__(self) -> str:
        ret = f"{type(self).__name__}("
        for k in self._get_attrs_to_names():
            ret += f"{k}={getattr(self, k)}, "
        ret = ret[:-2] + ")"
        return ret

    def get_user_config(self) -> Dict[str, Any]:
        """
        Get a user configuration ``dict`` that could be used to re-create this config exactly.

        Returns a ``dict`` mapping keys to their values in this config if the value of the key is
        different from its default.

        Returns:
            ``dict[str, object]``: the user configurations ``dict``
        """
        attrs_to_names = self._get_attrs_to_names()
        user_config = {}
        for a, n in attrs_to_names.items():
            v = getattr(self, a)
            if isinstance(v, Config):
                v = v.get_user_config()
                if len(v) > 0:
                    user_config[n] = v
            elif n not in self._defaulted:
                user_config[n] = v
        return user_config


from .key import Key
