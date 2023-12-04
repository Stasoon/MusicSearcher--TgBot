from aiogram import Dispatcher
from aiogram.types import ChatMemberUpdated, ContentType

from src.create_bot import dp


async def handle_new_chat_member(update: ChatMemberUpdated):
    pass
    # {"message_id": 999,
    #  "from": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов", "username": "mihasmirn",
    #           "language_code": "ru"},
    #  "chat": {"id": -4030233224, "title": "dsfsdgbfh", "type": "group", "all_members_are_administrators": true},
    #  "date": 1701521308,
    #  "new_chat_participant": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов",
    #                           "username": "mihasmirn", "language_code": "ru"},
    #  "new_chat_member": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов",
    #                      "username": "mihasmirn", "language_code": "ru"}, "new_chat_members": [
    #     {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов", "username": "mihasmirn",
    #      "language_code": "ru"}]}


async def handle_left_chat_member(update: ChatMemberUpdated):
    print(update)
    # {"message_id": 1000,
    #  "from": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов", "username": "mihasmirn",
    #           "language_code": "ru"},
    #  "chat": {"id": -4030233224, "title": "dsfsdgbfh", "type": "group", "all_members_are_administrators": true},
    #  "date": 1701521355,
    #  "left_chat_participant": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов",
    #                            "username": "mihasmirn", "language_code": "ru"},
    #  "left_chat_member": {"id": 5815704115, "is_bot": false, "first_name": "Миша", "last_name": "Смирнов",
    #                       "username": "mihasmirn", "language_code": "ru"}}\


@dp.chat_member_handler()
async def some_handler(msg: ChatMemberUpdated):
    print(msg)


def register_chat_members_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_new_chat_member, content_types=[ContentType.NEW_CHAT_MEMBERS])
    dp.register_message_handler(handle_left_chat_member, content_types=[ContentType.LEFT_CHAT_MEMBER])
