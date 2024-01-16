from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from src.database import advertisements
from src.database.models import Advertisement
from src.misc.admin_states import AdvertisementAdding
from src.utils.keyboard_utils import get_inline_kb_from_json, get_markup_from_text


class Messages:
    @staticmethod
    def ask_for_post_content():
        return "Пришлите <u>текст</u> поста, который хотите разослать. Добавьте нужные <u>медиа-файлы</u>"

    @staticmethod
    def get_button_data_incorrect():
        return 'Отправленная информация не верна. ' \
               'Пожалуйста, в первой строке напишите название кнопки, во второй - ссылку.'

    @staticmethod
    def prepare_post():
        return "<i>Итоговый вид рекламы:</i>"

    @staticmethod
    def get_mailing_canceled():
        return '⛔ Добавление рекламы отменено'

    @staticmethod
    def get_markup_adding_manual():
        return '''Отправьте боту название кнопки и адрес ссылки. Например, так: \n
Telegram telegram.org \n
Чтобы отправить несколько кнопок за раз, используйте разделитель «|». Каждый новый ряд – с новой строки. 
Например, так: \n
Telegram telegram.org | Новости telegram.org/blog
FAQ telegram.org/faq | Скачать telegram.org/apps'''

    @staticmethod
    def ask_about_save_ad():
        return "<u><b>Сохранить рекламу?</b></u>"


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('📄 Показы рекламы 📄')
    delete_ad_callback = CallbackData('delete_ad', 'ad_id')
    append_preview = CallbackData('preview', 'action', 'ad_id')

    @staticmethod
    def get_add_advertisement() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕', callback_data='add_advertisement'))

    @staticmethod
    def get_ad_actions_markup(ad: Advertisement) -> InlineKeyboardMarkup:
        if ad.markup_json is None:
            markup = InlineKeyboardMarkup()
        else:
            markup = get_inline_kb_from_json(data=ad.markup_json)

        markup.row(InlineKeyboardButton(
            text=f"Превью: {'✅' if ad.show_preview else '❌'}",
            callback_data=Keyboards.append_preview.new(action=not ad.show_preview, ad_id=ad.id))
        )
        markup.row(InlineKeyboardButton(
            text='❌ Удалить ❌',
            callback_data=Keyboards.delete_ad_callback.new(ad_id=ad.id))
        )
        return markup

    @staticmethod
    def get_ask_about_preview():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton('Да', callback_data=Keyboards.append_preview.new(action=True, ad_id='')))
        markup.add(InlineKeyboardButton('Нет', callback_data=Keyboards.append_preview.new(action=False, ad_id='')))
        return markup

    @staticmethod
    def add_button():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton('Продолжить без кнопки', callback_data='save_ad_wout_button'))
        return markup

    @staticmethod
    def get_save():
        markup = InlineKeyboardMarkup(row_width=1)
        save_button = InlineKeyboardButton('💾 Сохранить 💾', callback_data='save_ad')
        markup.add(save_button)
        return markup

    @staticmethod
    def get_save_or_cancel():
        markup = InlineKeyboardMarkup(row_width=1)

        save_button = InlineKeyboardButton('💾 Сохранить 💾', callback_data='save_ad')
        cancel_button = InlineKeyboardButton(text='🔙 Отменить', callback_data='cancel_ad_creating')

        markup.add(save_button, cancel_button)
        return markup


class Handlers:
    @staticmethod
    async def __handle_admin_ad_shows_button(message: Message):
        await message.answer(text='📄 Показы рекламы 📄', reply_markup=Keyboards.get_add_advertisement())
        for ad in advertisements.get_active_ads():
            text = f"{ad.text} \n\nПоказано раз: {ad.showed_count}"
            markup = Keyboards.get_ad_actions_markup(ad)
            await message.answer(text=text, reply_markup=markup, parse_mode='HTML')

    @staticmethod
    async def __handle_toggle_show_preview(callback: CallbackQuery, callback_data: Keyboards.append_preview):
        ad = advertisements.get_ad_by_id(ad_id=int(callback_data.get('ad_id')))
        if not ad:
            await callback.message.delete()
            return

        show_preview = True if callback_data.get('action') == 'True' else False
        ad = advertisements.change_show_preview(advertisement=ad, show_preview=show_preview)

        text = f"{ad.text} \n\nПоказано раз: {ad.showed_count}"
        markup = Keyboards.get_ad_actions_markup(ad)
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=not show_preview)

    @staticmethod
    async def __handle_delete_advertisement_callback(
            callback: CallbackQuery, callback_data: Keyboards.delete_ad_callback
    ):
        ad_id = callback_data.get('ad_id')
        advertisements.delete_ad(advertisement_id=ad_id)
        await callback.message.delete()

    @staticmethod
    async def __handle_add_advertisement_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.set_state(AdvertisementAdding.wait_for_content_message.state)
        await callback.message.answer('✏ Пришлите рекламный текст:')

    @staticmethod
    async def __handle_new_advertisement_content_message(message: Message, state: FSMContext):
        await state.update_data(text=message.html_text)

        await message.answer(text='Добавлять превью?', reply_markup=Keyboards.get_ask_about_preview())
        await state.set_state(AdvertisementAdding.add_preview.state)

    @staticmethod
    async def __handle_add_preview_callback(
            callback: CallbackQuery, callback_data: Keyboards.append_preview, state: FSMContext
    ):
        await callback.message.delete()
        await state.update_data(append_preview=callback_data.get('action'))

        await callback.message.answer(
            text=Messages.get_markup_adding_manual(),
            reply_markup=Keyboards.add_button(),
            disable_web_page_preview=True
        )
        await state.set_state(AdvertisementAdding.wait_for_markup_data.state)

    @staticmethod
    async def __handle_url_button_data(message: Message, state: FSMContext):
        state_data = await state.get_data()
        markup = get_markup_from_text(message.text)

        try:
            await message.answer(text=state_data.get('text'), reply_markup=markup)
        except Exception:
            await message.answer('Вы ввели неправильную информацию для кнопки. Попробуйте снова:',
                                 reply_markup=Keyboards.add_button())
            return

        await state.update_data(markup=markup)
        await message.answer(Messages.ask_about_save_ad(), reply_markup=Keyboards.get_save_or_cancel())
        await state.set_state(AdvertisementAdding.wait_for_confirm.state)

    @staticmethod
    async def __handle_continue_wout_button_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        data = await state.get_data()

        markup_json = data.get('markup')
        markup = InlineKeyboardMarkup.to_object(markup_json) if markup_json else None
        show_preview = True if data.get('append_preview') == 'True' else False

        await callback.message.answer(Messages.prepare_post())
        await callback.message.answer(
            text=data.get('text'), reply_markup=markup, disable_web_page_preview=not show_preview
        )

        await callback.message.answer(Messages.ask_about_save_ad(), reply_markup=Keyboards.get_save_or_cancel())
        await state.set_state(AdvertisementAdding.wait_for_confirm.state)

    @staticmethod
    async def __handle_save_ad_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        data = await state.get_data()
        await state.finish()

        show_preview = True if data.get('append_preview') == 'True' else False
        advertisements.create_ad(
            text=data.get('text'), markup_json=data.get('markup'), show_preview=show_preview
        )

        await callback.message.answer('✅ Сохранено')
        await Handlers.__handle_admin_ad_shows_button(callback.message)

    @staticmethod
    async def __handle_ad_creating_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer(Messages.get_mailing_canceled())
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
            cls.__handle_new_advertisement_content_message, state=AdvertisementAdding.wait_for_content_message
        )

        # Показывать превью? (при создании)
        dp.register_callback_query_handler(
            cls.__handle_add_preview_callback,
            Keyboards.append_preview.filter(),
            state=AdvertisementAdding.add_preview,
        )

        # обработка содержимого для url-кнопки
        dp.register_message_handler(
            cls.__handle_url_button_data,
            content_types=['text'],
            state=AdvertisementAdding.wait_for_markup_data
        )

        # обработка калбэка продолжения без url-кнопки
        dp.register_callback_query_handler(
            cls.__handle_continue_wout_button_callback,
            state=AdvertisementAdding.wait_for_markup_data,
        )

        # обработка калбэка подтверждения сохранения рекламы
        dp.register_callback_query_handler(
            cls.__handle_save_ad_callback, text='save_ad',
            state=AdvertisementAdding.wait_for_confirm, is_admin=True
        )

        # обработка отмены создания рекламы
        dp.register_callback_query_handler(
            cls.__handle_ad_creating_callback,
            text="cancel_ad_creating", state='*'
        )

        # Удаление рекламы
        dp.register_callback_query_handler(
            cls.__handle_delete_advertisement_callback, Keyboards.delete_ad_callback.filter()
        )

        dp.register_callback_query_handler(
            cls.__handle_toggle_show_preview, Keyboards.append_preview.filter()
        )
