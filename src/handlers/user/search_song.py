import re

from aiogram.utils.exceptions import NetworkError, FileIsTooBig, BadRequest
from aiogram.types import Message, InputFile, CallbackQuery
from aiogram.utils.markdown import quote_html
from aiogram import Dispatcher

from src.utils.message_utils import send_audio_message, send_and_delete_timer, get_media_file_url, send_advertisement
from src.messages.user import UserMessages
from src.utils.vkpymusic import SessionsManager, Song
from src.utils import logger, shazam_api, tiktok_api
from src.misc.callback_data import SongCallback
from config.settings import MAX_SONG_PAGES_COUNT, SONGS_PER_PAGE
from src.middlewares.throttling import rate_limit
from src.keyboards.user import UserKeyboards
from src.filters import IsSubscriberFilter
from src.database import songs_hashes


import json
async def send_error_notification(e, message: Message):
    """ Отправляет в чат с админами бота сообщение об ошибке """
    # Пока есть ошибки
    msg_dict = json.loads(message.as_json())
    formatted_msg_data = json.dumps(msg_dict, indent=2, ensure_ascii=False)
    logs_chat_id = 1136918511  # -1002062707336
    await message.bot.send_message(
        chat_id=logs_chat_id,
        text=f'Песня не найдена. \nОшибка: {e} \nЗапрос: {formatted_msg_data}'
    )


def get_song_file(song: Song) -> InputFile | str:
    """
    Если file_id песни есть в базе данных, возвращает его.
    Иначе возвращает InputFile на основе ссылки на песню.
    """
    file_id = songs_hashes.get_song_file_id(song_id=song.id, owner_id=song.owner_id)

    if file_id: return file_id
    return InputFile.from_url(url=song.url, filename=song.title)


async def __send_recognized_song(message: Message, file_url: str):
    song_data = await shazam_api.recognize_song(file_url=file_url)

    if not song_data:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')

    service = await SessionsManager().get_available_service()
    try:
        _, songs = await service.search_songs_by_text(text=f'{song_data.title} {song_data.subtitle}', count=5)
        markup = UserKeyboards.get_found_songs(songs, current_page_num=1, append_navigation=False)
        text = UserMessages.get_song_info(song_title=song_data.title, author_name=song_data.subtitle)

        if song_data.photo_url:
            cover = InputFile.from_url(url=song_data.photo_url, filename=f'{song_data.title}')
            await message.answer_photo(photo=cover, reply_markup=markup, caption=text, parse_mode='HTML')
        else:
            await message.answer(text=text, reply_markup=markup, parse_mode='HTML')
    except (AttributeError, BadRequest, NetworkError) as e:
        logger.error(e)
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')


# region Handlers

@rate_limit(limit=1, key='search_by_text')
async def handle_text_message(message: Message):
    await message.answer_chat_action(action='typing')

    service = await SessionsManager().get_available_service()
    founded_count, songs = await service.search_songs_by_text(text=message.text, count=SONGS_PER_PAGE)

    possible_pages_cnt = founded_count // SONGS_PER_PAGE if founded_count >= SONGS_PER_PAGE else 1
    max_pages = (
        possible_pages_cnt
        if possible_pages_cnt < MAX_SONG_PAGES_COUNT
        else MAX_SONG_PAGES_COUNT
    )

    if not songs:
        await message.reply(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        # !!!!!!!
        await send_error_notification('При текстовом поиске', message)
        return

    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, max_pages=max_pages)
    await message.answer(text=quote_html(message.text), reply_markup=markup)


@rate_limit(limit=1.5, key='search_by_media')
@send_and_delete_timer()
async def handle_media_message(message: Message):
    file_url = await get_media_file_url(message.bot, message)
    if not file_url: return
    await __send_recognized_song(message=message, file_url=file_url)


@rate_limit(limit=1.5, key='recognize_from_video')
@send_and_delete_timer()
async def handle_recognize_song_from_downloaded_video_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    video_url = await get_media_file_url(bot=callback.bot, message=callback.message)
    await __send_recognized_song(message=callback.message, file_url=video_url)


async def handle_youtube_link(message: Message):
    await message.answer_chat_action(action='typing')
    await message.answer('К сожалению, пока что я не умею обрабатывать ссылки на ютуб 😟')


@rate_limit(limit=2, key='download_tiktok')
@send_and_delete_timer()
async def handle_tik_tok_link(message: Message):
    download_link = await tiktok_api.get_tiktok_download_link(message.text)
    video_file = InputFile.from_url(download_link)
    try:
        await message.answer_video(video=video_file, reply_markup=UserKeyboards.get_recognize_song_from_video_button())
    except (NetworkError, FileIsTooBig):
        await message.answer(text=UserMessages.get_file_too_big_error())


@rate_limit(limit=1.2, key='show_song')
async def handle_show_song_callback(callback: CallbackQuery, callback_data: SongCallback):
    await callback.answer()
    await callback.bot.send_chat_action(chat_id=callback.from_user.id, action='UPLOAD_VOICE')

    song_id, owner_id = callback_data.get('id'), callback_data.get('owner_id')
    service = await SessionsManager().get_available_service()
    song = await service.get_song(owner_id=owner_id, audio_id=song_id)

    if not song:
        await callback.message.answer(UserMessages.get_song_not_found_error())
        return

    file = get_song_file(song)

    try:
        file_msg = await send_audio_message(callback=callback, song=song, file=file, cover=None)
    except NetworkError:
        await callback.message.answer(text=UserMessages.get_file_too_big_error())
    else:
        songs_hashes.save_song_if_not_hashed(
            song_id=song.id, owner_id=song.owner_id, file_id=file_msg.audio.file_id
        )
    finally:
        await send_advertisement(callback.bot, callback.from_user.id)


# endregion


def register_searching_handlers(dp: Dispatcher):
    # ссылка на ютуб
    dp.register_message_handler(
        handle_youtube_link,
        lambda message: 'https://youtu.be/' in message.text or 'https://www.youtube.com/' in message.text
    )

    # ссылка на тик ток
    dp.register_message_handler(
        handle_tik_tok_link, regexp=re.compile(r'https://\S+\.tiktok\.com/\S+')
    )

    # кружок / аудио / голосовое / видео
    dp.register_message_handler(
        handle_media_message, content_types=['video_note', 'audio', 'voice', 'video']
    )

    # поиск по тексту
    dp.register_message_handler(handle_text_message, content_types=['text'])

    # Узнать песню из видео после того, как она была скачана с TikTok / Youtube
    dp.register_callback_query_handler(
        handle_recognize_song_from_downloaded_video_callback,
        lambda callback: callback.data == 'recognize_song_from_video'
    )

    # Показать песню (если подписан)
    dp.register_callback_query_handler(
        handle_show_song_callback, SongCallback.filter(),
        IsSubscriberFilter(should_be_subscriber=True)
    )
