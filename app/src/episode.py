"""set metadata to episodes"""

from datetime import datetime

from src.connect import Jellyfin, TubeArchivist, clean_overview
from src.static_types import TAVideo


class Episode:
    """interact with an single episode"""

    def __init__(self, youtube_id: str, jf_id: str):
        self.youtube_id: str = youtube_id
        self.jf_id: str = jf_id

    def get_ta_video(self) -> TAVideo:
        """get ta metadata"""
        ta_video: TAVideo = TubeArchivist().get_video(self.youtube_id)
        return ta_video

    def sync(self, ta_video: TAVideo) -> None:
        """sync episode metadata"""
        self.update_metadata(ta_video)
        self.update_artwork(ta_video)

    def update_metadata(self, ta_video: TAVideo) -> None:
        """update jellyfin metadata from item_id"""
        published: str = ta_video["published"]
        published_date: datetime = datetime.fromisoformat(published)
        data: dict = {
            "Id": self.jf_id,
            "Name": ta_video.get("title"),
            "Genres": [],
            "Tags": [],
            "ProductionYear": published_date.year,
            "ProviderIds": {},
            "ParentIndexNumber": published_date.year,
            "PremiereDate": published_date.isoformat(),
            "Overview": self._get_desc(ta_video),
            "Studios": [{"Name": "YouTube"}],
        }
        path: str = f"Items/{self.jf_id}"
        Jellyfin().post(path, data)

    def update_artwork(self, ta_video: TAVideo) -> None:
        """update episode artwork in jf"""
        thumb_path: str = ta_video["vid_thumb_url"]
        thumb_base64: bytes = TubeArchivist().get_thumb(thumb_path)
        path: str = f"Items/{self.jf_id}/Images/Primary"
        Jellyfin().post_img(path, thumb_base64)

    def _get_desc(self, ta_video: TAVideo) -> str | bool:
        """get description"""
        raw_desc: str = ta_video["description"]
        if not raw_desc:
            return False

        desc_clean: str = clean_overview(raw_desc)
        return desc_clean
