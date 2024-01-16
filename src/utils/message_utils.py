from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest

from src.database.advertisements import get_random_ad, increase_counter_and_get_value, reset_counter
from src.database.subscriptions import has_subscription
from src.messages.user import UserMessages
from src.keyboards.user import UserKeyboards
from src.utils.keyboard_utils import get_inline_kb_from_json
from src.filters.is_subscriber import get_not_subscribed_channels


async def send_advertisement(bot: Bot, user_id: int):
    """ Отправляет рекламу """
    if has_subscription(user_id=user_id):
        return

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

    await bot.send_message(
        chat_id=user_id, text=text, reply_markup=markup,
        disable_web_page_preview=not ad.show_preview, parse_mode='HTML'
    )


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

            await func(update, *args)
            try:
                await timer_msg.delete()
            except BadRequest:
                pass
        return wrapper
    return decorator


async def send_audio_message(bot: Bot, chat_id: int, file, song_title=None, artist_name=None, cover=None) -> Message:
    """Sends an audio message in response to a callback query."""
    bot_username = (await bot.get_me()).username
    audio_message = await bot.send_audio(
        chat_id=chat_id, audio=file, title=song_title,
        performer=artist_name, thumb=cover,
        caption=UserMessages.get_audio_file_caption(bot_username=bot_username),
    )
    return audio_message


async def send_channels_to_subscribe(bot, user_id):
    """ Показывает сообщение с просьбой подписаться, нужные каналы и кнопку проверки"""
    channels_to_subscribe = await get_not_subscribed_channels(bot=bot, user_id=user_id)
    markup = UserKeyboards.get_not_subbed_markup(channels_to_subscribe)
    text = UserMessages.get_user_must_subscribe()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
