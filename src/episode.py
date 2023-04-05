"""set metadata to episodes"""

from datetime import datetime

from src.connect import Jellyfin, TubeArchivist


class Episode:
    """interact with an single episode"""

    def __init__(self, youtube_id, jf_id):
        self.youtube_id = youtube_id
        self.jf_id = jf_id

    def sync(self):
        """sync episode metadata"""
        ta_video = self.get_ta_video()
        self.update_metadata(ta_video)
        self.update_artwork(ta_video)

    def get_ta_video(self):
        """get video metadata from ta"""
        path = f"/video/{self.youtube_id}"
        ta_video = TubeArchivist().get(path)

        return ta_video

    def update_metadata(self, ta_video):
        """update jellyfin metadata from item_id"""
        published = ta_video.get("published")
        published_date = datetime.strptime(published, "%d %b, %Y")
        data = {
            "Id": self.jf_id,
            "Name": ta_video.get("title"),
            "Genres": [],
            "Tags": [],
            "ProductionYear": published_date.year,
            "ProviderIds": {},
            "ParentIndexNumber": published_date.year,
            "PremiereDate": published_date.isoformat(),
            "Overview": self._get_desc(ta_video),
        }
        path = f"Items/{self.jf_id}"
        Jellyfin().post(path, data)

    def update_artwork(self, ta_video):
        """update episode artwork in jf"""
        thumb_base64 = TubeArchivist().get_thumb(ta_video.get("vid_thumb_url"))
        path = f"Items/{self.jf_id}/Images/Primary"
        Jellyfin().post_img(path, thumb_base64)

    def _get_desc(self, ta_video):
        """get description"""
        raw_desc = ta_video.get("description").replace("\n", "<br>")
        if len(raw_desc) > 500:
            return raw_desc[:500] + " ..."

        return raw_desc
