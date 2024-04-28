from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from src.misc.admin_states import ReferralLinkStates
from src.database.reflinks import create_reflink, is_reflink_exists, get_all_links, delete_reflink, get_link


reflinks_callback_data = CallbackData('referral_links', 'action', 'link_name')


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('🔗 Реферальные ссылки 🔗')

    cancel_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Отменить', callback_data=reflinks_callback_data.new(action='cancel', link_name='None'))
    )

    @staticmethod
    def get_actions_with_link(link):
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(
            text=f"❌ Удалить",
            callback_data=reflinks_callback_data.new(action='show', link_name=link.name))
        )
        markup.add(InlineKeyboardButton(
            text='🔙 Отменить', callback_data=reflinks_callback_data.new(action='cancel', link_name='None'))
        )
        return markup

    @staticmethod
    def get_links():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text='➕ Добавить ссылку', callback_data=reflinks_callback_data.new(action='create', link_name='None')
            )
        )

        for n, link in enumerate(get_all_links()[:99], start=1):
            bttn = InlineKeyboardButton(
                text=f"{n}) {link.name} : 👥 {link.user_count}",
                callback_data=reflinks_callback_data.new(action='show', link_name=link.name)
            )
            markup.add(bttn)

        return markup


class Messages:
    @staticmethod
    def get_referral_links(bot_username: str) -> str:
        text = '🔗 Реферальные ссылки'
        return text

    @staticmethod
    def get_link_description(link, bot_username: str) -> str:
        return (
            f'Ссылка: <code>{link.name}</code> \n\n'
            f'🔗 <code>https://t.me/{bot_username}?start={link.name}</code> \n'
            f'📊 Кол-во переходов: {link.user_count} \n'
            f'📲 На ОП подписались: {link.passed_op_count} \n'
        )

    @staticmethod
    def select_link_to_delete():
        return '🔘 Нажмите на ссылку, которую хотите удалить: '


class Handlers:

    @staticmethod
    async def __handle_admin_reflinks_button(message: Message):
        await message.answer(text='🔗 Реферальные ссылки', reply_markup=Keyboards.get_links())

    @staticmethod
    async def __handle_add_link_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            '🔘 Введите название. Можно использовать цифры и английские буквы:',
            reply_markup=Keyboards.cancel_markup
        )
        await state.set_state(ReferralLinkStates.create)

    @staticmethod
    async def handle_show_link_callback(callback: CallbackQuery, callback_data: reflinks_callback_data):
        link = get_link(callback_data.get('link_name'))

        bot_username = (await callback.bot.get_me()).username
        text = Messages.get_link_description(link=link, bot_username=bot_username)

        await callback.message.answer(text=text, reply_markup=Keyboards.get_actions_with_link(link=link))

    @staticmethod
    async def __handle_new_link_name(message: Message, state: FSMContext):
        if not message.text.isascii():
            await message.answer('❗В сообщении есть русские буквы. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        elif not message.text.isalnum():
            await message.answer('❗В сообщении есть символы. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        elif is_reflink_exists(message.text):
            await message.answer('❗Такая ссылка уже существует. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)
        else:
            create_reflink(message.text)
            bot_username = (await message.bot.get_me()).username
            await message.answer(
                '✅ Реферальная ссылка создана. \n\n'
                f'<u><i>Имя ссылки</i></u>: <code>{message.text}</code> \n'
                f'<u><i>Ссылка</i></u>: '
                f'<code>https://t.me/{bot_username}?start={message.text}</code>'
            )
            await state.finish()
            await Handlers.__handle_admin_reflinks_button(message)

    @staticmethod
    async def __handle_link_to_delete_callback(callback: CallbackQuery, callback_data: reflinks_callback_data):
        delete_reflink(callback_data.get('link_name'))
        await callback.answer('✅ Ссылка удалена')
        await callback.message.edit_text(
            text=Messages.select_link_to_delete(),
            reply_markup=Keyboards.get_links()
        )

    @staticmethod
    async def __handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(text='🔗 Реферальные ссылки', reply_markup=Keyboards.get_links())
        await state.finish()

    @classmethod
    def register_reflinks_handlers(cls, dp: Dispatcher):
        # отмена
        dp.register_callback_query_handler(
            cls.__handle_cancel_callback, reflinks_callback_data.filter(action='cancel'), state='*'
        )

        dp.register_message_handler(
            cls.__handle_admin_reflinks_button, is_admin=True, text=Keyboards.reply_button_for_admin_menu.text
        )

        # показ ссылки
        dp.register_callback_query_handler(
            cls.handle_show_link_callback, reflinks_callback_data.filter(action='show')
        )

        # создание реферальной ссылки
        dp.register_callback_query_handler(
            cls.__handle_add_link_callback, reflinks_callback_data.filter(action='create'),
            is_admin=True, state=None
        )
        dp.register_message_handler(cls.__handle_new_link_name, is_admin=True, state=ReferralLinkStates.create)

        # удаление реферальной ссылки
        dp.register_callback_query_handler(
            cls.__handle_link_to_delete_callback, reflinks_callback_data.filter(action='delete'), state=None
        )
        dp.register_callback_query_handler(cls.__handle_link_to_delete_callback, reflinks_callback_data.filter())
