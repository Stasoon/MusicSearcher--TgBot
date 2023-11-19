from typing import Literal

from peewee import IntegrityError

from .models import NewSongsCatalog, PopularSongsCatalog
from src.utils.vkpymusic import Song


def __get_model(name: Literal['popular', 'new']):
    match name:
        case 'popular': return PopularSongsCatalog
        case 'new': return NewSongsCatalog


def rewrite_catalog(catalog: Literal['popular', 'new'], songs: list[Song]):
    model = __get_model(catalog)
    model.delete().execute()

    for song in songs:
        try:
            model.create(
                title=song.title, artist=song.artist,
                owner_id=song.owner_id, song_id=song.song_id,
                duration=song.duration
            )
        except IntegrityError:
            continue


def get_songs_from_catalog(category: Literal['popular', 'new'], count: int, offset: int = 0) -> list:
    model = __get_model(category)
    songs = model.select().limit(count).offset(offset)
    return songs
