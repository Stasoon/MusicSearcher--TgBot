import asyncio
import threading

from loguru import logger

from src.database import saved_songs
from src.utils import VkMusicParser


def update_songs_catalog():
    """ Обновляет каталог песен """
    logger.info('Начинаю парсинг песен с Vk')
    songs = VkMusicParser().get_new_songs()
    saved_songs.rewrite_catalog(catalog='new', songs=songs)

    songs = VkMusicParser().get_chart_songs()
    saved_songs.rewrite_catalog(catalog='popular', songs=songs)
    logger.info('Парсинг окончен')


async def run_periodic_catalog_updates(update_rate_seconds: int = 24 * 3600):
    """ Запускает обновление каталога с песнями каждые 24 часа в другом потоке """
    while True:
        thread = threading.Thread(target=update_songs_catalog)
        thread.start()
        await asyncio.sleep(update_rate_seconds)
