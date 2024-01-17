import asyncio
import re
import json
from concurrent.futures import ThreadPoolExecutor

from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.utils.exceptions import NetworkError, FileIsTooBig, BadRequest
from aiogram.types import Message, InputFile, CallbackQuery, ChatType
from aiogram.utils.markdown import quote_html
from aiogram import Dispatcher

from config import Config
from src.utils.cache_songs import get_cached_songs_for_request, cache_request, get_cached_song
from src.utils.message_utils import send_audio_message, send_and_delete_timer, get_media_file_url, send_advertisement
from src.messages.user import UserMessages
from src.utils.vk_parsing.song_cover import VkSongCover
from src.utils.vkpymusic import SessionsManager, Song
from src.utils import logger, shazam_api, tiktok_api
from src.misc.callback_data import SongCallback
from config.settings import MAX_SONG_PAGES_COUNT, SONGS_PER_PAGE
from src.middlewares.throttling import rate_limit
from src.keyboards.user import UserKeyboards
from src.filters import IsSubscriberFilter
from src.database import song_caches, youtube_videos
from src.utils.vkpymusic.Session import CaptchaNeeded, SessionAuthorizationFailed
from src.utils.youtube_api import get_download_link


async def send_error_notification(e, message: Message):
    """ Отправляет в чат с админами бота сообщение об ошибке """
    # Пока есть ошибки
    msg_dict = json.loads(message.as_json())
    formatted_msg_data = json.dumps(msg_dict, indent=2, ensure_ascii=False)
    logs_chat_id = Config.LOGS_CHAT_ID

    await message.bot.send_message(
        chat_id=logs_chat_id,
        text=f'Песня не найдена. \nОшибка: {e} \nЗапрос: {formatted_msg_data}'
    )


def get_song_file(song: Song) -> InputFile | str:
    """
    Если file_id песни есть в базе данных, возвращает его.
    Иначе возвращает InputFile на основе ссылки на песню.
    """
    file_id = song_caches.get_song_file_id(song_id=song.song_id, owner_id=song.owner_id)

    if file_id: return file_id
    return InputFile.from_url(url=song.url, filename=song.title)


async def __send_recognized_song(message: Message, file_url: str):
    try:
        song_data = await shazam_api.recognize_song(file_url=file_url)
    except Exception:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

    if not song_data:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

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

async def handle_api_error(error, message):
    await send_error_notification(e=error, message=message)
    return 0, []


async def handle_session_auth_error(error, message):
    await message.bot.send_message(
        chat_id=1136918511,
        text=f'Аккаунт ВК перестал работать! \n{error.message} \n{error.session_token}'
    )
    return 0, []


async def make_api_request(message: Message, query: str) -> tuple[int, list[Song]]:
    try:
        service = await SessionsManager().get_available_service()
        found_count, songs = await service.search_songs_by_text(
            text=query, count=MAX_SONG_PAGES_COUNT * SONGS_PER_PAGE
        )
        cache_request(q=query, songs=songs)
        return found_count, songs
    except CaptchaNeeded as e:
        await handle_api_error(e, message)
    except SessionAuthorizationFailed as e:
        await handle_session_auth_error(e, message)
    except Exception as e:
        await handle_api_error(e, message)


async def __send_found_songs(message: Message, query: str, found_count: int, songs: list[Song], caption: str):
    if not songs:
        # await send_error_notification(e="Песня не найдена\n", message=message)
        await message.reply(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

    possible_pages_cnt = found_count // SONGS_PER_PAGE if found_count >= SONGS_PER_PAGE else 1
    max_pages = possible_pages_cnt if possible_pages_cnt < MAX_SONG_PAGES_COUNT else MAX_SONG_PAGES_COUNT

    markup = UserKeyboards.get_found_songs(
        songs[:SONGS_PER_PAGE], current_page_num=1, max_pages=max_pages, target_data=hash(query.lower())
    )
    await message.answer(text=quote_html(caption), reply_markup=markup)


@rate_limit(limit=0.8, key='search_by_text_chat')
async def handle_chat_text_message(message: Message):
    query = message.text.strip().replace('найти', '', 1)
    found_count, songs_from_cache = get_cached_songs_for_request(q=query, count=SONGS_PER_PAGE, offset=0)

    if not songs_from_cache:
        found_count, songs = await make_api_request(message, query=query)
    else:
        songs = songs_from_cache
    await __send_found_songs(message, query=query, found_count=found_count, songs=songs, caption=query)


@rate_limit(limit=0.8, key='search_by_text')
async def handle_text_message(message: Message):
    try:
        await message.answer_chat_action(action='typing')
    except Exception:
        pass

    found_count, songs_from_cache = get_cached_songs_for_request(q=message.text, count=SONGS_PER_PAGE, offset=0)

    if not songs_from_cache:
        found_count, songs = await make_api_request(message, query=message.text)
    else:
        songs = songs_from_cache
    await __send_found_songs(message, query=message.text, found_count=found_count, songs=songs, caption=message.text)


@rate_limit(limit=0.8, key='search_by_media')
@send_and_delete_timer()
async def handle_media_message(message: Message):
    file_url = await get_media_file_url(message.bot, message)
    if not file_url: return
    await __send_recognized_song(message=message, file_url=file_url)


@rate_limit(limit=0.8, key='recognize_from_video')
@send_and_delete_timer()
async def handle_recognize_song_from_downloaded_video_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        video_url = await get_media_file_url(bot=callback.bot, message=callback.message)
        await __send_recognized_song(message=callback.message, file_url=video_url)
    except Exception as e:
        await callback.message.answer(text=UserMessages.get_song_not_found_error())
        logger.error(e)
        return


@rate_limit(limit=0.8, key='download_youtube')
@send_and_delete_timer()
async def handle_youtube_link(message: Message):
    url = message.text

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()

    video_id, download_link = await loop.run_in_executor(executor, get_download_link, url)
    video_from_db = youtube_videos.get_video_or_none(video_id=video_id)

    if video_from_db:
        video_file = video_from_db.file_id
    else:
        video_file = InputFile.from_url(download_link)

    markup = UserKeyboards.get_recognize_song_from_video_button()

    try:
        video_msg = await message.answer_video(video=video_file, reply_markup=markup)
        youtube_videos.save(video_id=video_id, file_id=video_msg.video.file_id)
    except Exception as e:
        logger.error(e)
        await message.answer(text=UserMessages.get_file_too_big_error())
    # await message.answer('К сожалению, скачивание видео с ютуба временно недоступно')


@rate_limit(limit=0.8, key='download_tiktok')
@send_and_delete_timer()
async def handle_tik_tok_link(message: Message):
    for _ in range(5):
        download_link = await tiktok_api.get_tiktok_download_link(message.text)
        video_file = InputFile.from_url(download_link)

        try:
            await message.answer_video(video=video_file, reply_markup=UserKeyboards.get_recognize_song_from_video_button())
        except (NetworkError, FileIsTooBig):
            await message.answer(text=UserMessages.get_file_too_big_error())
        except Exception:
            await asyncio.sleep(0.5)
        else:
            break


async def load_song_file(song_id, owner_id):
    song = get_cached_song(key=f"{owner_id}_{song_id}")

    if not song:
        service = await SessionsManager().get_available_service()
        song = await service.get_song(owner_id=owner_id, audio_id=song_id)

    file = InputFile.from_url(song.url, filename=song.get_file_name())
    song_title = song.title
    artist = song.artist
    return file, song_title, artist


async def handle_show_song_callback(callback: CallbackQuery, callback_data: SongCallback):
    await callback.answer()
    try: await callback.bot.send_chat_action(chat_id=callback.from_user.id, action='UPLOAD_VOICE')
    except Exception: pass

    song_id, owner_id = callback_data.get('id'), callback_data.get('owner_id')

    file = song_caches.get_song_file_id(song_id=song_id, owner_id=owner_id)
    song_title, artist = None, None

    # Если файла нет в БД, скачиваем
    if not file:
        file, song_title, artist = await load_song_file(song_id, owner_id)

    # Если не удалось найти песню нигде, отправляем пользователю сообщение
    if not file:
        await callback.message.answer(UserMessages.get_song_not_found_error())
        return

    cover_url = VkSongCover().get_cover_by_song_id(song_id=song_id, owner_id=owner_id)

    # Отправляем файл
    try:
        file_msg = await send_audio_message(
            bot=callback.bot, chat_id=callback.message.chat.id,
            song_title=song_title, artist_name=artist, file=file,
            cover=InputFile.from_url(cover_url)
        )
    except NetworkError:
        await callback.message.answer(text=UserMessages.get_file_too_big_error())
    else:
        song_caches.save_song_if_not_cached(
            song_id=song_id, owner_id=owner_id, file_id=file_msg.audio.file_id
        )
    finally:
        await send_advertisement(bot=callback.bot, user_id=callback.message.chat.id)


# endregion


def register_searching_handlers(dp: Dispatcher):
    # ссылка на ютуб
    dp.register_message_handler(
        handle_youtube_link,
        ChatTypeFilter([ChatType.PRIVATE]),
        lambda message: 'https://youtu.be/' in message.text or
                        'https://www.youtube.com/' in message.text or
                        'https://youtube.com/' in message.text
    )

    # ссылка на тик ток
    dp.register_message_handler(
        handle_tik_tok_link, ChatTypeFilter([ChatType.PRIVATE]), regexp=re.compile(r'https://\S+\.tiktok\.com/\S+')
    )

    # кружок / аудио / голосовое / видео
    dp.register_message_handler(
        handle_media_message, ChatTypeFilter([ChatType.PRIVATE]), content_types=['video_note', 'audio', 'voice', 'video']
    )

    # поиск по тексту в чате
    dp.register_message_handler(
        handle_chat_text_message, ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
        lambda message: message.text.lower().startswith('найти'), content_types=['text']
    )
    # поиск по тексту в боте
    dp.register_message_handler(handle_text_message, ChatTypeFilter([ChatType.PRIVATE]), content_types=['text'])

    # Узнать песню из видео после того, как она была скачана с TikTok / Youtube
    dp.register_callback_query_handler(
        handle_recognize_song_from_downloaded_video_callback,
        ChatTypeFilter(ChatType.PRIVATE,),
        lambda callback: callback.data == 'recognize_song_from_video'
    )

    # Показать песню в группе
    dp.register_callback_query_handler(
        handle_show_song_callback, SongCallback.filter(),
        ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    )
    # Показать песню в чате с ботом (если подписан)
    dp.register_callback_query_handler(
        handle_show_song_callback, SongCallback.filter(),
        ChatTypeFilter(ChatType.PRIVATE,),
        IsSubscriberFilter(should_be_subscriber=True)
    )
