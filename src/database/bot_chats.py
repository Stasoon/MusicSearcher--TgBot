from typing import Generator

from .models import BotChat


def add_bot_chat(chat_id: int) -> bool:
    chat, created = BotChat.get_or_create(chat_id=chat_id)
    return created


def get_bot_chat_ids() -> Generator[int, any, any]:
    yield from (chat.chat_id for chat in BotChat.select())


def get_bot_chats_count() -> int:
    return BotChat.select().count()
