from aiogram import Dispatcher

from .chat_members import register_chat_members_handlers
from .start_cmd import register_start_command_handlers
from .language_choice import register_language_command_handler
from .menu_buttons import register_navigation_handlers
from .search_song import register_searching_handlers
from .profiles import register_profiles_handlers
from .inline_mode import register_inline_mode_handlers
from .not_subscribers import register_not_subs_handlers


def register_user_handlers(dp: Dispatcher):
    handlers = (
        register_chat_members_handlers,
        register_start_command_handlers,
        register_language_command_handler,
        register_profiles_handlers,
        register_navigation_handlers,
        register_searching_handlers,
        register_not_subs_handlers,
        register_inline_mode_handlers,
    )

    for handler in handlers:
        handler(dp)
