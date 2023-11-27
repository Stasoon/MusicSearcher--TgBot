import json
from typing import List, Union

import redis.asyncio as redis

from src.utils import Song


redis_client = redis.Redis()


async def cache_song(song: Song, ttl: int = 43200):
    json_data = json.dumps(song.to_dict())
    key = f"{song.owner_id}_{song.song_id}"
    await redis_client.setex(key, ttl, json_data)
    return key


async def cache_request(q: str, songs: list[Song], ttl: int = 43200):
    """ Сохраняет песни, полученные из запроса, и ключи песен """
    query_hash = str(hash(q))
    song_ids = [await cache_song(song) for song in songs]
    await redis_client.setex(name=query_hash, time=ttl, value=json.dumps(song_ids))


async def get_cached_song(key: str) -> Song | None:
    """ key: owner_id_song_id """
    data = await redis_client.get(key)
    if data:
        song_data = json.loads(data)
        song = Song.from_json(song_data)
        return song


async def get_cached_songs(keys) -> List[Song]:
    """ Получает песни из redis по ключам формата "owner_id_audio_id" """
    songs = []
    for key in keys:
        song = await get_cached_song(key)
        if song:
            songs.append(song)
    return songs


async def get_cached_songs_for_request(q: str, offset: int = 0, count: int = 10) -> tuple[int, Union[List[Song], None]]:
    query_hash = str(hash(q))
    data = await redis_client.get(name=query_hash)
    if data:
        song_keys = json.loads(data)
        songs = await get_cached_songs(song_keys)
        return len(songs), songs[offset:count+offset]
    return 0, None
