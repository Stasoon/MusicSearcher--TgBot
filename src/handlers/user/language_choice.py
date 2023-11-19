from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from config import i18n
from src.database import users
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.misc.callback_data import LanguageChoiceCallback


async def handle_language_command(message: Message):
    await message.answer(
        text=UserMessages.get_choose_language(),
        reply_markup=UserKeyboards.get_languages_markup(),
        parse_mode='HTML'
    )


async def handle_language_choice_callback(
        callback: CallbackQuery, callback_data: LanguageChoiceCallback, state: FSMContext
):
    await state.finish()
    lang_code = callback_data.get('lang_code')
    users.update_user_lang_code(telegram_id=callback.from_user.id, new_lang_code=lang_code)
    i18n.change_locale_context(lang_code)

    await callback.answer(UserMessages.get_language_selected())
    await callback.message.delete()
    await callback.message.answer(
        text=UserMessages.get_search_song(),
        reply_markup=UserKeyboards.get_main_menu_markup()
    )


def register_language_command_handler(dp: Dispatcher):
    # Команда /lang
    dp.register_message_handler(handle_language_command, Command("lang"))

    # Выбор языка
    dp.register_callback_query_handler(handle_language_choice_callback, LanguageChoiceCallback.filter(), state='*')


