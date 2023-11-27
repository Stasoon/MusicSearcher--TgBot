import os
from typing import Final

from dotenv import load_dotenv, find_dotenv

from .paths_config import PathsConfig
from src.middlewares.i18n import I18nMiddleware


load_dotenv(find_dotenv())


class Config:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN')
    ADMIN_IDS: Final = [int(adm_id) for adm_id in os.getenv('ADMIN_IDS').strip().split(',')]

    RUCAPTCHA_TOKEN = os.getenv('RUCAPTCHA_TOKEN')
    VK_TOKENS: list[str] = []


with open('vk_tokens.txt') as file:
    Config.VK_TOKENS.append( file.readline().strip() )


i18n = I18nMiddleware(domain='messages', path=PathsConfig.LOCALES_DIR, default='ru')
