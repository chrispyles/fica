"""Utilities for fica"""

class ConfigProcessingException(Exception):
    """
    An exception that can be used to wrap errors thrown while processing config keys.

    For deeply-nested config objects, this exception can be used to pass errors up the chain of
    configs so that errors can be shown fully-contextualized.

    Args:
        key (``str``): the name of the key in the config
        message (``str``): the error message
    """

    key: str
    """the name of the key in the config"""

    message: str
    """the error message"""

    def __init__(self, key: str, message: str):
        super().__init__(f"An error occured while processing {key}: {message}")
        self.key = key
        self.message = message

    @classmethod
    def from_child(cls, key: str, e: "ConfigProcessingException") -> "ConfigProcessingException":
        """
        Create a new ``ConfigProcessingException`` instance from one that was thrown in a nested
        config.

        Args:
            key (``str``): the name of the key in the config
            e (``ConfigProcessingException``): the child exception
        """
        if not isinstance(e, cls):
            raise TypeError(f"Child exception has invalid type: {type(e)}")
        return cls(f"{key}.{e.key}", e.message)
