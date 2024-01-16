from datetime import datetime

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from src.database.models import User


class UserActivityMiddleware(BaseMiddleware):

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.update_user_activity(message.from_user.id)

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        await self.update_user_activity(callback_query.from_user.id)

    async def update_user_activity(self, user_id: int):
        user = User.get_or_none(telegram_id=user_id)
        if not user:
            return
        user.last_activity = datetime.now()
        user.save()
