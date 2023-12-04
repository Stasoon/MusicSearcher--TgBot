from typing import List

import aiohttp
from loguru import logger

from src.utils.vkpymusic.models.Song import Song
from src.utils.vkpymusic.models.Playlist import Playlist
from .CaptchaDecoder import BaseCaptchaDecoder
from .user_agents import get_vk_user_agent


class CaptchaNeeded(Exception):
    def __init__(self, message="Требуется ввод капчи!"):
        self.message = message
        super().__init__(self.message)


class SessionAuthorizationFailed(Exception):
    def __init__(self, message: str, session_token: str):
        self.message = message
        self.session_token = session_token
        super().__init__(f"{self.message} \nТокен сессии: \n{session_token}")


class Session:
    def __init__(self, name: str, token_for_audio: str, captcha_decoder: BaseCaptchaDecoder):
        self.name = name
        self.__token = token_for_audio
        self.captcha_decoder = captcha_decoder

    async def __process_api_error(self, method, params, error: dict):
        # Если ошибка - требование ввести капчу, повторяем запрос,
        # передавая старые параметры и данные решённой капчи
        if error.get('error_msg') == 'Captcha needed':
            captcha_sid = error.get('captcha_sid')
            captcha_url = error.get('captcha_img')
            captcha_bytes = await self.captcha_decoder.get_bytes_from_captcha_url(captcha_url)
            captcha_key = await self.captcha_decoder.get_captcha_key(captcha_bytes)
            params.update(captcha_sid=captcha_sid, captcha_key=captcha_key)
            await self.__get_response_content(method, params=params)
            raise CaptchaNeeded
        # Ошибка авторизации
        elif error.get('error_code') == 5:
            raise SessionAuthorizationFailed(error.get('error_msg'), self.__token)

    ##########################
    # COMMON REQUEST FOR AUDIO
    async def __get_response_content(self, method: str, params: dict[str, str or int]) -> dict:
        api_url = f"https://api.vk.com/method/audio.{method}"
        api_parameters = [
            ("access_token", self.__token),
            ("https", 1),
            ("lang", "ru"),
            ("extended", 1),
            ("v", "5.131"),
            *[pair for pair in params.items()]
        ]
        headers = {"User-Agent": get_vk_user_agent()}

        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=api_parameters, headers=headers) as response:
                content = await response.json()
                if error := content.get('error'):
                    await self.__process_api_error(method=method, params=params, error=error)
                return content

    ##############
    # ANY REQUESTS

    async def __get(
        self,
        owner_id: int,
        count: int = 100,
        offset: int = 0,
        playlist_id: int or None = None,
        access_key: str or None = None,
    ) -> dict:
        params = {
            "owner_id": owner_id,
            "count": count,
            "offset": offset
        }
        if playlist_id:
            params.update(album_id=playlist_id, access_key=access_key)
        return await self.__get_response_content("get", params)

    async def __search(self, text: str, count: int = 10, offset: int = 0) -> dict:
        params = {
            "q": text,
            "count": count,
            "offset": offset,
            "sort": 2,  # сортировка - по популярности
            "autocomplete": 1  # исправлять ошибки
        }
        return await self.__get_response_content("search", params)

    ############
    # CONVERTERS

    @staticmethod
    def __fetch_songs_from_response(response_content: dict) -> List[Song]:
        try:
            items = response_content["response"]["items"]
        except (KeyError, TypeError):
            items = response_content["response"]

        songs = [Song.from_json(item) for item in items]
        return songs

    @staticmethod
    def __fetch_playlists_from_response(response_content: dict) -> List[Playlist]:
        try:
            items = response_content["response"]["items"]
        except (KeyError, TypeError):
            items = response_content["response"]

        playlists: list[Playlist] = [Playlist.from_json(item) for item in items]
        return playlists

    ##############
    # MAIN METHODS

    # region SONGS

    async def get_song(self, owner_id: int, audio_id: int) -> Song | None:
        params = {
            "audios": f"{owner_id}_{audio_id}"
        }
        try:
            content = await self.__get_response_content(method='getById', params=params)
            content = content['response'][0]
            song = Song.from_json(content)
        except Exception as e:
            logger.error(f"{e}")
            logger.error(e)
            return
        return song

    async def get_profile_songs(
            self, user_id: int, count: int = 8, offset: int = 0
    ) -> tuple[int, List[Song]]:
        """
        Поиск песен по owner/user id.
        """
        user_id = int(user_id)

        try:
            response = await self.__get(user_id, count, offset)
            results_count = response['response']['count']
            songs = self.__fetch_songs_from_response(response)
        except Exception:
            return 0, []
        else:
            return results_count, songs

    async def search_songs_by_text(self, text: str, count: int = 8, offset: int = 0) -> tuple[int, List[Song]]:
        """
        Поиск песен по тексту.
        """
        try:
            response = await self.__search(text, count, offset)
            results_count = response['response']['count']
            songs = self.__fetch_songs_from_response(response)
        except (CaptchaNeeded, SessionAuthorizationFailed) as e:
            raise e
        except Exception as e:
            logger.error(e)
            return 0, []

        if not results_count or len(songs) == 0:
            return 0, []
        else:
            return results_count, songs

    async def get_playlist_songs(
            self,
            owner_id: int,
            playlist_id: int,
            access_key: str,
            count: int = 8,
            offset: int = 0,
    ) -> List[Song]:
        try:
            response = await self.__get(
                owner_id=owner_id, playlist_id=playlist_id,
                access_key=access_key,
                count=count, offset=offset
            )
            songs = self.__fetch_songs_from_response(response)
        except Exception as e:
            logger.error(e)
            return []
        else:
            return songs

    async def get_profile_playlists(
            self, user_id: int, count: int = 50, offset: int = 0
    ) -> tuple[int, List[Playlist]]:
        """
        Поиск плейлистов по owner/user id.
        """
        params = {
            "owner_id": user_id,
            "count": count,
            "offset": offset,
        }
        try:
            content = await self.__get_response_content(method="getPlaylists", params=params)
            results_count = content['response']['count']
            playlists = self.__fetch_playlists_from_response(response_content=content)
        except Exception as e:
            logger.error(f"{e}")
            return 0, []
        else:
            return results_count, playlists
