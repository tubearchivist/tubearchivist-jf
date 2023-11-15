"""describe types"""

from typing import TypedDict


class ConfigType(TypedDict):
    """describes the confic dict"""

    ta_video_path: str
    ta_url: str
    ta_token: str
    jf_url: str
    jf_token: str
    jf_folder: str | None


class TAChannel(TypedDict):
    """describes channel from TA API"""

    channel_name: str
    channel_description: str
    channel_thumb_url: str
    channel_banner_url: str
    channel_tvart_url: str


class TAVideo(TypedDict):
    """describes video from TA API"""

    published: str
    title: str
    vid_thumb_url: str
    description: str
    channel: TAChannel


class JFShow(TypedDict):
    """describes a show from JF API"""

    Id: str
    Path: str
    Name: str


class JFEpisode(TypedDict):
    """describes an episode in JF API"""

    Id: str
    Path: str
    Studios: list
