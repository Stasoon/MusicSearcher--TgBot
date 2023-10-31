from typing import List

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from src.utils.vkpymusic import AsyncService, TokenReceiver, VkSong


class VkMusicApi:
    service: AsyncService = None

    @classmethod
    def authorise(cls, login: str, password: str):
        # AsyncService.del_config()
        # token_receiver = TokenReceiver(login=login, password=password)
        #
        # if token_receiver.auth():
        #     token_receiver.get_token()
        #     token_receiver.save_to_config()

        cls.service = AsyncService.parse_config()

    @classmethod
    async def get_songs_by_text(cls, text: str, count: int = 10, offset: int = 0) -> list[VkSong]:
        songs = await cls.service.search_songs_by_text(text=text, count=count, offset=offset)
        return songs

    @classmethod
    async def get_song_by_id(cls, owner_id: int, song_id: int) -> VkSong:
        """ Получает песню из VK """
        song = await cls.service.get_song_by_id(owner_id=owner_id, audio_id=song_id)
        return song


class VkMusicParser:
    BASE_URL = 'https://vk.com/audio?block={}'

    async def get_chart_songs(self) -> List[VkSong]:
        return await self.__parse_songs(block_name='chart')

    async def get_new_songs(self) -> List[VkSong]:
        return await self.__parse_songs(block_name='new_songs')

    async def __parse_songs(self, block_name: str) -> List[VkSong]:
        async with async_playwright() as parser:
            browser = await parser.chromium.launch()
            page = await browser.new_page()
            await page.goto(self.BASE_URL.format(block_name))

            await page.wait_for_selector('.audio_row__inner', state='visible')
            content = await page.content()
            await browser.close()

        return self.parse_songs_from_content(content)

    def parse_songs_from_content(self, content: str) -> List[VkSong]:
        songs = []
        soup = BeautifulSoup(content, 'html.parser')
        song_elements = soup.find_all('div', class_='audio_row_content')

        for song_element in song_elements:
            try:
                song = self.__get_song_from_element_by_bs4(song_element)
                songs.append(song)
            except (TypeError, ValueError) as e:
                continue

        return songs

    def __get_song_from_element_by_bs4(self, song_element) -> VkSong:
        title_element = song_element.find('a', class_='audio_row__title_inner')
        title = title_element.text

        href = title_element['href']
        owner_id, song_id = map(int, href.replace(f'/audio-', '').split('_'))

        artist_element = song_element.find('div', class_='audio_row__performers')
        artist = artist_element.text

        duration_element = song_element.find('div', class_='audio_row__duration')
        duration_str = duration_element.text
        duration = self.__get_seconds_from_duration(duration_str)

        return VkSong(title=title, artist=artist, owner_id=owner_id, audio_id=song_id, duration=duration)

    @staticmethod
    def __get_seconds_from_duration(duration: str, splitter: str = ':') -> int:
        parts = duration.split(splitter)
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            seconds = int(parts[0])
            return seconds
