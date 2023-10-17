from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, Voice, Video, VideoNote, InputFile
from aiogram.utils.exceptions import NetworkError

from config import Config
from src.database import create_user
from src.messages.user import UserMessages
from src.keyboards.user import UserKeyboards
from src.misc.callback_data import SongsNavCallback, ShowSongCallback
# from src.utils.tiktok_api import trending_videos
from src.utils import vk_api, shazam_api


# region Menu


async def handle_start_command(message: Message):
    user = message.from_user
    create_user(telegram_id=user.id, name=user.first_name)

    await message.answer(text=UserMessages.get_welcome(user_name=user.first_name), parse_mode='HTML')
    await message.answer(
        text=UserMessages.get_search_song(),
        reply_markup=UserKeyboards.get_main_menu_markup(),
        parse_mode='HTML'
    )


# async def handle_new_songs_button(message: Message):
#     songs = vk_api.get(count=8, offset=0)
#     markup = UserKeyboards.get_found_songs(songs, category='new')
#     await message.answer(text='Новинки', reply_markup=markup, parse_mode='HTML')


async def handle_popular_songs_button(message: Message):
    songs = vk_api.get_popular_songs(count=8, offset=0)
    text = UserMessages.get_popular()
    markup = UserKeyboards.get_found_songs(songs, category='popular')
    await message.answer(text=text, reply_markup=markup, parse_mode='HTML')


async def handle_search_song_button(message: Message):
    await message.answer(text=UserMessages.get_search_song(), parse_mode='HTML')


async def handle_songs_nav_callback(callback: CallbackQuery, callback_data: SongsNavCallback):
    action = callback_data.get('action')
    current_page_num = int(callback_data.get('page_num'))
    page_to_show_num = current_page_num + (1 if action == 'next' else -1)

    # Проверка на допустимый диапазон страниц
    if page_to_show_num < 1 or page_to_show_num > 5:
        await callback.answer()
        return

    # Рассчитываем смещение
    count = 8
    offset = page_to_show_num * count

    # Получаем песни
    songs = []

    match callback_data.get('category'):
        case 'search':
            songs = vk_api.get_songs_by_text(text=callback.message.text, count=count, offset=offset)
        case 'popular':
            songs = vk_api.get_popular_songs(count=8, offset=offset)
        # case 'new':
        #     songs = vk_api.get_new(count=8, offset=offset)

    # Создаём клавиатуру и отправляем
    markup = UserKeyboards.get_found_songs(songs=songs, current_page_num=page_to_show_num,
                                           category=callback_data.get('category'))
    await callback.message.edit_reply_markup(reply_markup=markup)


async def handle_show_song_callback(callback: CallbackQuery, callback_data: ShowSongCallback):
    await callback.answer()

    song = vk_api.get_song_by_id(song_id=callback_data.get('song_id'), owner_id=callback_data.get('owner_id'))
    file = InputFile.from_url(url=song.url, filename=f'{song.artist} - {song.title}')
    # cover = InputFile.from_url(url=song.cover)

    await callback.bot.send_chat_action(chat_id=callback.from_user.id, action='UPLOAD_VOICE')
    try:
        await callback.message.answer_audio(file)
    except NetworkError:
        await callback.message.answer()


# endregion

# region Searching


async def handle_text_message(message: Message):
    songs = vk_api.get_songs_by_text(text=message.text, count=8)

    if not songs:
        await message.answer(text=UserMessages.get_song_not_found(), parse_mode='HTML')
        return

    markup = UserKeyboards.get_found_songs(songs, current_page_num=1)
    await message.answer(message.text, reply_markup=markup)


async def __get_media_file_url(bot: Bot, message: Message) -> str | None:
    bot_token = Config.BOT_TOKEN
    media = None

    if message.voice:
        media = message.voice
    elif message.audio:
        media = message.audio
    elif message.video_note:
        media = message.video_note
    elif message.video:
        media = message.video

    if not media:
        file = await bot.get_file(media.file_id)
        print(f'https://api.telegram.org/file/bot{bot_token}/{file.file_path}')
        return f'https://api.telegram.org/file/bot{bot_token}/{file.file_path}'
    return None


async def handle_media_message(message: Message):
    timer_msg = await message.answer('⏳')
    file_url = await __get_media_file_url(message.bot, message)
    if not file_url:
        return

    song_data = (await shazam_api.recognize_song(file_url=file_url)).track

    if not song_data:
        await message.answer(text=UserMessages.get_song_not_found(), parse_mode='HTML')
        await timer_msg.delete()
        return

    cover = InputFile.from_url(url=song_data.photo_url, filename=f'{song_data.title} - обложка')
    songs = vk_api.get_songs_by_text(text=f'{song_data.title} {song_data.subtitle}', count=5)
    await timer_msg.delete()

    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, append_navigation=False)
    text = UserMessages.get_song_info(song_title=song_data.title, author_name=song_data.subtitle)
    await message.answer_photo(
        photo=cover,
        reply_markup=markup,
        caption=text,
        parse_mode='HTML'
    )


async def handle_youtube_link():
    return


# endregion


def register_user_handlers(dp: Dispatcher):
    # Команда /start
    dp.register_message_handler(handle_start_command, commands="start")

    # Кнопки меню
    # router.message.register(handle_new_songs_button, F.text.lower().contains("новинки"))
    dp.register_message_handler(handle_popular_songs_button, lambda message: message.text == "🎧 Популярное")
    dp.register_message_handler(handle_search_song_button, lambda message: message.text == "🔍 Поиск")

    # Навигация по страницам с песнями
    dp.register_callback_query_handler(handle_songs_nav_callback, SongsNavCallback.filter())
    dp.register_callback_query_handler(handle_show_song_callback, ShowSongCallback.filter())

    # Поиск
    dp.register_message_handler(handle_text_message, content_types=['text'])
    dp.register_message_handler(handle_media_message, content_types=['video_note', 'voice', 'video'])

    dp.register_message_handler(
        handle_youtube_link,
        lambda message: 'https://youtu.be/' in message.text or 'https://www.youtube.com/' in message.text
    )
