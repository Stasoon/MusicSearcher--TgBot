from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest
from aiogram import Bot

from src.messages.user import UserMessages


async def get_media_file_url(bot: Bot, message: Message) -> str | None:
    """ Возвращает ссылку из бота на файл, прикреплённый к сообщению """
    bot_token = bot._token
    media = None

    if message.voice:
        media = message.voice
    elif message.audio:
        media = message.audio
    elif message.video_note:
        media = message.video_note
    elif message.video:
        media = message.video

    if media:
        file = await bot.get_file(media.file_id)
        return f'https://api.telegram.org/file/bot{bot_token}/{file.file_path}'
    return None


def send_and_delete_timer():
    """ Перед отработкой хэндлера отправляет песочные часы, и удаляет их после отработки хэндлера """
    def decorator(func):
        async def wrapper(update: Message | CallbackQuery, *args):
            if isinstance(update, CallbackQuery):
                message = update.message
            else:
                message = update

            timer_msg = await message.answer('⏳')
            await message.answer_chat_action(action='typing')
            await func(update, *args)
            try:
                await timer_msg.delete()
            except BadRequest:
                pass
        return wrapper
    return decorator


async def send_audio_message(callback, song, file, cover) -> Message:
    """  """
    bot_username = (await callback.bot.get_me()).username
    audio_message = await callback.message.answer_audio(
        audio=file, title=song.title, performer=song.artist, thumb=cover,
        caption=UserMessages.get_audio_file_caption(bot_username=bot_username)
    )
    return audio_message


