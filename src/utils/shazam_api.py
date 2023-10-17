import requests
from shazamio import Shazam, Serialize
from shazamio.schemas.models import ResponseTrack


async def recognize_song(file_url: str) -> ResponseTrack:
    """ Получает информацию о треке по url """
    response = requests.get(file_url)
    print(file_url)
    print('файл получен')

    shazam = Shazam()
    out = await shazam.recognize_song(response.content)
    song = Serialize.full_track(data=out)

    return song


