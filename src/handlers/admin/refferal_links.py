from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from src.misc.admin_states import ReferralLinkStates
from src.database.reflinks import create_reflink, is_reflink_exists, get_all_links, delete_reflink


reflinks_callback_data = CallbackData('referral_links', 'action')
delete_reflink_callback_data = CallbackData('referral_links', 'link_name')


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('🔗 Реферальные ссылки 🔗')
    reflinks_markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('➕ Добавить ссылку', callback_data=reflinks_callback_data.new('create')),
        InlineKeyboardButton('➖ Удалить ссылку', callback_data=reflinks_callback_data.new('delete')),
    )

    cancel_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Отменить', callback_data=reflinks_callback_data.new('cancel'))
    )

    @staticmethod
    def get_links_to_delete_markup():
        markup = InlineKeyboardMarkup(row_width=1)
        for n, link in enumerate(get_all_links()[:99], start=1):
            bttn = InlineKeyboardButton(
                text=f"❌ {n}) {link.name} : 👥 {link.user_count}",
                callback_data=delete_reflink_callback_data.new(link_name=link.name)
            )
            markup.add(bttn)
        markup.add(InlineKeyboardButton('🔙 Отменить', callback_data=reflinks_callback_data.new('cancel')))
        return markup


class Messages:
    @staticmethod
    def get_referral_links(bot_username: str) -> str:
        text = '🔗 Реферальные ссылки \n\n' \
               '<b>Список реферальных ссылок:</b> \n\n'

        for n, link in enumerate(get_all_links(), start=1):
            text += (
                f'{n} — <code>{link.name}</code> \n'
                f'🔗 <code>https://t.me/{bot_username}?start={link.name}</code> \n'
                f'📊 Кол-во переходов: {link.user_count} \n'
                f'📲 На ОП подписались: {link.passed_op_count} \n'
            )
            text += '-' * 30 + '\n'
        return text

    @staticmethod
    def select_link_to_delete():
        return '🔘 Нажмите на ссылку, которую хотите удалить: '


class Handlers:

    @staticmethod
    async def __handle_admin_reflinks_button(message: Message):
        bot_username = (await message.bot.get_me()).username
        text = Messages.get_referral_links(bot_username=bot_username)
        await message.answer(text=text, reply_markup=Keyboards.reflinks_markup, parse_mode='HTML')

    @staticmethod
    async def __handle_add_link_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            '🔘 Введите название. Можно использовать цифры и английские буквы:',
            reply_markup=Keyboards.cancel_markup
        )
        await state.set_state(ReferralLinkStates.create)

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
    async def __handle_delete_link_callback(callback: CallbackQuery):
        await callback.message.edit_text(
            text=Messages.select_link_to_delete(), reply_markup=Keyboards.get_links_to_delete_markup()
        )

    @staticmethod
    async def __handle_link_to_delete_callback(callback: CallbackQuery, callback_data: reflinks_callback_data):
        delete_reflink(callback_data.get('link_name'))
        await callback.answer('✅ Ссылка удалена')
        await callback.message.edit_text(
            text=Messages.select_link_to_delete(),
            reply_markup=Keyboards.get_links_to_delete_markup()
        )

    @staticmethod
    async def __handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
        bot_username = (await callback.bot.get_me()).username
        text = Messages.get_referral_links(bot_username=bot_username)
        await callback.message.edit_text(
            text=text, reply_markup=Keyboards.reflinks_markup
        )
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

        # создание реферальной ссылки
        dp.register_callback_query_handler(
            cls.__handle_add_link_callback, reflinks_callback_data.filter(action='create'),
            is_admin=True, state=None
        )
        dp.register_message_handler(cls.__handle_new_link_name, is_admin=True, state=ReferralLinkStates.create)

        # удаление реферальной ссылки
        dp.register_callback_query_handler(
            cls.__handle_delete_link_callback, reflinks_callback_data.filter(action='delete'), state=None
        )
        dp.register_callback_query_handler(cls.__handle_link_to_delete_callback, delete_reflink_callback_data.filter())
