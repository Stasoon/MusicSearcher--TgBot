from aiogram import Dispatcher

from .commands import register_command_handlers
from .navigation import register_navigation_handlers
from .not_subscribers import register_not_subs_handlers
from .searching import register_searching_handlers

from .inline_mode import register_inline_mode_handlers


def register_user_handlers(dp: Dispatcher):
    handlers = [
        register_command_handlers,
        register_navigation_handlers,
        register_not_subs_handlers,
        register_searching_handlers,

        register_inline_mode_handlers
    ]

    for handler in handlers:
        handler(dp)
