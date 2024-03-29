import re
from dataclasses import dataclass

from .VkItem import VkItem


@dataclass
class Song(VkItem):
    title: str
    artist: str
    duration: int
    song_id: int
    owner_id: int
    url: str = None

    def __repr__(self):
        return f"{self.artist} - {self.title}"

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_json(cls, item):
        title = str(item["title"])
        artist = str(item["artist"])
        duration = int(item["duration"])
        track_id = int(item["id"]) if item.get('id') else item["song_id"]
        owner_id = int(item["owner_id"])
        url = str(item["url"])

        song = cls(
            song_id=track_id, owner_id=owner_id,
            title=title, artist=artist,
            duration=duration, url=url
        )
        return song

    def get_file_name(self) -> str:
        safe_name = re.sub(r"[^A-zА-я0-9+\s]", "", str(self))
        return f"{safe_name}.mp3"
