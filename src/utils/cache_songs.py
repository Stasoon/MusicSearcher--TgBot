import hashlib
import json
import datetime
from typing import List, Union, Literal, Type

import redis

from peewee import CharField, TextField, DateTimeField, IntegrityError
from src.database.models import _BaseModel
from src.utils import Song
from src.utils.vkpymusic import Playlist

redis_client = redis.Redis()


class CachedInstance(_BaseModel):
    key = CharField(unique=True)
    data = TextField()


class CachedRequest(_BaseModel):
    query_hash = CharField(unique=True)
    song_ids = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)


def hash_str(s: str):
    return hashlib.md5(s.lower().replace('\n', ' ').encode()).hexdigest()


def get_song_key(owner_id: int, song_id: int):
    return f"{owner_id}_{song_id}"


def get_playlist_key(owner_id: int, playlist_id: int):
    return f"playlist_{playlist_id}_{owner_id}"


def cache_instance(key: str, instance: Song | Playlist):
    song_data = json.dumps(instance.to_dict())
    instance = CachedInstance.get_or_none(key=key)

    if not instance:
        CachedInstance.create(key=key, data=song_data)

    return key


def cache_request(q: str, instances: list[Song | Playlist], instance_type: Literal['song', 'playlist']):
    """ Сохраняет песни, полученные из запроса, и ключи песен """
    query_hash = hash_str(q)
    if instance_type == 'song':
        ids = [cache_instance(get_song_key(song.owner_id, song.song_id), song) for song in instances]
    else:
        ids = [
            cache_instance(get_playlist_key(playlist.owner_id, playlist.playlist_id), playlist)
            for playlist in instances
        ]

    song_ids_json = json.dumps(ids)

    try:
        CachedRequest.create(query_hash=query_hash, song_ids=song_ids_json)
    except IntegrityError:
        cached_request = CachedRequest.get(CachedRequest.query_hash == query_hash)
        cached_request.song_ids = song_ids_json
        cached_request.save()


def get_cached_instance(key: str, instance_type: Type[Song] | Type[Playlist]) -> Song | Playlist | None:
    instance = CachedInstance.get_or_none(CachedInstance.key == key)
    if instance:
        return instance_type.from_json(json.loads(instance.data))
    return None


def get_cached_songs(keys) -> List[Song]:
    """ Получает песни из redis по ключам формата "owner_id_audio_id" """
    songs = []
    for key in keys:
        song = get_cached_instance(key, Song)
        if song:
            songs.append(song)
    return songs


def get_cached_songs_for_request(
        q: str, offset: int = 0, count: int = 10, query_hashed: bool = False
) -> tuple[int, Union[datetime.date, None], list[Song]] | tuple[int, None, None]:

    query_hash = hash_str(q) if not query_hashed else q
    data = CachedRequest.get_or_none(query_hash=query_hash)

    if data:
        song_keys = json.loads(data.song_ids)
        song_count = len(song_keys)
        songs = get_cached_songs(song_keys[offset:count+offset])

        return song_count, data.timestamp, songs
    return 0, None, None
