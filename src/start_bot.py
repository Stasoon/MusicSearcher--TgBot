import asyncio

from aiocron import crontab
from aiogram import executor
from aiogram.types import AllowedUpdates

from src.middlewares.throttling import ThrottlingMiddleware
from src.middlewares.user_activity import UserActivityMiddleware
from src.set_bot_commands import set_bot_commands
from src.utils.cache_songs import redis_client
from src.utils.update_songs_catalog import run_periodic_catalog_updates
from src.handlers import register_all_handlers
from src.filters import register_all_filters
from src.database import register_models
from src.create_bot import bot, dp
from config import Config, i18n
from src.utils import logger
from src.utils.vkpymusic import RuCaptchaDecoder, SessionsManager, Session


async def on_startup(_):
    # Запуск базы данных
    register_models()

    # Установка команд бота
    await set_bot_commands(bot=bot)

    # Регистрация middlewares
    dp.middleware.setup(UserActivityMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(i18n)

    # Регистрация фильтров
    register_all_filters(dp)

    # Регистрация хэндлеров
    register_all_handlers(dp)

    # Авторизация в ВК
    manager = SessionsManager()
    captcha_decoder = RuCaptchaDecoder(rucaptcha_token=Config.RUCAPTCHA_TOKEN)
    for n, token in enumerate(Config.VK_TOKENS):
        vk_session = Session(name=str(n), token_for_audio=token, captcha_decoder=captcha_decoder)
        manager.add_session(vk_session)

    # Обновление каталогов песен. Первое обновление сразу при запуске бота, следующие - в 00:15
    asyncio.create_task(run_periodic_catalog_updates())
    cron = crontab('15 0 * * *', func=run_periodic_catalog_updates, start=False)
    cron.start()

    logger.info('Бот запущен!')


async def on_shutdown(_):
    logger.info('Бот остановлен')
    redis_client.close()


def start_bot():
    try:
        executor.start_polling(
            dispatcher=dp,
            on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True,
            allowed_updates=AllowedUpdates.all()
        )
    except Exception as e:
        logger.exception(e)
