"""handle config file"""

import json
import os

from src.static_types import ConfigType


def get_config() -> ConfigType:
    """get connection config"""
    
    if os.path.exists("config.json"):
        print("config.json file found, skipping environment variables")
        with open("config.json", "r", encoding="utf-8") as f:
            config_content: ConfigType = json.loads(f.read())
        return config_content
    elif "TA_URL" in os.environ:
        print("Environment variables found, continuing")
        data = {}
        data['ta_video_path'] = os.getenv('TA_VIDEO_PATH', '/youtube')
        data['ta_url'] = os.getenv('TA_URL')
        data['ta_token'] = os.getenv('TA_TOKEN')
        data['jf_url'] = os.getenv('JF_URL')
        data['jf_token'] = os.getenv('JF_TOKEN')
        config_content: ConfigType = json.loads(json.dumps(data))
        return config_content
    else:
        raise ValueError("No config.json or environment variable found, exiting")