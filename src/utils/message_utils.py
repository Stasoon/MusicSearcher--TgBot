from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest

from src.database.advertisements import get_random_ad, increase_counter_and_get_value, reset_counter
from src.messages.user import UserMessages
from src.utils.keyboards_utils import get_inline_kb_from_json


async def send_advertisement(bot: Bot, user_id: int):
    """ Отправляет рекламу """
    count = increase_counter_and_get_value(user_id=user_id)
    show_ad_every = 4
    if count < show_ad_every:
        return

    ad = get_random_ad()
    if not ad:
        return

    reset_counter(user_id=user_id)
    text = ad.text
    markup = get_inline_kb_from_json(ad.markup_json) if ad.markup_json else None
    await bot.send_message(chat_id=user_id, text=text, reply_markup=markup, parse_mode='HTML')


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


async def send_audio_message(callback, song, file, cover=None) -> Message:
    """ Отправляет аудио-сообщение с музыкой и подписью в ответ на callback запрос. """
    bot_username = (await callback.bot.get_me()).username
    audio_message = await callback.message.answer_audio(
        audio=file, title=song.title, performer=song.artist, thumb=cover,
        caption=UserMessages.get_audio_file_caption(bot_username=bot_username)
    )
    return audio_message


