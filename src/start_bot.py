from aiogram import executor
from aiogram.types import BotCommand

from src.utils import logger, vk_api
from src.create_bot import bot, dp
from src.database import register_models
from src.handlers import register_all_handlers
from config import Config


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

    # Регистрация хэндлеров
    register_all_handlers(dp)

    # Авторизация в ВК
<<<<<<< HEAD
    VkMusicApi.authorise(login=Config.VK_LOGIN, password=Config.VK_PASSWD)
=======
    vk_api.VkMusicApi.authorise(login=Config.VK_LOGIN, password=Config.VK_PASSWD)
>>>>>>> parent of 39c5186 (Work)

    logger.info('Бот запущен!')


async def on_shutdown(_):
    logger.info('Бот остановлен')


def start_bot():
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(run_periodic_catalog_updates())

        executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    except Exception as e:
        logger.exception(e)

