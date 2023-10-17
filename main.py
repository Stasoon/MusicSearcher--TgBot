import asyncio

from src.start_bot import start_bot
from src.utils import setup_logger


def main():
    setup_logger()
    start_bot()


if __name__ == '__main__':
    main()
