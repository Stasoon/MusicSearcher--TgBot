import os.path

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from config import Config
from src.misc.admin_states import DefaultCoverSetting


class Keyboards:

    reply_button_for_admin_menu = KeyboardButton('🖼 Обложки песен 🖼')

    @staticmethod
    def get_cancel(can_delete: bool) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        if can_delete:
            markup.add(InlineKeyboardButton(text='Убрать обложку', callback_data='del_cover'))

        markup.add(InlineKeyboardButton(text='Отменить', callback_data='cancel_edit_cover'))
        return markup


async def handle_default_cover_button(message: Message, state: FSMContext):
    is_default_cover_exists = os.path.exists(Config.DEFAULT_COVER_PATH)

    text = 'Пришлите фото для обложки песен по умолчанию:'
    markup = Keyboards.get_cancel(can_delete=is_default_cover_exists)

    if is_default_cover_exists:
        await message.answer_photo(photo=InputFile(Config.DEFAULT_COVER_PATH), caption=text, reply_markup=markup)
    else:
        await message.answer(text=text, reply_markup=markup)

    await state.set_state(DefaultCoverSetting.wait_for_photo)


async def handle_new_cover_message(message: Message, state: FSMContext):
    file = [ph for ph in message.photo if ph.height <= 320 and ph.file_size//1024 <= 200]

    await file[-1].download(destination_file=Config.DEFAULT_COVER_PATH)
    await message.answer(text='Фото обновлено', reply_markup=None)

    await state.finish()


async def handle_delete_cover_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Фото удалено')

    if os.path.exists(Config.DEFAULT_COVER_PATH):
        os.remove(Config.DEFAULT_COVER_PATH)

    await state.finish()


async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='Отменено')
    await state.finish()


def register_edit_default_cover_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_default_cover_button, Text(equals=Keyboards.reply_button_for_admin_menu.text))

    dp.register_callback_query_handler(handle_delete_cover_callback, text='del_cover', state='*')
    dp.register_callback_query_handler(handle_cancel_callback, text='cancel_edit_cover', state='*')

    dp.register_message_handler(
        handle_new_cover_message, state=DefaultCoverSetting.wait_for_photo, content_types=['photo']
    )

