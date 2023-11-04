from aiogram.utils.exceptions import NetworkError, FileIsTooBig
from aiogram.types import Message, InputFile, CallbackQuery
from aiogram import Dispatcher

from src.utils.message_utils import send_audio_message, send_and_delete_timer, get_media_file_url, send_advertisement
from src.misc.callback_data import ShowSongCallback
from src.middlewares.throttling import rate_limit
from src.keyboards.user import UserKeyboards
from src.filters import IsSubscriberFilter
from src.messages.user import UserMessages
from src.utils.vk_music_api import VkMusicApi
from src.utils import shazam_api, VkSong
from src.utils import tiktok_api
from src.database import songs_hashes


def get_song_file(song: VkSong) -> InputFile | str:
    file_id = songs_hashes.get_song_file_id(song_id=song.song_id, owner_id=song.owner_id)

    if file_id: return file_id
    return InputFile.from_url(url=song.url, filename=song.title)


async def __send_recognized_song(message: Message, file_url: str):
    try:
        song_data = await shazam_api.recognize_song(file_url=file_url)
        cover = InputFile.from_url(url=song_data.photo_url, filename=f'{song_data.title}')
    except Exception:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

    songs = await VkMusicApi.get_songs_by_text(text=f'{song_data.title} {song_data.subtitle}', count=5)
    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, append_navigation=False)
    text = UserMessages.get_song_info(song_title=song_data.title, author_name=song_data.subtitle)

    await message.answer_photo(photo=cover, reply_markup=markup, caption=text, parse_mode='HTML')


# region Handlers

@rate_limit(limit=1, key='search_by_text')
async def handle_text_message(message: Message):
    await message.answer_chat_action(action='typing')
    songs = await VkMusicApi.get_songs_by_text(text=message.text, count=8)

    if not songs:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, max_pages=12)
    await message.answer(message.text, reply_markup=markup)


@rate_limit(limit=1.5, key='search_by_media')
@send_and_delete_timer()
async def handle_media_message(message: Message):
    file_url = await get_media_file_url(message.bot, message)
    if not file_url: return
    await __send_recognized_song(message=message, file_url=file_url)


@rate_limit(limit=1.5, key='show_song')
@send_and_delete_timer()
async def handle_recognize_song_from_downloaded_video_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    video_url = await get_media_file_url(bot=callback.bot, message=callback.message)
    await __send_recognized_song(message=callback.message, file_url=video_url)


async def handle_youtube_link(message: Message):
    await message.answer_chat_action(action='typing')
    await message.answer('К сожалению, пока что я не умею обрабатывать ссылки на ютуб 😟')


@rate_limit(limit=2, key='show_song')
@send_and_delete_timer()
async def handle_tik_tok_link(message: Message):
    download_link = await tiktok_api.get_tiktok_download_link(message.text)
    video_file = InputFile.from_url(download_link)
    try:
        await message.answer_video(video=video_file, reply_markup=UserKeyboards.get_recognize_song_from_video_button())
    except (NetworkError, FileIsTooBig):
        await message.answer(UserMessages.get_file_too_big_error())


@rate_limit(limit=1, key='show_song')
async def handle_show_song_callback(callback: CallbackQuery, callback_data: ShowSongCallback):
    await callback.answer()
    await callback.bot.send_chat_action(chat_id=callback.from_user.id, action='UPLOAD_VOICE')

    song_id, owner_id = callback_data.get('song_id'), callback_data.get('owner_id')
    song = await VkMusicApi.get_song_by_id(owner_id=owner_id, song_id=song_id)

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
            song_id=song.song_id, owner_id=song.owner_id, file_id=file_msg.audio.file_id
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
        handle_tik_tok_link, lambda message: 'https://www.tiktok.com/' in message.text
    )

    # поиск по тексту
    dp.register_message_handler(handle_text_message, content_types=['text'])

    # кружок / аудио / голосовое / видео
    dp.register_message_handler(
        handle_media_message, content_types=['video_note', 'audio', 'voice', 'video']
    )

    # Узнать песню из видео после того, как она была скачана с TikTok / Youtube
    dp.register_callback_query_handler(
        handle_recognize_song_from_downloaded_video_callback,
        lambda callback: callback.data == 'recognize_song_from_video'
    )

    # Показать песню (если подписан)
    dp.register_callback_query_handler(
        handle_show_song_callback, ShowSongCallback.filter(), IsSubscriberFilter(should_be_subscriber=True)
    )
