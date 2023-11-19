from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, MenuButtonCommands


async def set_bot_commands(bot: Bot):
    await bot.delete_my_commands(scope=None, language_code=None)

    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.set_my_commands(
        commands=[
            BotCommand(command='start', description='Запуск бота'),
            BotCommand(command='lang', description='Сменить язык'),
            BotCommand(command='profiles', description='Профили ВКонтакте')
        ],
        scope=BotCommandScopeAllPrivateChats(), language_code='ru'
    )


