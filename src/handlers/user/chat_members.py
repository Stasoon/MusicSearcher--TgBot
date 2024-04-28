from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatMemberUpdated, ChatJoinRequest
from aiogram.utils.exceptions import CantInitiateConversation

from src.database import join_request_channels
from src.database.models import WaitAnswerWelcome
from src.database.users import create_user_if_not_exist
from src.misc.user_states import AnswerWelcomeStates


async def handle_left_chat_member(update: ChatMemberUpdated):
    chat = join_request_channels.get_join_request_channel_or_none(channel_id=update.chat.id)

    if chat and chat.goodbye_text:
        try:
            await update.bot.send_message(
                chat_id=update.old_chat_member.user.id, text=chat.goodbye_text
            )
        except CantInitiateConversation:
            pass


async def handle_join_request(join_request: ChatJoinRequest):
    user = join_request.from_user
    create_user_if_not_exist(telegram_id=user.id, firstname=user.first_name, username=user.username)

    channel = join_request_channels.get_join_request_channel_or_none(channel_id=join_request.chat.id)
    if not channel:
        return

    if channel.welcome_text:
        await join_request.bot.send_message(chat_id=user.id, text=channel.welcome_text)
        channel.sent_welcomes_count += 1
        channel.save()

    if channel.allow_approving:
        join_request_channels.increase_requests_approved_count(channel_id=channel.channel_id)
        await join_request.approve()

    WaitAnswerWelcome.get_or_create(channel=channel, user_id=user.id)


# async def handle_start_group(update: ChatMemberUpdated):
#     print(update)


def register_chat_members_handlers(dp: Dispatcher):
    # Запрос на вступление в канал / чат
    dp.register_chat_join_request_handler(handle_join_request)

    # Отписка от канала / чата
    dp.register_chat_member_handler(handle_left_chat_member, lambda update: update.new_chat_member.status == 'left')
