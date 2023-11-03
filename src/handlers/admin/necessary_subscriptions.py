from urllib.parse import urlparse

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import Unauthorized

from src.misc.admin_states import ChannelAdding
from src.database.channel import get_channels, save_channel, delete_channel


# region AddChannels

class Keyboards:
    channel_callback = CallbackData('channel', 'id', 'action')
    reply_button_for_admin_menu = types.KeyboardButton(text='📲 Обязательные подписки 📲')

    add_channel_button = InlineKeyboardButton(text='➕ Добавить канал', callback_data='addchannel')
    delete_channel_button = InlineKeyboardButton(text='➖ Удалить канал', callback_data='delchannel')
    subchecking_menu = InlineKeyboardMarkup(row_width=1).add(add_channel_button, delete_channel_button)

    cancel_button = InlineKeyboardButton(text='🔙 Отменить', callback_data='cancel')
    cancel_markup = InlineKeyboardMarkup(row_width=1).add(cancel_button)

    @classmethod
    def get_channels_markup(cls) -> InlineKeyboardMarkup:
        channels_markup = InlineKeyboardMarkup(row_width=1)
        for channel in get_channels():
            channels_markup.add(
                InlineKeyboardButton(
                    text=channel.title,
                    callback_data=cls.channel_callback.new(
                        id=channel.channel_id,
                        action='delete'
                    )
                )
            )
        channels_markup.add(Keyboards.cancel_button)
        return channels_markup


class Handlers:
    @staticmethod
    async def send_subchecking_menu(message: types.Message):
        text = '📲 Каналы на ОП: \n\n'
        text += " \n".join(
            f"{n}) <a href='{channel.url}'>{channel.title}</a>" for n, channel in enumerate(get_channels(), start=1)
        ) + ' \n\nЧто вы хотите сделать?'
        await message.answer(text=text, reply_markup=Keyboards.subchecking_menu, parse_mode='HTML')

    @staticmethod
    async def __handle_subchecking_message(message: types.Message) -> None:
        await Handlers.send_subchecking_menu(message)

    @staticmethod
    async def __handle_addchannel_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
        await callback.message.delete()
        await callback.message.answer('1) Пригласите бота в нужный канал \n'
                                      '2) Назначьте его администратором, чтобы он мог видеть участников \n'
                                      '3) Перешлите сюда любой пост из канала', reply_markup=Keyboards.cancel_markup)
        await state.set_state(ChannelAdding.wait_for_post)

    @staticmethod
    async def __handle_channel_post_message(message: types.Message, state: FSMContext):
        if not message.is_forward():
            await message.answer('Это не пост из канала! Отправьте боту пост из канала, который хотите добавить')
            return

        try:
            channel = message.forward_from_chat
            bot_as_member = await channel.get_member(message.bot.id)
            if not bot_as_member.is_chat_admin():
                raise Unauthorized
        except Unauthorized:
            await message.answer(
                'Бот не является админом в чате! Сделайте бота админом в канале, чтобы он мог видеть участников, '
                'и повторите попытку. '
            )
        except AttributeError:
            await message.answer('Это не сообщение из канала, либо бот не добавлен в канал! Повторите попытку')
        else:
            await state.update_data(channel_id=channel.id, title=channel.title)
            await message.answer('Теперь пришлите ссылку, по которой будут вступать пользователи:',
                                 reply_markup=Keyboards.cancel_markup)
            await state.set_state(ChannelAdding.wait_for_url)

    @staticmethod
    async def __handle_message_with_url(message: types.Message, state: FSMContext):
        channel_data = await state.get_data()
        parsed_url = urlparse(message.text)
        if bool(parsed_url.scheme and parsed_url.netloc):
            save_channel(channel_data.get('channel_id'), channel_data.get('title'), message.text)
            await message.answer('✅ Канал добавлен на ОП!')
            await state.finish()
        else:
            await message.answer('Это не ссылка. Отправьте ссылку, по которой будут вступать пользователи:')

    @staticmethod
    async def __handle_delchannel_callback(callback: types.CallbackQuery) -> None:
        await callback.message.delete()
        await callback.message.answer('Нажмите на канал, который хотите исключить: ',
                                      reply_markup=Keyboards.get_channels_markup())

    @staticmethod
    async def __handle_delete_channel_action_callback(callback: types.CallbackQuery, callback_data: dict):
        delete_channel(callback_data.get('id'))
        await callback.message.delete()
        await callback.message.answer('✅ Канал исключён из ОП')
        await Handlers.send_subchecking_menu(callback.message)

    @staticmethod
    async def __handle_cancel_callback(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await callback.message.delete()
        await Handlers.send_subchecking_menu(callback.message)

    @classmethod
    def register_necessary_subscriptions_handlers(cls, dp: Dispatcher):
        # обработка текста кнопки из меню админа
        dp.register_message_handler(cls.__handle_subchecking_message,
                                    is_admin=True,
                                    text=Keyboards.reply_button_for_admin_menu.text)

        # обработка калбэка добавить канал
        dp.register_callback_query_handler(cls.__handle_addchannel_callback, text='addchannel')

        # обработка пересланного поста для добавления канала
        dp.register_message_handler(cls.__handle_channel_post_message,
                                    is_admin=True,
                                    content_types=['any'],
                                    state=ChannelAdding.wait_for_post)

        # обработка сообщения со ссылкой
        dp.register_message_handler(cls.__handle_message_with_url,
                                    is_admin=True,
                                    content_types=['text'],
                                    state=ChannelAdding.wait_for_url)

        # обработка калбэка отмены добавления канала
        dp.register_callback_query_handler(cls.__handle_cancel_callback, text='cancel', state='*')

        # обработка удаления канала из ОП
        dp.register_callback_query_handler(cls.__handle_delchannel_callback, text='delchannel')
        dp.register_callback_query_handler(cls.__handle_delete_channel_action_callback,
                                           Keyboards.channel_callback.filter(action='delete'))

# endregion
