from aiogram.types import ChatMemberStatus, CallbackQuery
from aiogram.utils.exceptions import Unauthorized, ChatNotFound, BotKicked
from aiogram.dispatcher.filters import BoundFilter
from aiogram import Bot

from src.database.channel import get_channels, get_channel_ids
from src.utils import logger


async def get_not_subscribed_channels(bot, user_id):
    not_subbed_channels = [
        channel for channel in get_channels()
        if not await check_status_in_channel_is_member(bot, channel.channel_id, user_id)
    ]
    return not_subbed_channels


async def check_status_in_channel_is_member(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        user = await bot.get_chat_member(channel_id, user_id)
    except (Unauthorized, ChatNotFound, BotKicked) as e:
        logger.exception(e)
        return True

    if user.status != ChatMemberStatus.LEFT:
        return True
    return False


class IsSubscriberFilter(BoundFilter):
    """
    Фильтр "is_subscriber".
    """
    key = "is_subscriber"

    def __init__(self, should_be_subscriber: bool = True):
        self.is_sub = should_be_subscriber

    async def check(self, callback: CallbackQuery):
        for channel_id in get_channel_ids():
            if not await check_status_in_channel_is_member(callback.bot, channel_id, callback.from_user.id):
                return self.is_sub is False

        return self.is_sub is True
