import os
from typing import Final

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN')

    VK_LOGIN: Final = os.getenv('VK_LOGIN')
    VK_PASSWD: Final = os.getenv('VK_PASSWORD')

    TIKTOK_TOKEN: Final = os.getenv('TIKTOK_TOKEN')
