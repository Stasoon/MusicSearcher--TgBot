from aiogram import Dispatcher
from aiogram.types import Message

from src.database import create_user
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages


async def handle_start_command(message: Message):
    user = message.from_user
    args = message.get_full_command()
    referral_link = args[-1] if len(args) == 2 else None
    create_user(telegram_id=user.id, firstname=user.first_name, username=user.username, reflink=referral_link)

    await message.answer(text=UserMessages.get_welcome(user_name=user.first_name), parse_mode='HTML')
    await message.answer(
        text=UserMessages.get_search_song(),
        reply_markup=UserKeyboards.get_main_menu_markup(),
        parse_mode='HTML'
    )


async def handle_language_command(message: Message):
    await message.answer(
        text=UserMessages.get_choose_language(),
        reply_markup=UserKeyboards.get_languages_markup(),
        parse_mode='HTML'
    )


def register_command_handlers(dp: Dispatcher):
    # Команда /start
    dp.register_message_handler(handle_start_command, commands="start")

    # Команда /lang
    dp.register_message_handler(handle_language_command, commands="lang")
