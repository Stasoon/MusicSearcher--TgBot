import os
import random
import configparser

import aiohttp
from loguru import logger

from .VkSong import VkSong


class AsyncService:
    def __init__(self, token: str):
        self.__token = token

    @property
    def user_agent(self) -> str:
        agents = (
        'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)',
        'KateMobileAndroid/56 lite-460 (Android 6.0; SDK 23; x86; unknown Android SDK built for x86; ru)',
        'KateMobileAndroid/56 (Android 9.2; SDK 22; x86; unknown Android SDK built for x64; fr)',
        'KateMobileAndroid/56 lite-640 (iOS 17; SDK 20; x64; unknown Android SDK built for x64; ru)',
        'KateMobileAndroid/56 (iOS 18; SDK 20; x64; unknown Android SDK built for x64; fr)',
        'KateMobileAndroid/56 lite-460 (iOS 15; SDK 20; x64; unknown Android SDK built for x86; en)',
        )
        return random.choice(agents)

    @classmethod
    def parse_config(cls, filename: str = "config_vk.ini"):
        """
        Create an instance of Service from config.

        Args:
            filename (str): Filename of config (default value = "config_vk.ini").
        """
        dirname = os.path.dirname(__file__)
        configfile_path = os.path.join(dirname, filename)

        try:
            config = configparser.ConfigParser()
            config.read(configfile_path, encoding="utf-8")
            token = config["VK"]["token_for_audio"]

            return AsyncService(token=token)
        except Exception as e:
            logger.warning(e)

    @staticmethod
    def del_config(filename: str = "config_vk.ini"):
        """
        Delete config created by 'TokenReceiver'.

        Args:
            filename (str): Filename of config (default value = "config_vk.ini").
        """
        dirname = os.path.dirname(__file__)
        configfile_path = os.path.join(dirname, filename)

        try:
            os.remove(configfile_path)
            logger.info("Config successful deleted!")
        except Exception as e:
            logger.warning(e)

    ##########################
    # COMMON REQUEST FOR AUDIO

    async def __get_response_content(
        self, method: str, params: list[tuple[str, str or int]]
    ) -> dict:
        api_url = f"https://api.vk.com/method/audio.{method}"
        api_parameters = [
            ("access_token", self.__token),
            ("https", 1),
            ("lang", "ru"),
            ("extended", 1),
            ("v", "5.131"),
        ]

        for pair in params:
            api_parameters.append(pair)

        headers = {"User-Agent": self.user_agent}
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=api_parameters, headers=headers) as response:
                content = await response.json()
                return content

    ##############
    # ANY REQUESTS

    async def __get(
        self,
        user_id: int,
        count: int = 100,
        offset: int = 0
    ) -> dict:
        params = [
            ("owner_id", user_id),
            ("count", count),
            ("offset", offset),
        ]
        return await self.__get_response_content("get", params)

    async def __search(self, text: str, count: int = 10, offset: int = 0) -> dict:
        params = [
            ("q", text),
            ("count", count),
            ("offset", offset),
            ("sort", 2),  # сортировка - по популярности
            ("autocomplete", 1)  # исправлять ошибки
        ]
        return await self.__get_response_content("search", params)

    ############
    # CONVERTERS

    async def __response_to_songs(self, response_content: dict):
        try:
            items = response_content["response"]["items"]
        except (KeyError, TypeError):
            items = response_content["response"]

        songs: list[VkSong] = []
        for item in items:
            song = VkSong.from_json(item)
            songs.append(song)
        return songs

    ##############
    # MAIN METHODS

    async def get_song_by_id(self, owner_id: int, audio_id: int):
        params = [
            ("audios", f"{owner_id}_{audio_id}")
        ]

        try:
            content = await self.__get_response_content(method='getById', params=params)
            content = content['response'][0]
            song = VkSong.from_json(content)
        except Exception as e:
            logger.error(e)
            return
        return song

    async def search_songs_by_text(
        self, text: str, count: int = 3, offset: int = 0
    ) -> list[VkSong] | None:
        """
        Search songs by text/query.

        Args:
            text (str):   Text of query. Can be title of song, author, etc.
            count (int):  Count of resulting songs (for VK API: default/max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[VkSong]: List of songs.
        """
        try:
            response = await self.__search(text, count, offset)
            songs = await self.__response_to_songs(response)
        except Exception as e:
            logger.error(e)
            return

        if len(songs) == 0:
            return None
        else:
            return songs

    async def get_popular(self, count: int = 10, offset: int = 0):
        params = [
            ("count", count),
            ("offset", offset),
            ("only_eng", 0),
        ]
        response = await self.__get_response_content(method='getPopular', params=params)
        songs = await self.__response_to_songs(response)
        return songs
