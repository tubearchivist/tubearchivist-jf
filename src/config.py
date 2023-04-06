"""handle config file"""

import json

from src.static_types import ConfigType


def get_config() -> ConfigType:
    """get connection config"""
    with open("config.json", "r", encoding="utf-8") as f:
        config_content: ConfigType = json.loads(f.read())

    return config_content
