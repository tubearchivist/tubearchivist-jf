"""set metadata to shows"""

import base64
import os
from time import sleep

from src.config import get_config
from src.connect import Jellyfin, TubeArchivist
from src.episode import Episode


class Library:
    """grouped series"""

    def __init__(self):
        self.yt_collection = self.get_yt_collection()

    def get_yt_collection(self):
        """get collection id for youtube folder"""
        path = "Items?Recursive=true&includeItemTypes=Folder"
        folders = Jellyfin().get(path)
        for folder in folders["Items"]:
            if folder.get("Name").lower() == "youtube":
                return folder.get("Id")

        raise ValueError("youtube folder not found")

    def validate_series(self):
        """validate all series"""
        all_shows = self._get_all_series()
        for show in all_shows["Items"]:
            show_handler = Show(show)
            folders = show_handler.create_folders()
            show_handler.validate_show()
            show_handler.validate_episodes()
            show_handler.delete_folders(folders)

        self.set_collection_art()

    def _get_all_series(self):
        """get all shows indexed in jf"""
        path = f"Items?Recursive=true&IncludeItemTypes=Series&fields=ParentId,Path&ParentId={self.yt_collection}"  # noqa: E501
        all_shows = Jellyfin().get(path)

        return all_shows

    def set_collection_art(self):
        """set collection ta art"""
        with open("assets/collection-art.jpg", "rb") as f:
            asset = f.read()

        folders = Jellyfin().get("Library/MediaFolders")
        for folder in folders["Items"]:
            if folder.get("Name").lower() == "youtube":
                jf_id = folder.get("Id")
                path = f"Items/{jf_id}/Images/Primary"
                Jellyfin().post_img(path, base64.b64encode(asset))


class Show:
    """interact with a single show"""

    def __init__(self, show):
        self.show = show

    def _get_all_episodes(self):
        """get all episodes of show"""
        series_id = self.show.get("Id")
        path = f"Shows/{series_id}/Episodes?fields=Path"
        all_episodes = Jellyfin().get(path)

        return all_episodes["Items"]

    def _get_expected_seasons(self):
        """get all expected seasons"""
        episodes = self._get_all_episodes()
        all_years = {os.path.split(i["Path"])[-1][:4] for i in episodes}

        return all_years

    def _get_existing_seasons(self):
        """get all seasons indexed of series"""
        series_id = self.show.get("Id")
        path = f"Shows/{series_id}/Seasons"
        all_seasons = Jellyfin().get(path)

        return [str(i.get("IndexNumber")) for i in all_seasons["Items"]]

    def create_folders(self):
        """create season folders if needed"""
        all_expected = self._get_expected_seasons()
        all_existing = self._get_existing_seasons()

        base = get_config().get("ta_video_path")
        channel_name = os.path.split(self.show["Path"])[-1]
        folders = []
        for year in all_expected:
            if year not in all_existing:
                path = os.path.join(base, channel_name, year)
                os.mkdir(path)
                folders.append(path)

        self._wait_for_seasons()
        return folders

    def delete_folders(self, folders):
        """delete temporary folders created"""
        for folder in folders:
            os.removedirs(folder)

    def _wait_for_seasons(self):
        """wait for seasons to be created"""
        jf_id = self.show["Id"]
        path = f"Items/{jf_id}/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default"  # noqa: E501
        Jellyfin().post(path, False)
        for _ in range(12):
            all_existing = set(self._get_existing_seasons())
            all_expected = self._get_expected_seasons()
            if all_expected.issubset(all_existing):
                return

            print(f"[setup][{jf_id}] waiting for seasons to be created")
            sleep(5)

        raise TimeoutError("timeout reached for creating season folder")

    def validate_show(self):
        """set show metadata"""
        ta_channel = self._get_ta_channel()
        self.update_metadata(ta_channel)
        self.update_artwork(ta_channel)

    def _get_ta_channel(self):
        """get ta channel metadata"""
        episode = self._get_all_episodes()[0]
        youtube_id = os.path.split(episode["Path"])[-1][9:20]
        path = f"/video/{youtube_id}"
        ta_video = TubeArchivist().get(path)

        return ta_video.get("channel")

    def update_metadata(self, ta_channel):
        """update channel metadata"""
        path = "Items/" + self.show["Id"]
        data = {
            "Id": self.show["Id"],
            "Name": ta_channel.get("channel_name"),
            "Overview": ta_channel.get("channel_description"),
            "Genres": [],
            "Tags": [],
            "ProviderIds": {},
        }
        Jellyfin().post(path, data)

    def update_artwork(self, ta_channel):
        """set channel artwork"""
        jf_id = self.show["Id"]
        jf_handler = Jellyfin()
        primary = TubeArchivist().get_thumb(ta_channel["channel_thumb_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Primary", primary)
        jf_handler.post_img(f"Items/{jf_id}/Images/Logo", primary)
        banner = TubeArchivist().get_thumb(ta_channel["channel_banner_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Banner", banner)
        tvart = TubeArchivist().get_thumb(ta_channel["channel_tvart_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Backdrop", tvart)

    def validate_episodes(self):
        """sync all episodes"""
        all_episodes = self._get_all_episodes()
        for video in all_episodes:
            youtube_id = os.path.split(video["Path"])[-1][9:20]
            jf_id = video["Id"]
            Episode(youtube_id, jf_id).sync()
