from .models import YoutubeVideo


def save(video_id: str, file_id: str) -> None:
    YoutubeVideo.get_or_create(video_id=video_id, file_id=file_id)


def get_video_or_none(video_id: str) -> YoutubeVideo | None:
    return YoutubeVideo.get(YoutubeVideo.video_id == video_id)
