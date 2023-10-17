import io
import requests

from src.utils.vkpymusic import TokenReceiver, Service, Song

# import vk_api
# from vk_api.audio import VkAudio
# vk = vk_api.VkApi(login='+79781685372', password='.barN15sVA/', app_id=2685278)
# vk.auth()
# audio = VkAudio(vk)


class VkMusicApi:
    service = None

    @classmethod
    def authorise(cls, login: str, password: str):
        Service.del_config()
        token_receiver = TokenReceiver(login=login, password=password)

        if token_receiver.auth():
            token_receiver.get_token()
            token_receiver.save_to_config()

        cls.service = Service.parse_config()

    @classmethod
    def get_songs_by_text(cls, text: str, count: int = 10, offset: int = 0) -> list[Song]:
        # s = audio.search(q=text, count=count, offset=offset)
        # print([i for i in s])
        songs = cls.service.search_songs_by_text(text=text, count=count, offset=offset)
        return songs

    @classmethod
    def get_song_by_id(cls, owner_id: int, song_id: int) -> Song:
        # cover = (audio.get_audio_by_id(owner_id, song_id)).get('track_covers')[1]
        return cls.service.get_song_by_id(owner_id=owner_id, audio_id=song_id)

    @classmethod
    def get_new_songs(cls, offset: int = 0):
        # songs = audio.get_news_iter(offset=offset)
        # print([i for i in songs])
        pass

    @classmethod
    def get_popular_songs(cls, count: int = 10, offset: int = 0):
        songs = cls.service.get_popular(count=count, offset=offset)
        return songs
