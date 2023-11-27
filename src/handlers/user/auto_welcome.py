from aiogram import Dispatcher
from aiogram.types import ChatJoinRequest, ChatMemberUpdated
# from aiogram.dispatcher.filters.filters import MagicFilter

from src.database.users import create_user_if_not_exist


async def handle_join_request(join_request: ChatJoinRequest):
    user = join_request.from_user
    create_user_if_not_exist(telegram_id=user.id, firstname=user.first_name, username=user.username)

    await join_request.bot.send_message(user.id, 'Реклама')
    await join_request.approve()


# async def handle_(update: ChatMemberUpdated):
#     print(update)


def register_auto_welcome_handlers(dp: Dispatcher):
    dp.chat_join_request_handler(handle_join_request)
    # dp.register_message_handler(handle_, content_types=['left_chat_member'])
