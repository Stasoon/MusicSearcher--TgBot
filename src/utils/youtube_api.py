from pytube import YouTube


async def get_download_link(url: str) -> str | None:
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    print(video.url)
    return video.url or None
