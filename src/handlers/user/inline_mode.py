from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultAudio, InlineQueryResultArticle, InputTextMessageContent

from src.filters import IsSubscriberFilter
from src.handlers.user.navigation import __get_song_file
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.utils import VkMusicApi


def get_not_found():
    not_found_text = UserMessages.get_song_not_found_error()
    input_msg_content = InputTextMessageContent(message_text=not_found_text)

    return InlineQueryResultArticle(
        id="0", title=UserMessages.get_song_not_found_error(),
        input_message_content=input_msg_content
    )


async def handle_inline(query: InlineQuery):
    max_offset = 20
    offset = int(query.offset) if len(query.offset) > 0 else 0
    next_offset = offset + 10
    if offset + 10 > max_offset:
        return

    songs = await VkMusicApi.get_songs_by_text(text=query.query, offset=offset)

    if not songs:
        await query.answer(results=[get_not_found()], cache_time=1, is_personal=True)
        return

    response_items = []
    bot_username = (await query.bot.get_me()).username
    markup = UserKeyboards.get_(bot_username=bot_username)

    for song in songs:
        audio = __get_song_file(song)
        if not isinstance(audio, str): audio = song.url

        response_items.append(
            InlineQueryResultAudio(
                id=f"{song.owner_id}_{song.audio_id}",
                audio_url=audio, title=song.title, performer=song.artist,
                reply_markup=markup, parse_mode='HTML'
            )
        )

    await query.answer(response_items, cache_time=1, is_personal=True, next_offset=next_offset)


def register_inline_mode_handlers(dp: Dispatcher):
    dp.register_inline_handler(handle_inline, IsSubscriberFilter())
