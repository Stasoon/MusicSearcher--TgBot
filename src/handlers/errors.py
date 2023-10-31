import traceback

from aiogram import Dispatcher
from loguru import logger


async def handle_errors(update, exception):
    logger.error(f'Произошла ошибка: {exception} \nПри обработке апдейта: {update} \n{traceback.format_exc()}')


def register_errors_handler(dp: Dispatcher):
    dp.register_errors_handler(handle_errors)
