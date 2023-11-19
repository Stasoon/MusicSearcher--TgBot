from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message

from src.database.users import create_user
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.utils.message_utils import send_channels_to_subscribe


async def handle_show_channels_to_subscribe_start_command(message: Message, state: FSMContext):
    await state.finish()
    await send_channels_to_subscribe(bot=message.bot, user_id=message.from_user.id)


async def handle_start_command(message: Message, state: FSMContext):
    await state.finish()
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


def register_start_command_handlers(dp: Dispatcher):
    # При переходе из инлайн режима, если необходимо подписаться
    dp.register_message_handler(
        handle_show_channels_to_subscribe_start_command,
        CommandStart(deep_link='show_channels_to_subscribe'),
        state='*'
    )

    # Команда /start
    dp.register_message_handler(handle_start_command, CommandStart(), state='*')
