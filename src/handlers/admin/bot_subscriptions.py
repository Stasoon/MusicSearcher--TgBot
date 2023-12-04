from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from src.database.subscriptions import add_subscribed_user, has_subscription, get_users_with_subscription
from src.misc.admin_states import BotSubscriptionStates


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('💳 Подписки на бота 💳')
    # bot_subscriptions_callback = CallbackData('bot_subs', 'action')

    @staticmethod
    def get_cancel_give() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        cancel_button = InlineKeyboardButton(text='Отменить', callback_data='cancel_give_subscription')
        markup.add(cancel_button)
        return markup


class Messages:
    @staticmethod
    def get_subscribers_list() -> str:
        subscribers = get_users_with_subscription()
        text = "\n".join([
            f"{n}) <code>{sub.telegram_id}</code> - <a href='tg://user?id={sub.telegram_id}'>{sub.name}</a>"
            for n, sub in enumerate(subscribers, start=1)
        ])
        return text


async def handle_bot_subscriptions_button(message: Message, state: FSMContext):
    await message.answer(text=f'Список пользователей с подпиской: \n{Messages.get_subscribers_list()}')
    await message.answer(
        text='Введите telegram id человека, которому хотите подарить подписку:',
        reply_markup=Keyboards.get_cancel_give()
    )
    await state.set_state(BotSubscriptionStates.id_to_give_subscription)


async def handle_user_to_give_subscription_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer('ID может быть только числом!')
        return

    if has_subscription(user_id=user_id):
        await message.answer('Пользователь уже имеет подписку!')
        await state.finish()
        return

    subscription = add_subscribed_user(telegram_id=user_id)
    if not subscription:
        await message.answer('Пользователь не найден! \nПопробуйте снова или нажмите кнопку отмена:')
        return

    await message.answer('✅ Подписка подарена пользователю')
    await state.finish()


async def handle_cancel_subscription_giving(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Отменено')
    await state.finish()


def register_bot_subscriptions_handlers(dp: Dispatcher):
    dp.register_message_handler(
        handle_bot_subscriptions_button, Text(equals=Keyboards.reply_button_for_admin_menu.text)
    )
    dp.register_message_handler(
        handle_user_to_give_subscription_id, state=BotSubscriptionStates.id_to_give_subscription
    )
    dp.register_callback_query_handler(
        handle_cancel_subscription_giving, text='cancel_give_subscription',
        state=BotSubscriptionStates.id_to_give_subscription
    )
