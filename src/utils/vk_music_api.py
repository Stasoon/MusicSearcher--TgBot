from playwright.async_api import async_playwright

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
