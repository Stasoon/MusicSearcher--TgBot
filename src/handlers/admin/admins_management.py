from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from src.misc.admin_states import AdminAdding
from src.database.admins import add_admin, delete_admin, is_admin_exist, get_admins


admins_management_callback_data = CallbackData('admins_management', 'action')


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('👤 Управление админами 👤')

    menu_markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('➕ Добавить админа', callback_data=admins_management_callback_data.new('add')),
        InlineKeyboardButton('➖ Исключить админа', callback_data=admins_management_callback_data.new('delete')),
    )

    cancel_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Отменить', callback_data=admins_management_callback_data.new('cancel'))
    )


class Messages:
    @staticmethod
    def get_admins() -> str:
        text = '👤 Управление админами 👤 \n\n' \
               '<b>White-лист администраторских ID:</b> \n\n'
        for n, admin in enumerate(get_admins(), start=1):
            text += f'{n}) <code>{admin.telegram_id}</code> - <a href="tg://user?id={admin.telegram_id}">[ссылка]</a> \n'
        return text


class Handlers:
    @staticmethod
    async def __handle_admin_management_button(message: Message):
        await message.answer(Messages.get_admins(), reply_markup=Keyboards.menu_markup)

    @staticmethod
    async def __handle_add_admin_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer(
            text='🔘 Получите id человека в боте @getmyid_bot. \nЗатем пришлите его сюда',
            reply_markup=Keyboards.cancel_markup
        )
        await state.set_state(AdminAdding.wait_for_new_admin_id)

    @staticmethod
    async def __handle_new_admins_message(message: Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer(
                text='❗id не может содержать букв! Попробуйте снова:',
                reply_markup=Keyboards.cancel_markup
            )
            return

        await state.finish()

        if is_admin_exist(int(message.text)):
            await message.answer(
                '❗ Этот человек уже является админом!',
                reply_markup=Keyboards.cancel_markup
            )
            await Handlers.__handle_admin_management_button(message)
            return

        add_admin(telegram_id=int(message.text), admin_name='Админ')
        await message.answer('✅ Админ добавлен')
        await Handlers.__handle_admin_management_button(message)

    @staticmethod
    async def __handle_delete_admin_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await callback.message.answer(
            text='🔘 Пришлите мне id админа, которого хотите исключить:',
            reply_markup=Keyboards.cancel_markup
        )
        await state.set_state(AdminAdding.wait_for_admin_to_delete_id)

    @staticmethod
    async def __handle_admin_to_delete_id(message: Message, state: FSMContext):
        if delete_admin(message.text):
            await message.answer('✅ Админ исключён!')
            await state.finish()
            await Handlers.__handle_admin_management_button(message)
        else:
            await message.answer('❗Админа с таким id не существует. Попробуйте снова:',
                                 reply_markup=Keyboards.cancel_markup)

    @staticmethod
    async def __handle_cancel_management_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.finish()
        await callback.message.answer(Messages.get_admins(), reply_markup=Keyboards.menu_markup)

    @classmethod
    def register_admin_management_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(
            cls.__handle_admin_management_button,
            text=Keyboards.reply_button_for_admin_menu.text,
            is_admin=True
        )

        # добавление
        dp.register_callback_query_handler(
            cls.__handle_add_admin_callback,
            admins_management_callback_data.filter(action='add'),
            state=None
        )
        dp.register_message_handler(
            cls.__handle_new_admins_message,
            state=AdminAdding.wait_for_new_admin_id,
            is_admin=True
        )

        # удаление
        dp.register_callback_query_handler(
            cls.__handle_delete_admin_callback,
            admins_management_callback_data.filter(action='delete'),
            state=None
        )
        dp.register_message_handler(
            cls.__handle_admin_to_delete_id,
            state=AdminAdding.wait_for_admin_to_delete_id,
            is_admin=True
        )

        # отмена
        dp.register_callback_query_handler(
            cls.__handle_cancel_management_callback,
            admins_management_callback_data.filter(action='cancel'),
            state='*'
        )



