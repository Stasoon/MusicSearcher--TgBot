import asyncio
from aiogram import executor
from aiogram.types import BotCommand

from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.update_songs_catalog import run_periodic_catalog_updates
from src.handlers import register_all_handlers
from src.filters import register_all_filters
from src.database import register_models
from src.create_bot import bot, dp
from src.utils import VkMusicApi
from config import Config, i18n
from src.utils import logger


async def set_bot_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command='start', description='Запуск бота'),
            BotCommand(command='lang', description='Сменить язык')
        ]
    )


async def on_startup(_):
    # Запуск базы данных
    register_models()

    # Установка команд бота
    await set_bot_commands()

    # Регистрация middlewares
    dp.middleware.setup(i18n)
    dp.middleware.setup(ThrottlingMiddleware())

    # Регистрация фильтров
    register_all_filters(dp)

    # Регистрация хэндлеров
    register_all_handlers(dp)

    # Авторизация в ВК
    vk_api = VkMusicApi()
    vk_api.add_service(client_name='Stas')#, login='+79782128315', password='[ST1920ii9As/]')
    # vk_api.add_service(client_name='Misha')  # , login='+79781685372', password='.barN15sVA/')
    vk_api.add_service(client_name='Alex')#, login='+79259675328', password='StAs123456')

    asyncio.create_task(run_periodic_catalog_updates())

    logger.info('Бот запущен!')


async def on_shutdown(_):
    logger.info('Бот остановлен')


def start_bot():
    try:
        executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    except Exception as e:
        logger.exception(e)
