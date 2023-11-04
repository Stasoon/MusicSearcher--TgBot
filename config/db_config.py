import os
from typing import Final

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class DatabaseConfig:
    NAME: Final[str] = os.getenv('DB_NAME')
    USER: Final[str] = os.getenv('DB_USER')
    PASSWORD: Final[str] = os.getenv('DB_PASSWORD')
    PORT: Final[int] = int(os.getenv('DB_PORT', 5432))
    HOST: Final[str] = os.getenv('DB_HOST', '0.0.0.0')
