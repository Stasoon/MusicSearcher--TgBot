from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, StateFilter
from aiogram.types import KeyboardButton, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from src.database import subscriptions
from src.misc.admin_states import BotSubscriptionStates


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('💳 Подписки на бота 💳')
    bot_subscriptions_callback = CallbackData('bot_subs', 'action')

    @classmethod
    def get_subscription_actions(cls) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        gift_button = InlineKeyboardButton(
            text='🎁 Подарить', callback_data=cls.bot_subscriptions_callback.new(action='give')
        )
        take_back_button = InlineKeyboardButton(
            text='⛔ Забрать', callback_data=cls.bot_subscriptions_callback.new(action='take_back')
        )
        return markup.add(gift_button, take_back_button)

    @classmethod
    def get_cancel_give(cls) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        cancel_button = InlineKeyboardButton(
            text='Отменить', callback_data=cls.bot_subscriptions_callback.new(action='cancel')
        )
        markup.add(cancel_button)
        return markup


class Messages:
    @staticmethod
    def get_subscribers_list() -> str:
        subscribers = subscriptions.get_users_with_subscription()
        text = "\n".join([
            f"{n}) <code>{sub.telegram_id}</code> - <a href='tg://user?id={sub.telegram_id}'>{sub.name}</a>"
            for n, sub in enumerate(subscribers, start=1)
        ])
        return text

    @staticmethod
    def get_gift_message() -> str:
        return (
            'Вам выдана премиум подписка 🎁 \n\n'
            'В боте отключена вся реклама, для вашего комфортного прослушивания. \n\n'
            'Амбиции ❤'
        )

    @classmethod
    def get_subscriptions_menu_message_data(cls) -> dict:
        text = f'Список пользователей с подпиской: \n{cls.get_subscribers_list()}'
        reply_markup = Keyboards.get_subscription_actions()
        return {'text': text, 'reply_markup': reply_markup}


async def handle_bot_subscriptions_button(message: Message):
    await message.answer(**Messages.get_subscriptions_menu_message_data())


async def handle_give_subscription_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Напишите телеграм id пользователя, которому хотите подарить подписку:',
        reply_markup=Keyboards.get_cancel_give()
    )
    await state.set_state(BotSubscriptionStates.id_to_give_subscription)


async def handle_user_to_give_subscription_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer('ID может быть только числом!')
        return

    if subscriptions.has_subscription(user_id=user_id):
        await message.answer('Пользователь уже имеет подписку!')
        await state.finish()
        return

    subscription = subscriptions.add_subscribed_user(telegram_id=user_id)
    if not subscription:
        await message.answer('Пользователь не найден! \nПопробуйте снова или нажмите кнопку отмена:')
        return

    await message.bot.send_message(chat_id=user_id, text=Messages.get_gift_message())
    await message.answer('✅ Подписка подарена пользователю')
    await state.finish()
    await message.answer(**Messages.get_subscriptions_menu_message_data())


async def handle_take_back_subscription_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Напишите телеграм id пользователя, у которого хотите <b>забрать</b> подписку:',
        reply_markup=Keyboards.get_cancel_give()
    )
    await state.set_state(BotSubscriptionStates.id_to_take_back_subscription)


async def handle_user_id_to_unsubscribe(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer('ID может быть только числом! \nПопробуйте ещё раз:')
        return

    if not subscriptions.has_subscription(user_id=user_id):
        await message.answer('У пользователя нет подписки! \nПопробуйте ещё раз:')
        return

    is_subscription_removed = subscriptions.remove_subscription(user_id=user_id)
    if not is_subscription_removed:
        await message.answer('Пользователь не найден! \nПопробуйте снова:')
        return

    await message.answer('⛔ Пользователь лишён подписки')
    await state.finish()
    await message.answer(**Messages.get_subscriptions_menu_message_data())


async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(**Messages.get_subscriptions_menu_message_data())
    await state.finish()


def register_bot_subscriptions_handlers(dp: Dispatcher):
    dp.register_message_handler(
        handle_bot_subscriptions_button, Text(equals=Keyboards.reply_button_for_admin_menu.text)
    )

    dp.register_callback_query_handler(
        handle_give_subscription_callback, Keyboards.bot_subscriptions_callback.filter(action='give')
    )
    dp.register_message_handler(
        handle_user_to_give_subscription_id, state=BotSubscriptionStates.id_to_give_subscription
    )

    dp.register_callback_query_handler(
        handle_take_back_subscription_callback, Keyboards.bot_subscriptions_callback.filter(action='take_back')
    )
    dp.register_message_handler(
        handle_user_id_to_unsubscribe, state=BotSubscriptionStates.id_to_take_back_subscription
    )

    dp.register_callback_query_handler(
        handle_cancel_callback,
        Keyboards.bot_subscriptions_callback.filter(action='cancel'),
        state=BotSubscriptionStates.states,
    )
