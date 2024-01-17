import json
from typing import List, Union

import redis

from src.utils import Song


redis_client = redis.Redis()


def cache_song(song: Song, ttl: int = 43200):
    json_data = json.dumps(song.to_dict())
    key = f"{song.owner_id}_{song.song_id}"
    redis_client.setex(key, ttl, json_data)
    return key


def cache_request(q: str, songs: list[Song], ttl: int = 43200):
    """ Сохраняет песни, полученные из запроса, и ключи песен """
    query_hash = str(hash(q.lower()))
    song_ids = [cache_song(song) for song in songs]
    redis_client.setex(name=query_hash, time=ttl, value=json.dumps(song_ids))


def get_cached_song(key: str) -> Song | None:
    """ key: owner_id_song_id """
    data = redis_client.get(key)
    if data:
        song_data = json.loads(data)
        song = Song.from_json(song_data)
        return song


def get_cached_songs(keys) -> List[Song]:
    """ Получает песни из redis по ключам формата "owner_id_audio_id" """
    songs = []
    for key in keys:
        song = get_cached_song(key)
        if song:
            songs.append(song)
    return songs


def get_cached_songs_for_request(
        q: str, offset: int = 0, count: int = 10, query_hashed: bool = False
) -> tuple[int, Union[List[Song], None]]:

    query_hash = str(hash(q.lower())) if not query_hashed else q
    data = redis_client.get(name=query_hash)

    if data:
        song_keys = json.loads(data)
        song_count = len(song_keys)
        songs = get_cached_songs(song_keys[offset:count+offset])
        return song_count, songs
    return 0, None
