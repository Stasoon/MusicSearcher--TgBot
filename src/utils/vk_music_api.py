import asyncio
from cachetools import TTLCache

from playwright.async_api import async_playwright

from src.utils.vkpymusic import AsyncService, VkSong


class VkMusicApi:
    __instance = None
    services: dict[str, AsyncService] = {}
    service_cache = TTLCache(maxsize=50, ttl=4)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        VkMusicApi.__instance = None

    def add_service(self, client_name: str):
        # AsyncService.del_config()
        # token_receiver = TokenReceiver(client=client_name, login=login, password=password)
        #
        # if token_receiver.auth():
        #     token_receiver.get_token()
        #     token_receiver.save_to_config(f'{client_name}.ini')

        new_service = AsyncService.parse_config(f'{client_name}.ini')
        self.services[client_name] = new_service

    async def get_available_service(self) -> AsyncService:
        while True:
            # Неиспользованные сервисы
            not_used = [service_name for service_name in self.services if service_name not in self.service_cache]
            # Сервисы, в которых нет превышения лимита
            not_exceeded = [ser for ser in self.service_cache.keys() if self.service_cache.get(ser) < 3]
            available_services = not_used + not_exceeded

            # Если нет доступных сервисов, ждём пол секунды и пробуем снова
            if not available_services:
                await asyncio.sleep(1)
                continue
            # Если есть неиспользованные сервисы, берём первый из них
            if not_used:
                service_name = not_used[0]
                self.service_cache[service_name] = 0
            # Иначе берём наименее загруженный
            else:
                service_name = min(not_exceeded, key=self.service_cache.get)

            service = self.services[service_name]
            self.service_cache[service_name] += 1
            return service

    async def get_songs_by_text(self, text: str, count: int = 10, offset: int = 0) -> list[VkSong]:
        service = await self.get_available_service()
        songs = await service.search_songs_by_text(text=text, count=count, offset=offset)
        return songs

    async def get_song_by_id(self, owner_id: int, song_id: int) -> VkSong:
        """ Получает песню из VK """
        service = await self.get_available_service()
        song = await service.get_song_by_id(owner_id=owner_id, audio_id=song_id)
        return song


class VkMusicParser:
    BASE_URL = 'https://vk.com/audio'

    @classmethod
    async def get_chart_songs(cls):
        """
        Получает новые песни из чарта Vk.
        """
        return await cls.__parse_songs(block_name='chart')

    @classmethod
    async def get_new_songs(cls):
        """
        Получает новые песни из Vk.
        """
        return await cls.__parse_songs(block_name='new_songs')

    @classmethod
    async def __parse_songs(cls, block_name: str) -> list[VkSong]:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"{cls.BASE_URL}?block={block_name}")
            await page.wait_for_selector('.audio_row__inner')

            footer = await page.wait_for_selector('.footer_wrap')
            await footer.scroll_into_view_if_needed()
            await page.wait_for_timeout(2000)

            song_elements = await page.query_selector_all('.audio_row__inner')

            songs = []

            for song_element in song_elements:
                try:
                    song = await cls.__get_song_from_element(song_element)
                except (TypeError, ValueError):
                    continue
                songs.append(song)

            await browser.close()
            return songs

    @classmethod
    async def __get_song_from_element(cls, song_element) -> VkSong:
        title_element = await song_element.query_selector('.audio_row__title_inner')
        title = await title_element.inner_text()

        href = await title_element.get_attribute(name='href')
        owner_id, song_id = map(int, str(href).replace('/audio', '').split('_'))

        artist_element = await song_element.query_selector('.audio_row__performers')
        artist = await artist_element.inner_text()

        duration_element = await song_element.query_selector('.audio_row__duration')
        duration_str = await duration_element.inner_text()
        duration = cls.__get_seconds_from_duration(duration_str)

        song = VkSong(title=title, artist=artist, owner_id=owner_id, song_id=song_id, duration=duration)
        return song

    @staticmethod
    def __get_seconds_from_duration(duration: str, splitter: str = ':'):
        parts = duration.split(splitter)
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            seconds = int(parts[0])
            return seconds
