"""A library for managing and documenting user-supplied configurations"""

__all__ = ["Config", "EMPTY", "Key", "SUBKEYS"]

from .config import Config
from .key import EMPTY, Key, SUBKEYS
from .version import __version__
