from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import Config


bot = Bot(token=Config.BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=MemoryStorage())
