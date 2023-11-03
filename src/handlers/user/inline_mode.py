from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultAudio, InlineQueryResultArticle, InputTextMessageContent

from src.filters import IsSubscriberFilter
from src.handlers.user.searching import get_song_file
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


# # Дописать проверку подписки
# async def inline_search(query: InlineQuery):
#     results = []
#     channels = ['stascsa', 'testchannel', 'wb']
#     for channel_link in channels:
#         # Создаем описание со ссылкой на канал
#         channel_link = "https://t.me/your_channel_username"  # Замените на фактическую ссылку на канал
#         description_with_link = f"<a href='{channel_link}'>Перейти в канал</a>"
#
#         # Создаем InlineQueryResultArticle с описанием, содержащим ссылку
#         result = InlineQueryResultArticle(
#             id="1",
#             title="Заголовок результата",
#             input_message_content=InputTextMessageContent(message_text="Текст сообщения"),
#             description=description_with_link,
#         )
#
#         results.append(result)
#
#     # Отправляем результаты в ответ на инлайн-запрос
#     await query.answer(results, cache_time=1)


async def handle_search_song_inline(query: InlineQuery):
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
        audio = get_song_file(song)
        if not isinstance(audio, str): audio = song.url

        response_items.append(
            InlineQueryResultAudio(
                id=f"{song.owner_id}_{song.song_id}",
                audio_url=audio, title=song.title, performer=song.artist,
                reply_markup=markup, parse_mode='HTML'
            )
        )

    await query.answer(response_items, cache_time=1, is_personal=True, next_offset=next_offset)


def register_inline_mode_handlers(dp: Dispatcher):
    dp.register_inline_handler(handle_search_song_inline, IsSubscriberFilter(True))
    # dp.register_inline_handler(inline_search)
