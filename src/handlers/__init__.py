from aiogram import Dispatcher

from .user import register_user_handlers
from .admin import register_admin_handlers
from .errors import register_errors_handler


def register_all_handlers(dp: Dispatcher):
    register_admin_handlers(dp)
    register_user_handlers(dp)
    register_errors_handler(dp)
