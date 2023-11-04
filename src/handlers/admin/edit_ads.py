from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from src.database import advertisements
from src.misc.admin_states import AdvertisementEditing
from src.utils.keyboards_utils import get_inline_kb_from_json


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('📄 Показы рекламы 📄')
    delete_ad_callback = CallbackData('delete_ad', 'ad_id')

    @staticmethod
    def get_add_advertisement() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕', callback_data='add_advertisement'))

    @staticmethod
    def add_delete_ad_button_to_markup(markup_json: dict, advertisement_id: int) -> InlineKeyboardMarkup:
        if markup_json is None:
            markup = InlineKeyboardMarkup()
        else:
            markup = get_inline_kb_from_json(data=markup_json)

        markup.row(
            InlineKeyboardButton(
                text='❌ Удалить ❌',
                callback_data=Keyboards.delete_ad_callback.new(ad_id=advertisement_id)
            )
        )
        return markup


class Handlers:
    @staticmethod
    async def __handle_admin_ad_shows_button(message: Message):
        await message.answer(text='📄 Показы рекламы 📄', reply_markup=Keyboards.get_add_advertisement())
        for ad in advertisements.get_active_ads():
            text = f"{ad.text} \n\nПоказано раз: {ad.showed_count}"
            markup = Keyboards.add_delete_ad_button_to_markup(ad.markup_json, advertisement_id=ad.id)
            await message.answer(text=text, reply_markup=markup, parse_mode='HTML')

    @staticmethod
    async def __handle_delete_advertisement_callback(callback: CallbackQuery, callback_data: Keyboards.delete_ad_callback):
        ad_id = callback_data.get('ad_id')
        advertisements.delete_ad(advertisement_id=ad_id)
        await callback.message.delete()

    @staticmethod
    async def __handle_add_advertisement_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.set_state(AdvertisementEditing.wait_for_content_message.state)
        await callback.message.answer('✏ Пришлите рекламный текст:')

    @staticmethod
    async def __handle_new_advertisement_content_message(message: Message, state: FSMContext):
        advertisements.create_ad(text=message.html_text)
        await message.answer('✅ Сохранено')
        await Handlers.__handle_admin_ad_shows_button(message)
        await state.finish()

    @classmethod
    def register_edit_ads_handlers(cls, dp: Dispatcher):
        # Кнопка из меню
        dp.register_message_handler(
            cls.__handle_admin_ad_shows_button,
            lambda message: message.text == Keyboards.reply_button_for_admin_menu.text,
            is_admin=True,
        )
        # Добавление рекламы
        dp.register_callback_query_handler(
            cls.__handle_add_advertisement_callback, lambda callback: callback.data == 'add_advertisement'
        )
        # Сообщение с текстом новой рекламы
        dp.register_message_handler(
            cls.__handle_new_advertisement_content_message, state=AdvertisementEditing.wait_for_content_message
        )
        # Удаление рекламы
        dp.register_callback_query_handler(
            cls.__handle_delete_advertisement_callback, Keyboards.delete_ad_callback.filter()
        )
