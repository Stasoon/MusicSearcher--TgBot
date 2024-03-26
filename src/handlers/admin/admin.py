from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ReplyKeyboardMarkup, ChatType

from . import statistic
from . import mailing
from . import necessary_subscriptions
from . import refferal_links
from . import admins_management
from . import edit_ads
from . import welcomes
from . import bot_subscriptions
from . import edit_default_cover


admin_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True, row_width=1
).add(
    statistic.Keyboards.reply_button_for_admin_menu,
    mailing.Keyboards.reply_button_for_admin_menu,
    necessary_subscriptions.Keyboards.reply_button_for_admin_menu,
    welcomes.Keyboards.reply_button_for_admin_menu,
    edit_ads.Keyboards.reply_button_for_admin_menu,
    edit_default_cover.Keyboards.reply_button_for_admin_menu,
    refferal_links.Keyboards.reply_button_for_admin_menu,
    admins_management.Keyboards.reply_button_for_admin_menu,
    bot_subscriptions.Keyboards.reply_button_for_admin_menu,
)


async def handle_admin_command(message: types.Message):
    await send_admin_menu(message)


async def send_admin_menu(message: types.Message):
    await message.answer('💼 Меню администратора: ', reply_markup=admin_kb)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_admin_command, ChatTypeFilter(ChatType.PRIVATE,), is_admin=True, commands=['admin'])

    statistic.Handlers.register_admin_statistic_handlers(dp)
    mailing.Handlers.register_mailing_handlers(dp)
    necessary_subscriptions.Handlers.register_necessary_subscriptions_handlers(dp)
    refferal_links.Handlers.register_reflinks_handlers(dp)
    admins_management.Handlers.register_admin_management_handlers(dp)
    edit_ads.Handlers.register_edit_ads_handlers(dp)
    edit_default_cover.register_edit_default_cover_handlers(dp)
    welcomes.Handlers.register_welcome_handlers(dp)
    bot_subscriptions.register_bot_subscriptions_handlers(dp)
