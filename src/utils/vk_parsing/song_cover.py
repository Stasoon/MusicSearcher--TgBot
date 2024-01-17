import random

import vk_api
from vk_api.audio import VkAudio

from src.utils import logger
from src.utils.singleton import SingletonMeta


def two_factor():
    code = input('Write two factor auth code: ')
    return code, True


class VkSongCover(metaclass=SingletonMeta):
    sessions = []

    def make_auth(self, login: str, password: str) -> vk_api.VkApi | None:
        vk_session = vk_api.VkApi(login=login, password=password, app_id=2685278, auth_handler=two_factor)

        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            logger.error(error_msg)
            return None

        self.sessions.append(vk_session)
        return vk_session

    def get_cover_by_song_id(self, owner_id: int, song_id: int) -> str | None:
        if not self.sessions:
            return None

        try:
            audio = VkAudio(random.choice(self.sessions))
            song = audio.get_audio_by_id(owner_id=owner_id, audio_id=song_id)
            song_covers = song.get('track_covers')

            if not song_covers or len(song_covers) == 0:
                return None

            return song_covers[0]
        except Exception as e:
            logger.error(e)
            return None
