from .models import SongCache


def save_song_if_not_cached(song_id: int, owner_id: int, file_id: str) -> bool:
    existing_record = SongCache.get_or_none(song_id=song_id, owner_id=owner_id)
    if existing_record:
        return False
    SongCache.create(song_id=song_id, owner_id=owner_id, file_id=file_id)
    return True


def get_song_file_id(song_id: int, owner_id: int) -> str | None:
    song_hash = SongCache.get_or_none(song_id=song_id, owner_id=owner_id)
    return song_hash.file_id if song_hash else None


def get_cached_songs_count() -> int:
    return SongCache.select().count()
