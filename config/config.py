import os
from typing import Final

from dotenv import load_dotenv, find_dotenv

from .paths_config import PathsConfig
from src.middlewares.i18n import I18nMiddleware


load_dotenv(find_dotenv())


SONGS_PER_PAGE: Final[int] = 8
MAX_SONG_PAGES_COUNT: Final[int] = 12


class Config:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN')
    ADMIN_IDS: Final = [int(adm_id) for adm_id in os.getenv('ADMIN_IDS').strip().split(',')]

    RUCAPTCHA_TOKEN = os.getenv('RUCAPTCHA_TOKEN')
    LOGS_CHAT_ID: Final[int] = os.getenv('LOGS_CHAT_ID')
    VK_TOKENS: list[str] = []

    DEFAULT_COVER_PATH = 'cover.jpg'


with open('vk_tokens.txt') as file:
    Config.VK_TOKENS = file.read().strip().split()


i18n = I18nMiddleware(domain='messages', path=PathsConfig.LOCALES_DIR, default='ru')
