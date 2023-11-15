"""handle config file"""

import json
import os
from typing import Literal

from src.static_types import ConfigType


def get_config() -> ConfigType:
    """get connection config"""
    config_content: ConfigType | Literal[False] = (
        get_config_file() or get_config_env()
    )
    if not config_content:
        raise ValueError("No config.json or environment variable found")

    return config_content


def get_config_file() -> ConfigType | Literal[False]:
    """read config file if available"""
    if os.path.exists("./config.json"):
        with open("./config.json", "r", encoding="utf-8") as f:
            config_content: ConfigType = json.loads(f.read())

        return config_content

    return False


def get_config_env() -> ConfigType | Literal[False]:
    """read config from environment"""
    if "TA_URL" in os.environ:
        config_content: ConfigType = {
            "ta_video_path": "/youtube",
            "ta_url": os.environ["TA_URL"],
            "ta_token": os.environ["TA_TOKEN"],
            "jf_url": os.environ["JF_URL"],
            "jf_token": os.environ["JF_TOKEN"],
            "jf_folder": os.environ['JF_FOLDER']
        }
        return config_content

    return False
