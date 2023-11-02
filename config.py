import os
from typing import Final
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

from src.middlewares.i18n import I18nMiddleware


load_dotenv(find_dotenv())


class Config:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN')
    ADMIN_IDS: Final = [int(adm_id) for adm_id in os.getenv('ADMIN_IDS').strip().split(',')]

    VK_LOGIN: Final = os.getenv('VK_LOGIN')
    VK_PASSWD: Final = os.getenv('VK_PASSWORD')

    TIKTOK_TOKEN: Final = os.getenv('TIKTOK_TOKEN')

    WORKDIR = Path(__file__).parent
    WEBDRIVER_PATH = WORKDIR / 'webdriver/chromedriver.exe'
    LOCALES_DIR = WORKDIR/'locales'
    CSV_FOLDER = './db_exports'


i18n = I18nMiddleware(domain='messages', path=Config.LOCALES_DIR, default='ru')
