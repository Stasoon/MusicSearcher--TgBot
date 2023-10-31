<<<<<<< HEAD
import random

import aiohttp
from shazamio import Shazam, Serialize
from shazamio.schemas.models import TrackInfo
from shazamio.user_agent import USER_AGENTS
from typing import Literal
=======
import requests
from shazamio import Shazam, Serialize
from shazamio.schemas.models import ResponseTrack
>>>>>>> parent of 39c5186 (Work)


async def recognize_song(file_url: str) -> ResponseTrack:
    """ Получает информацию о треке по url """
<<<<<<< HEAD
    async with aiohttp.ClientSession(headers={"User-Agent": random.choice(USER_AGENTS)}) as session:
        async with session.get(file_url) as response:
            data = await response.read()
=======
    response = requests.get(file_url)
    print(file_url)
    print('файл получен')
>>>>>>> parent of 39c5186 (Work)

    shazam = Shazam()
    out = await shazam.recognize_song(response.content)
    song = Serialize.full_track(data=out)

    return song


