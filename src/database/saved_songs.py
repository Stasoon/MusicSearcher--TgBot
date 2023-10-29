from typing import Literal

from .models import NewSongsCatalog, PopularSongsCatalog
from src.utils.vkpymusic import VkSong


def __get_model(name: Literal['popular', 'new']):
    match name:
        case 'popular': return PopularSongsCatalog
        case 'new': return NewSongsCatalog


def rewrite_catalog(catalog: Literal['popular', 'new'], songs: list[VkSong]):
    model = __get_model(catalog)
    model.delete().execute()

    for song in songs:
        model.create(
            title=song.title, artist=song.artist,
            owner_id=song.owner_id, audio_id=song.audio_id,
            duration=song.duration
        )


def get_songs_from_catalog(category: Literal['popular', 'new'], count: int, offset: int = 0) -> list:
    model = __get_model(category)
    songs = model.select().limit(count).offset(offset)
    return songs
