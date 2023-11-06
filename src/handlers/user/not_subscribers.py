from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from src.database.reflinks import increase_op_count
from src.filters import IsSubscriberFilter
from src.messages.user import UserMessages


async def handle_not_subscriber_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    markup = await IsSubscriberFilter.get_notsubbed_channels_markup_or_none(callback.bot, user_id)

    await callback.message.edit_text(
        text=UserMessages.get_user_must_subscribe(),
        reply_markup=markup,
        parse_mode='HTML'
    )


async def handle_user_subscribed_callback(callback: CallbackQuery):
    message = callback.message
    markup = await IsSubscriberFilter.get_notsubbed_channels_markup_or_none(message.bot, callback.from_user.id)

    if not markup:
        await callback.answer(text=UserMessages.get_user_subscribed(), show_alert=True)
        increase_op_count(callback.from_user.id)
        await message.delete()
    else:
        await callback.answer(text=UserMessages.get_not_all_channels_subscribed(), show_alert=True)


def register_not_subs_handlers(dp: Dispatcher):
    # Нажатие на кнопку "Я подписался"
    dp.register_callback_query_handler(handle_user_subscribed_callback, text='check_subscription')
    # Действия при отсутствии подписки
    dp.register_callback_query_handler(handle_not_subscriber_callback, IsSubscriberFilter(False))
