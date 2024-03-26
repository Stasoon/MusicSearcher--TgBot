from dataclasses import dataclass


@dataclass
class Playlist:
    title: str
    photo: str
    count: int
    access_key: str
    playlist_id: int
    owner_id: int

    def __repr__(self):
        return self.title

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_json(cls, item):
        title = str(item["title"])
        #description = str(item["description"])

        if item.get("thumbs"):
            photo = str(item["thumbs"][0]["photo_1200"])
        elif item.get('photo'):
            try:
                photo = str(item["photo"]["photo_1200"])
            except TypeError:
                photo = str(item["photo"])
        else:
            photo = None

        count = int(item["count"])
        owner_id = int(item["owner_id"])
        playlist_id = int(item["id"]) if item.get('id') else int(item['playlist_id'])
        access_key = str(item["access_key"])

        playlist = cls(
            playlist_id=playlist_id, owner_id=owner_id,
            title=title, #description=description,
            photo=photo, count=count, access_key=access_key
        )
        return playlist
