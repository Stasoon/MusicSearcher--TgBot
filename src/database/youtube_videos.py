from .models import YoutubeVideo


def save(video_id: str, file_id: str) -> None:
    try:
        YoutubeVideo.get_or_create(video_id=video_id, file_id=file_id)
    except Exception:
        pass


def get_video_or_none(video_id: str) -> YoutubeVideo | None:
    return YoutubeVideo.get_or_none(YoutubeVideo.video_id == video_id)
