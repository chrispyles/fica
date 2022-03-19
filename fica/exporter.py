"""Config exporters for different formats"""

import json
import yaml

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .config import Config


class ConfigExporter(ABC):
    """
    """

    @property
    @abstractmethod
    def comment_char(self) -> str:
        """
        """
        ...

    def get_descriptions(self, config: Config, config_dict: Dict[str, Any]) -> List[str]:
        """
        """
        descriptions = []
        for k in config_dict:
            key = config.get_key(k)
            descriptions.append(key.get_description() if key.get_description() is not None else "")

            if isinstance(config_dict[k], dict):
                subkey_config = key.to_pair().value
                subkey_descriptions = self.get_descriptions(subkey_config, config_dict[k])
                descriptions.extend(subkey_descriptions)

        return descriptions

    def add_descriptions(self, lines: List[str], descriptions: List[str]) -> List[str]:
        """
        """
        pad_to = max(len(l) for l in lines) + 1
        pad_line = lambda l: l + " " * (pad_to - len(l))
        concat_line = lambda l, d: pad_line(l) + " " + self.comment_char + " " + d
        return [concat_line(l, d) for l, d in zip(lines, descriptions)]

    @abstractmethod
    def export(self, config: Config) -> str:
        """
        """
        ...


class YamlExporter(ConfigExporter):
    """
    """

    comment_char = "#"
    
    def export(self, config: Config) -> str:
        config_dict = config.to_dict()
        descriptions = self.get_descriptions(config, config_dict)
        conf_str = yaml.dump(config_dict)
        return "\n".join(self.add_descriptions(conf_str.split("\n"), descriptions))


def create_exporter(exporter_type, **kwargs):
    """
    """
    return {
        "yaml": YamlExporter,
    }[exporter_type](**kwargs)
