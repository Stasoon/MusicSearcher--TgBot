from aiogram import Dispatcher
from aiogram.types import ChatJoinRequest

from src.database.users import create_user_if_not_exist
from src.database.join_request_channels import get_join_request_channel_or_none, increase_requests_approved_count


async def handle_join_request(join_request: ChatJoinRequest):
    user = join_request.from_user
    create_user_if_not_exist(telegram_id=user.id, firstname=user.first_name, username=user.username)

    channel = get_join_request_channel_or_none(channel_id=join_request.chat.id)
    request_invite_link = join_request.invite_link.invite_link.replace('...', '')

    if not channel or channel.invite_link.startswith(request_invite_link):
        increase_requests_approved_count(channel_id=channel.channel_id)

        await join_request.bot.send_message(chat_id=user.id, text=channel.welcome_text)
        await join_request.approve()

    # {
    # "chat": {"id": -1002028682085, "title": "cdsgfjk", "type": "channel"},
    # "from": {
    #   "id": 5893917784,
    #   "is_bot": false,
    #   "first_name": "Петя",
    #   "last_name": "Ткаченко",
    #   "username": "petkach1",
    #   "language_code": "ru"
    # },
    # "user_chat_id": 5893917784,
    # "date": 1701518680,
    #  "invite_link": {
    #  "invite_link": "https://t.me/+EnmKxAnB...",
    #  "name": "testbot",
    #  "creator": {
        #  "id": 1136918511,
        #  "is_bot": false,
        #  "first_name": "StAs",
        #  "username": "stascsa",
        #  "language_code": "ru"
    #  }, "pending_join_request_count": 1, "creates_join_request": 10801,
    #                  "is_primary": false, "is_revoked": false}}


def register_join_requests_approving_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(handle_join_request)
