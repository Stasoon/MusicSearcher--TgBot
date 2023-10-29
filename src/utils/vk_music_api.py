from selenium.webdriver.common.by import By

from selenium import webdriver
from chromedriver_py import binary_path

from src.utils.vkpymusic import AsyncService, VkSong


class VkMusicApi:
    service: AsyncService = None

    @classmethod
    def authorise(cls, login: str, password: str):
        # AsyncService.del_config()
        # token_receiver = TokenReceiver(login=login, password=password)

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
    """
    Парсер песен с сайта Vk, использующий Selenium.
    """
    BASE_URL = 'https://vk.com/audio'

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        svc = webdriver.ChromeService(executable_path=binary_path)

        self.driver = webdriver.Chrome(service=svc, options=chrome_options)

    def get_chart_songs(self):
        """
        Получает новые песни из чарта Vk.
        Работает медленно, поэтому использовать только для получения песен для дальнейшей сериализации
        """
        return self.__parse_songs(block_name='chart')

    def get_new_songs(self):
        """
        Получает новые песни из Vk.
        Работает медленно, поэтому использовать только для получения песен для дальнейшей сериализации
        """
        return self.__parse_songs(block_name='new_songs')

    def __parse_songs(self, block_name: str) -> list[VkSong]:
        self.driver.get(f'{self.BASE_URL}?block={block_name}')
        self.driver.implicitly_wait(1)

        song_elements = self.driver.find_elements(by=By.CLASS_NAME, value='audio_row_content')
        songs = []

        for song_element in song_elements:
            try:
                song = self.__get_song_from_element(song_element)
            except (TypeError, ValueError):
                continue
            songs.append(song)

        self.driver.quit()
        return songs

    @staticmethod
    def __get_seconds_from_duration(duration: str, splitter: str = ':'):
        parts = duration.split(splitter)
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            seconds = int(parts[0])
            return seconds

    def __get_song_from_element(self, song_element) -> VkSong:
        title_element = song_element.find_element(By.CLASS_NAME, value='audio_row__title_inner')
        title = title_element.text

        href = title_element.get_attribute('href')
        owner_id, song_id = map(int, str(href).replace(f'{self.BASE_URL}', '').split('_'))

        artist_element = song_element.find_element(By.CLASS_NAME, value='audio_row__performers')
        artist = artist_element.text

        duration_element = song_element.find_element(By.CLASS_NAME, value='audio_row__duration')
        duration_str = duration_element.text
        duration = self.__get_seconds_from_duration(duration_str)

        return VkSong(title=title, artist=artist, owner_id=owner_id, audio_id=song_id, duration=duration)

