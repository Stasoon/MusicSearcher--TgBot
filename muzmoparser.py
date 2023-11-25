from typing import List

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

from src.utils.vkpymusic.models.Song import Song
from src.utils.vkpymusic.models.Playlist import Playlist
from .CaptchaDecoder import BaseCaptchaDecoder
from .user_agents import get_vk_user_agent


# class Session:
#     def __init__(self, name: str, token_for_audio: str, captcha_decoder: BaseCaptchaDecoder):
#         self.name = name
#         self.__token = token_for_audio
#         self.captcha_decoder = captcha_decoder
#
#     ##########################
#     # COMMON REQUEST FOR AUDIO
#     async def __get_response_content(self, method: str, params: dict[str, str or int]) -> dict:
#         api_url = f"https://api.vk.com/method/audio.{method}"
#         api_parameters = [
#             ("access_token", self.__token),
#             ("https", 1),
#             ("lang", "ru"),
#             ("extended", 1),
#             ("v", "5.131"),
#             *[pair for pair in params.items()]
#         ]
#         headers = {"User-Agent": get_vk_user_agent()}
#
#         async with aiohttp.ClientSession() as session:
#             async with session.post(api_url, data=api_parameters, headers=headers) as response:
#                 content = await response.json()
#                 if error := content.get('error'):
#                     # Если ошибка - требование ввести капчу, повторяем запрос,
#                     # передавая старые параметры и данные решённой капчи
#                     if error.get('error_msg') == 'Captcha needed':
#                         captcha_sid = error.get('captcha_sid')
#                         captcha_url = error.get('captcha_img')
#                         captcha_bytes = await self.captcha_decoder.get_bytes_from_captcha_url(captcha_url)
#                         captcha_key = await self.captcha_decoder.get_captcha_key(captcha_bytes)
#                         params.update(captcha_sid=captcha_sid, captcha_key=captcha_key)
#                         return await self.__get_response_content(method, params=params)
#                 return content
#
#     ##############
#     # ANY REQUESTS
#
#     async def __get(
#         self,
#         owner_id: int,
#         count: int = 100,
#         offset: int = 0,
#         playlist_id: int or None = None,
#         access_key: str or None = None,
#     ) -> dict:
#         params = {
#             "owner_id": owner_id,
#             "count": count,
#             "offset": offset
#         }
#         if playlist_id:
#             params.update(album_id=playlist_id, access_key=access_key)
#         return await self.__get_response_content("get", params)
#
#     async def __search(self, text: str, count: int = 10, offset: int = 0) -> dict:
#         params = {
#             "q": text,
#             "count": count,
#             "offset": offset,
#             "sort": 2,  # сортировка - по популярности
#             "autocomplete": 0  # исправлять ошибки
#         }
#         return await self.__get_response_content("search", params)
#
#     ############
#     # CONVERTERS
#
#     @staticmethod
#     def __fetch_songs_from_response(response_content: dict) -> List[Song]:
#         try:
#             items = response_content["response"]["items"]
#         except (KeyError, TypeError):
#             items = response_content["response"]
#
#         songs = [Song.from_json(item) for item in items]
#         return songs
#
#     @staticmethod
#     def __fetch_playlists_from_response(response_content: dict) -> List[Playlist]:
#         try:
#             items = response_content["response"]["items"]
#         except (KeyError, TypeError):
#             items = response_content["response"]
#
#         playlists: list[Playlist] = [Playlist.from_json(item) for item in items]
#         return playlists
#
#     ##############
#     # MAIN METHODS
#
#     # region SONGS
#
#     async def get_song(self, owner_id: int, audio_id: int) -> Song | None:
#         params = {
#             "audios": f"{owner_id}_{audio_id}"
#         }
#         try:
#             content = await self.__get_response_content(method='getById', params=params)
#             content = content['response'][0]
#             song = Song.from_json(content)
#         except Exception as e:
#             logger.error(e)
#             return
#         return song
#
#     async def get_profile_songs(
#             self, user_id: int, count: int = 8, offset: int = 0
#     ) -> tuple[int, List[Song]]:
#         """
#         Поиск песен по owner/user id.
#         """
#         user_id = int(user_id)
#
#         try:
#             response = await self.__get(user_id, count, offset)
#             results_count = response['response']['count']
#             songs = self.__fetch_songs_from_response(response)
#         except Exception:
#             return 0, []
#         else:
#             return results_count, songs
#
#     async def search_songs_by_text(self, text: str, count: int = 8, offset: int = 0) -> tuple[int, List[Song]]:
#         """
#         Поиск песен по тексту.
#         """
#         try:
#             response = await self.__search(text, count, offset)
#             results_count = response['response']['count']
#             songs = self.__fetch_songs_from_response(response)
#         except Exception as e:
#             logger.error(e)
#             return 0, []
#
#         if not results_count or len(songs) == 0:
#             return 0, []
#         else:
#             return results_count, songs
#
#     async def get_playlist_songs(
#             self,
#             owner_id: int,
#             playlist_id: int,
#             access_key: str,
#             count: int = 8,
#             offset: int = 0,
#     ) -> List[Song]:
#         try:
#             response = await self.__get(
#                 owner_id=owner_id, playlist_id=playlist_id,
#                 access_key=access_key,
#                 count=count, offset=offset
#             )
#             songs = self.__fetch_songs_from_response(response)
#         except Exception as e:
#             logger.error(e)
#             return []
#         else:
#             return songs
#
#     async def get_profile_playlists(
#             self, user_id: int, count: int = 50, offset: int = 0
#     ) -> tuple[int, List[Playlist]]:
#         """
#         Поиск плейлистов по owner/user id.
#         """
#         params = {
#             "owner_id": user_id,
#             "count": count,
#             "offset": offset,
#         }
#         try:
#             content = await self.__get_response_content(method="getPlaylists", params=params)
#             results_count = content['response']['count']
#             playlists = self.__fetch_playlists_from_response(response_content=content)
#         except Exception as e:
#             logger.error(f"{e}")
#             return 0, []
#         else:
#             return results_count, playlists


class Session:
    def __init__(self, name: str, token_for_audio: str, captcha_decoder: BaseCaptchaDecoder):
        self.name = name
        self.__token = token_for_audio
        self.captcha_decoder = captcha_decoder

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
                    # Если ошибка - требование ввести капчу, повторяем запрос,
                    # передавая старые параметры и данные решённой капчи
                    if error.get('error_msg') == 'Captcha needed':
                        captcha_sid = error.get('captcha_sid')
                        captcha_url = error.get('captcha_img')
                        captcha_bytes = await self.captcha_decoder.get_bytes_from_captcha_url(captcha_url)
                        captcha_key = await self.captcha_decoder.get_captcha_key(captcha_bytes)
                        params.update(captcha_sid=captcha_sid, captcha_key=captcha_key)
                        return await self.__get_response_content(method, params=params)
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
            "autocomplete": 0  # исправлять ошибки
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

    def get_song_from_html(self, s):
        l_data = s.find(class_='track__info-l')
        song_id = int(l_data.get('href').replace('/song/', '')) if l_data.get('href') and l_data.get('href') != '#' else 0
        title = l_data.find(class_='track__title').get_text().strip()
        artist = l_data.find('div', class_='track__desc').get_text().strip()

        r_data = s.find('div', class_='track__info-r')
        url = r_data.find('a', class_='track__download-btn')['href']
        duration = r_data.find('div', 'track__time').find('div', 'track__fulltime').get_text()
        minutes, seconds = map(int, duration.split(':'))
        return Song(url=url, title=title, artist=artist, duration=seconds+minutes*60, song_id=song_id, owner_id=0)

    async def get_song(self, owner_id: int, audio_id: int) -> Song | None:
        print(audio_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://eu.hitmotop.com/song/{audio_id}') as resp:
                data = await resp.text()
        parser = BeautifulSoup(data, 'html.parser')
        s = parser.find('div', 'track__info')
        return self.get_song_from_html(s)

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
        url = f'https://eu.hitmotop.com/search?q={text}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                page_source = await response.text()

        parser = BeautifulSoup(page_source, 'html.parser')

        songs = []
        for s in parser.find_all('div', 'track__info'):
            songs.append(
                self.get_song_from_html(s)
            )

        return len(songs), songs[offset:count+offset]

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
