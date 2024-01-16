from pytube import YouTube


def get_download_link(url: str) -> tuple[str | None, str | None]:
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)

    video_streams = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc()

    # Выбираем первый видео-стрим с разрешением, которое не превышает 50 МБ
    max_size_mb = 50
    selected_stream = None

    for stream in video_streams:
        if stream.filesize / (1024 * 1024) <= max_size_mb:
            selected_stream = stream
            break
    return (yt.video_id, selected_stream.url) or (None, None)
