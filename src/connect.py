"""handle connections"""

import base64
import os

import requests

from src.config import get_config
from src.static_types import ConfigType, TAVideo

CONFIG: ConfigType = get_config()


class Jellyfin:
    """connect to jellyfin"""

    headers: dict = {
        "Authorization": "MediaBrowser Token=" + CONFIG["jf_token"]
    }
    base: str = CONFIG["jf_url"]

    def get(self, path: str) -> dict:
        """make a get request"""
        url: str = f"{self.base}/{path}"
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.ok:
            return response.json()

        print(response.text)
        return {}

    def post(self, path: str, data: dict | bool) -> None:
        """make a post request"""
        url: str = f"{self.base}/{path}"
        response = requests.post(
            url, headers=self.headers, json=data, timeout=10
        )
        if not response.ok:
            print(response.text)

    def post_img(self, path: str, thumb_base64: bytes) -> None:
        """set image"""
        url: str = f"{self.base}/{path}"
        new_headers: dict = self.headers.copy()
        new_headers.update({"Content-Type": "image/jpeg"})
        response = requests.post(
            url, headers=new_headers, data=thumb_base64, timeout=10
        )
        if not response.ok:
            print(response.text)

    def ping(self) -> None:
        """ping the server"""
        response = self.get("Users")
        if not response:
            raise ConnectionError("failed to connect to jellyfin")

        print("[connection] verified jellyfin connection")


class TubeArchivist:
    """connect to Tube Archivist"""

    ta_token: str = CONFIG["ta_token"]
    headers: dict = {"Authorization": f"Token {ta_token}"}
    base: str = CONFIG["ta_url"]

    def get(self, path: str) -> TAVideo:
        """get document from ta"""
        url: str = f"{self.base}/api/{path}"
        response = requests.get(url, headers=self.headers, timeout=10)

        if response.ok:
            response_json = response.json()
            if "data" in response_json:
                return response.json().get("data")

            return response.json()

        raise ValueError(f"video not found in TA: {path}")

    def get_thumb(self, path: str) -> bytes:
        """get encoded thumbnail from ta"""
        url: str = CONFIG["ta_url"] + path
        response = requests.get(
            url, headers=self.headers, stream=True, timeout=10
        )
        base64_thumb: bytes = base64.b64encode(response.content)

        return base64_thumb

    def ping(self) -> None:
        """ping tubearchivist server"""
        response = self.get("ping/")
        if not response:
            raise ConnectionError("failed to connect to tube archivist")

        print("[connection] verified tube archivist connection")


def env_check() -> None:
    """check if ta_video_path is accessible"""
#    if not os.path.exists("config.json"):
#        raise FileNotFoundError("config.json file not found")
    if not CONFIG["ta_url"]:
        raise ValueError("TA_URL not set")
    else:
        print("TA_URL =", CONFIG["ta_url"])

    if not CONFIG["ta_token"]:
        raise ValueError("TA_TOKEN not set")
    else:
        print("TA_TOKEN =", CONFIG["ta_token"])

    if not CONFIG["jf_url"]:
        raise ValueError("JF_URL not set")
    else:
        print("JF_URL =", CONFIG["jf_url"])

    if not CONFIG["jf_token"]:
        raise ValueError("JF_TOKEN not set")
    else:
        print("JF_TOKEN =", CONFIG["jf_token"])

    if not os.path.exists(CONFIG["ta_video_path"]):
        raise FileNotFoundError("failed to access ta_video_path", CONFIG["ta_video_path"])


def clean_overview(overview_raw: str) -> str:
    """parse and clean raw overview text"""
    if len(overview_raw) > 500:
        overview_raw = overview_raw[:500] + " ..."

    desc_clean: str = overview_raw.replace("\n", "<br>")

    return desc_clean
