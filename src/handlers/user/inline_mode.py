from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultAudio, InlineQueryResultArticle, InputTextMessageContent

from src.filters import IsSubscriberFilter
from src.handlers.user.search_song import get_song_file
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.utils.vkpymusic import SessionsManager


def get_not_found_article() -> InlineQueryResultArticle:
    not_found_text = UserMessages.get_song_not_found_error()
    input_msg_content = InputTextMessageContent(message_text=not_found_text)

    return InlineQueryResultArticle(
        id="0", title=UserMessages.get_song_not_found_error(),
        input_message_content=input_msg_content
    )


async def handle_search_song_inline(query: InlineQuery):
    service = await SessionsManager().get_available_service()
    _, songs = await service.search_songs_by_text(text=query.query, count=20)

    if not songs:
        await query.answer(results=[get_not_found_article()], cache_time=1, is_personal=True)
        return

    response_items = []
    bot_username = (await query.bot.get_me()).username
    markup = UserMessages.get_audio_file_caption(bot_username=bot_username)

    for song in songs:
        audio = get_song_file(song)
        if not isinstance(audio, str):
            audio = song.url

        response_items.append(
            InlineQueryResultAudio(
                id=f"{song.owner_id}_{song.song_id}",
                audio_url=audio, title=song.title, performer=song.artist,
                caption=markup, parse_mode='HTML'
            )
        )

    bot_full_name = (await query.bot.get_me()).full_name
    await query.answer(
        results=response_items, next_offset="break",
        switch_pm_text=bot_full_name, switch_pm_parameter='_',
        cache_time=10_000, is_personal=False  # Если введённый запрос уже был, телеграм отправит результат сразу
    )


async def unsubscribed_inline_search(query: InlineQuery):
    await query.answer(
        results=[], cache_time=1, is_personal=True,
        switch_pm_text='Нажмите и подпишитесь на спонсоров в боте',
        switch_pm_parameter='show_channels_to_subscribe'
    )


def register_inline_mode_handlers(dp: Dispatcher):
    # Поиск без подписки
    dp.register_inline_handler(unsubscribed_inline_search, IsSubscriberFilter(False))

    # Обычный поиск
    # Срабатывает, если текст запроса не пустой и отсутствует смещение
    dp.register_inline_handler(
        handle_search_song_inline,
        lambda query: query.query.strip() != '' and query.offset == ""
    )
