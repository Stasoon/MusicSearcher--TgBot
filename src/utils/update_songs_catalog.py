import asyncio
from typing import Literal

from loguru import logger

from src.database import song_catalogs
from src.utils import VkMusicParser


async def update_songs_catalog(catalog_name: Literal['new', 'popular']):
    """ Обновляет каталог песен """
    if catalog_name == 'new':
        songs = await VkMusicParser().get_new_songs()
    else:
        songs = await VkMusicParser().get_chart_songs()
    song_catalogs.rewrite_catalog(catalog=catalog_name, songs=songs)


async def run_periodic_catalog_updates():
    """ Запускает обновление каталога с песнями каждый день в 00:15 """
    logger.info('Начинаю парсинг песен с Vk')
    await asyncio.gather(
        update_songs_catalog('new'),
        update_songs_catalog('popular')
    )
    logger.info('Парсинг окончен')
