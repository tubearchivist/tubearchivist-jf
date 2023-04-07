"""set metadata to shows"""

import base64
import os
from time import sleep

from src.config import get_config
from src.connect import Jellyfin, TubeArchivist
from src.episode import Episode
from src.static_types import JFEpisode, JFShow, TAChannel, TAVideo


class Library:
    """grouped series"""

    COLLECTION_ART = "assets/collection-art.jpg"

    def __init__(self) -> None:
        self.yt_collection: str = self.get_yt_collection()

    def get_yt_collection(self) -> str:
        """get collection id for youtube folder"""
        path: str = "Items?Recursive=true&includeItemTypes=Folder"
        folders: dict = Jellyfin().get(path)
        for folder in folders["Items"]:
            if folder.get("Name").lower() == "youtube":
                return folder.get("Id")

        raise ValueError("youtube folder not found")

    def validate_series(self) -> None:
        """validate all series"""
        all_shows: list[JFShow] = self._get_all_series()["Items"]
        for show in all_shows:
            show_handler = Show(show)
            folders: list[str] = show_handler.create_folders()
            show_handler.validate_show()
            show_handler.validate_episodes()
            show_handler.delete_folders(folders)

        collection_id: str = self._get_collection()
        self.set_collection_art(collection_id)
        self.refresh_collection(collection_id)

    def _get_all_series(self) -> dict:
        """get all shows indexed in jf"""
        path: str = f"Items?Recursive=true&IncludeItemTypes=Series&fields=ParentId,Path&ParentId={self.yt_collection}"  # noqa: E501
        all_shows: dict = Jellyfin().get(path)

        return all_shows

    def _get_collection(self) -> str:
        """get youtube collection id"""
        folders: dict = Jellyfin().get("Library/MediaFolders")
        for folder in folders["Items"]:
            if folder.get("Name").lower() == "youtube":
                return folder["Id"]

        raise ValueError("youtube collection folder not found")

    def set_collection_art(self, collection_id: str) -> None:
        """set collection ta art"""
        with open(self.COLLECTION_ART, "rb") as f:
            asset: bytes = f.read()

        path: str = f"Items/{collection_id}/Images/Primary"
        Jellyfin().post_img(path, base64.b64encode(asset))

    def refresh_collection(self, collection_id: str) -> None:
        """trigger collection refresh"""
        path: str = f"Items/{collection_id}/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default"  # noqa: E501
        Jellyfin().post(path, False)


class Show:
    """interact with a single show"""

    def __init__(self, show: JFShow):
        self.show: JFShow = show

    def _get_all_episodes(self) -> list[JFEpisode]:
        """get all episodes of show"""
        series_id: str = self.show["Id"]
        path: str = f"Shows/{series_id}/Episodes?fields=Path"
        all_episodes = Jellyfin().get(path)

        return all_episodes["Items"]

    def _get_expected_seasons(self) -> set[str]:
        """get all expected seasons"""
        episodes: list[JFEpisode] = self._get_all_episodes()
        all_years: set[str] = {
            os.path.split(i["Path"])[-1][:4] for i in episodes
        }

        return all_years

    def _get_existing_seasons(self) -> list[str]:
        """get all seasons indexed of series"""
        series_id: str = self.show["Id"]
        path: str = f"Shows/{series_id}/Seasons"
        all_seasons: dict = Jellyfin().get(path)

        return [str(i.get("IndexNumber")) for i in all_seasons["Items"]]

    def create_folders(self) -> list[str]:
        """create season folders if needed"""
        all_expected: set[str] = self._get_expected_seasons()
        all_existing: list[str] = self._get_existing_seasons()

        base: str = get_config()["ta_video_path"]
        channel_name: str = os.path.split(self.show["Path"])[-1]
        folders: list[str] = []
        for year in all_expected:
            if year not in all_existing:
                path: str = os.path.join(base, channel_name, year)
                os.mkdir(path)
                folders.append(path)

        self._wait_for_seasons()
        return folders

    def delete_folders(self, folders: list[str]) -> None:
        """delete temporary folders created"""
        for folder in folders:
            os.removedirs(folder)

    def _wait_for_seasons(self) -> None:
        """wait for seasons to be created"""
        jf_id: str = self.show["Id"]
        path: str = f"Items/{jf_id}/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default"  # noqa: E501
        Jellyfin().post(path, False)
        for _ in range(12):
            all_existing: set[str] = set(self._get_existing_seasons())
            all_expected: set[str] = self._get_expected_seasons()
            if all_expected.issubset(all_existing):
                return

            print(f"[setup][{jf_id}] waiting for seasons to be created")
            sleep(5)

        raise TimeoutError("timeout reached for creating season folder")

    def validate_show(self) -> None:
        """set show metadata"""
        ta_channel: TAChannel = self._get_ta_channel()
        self.update_metadata(ta_channel)
        self.update_artwork(ta_channel)

    def _get_ta_channel(self) -> TAChannel:
        """get ta channel metadata"""
        episode: JFEpisode = self._get_all_episodes()[0]
        youtube_id: str = os.path.split(episode["Path"])[-1][9:20]
        path = f"/video/{youtube_id}"

        ta_video: TAVideo = TubeArchivist().get(path)
        ta_channel: TAChannel = ta_video["channel"]

        return ta_channel

    def update_metadata(self, ta_channel: TAChannel) -> None:
        """update channel metadata"""
        path: str = "Items/" + self.show["Id"]
        data = {
            "Id": self.show["Id"],
            "Name": ta_channel["channel_name"],
            "Overview": ta_channel["channel_description"],
            "Genres": [],
            "Tags": [],
            "ProviderIds": {},
        }
        Jellyfin().post(path, data)

    def update_artwork(self, ta_channel: TAChannel) -> None:
        """set channel artwork"""
        jf_id: str = self.show["Id"]
        jf_handler = Jellyfin()

        primary = TubeArchivist().get_thumb(ta_channel["channel_thumb_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Primary", primary)
        jf_handler.post_img(f"Items/{jf_id}/Images/Logo", primary)

        banner = TubeArchivist().get_thumb(ta_channel["channel_banner_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Banner", banner)

        tvart = TubeArchivist().get_thumb(ta_channel["channel_tvart_url"])
        jf_handler.post_img(f"Items/{jf_id}/Images/Backdrop", tvart)

    def validate_episodes(self) -> None:
        """sync all episodes"""
        all_episodes: list[JFEpisode] = self._get_all_episodes()
        for video in all_episodes:
            youtube_id: str = os.path.split(video["Path"])[-1][9:20]
            Episode(youtube_id, video["Id"]).sync()
