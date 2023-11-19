from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from src.database.reflinks import increase_op_count
from src.filters.is_subscriber import IsSubscriberFilter, get_not_subscribed_channels
from src.messages.user import UserMessages
from src.keyboards.user import UserKeyboards


async def handle_not_subscriber_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    channels = await get_not_subscribed_channels(callback.bot, user_id)
    markup = UserKeyboards.get_not_subbed_markup(channels)

    await callback.message.delete()
    await callback.message.answer(
        text=UserMessages.get_user_must_subscribe(),
        reply_markup=markup,
        parse_mode='HTML'
    )


async def handle_user_subscribed_callback(callback: CallbackQuery):
    message = callback.message
    unsubbed_channels = await get_not_subscribed_channels(message.bot, callback.from_user.id)

    if not unsubbed_channels:
        await callback.answer(text=UserMessages.get_user_subscribed(), show_alert=True)
        increase_op_count(callback.from_user.id)
        await message.delete()
    else:
        await callback.answer(text=UserMessages.get_not_all_channels_subscribed(), show_alert=True)


def register_not_subs_handlers(dp: Dispatcher):
    # Нажатие на кнопку "Я подписался"
    dp.register_callback_query_handler(
        handle_user_subscribed_callback,
        lambda callback: callback.data == 'check_subscription'
    )

    # Действия при отсутствии подписки
    dp.register_callback_query_handler(handle_not_subscriber_callback, IsSubscriberFilter(False))
