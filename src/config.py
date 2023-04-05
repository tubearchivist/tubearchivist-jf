"""handle config file"""

import json


def get_config():
    """get connection config"""
    with open("config.json", "r", encoding="utf-8") as f:
        config_content = json.loads(f.read())

    return config_content
