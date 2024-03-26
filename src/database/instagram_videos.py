from .models import InstagramVideo


def save(video_id: str, file_id: str) -> None:
    try:
        InstagramVideo.get_or_create(video_id=video_id, file_id=file_id)
    except Exception:
        pass


def get_video_or_none(video_id: str) -> InstagramVideo | None:
    return InstagramVideo.get_or_none(InstagramVideo.video_id == video_id)
