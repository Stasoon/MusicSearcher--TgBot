from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import markdown
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import Unauthorized
from aiogram.types import (
    Message, CallbackQuery, ContentType, ChatType,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)

from src.database.models import JoinRequestChannel
from src.database import join_request_channels
from src.misc.admin_states import JoinRequestChannelAdding, JoinRequestChannelEditing


class Messages:
    @staticmethod
    def get_channel_description(channel: JoinRequestChannel) -> str:
        channel = join_request_channels.get_join_request_channel_or_none(channel.channel_id)
        result = (
            f'💬 <b>{markdown.quote_html(channel.channel_title)}</b> \n'
            f'🆔 <code>{channel.channel_id}</code> \n\n'
            f'<b>🔢 Одобрено заявок:</b> <code>{channel.approved_requests_count}</code> \n'
            f'Отправлено приветствий: {channel.sent_welcomes_count} \n'
            f'Ответили боту: {channel.answered_welcomes_count}\n\n'
            f'<b>👋 Текст приветствия:</b> \n{channel.welcome_text} \n\n'
            f'<b>🚶 Текст прощания:</b> \n{channel.goodbye_text} \n\n'
        )
        return result

    @staticmethod
    def get_bot_have_no_rights() -> str:
        return (
            'Вы не дали боту права на добавление участников! \n'
            'Сделайте бота администратором и дайте нужные права. \n\n'
            'Затем попробуйте ещё раз:'
        )

    @staticmethod
    def ask_for_welcome_text() -> str:
        return 'Введите текст приветственного сообщения: '

    @staticmethod
    def ask_for_goodbye_text() -> str:
        return 'Введите текст прощания: '

    @staticmethod
    def get_data_changed() -> str:
        return '✅ Данные изменены'


class Keyboards:
    join_request_channels_callback = CallbackData('join_req_channels', 'action', 'channel_id')

    reply_button_for_admin_menu = KeyboardButton('👋 Принятие заявок / приветствие 👋')
    inline_cancel_button = InlineKeyboardButton(
        '🔙 Отменить', callback_data=join_request_channels_callback.new(action='cancel', channel_id='')
    )

    @staticmethod
    def get_edit_channel(channel: JoinRequestChannel):
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(
            text='Принимать заявки: ' + ('да ✅' if channel.allow_approving else 'нет ❌'),
            callback_data=Keyboards.join_request_channels_callback.new(
                action='toggle_accept', channel_id=channel.channel_id
            )))
        markup.row(InlineKeyboardButton(
            text='✏ Изменить приветствие', callback_data=Keyboards.join_request_channels_callback.new(
                action='edit_welcome_text', channel_id=channel.channel_id
            )))
        markup.row(InlineKeyboardButton(
            text='✏ Изменить прощание', callback_data=Keyboards.join_request_channels_callback.new(
                action='edit_goodbye_text', channel_id=channel.channel_id
            )))
        markup.row(Keyboards.inline_cancel_button)
        return markup

    @staticmethod
    def get_channels_list() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for channel in join_request_channels.get_all_join_request_channels():
            markup.row(InlineKeyboardButton(
                text=f"{channel.channel_title}: {channel.approved_requests_count}",
                callback_data=Keyboards.join_request_channels_callback.new(
                    action='show', channel_id=channel.channel_id))
            )

        add_button = InlineKeyboardButton(
            text='➕', callback_data=Keyboards.join_request_channels_callback.new(action='add', channel_id='')
        )
        delete_button = InlineKeyboardButton(
            text='➖', callback_data=Keyboards.join_request_channels_callback.new(action='delete', channel_id='')
        )
        markup.add(add_button, delete_button)
        return markup

    @staticmethod
    def get_channels_to_delete() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        for channel in join_request_channels.get_all_join_request_channels():
            channel_button = InlineKeyboardButton(
                text=f'❌ {channel.channel_title}',
                callback_data=Keyboards.join_request_channels_callback.new(
                    action='delete', channel_id=channel.channel_id
                )
            )
            markup.add(channel_button)

        markup.add(Keyboards.inline_cancel_button)
        return markup

    @staticmethod
    def get_cancel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(Keyboards.inline_cancel_button)


class Handlers:
    @staticmethod
    def __get_channel_message_data(channel_id: int) -> dict:
        channel = join_request_channels.get_join_request_channel_or_none(channel_id=channel_id)
        return {
            'text': Messages.get_channel_description(channel=channel),
            'reply_markup': Keyboards.get_edit_channel(channel=channel),
            'disable_web_page_preview': True
        }

    @staticmethod
    async def handle_join_accept_channels_button(message: Message):
        await message.answer(
            text='Каналы и чаты с одобрением заявок:',
            reply_markup=Keyboards.get_channels_list()
        )

    @staticmethod
    async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
        await state.finish()
        await callback.answer('❌ Отменено')
        await callback.message.delete()
        await Handlers.handle_join_accept_channels_button(callback.message)

    @staticmethod
    async def handle_show_channel_callback(callback: CallbackQuery, callback_data: dict):
        channel_id = int(callback_data.get('channel_id'))
        await callback.message.edit_text(**Handlers.__get_channel_message_data(channel_id=channel_id))

    @staticmethod
    async def handle_add_channel_to_list_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text='➕ <b>Добавление канала / чата </b> ➕ \n\n'
                 '1) Добавьте бота в канал и дайте ему права: \n'
                 '<b>Добавление участников - ✔</b> (для канала) \n'
                 '<b>Пригласительные ссылки - ✔</b> (для чата) \n'
                 '2) Перешлите боту любой пост из канала / чата, который хотите добавить:',
            reply_markup=Keyboards.get_cancel()
        )
        await state.set_state(JoinRequestChannelAdding.wait_for_post)

    @staticmethod
    async def handle_channel_to_add_post_message(message: Message, state: FSMContext):
        if message.forward_from_chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
            await message.answer('Это не пост из канала! Попробуйте снова: ')
            return

        try:
            chat = await message.bot.get_chat(chat_id=message.forward_from_chat.id)
            bot_as_member = await chat.get_member(message.bot.id)
        except Unauthorized:
            await message.answer(text='Вы не добавили бота в этот канал / чат! \nСделайте это и попробуйте снова: ')
            return
        else:
            is_bot_have_rights = bot_as_member.is_chat_admin() and bot_as_member.can_invite_users
            if not is_bot_have_rights:
                await message.answer(text=Messages.get_bot_have_no_rights())
                return

        chat = message.forward_from_chat

        await state.update_data(chat_id=chat.id, chat_title=chat.title)
        await message.answer(Messages.ask_for_welcome_text())
        await state.set_state(JoinRequestChannelAdding.wait_for_welcome_text)

    @staticmethod
    async def handle_channel_welcome_text(message: Message, state: FSMContext):
        await state.update_data(welcome_text=message.html_text)

        await message.answer(Messages.ask_for_goodbye_text())
        await state.set_state(JoinRequestChannelAdding.wait_for_goodbye_text)

    @staticmethod
    async def handle_channel_goodbye_text(message: Message, state: FSMContext):
        data = await state.get_data()
        join_request_channels.add_join_request_channel(
            channel_id=data.get('chat_id'), channel_title=data.get('chat_title'),
            welcome_text=data.get('welcome_text'), goodbye_text=message.html_text,
        )
        await message.answer('✅ Готово! Канал добавлен', reply_markup=Keyboards.get_channels_list())
        await state.finish()

    # ИЗМЕНЕНИЕ
    # переключение принятия заявок
    @classmethod
    async def handle_toggle_accept_joins(
            cls, callback: CallbackQuery, callback_data: Keyboards.join_request_channels_callback
    ):
        channel_id = callback_data.get('channel_id')
        channel = join_request_channels.get_join_request_channel_or_none(channel_id=channel_id)
        if not channel:
            return
        join_request_channels.update_allow_joins_approving(
            channel_id=channel_id,
            accept=not channel.allow_approving
        )
        msg_data = cls.__get_channel_message_data(channel_id=channel_id)
        await callback.message.edit_text(**msg_data)

    # изменить текст приветствия
    @staticmethod
    async def handle_edit_welcome_text(
            callback: CallbackQuery, state: FSMContext, callback_data: Keyboards.join_request_channels_callback
    ):
        channel_id = int(callback_data.get('channel_id'))
        await state.update_data(channel_id=channel_id)
        await callback.message.edit_text(
            text=Messages.ask_for_welcome_text(), reply_markup=Keyboards.get_cancel()
        )
        await state.set_state(JoinRequestChannelEditing.edit_welcome_text)

    @staticmethod
    async def handle_new_welcome_text(message: Message, state: FSMContext):
        data = await state.get_data()
        channel_id = int(data.get('channel_id'))
        join_request_channels.update_welcome_text(channel_id=channel_id, new_welcome=message.text)

        await message.answer(text=Messages.get_data_changed())
        await message.answer(**Handlers.__get_channel_message_data(channel_id=channel_id))
        await state.finish()

    # изменить текст прощания
    @staticmethod
    async def handle_edit_goodbye_text(
            callback: CallbackQuery, state: FSMContext, callback_data: Keyboards.join_request_channels_callback
    ):
        channel_id = int(callback_data.get('channel_id'))
        await state.update_data(channel_id=channel_id)
        await callback.message.edit_text(
            text=Messages.ask_for_goodbye_text(), reply_markup=Keyboards.get_cancel()
        )
        await state.set_state(JoinRequestChannelEditing.edit_goodbye_text)

    @staticmethod
    async def handle_new_goodbye_text(message: Message, state: FSMContext):
        data = await state.get_data()
        channel_id = int(data.get('channel_id'))
        join_request_channels.update_goodbye_text(channel_id=channel_id, new_goodbye=message.text)

        await message.answer(text=Messages.get_data_changed())
        await message.answer(**Handlers.__get_channel_message_data(channel_id=channel_id))
        await state.finish()

    # УДАЛЕНИЕ
    @staticmethod
    async def handle_delete_channel_callbacks(callback: CallbackQuery, callback_data: dict):
        channel_id = callback_data.get('channel_id')
        text = 'Какой канал вы хотите убрать?'

        if not channel_id:
            await callback.message.edit_text(text=text, reply_markup=Keyboards.get_channels_to_delete())
            return

        join_request_channels.  delete_join_request_channel(channel_id)
        await callback.message.edit_text('Канал удалён из списка')
        await callback.message.edit_text(text=text, reply_markup=Keyboards.get_channels_to_delete())

    @classmethod
    def register_welcome_handlers(cls, dp: Dispatcher):
        # отмена
        dp.register_callback_query_handler(
            cls.handle_cancel_callback, Keyboards.join_request_channels_callback.filter(action='cancel'), state='*')

        # список каналов
        dp.register_message_handler(cls.handle_join_accept_channels_button,
                                    text=Keyboards.reply_button_for_admin_menu.text)

        # добавить канал
        dp.register_callback_query_handler(
            cls.handle_add_channel_to_list_callback, Keyboards.join_request_channels_callback.filter(action='add')
        )
        dp.register_message_handler(
            cls.handle_new_welcome_text, content_types=[ContentType.TEXT],
            state=JoinRequestChannelEditing.edit_welcome_text
        )

        dp.register_message_handler(
            cls.handle_channel_to_add_post_message,
            lambda msg: msg.is_forward(),
            content_types=[ContentType.ANY],
            state=JoinRequestChannelAdding.wait_for_post
        )

        dp.register_message_handler(
            cls.handle_channel_welcome_text, state=JoinRequestChannelAdding.wait_for_welcome_text)
        dp.register_message_handler(
            cls.handle_channel_goodbye_text, state=JoinRequestChannelAdding.wait_for_goodbye_text)

        # показать / изменить канал
        dp.register_callback_query_handler(
            cls.handle_show_channel_callback, Keyboards.join_request_channels_callback.filter(action='show'))

        # переключатель принятия заявок
        dp.register_callback_query_handler(
            cls.handle_toggle_accept_joins, Keyboards.join_request_channels_callback.filter(action='toggle_accept')
        )

        # изменение текста приветствия
        dp.register_callback_query_handler(
            cls.handle_edit_welcome_text, Keyboards.join_request_channels_callback.filter(action='edit_welcome_text')
        )
        dp.register_message_handler(
            cls.handle_new_welcome_text, content_types=[ContentType.TEXT],
            state=JoinRequestChannelEditing.edit_welcome_text
        )

        # изменение текста прощания
        dp.register_callback_query_handler(
            cls.handle_edit_goodbye_text, Keyboards.join_request_channels_callback.filter(action='edit_goodbye_text')
        )
        dp.register_message_handler(
            cls.handle_new_goodbye_text, content_types=[ContentType.TEXT],
            state=JoinRequestChannelEditing.edit_goodbye_text
        )

        # удалить канал
        dp.register_callback_query_handler(
            cls.handle_delete_channel_callbacks, Keyboards.join_request_channels_callback.filter(action='delete')
        )
