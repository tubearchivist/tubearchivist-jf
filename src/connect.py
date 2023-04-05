"""handle connections"""

import base64
import os

import requests

from src.config import get_config

CONFIG = get_config()


class Jellyfin:
    """connect to jellyfin"""

    headers = {"Authorization": "MediaBrowser Token=" + CONFIG["jf_token"]}
    base = CONFIG["jf_url"]

    def get(self, path):
        """make a get request"""
        url = f"{self.base}/{path}"
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.ok:
            return response.json()

        print(response.text)
        return False

    def post(self, path, data):
        """make a post request"""
        url = f"{self.base}/{path}"
        response = requests.post(
            url, headers=self.headers, json=data, timeout=10
        )
        if not response.ok:
            print(response.text)

    def post_img(self, path, thumb_base64):
        """set image"""
        url = f"{self.base}/{path}"
        new_headers = self.headers.copy()
        new_headers.update({"Content-Type": "image/jpeg"})
        response = requests.post(
            url, headers=new_headers, data=thumb_base64, timeout=10
        )
        if not response.ok:
            print(response.text)

    def ping(self):
        """ping the server"""
        path = "Users"
        response = self.get(path)
        if not response:
            raise ConnectionError("failed to connect to jellyfin")

        print("[connection] verified jellyfin connection")


class TubeArchivist:
    """connect to Tube Archivist"""

    headers = {"Authorization": "Token " + CONFIG.get("ta_token")}
    base = CONFIG["ta_url"]

    def get(self, path):
        """get document from ta"""
        url = f"{self.base}/api/{path}"
        response = requests.get(url, headers=self.headers, timeout=10)

        if response.ok:
            response_json = response.json()
            if "data" in response_json:
                return response.json().get("data")

            return response.json()

        print(response.text)
        return False

    def get_thumb(self, path):
        """get encoded thumbnail from ta"""
        url = CONFIG.get("ta_url") + path
        response = requests.get(
            url, headers=self.headers, stream=True, timeout=10
        )

        return base64.b64encode(response.content)

    def ping(self):
        """ping tubearchivist server"""
        response = self.get("ping/")
        if not response:
            raise ConnectionError("failed to connect to tube archivist")

        print("[connection] verified tube archivist connection")


def folder_check():
    """check if ta_video_path is accessible"""
    if not os.path.exists("config.json"):
        raise FileNotFoundError("config.json file not found")

    if not os.path.exists(CONFIG["ta_video_path"]):
        raise FileNotFoundError("failed to access ta_video_path")
