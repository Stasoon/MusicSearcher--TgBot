import re
from dataclasses import dataclass


@dataclass
class VkSong:
    title: str
    artist: str
    duration: int
    song_id: int
    owner_id: int
    url: str = None

    def __str__(self):
        return f"{self.artist} - {self.title}"

    def to_dict(self) -> dict:
        return self.__dict__

    def to_safe(self):
        def safe_format(string):
            safe_string = re.sub(r"[^A-zА-я0-9+\s]", "", string)
            return safe_string

        self.title = safe_format(self.title)
        self.artist = safe_format(self.artist)

    @classmethod
    def from_json(cls, item):
        title = str(item["title"])
        artist = str(item["artist"])
        duration = int(item["duration"])
        track_id = int(item["id"])
        owner_id = int(item["owner_id"])
        url = str(item["url"])

        song = cls(title, artist, duration, track_id, owner_id, url)
        return song
