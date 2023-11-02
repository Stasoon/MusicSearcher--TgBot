import asyncio
from typing import Literal

from loguru import logger

from src.database import saved_songs
from src.utils import VkMusicParser


async def update_songs_catalog(catalog_name: Literal['new', 'popular']):
    """ Обновляет каталог песен """
    songs = await VkMusicParser().get_new_songs()
    saved_songs.rewrite_catalog(catalog=catalog_name, songs=songs)


async def run_periodic_catalog_updates(update_rate_seconds: int = 24 * 3600):
    """ Запускает обновление каталога с песнями каждые 24 часа в другом потоке """
    while True:
        logger.info('Начинаю парсинг песен с Vk')
        await asyncio.gather(
            update_songs_catalog('new'),
            update_songs_catalog('popular')
        )

        logger.info('Парсинг окончен')
        await asyncio.sleep(update_rate_seconds)
