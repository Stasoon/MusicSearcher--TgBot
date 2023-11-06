import random

import aiohttp
from shazamio import Shazam, Serialize
from shazamio.schemas.models import TrackInfo
from shazamio.user_agent import USER_AGENTS
from typing import Literal


async def recognize_song(file_url: str) -> TrackInfo:
    """ Получает информацию о треке по url """
    async with aiohttp.ClientSession(headers={"User-Agent": random.choice(USER_AGENTS)}) as session:
        async with session.get(file_url) as response:
            data = await response.read()

    shazam = Shazam()
    out = await shazam.recognize_song(data)
    song = Serialize.full_track(data=out).track
    try:
        song.photo_url = out['track']['images']['coverart']
    except (TypeError, KeyError):
        pass
    return song


# async def get_top_tracks_names(
#         country: Literal['RU'] = 'RU',
#         count: int = 10,
#         offset: int = 0
# ):
#     shazam = Shazam()
#     top_songs = await shazam.top_country_tracks(country_code=country, limit=count, offset=offset)
#     return (f"{song.get('title')} {song.get('subtitle')}" for song in top_songs['tracks'])
