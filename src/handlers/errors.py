import traceback

from aiogram import Dispatcher
from src.utils import logger


async def handle_errors(update, exception):
    logger.error(
        f'Произошла ошибка: {exception} \n'
        f'При обработке апдейта: {update} \n'
        f'{traceback.format_exc()}'
    )


def register_errors_handler(dp: Dispatcher):
    dp.register_errors_handler(handle_errors)
