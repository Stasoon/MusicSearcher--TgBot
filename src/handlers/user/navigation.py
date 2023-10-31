from typing import Literal

from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.utils.exceptions import NetworkError
from aiogram import Dispatcher

from src.misc.callback_data import SongsNavigationCallback, ShowSongCallback, LanguageChoiceCallback
from src.database import users, songs_hashes, saved_songs
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.filters import IsSubscriberFilter
from src.utils.vk_music_api import VkMusicApi
from src.utils.vkpymusic import VkSong
from config import i18n


# region Utils

__ = i18n.lazy_gettext


def __get_song_file(song: VkSong) -> InputFile | str:
    file_id = songs_hashes.get_song_file_id(song_id=song.song_id, owner_id=song.owner_id)

    if file_id: return file_id
    return InputFile.from_url(url=song.url, filename=song.title)


def calculate_page_to_show_number(callback_data: SongsNavigationCallback) -> int:
    action = callback_data.get('action')
    max_pages = int(callback_data.get('max_pages'))
    current_page_num = int(callback_data.get('page_num'))

    page_to_show_num = 1
    if action == 'next':
        page_to_show_num = (current_page_num + 1) if current_page_num < max_pages else 1
    elif action == 'prev':
        page_to_show_num = (current_page_num - 1) if current_page_num > 1 else max_pages
    return page_to_show_num


async def send_audio_message(callback, song, file, cover) -> Message:
    bot_username = (await callback.bot.get_me()).username
    audio_message = await callback.message.answer_audio(
        audio=file, title=song.title, performer=song.artist, thumb=cover,
        caption=UserMessages.get_audio_file_caption(bot_username=bot_username)
    )
    return audio_message


async def get_next_page_songs(
        category: Literal['new', 'popular', 'search'],
        callback: CallbackQuery,
        songs_per_page: int,
        offset: int
) -> list[VkSong]:
    if category == 'search':
        return await VkMusicApi.get_songs_by_text(text=callback.message.text, count=songs_per_page, offset=offset)
    elif category in ('popular', 'new'):
        return saved_songs.get_songs_from_catalog(category=category, count=songs_per_page, offset=offset)
    return []


# endregion


# region Menu


async def handle_language_choice_callback(callback: CallbackQuery, callback_data: LanguageChoiceCallback):
    lang_code = callback_data.get('lang_code')
    users.update_user_lang_code(telegram_id=callback.from_user.id, new_lang_code=lang_code)
    i18n.change_locale_context(lang_code)

    await callback.answer(UserMessages.get_language_selected())
    await callback.message.delete()
    await callback.message.answer(
        text=UserMessages.get_search_song(),
        reply_markup=UserKeyboards.get_main_menu_markup()
    )


async def handle_new_songs_button(message: Message):
    await message.answer_chat_action(action='typing')

    songs = saved_songs.get_songs_from_catalog('new', count=8, offset=0)
    text = UserMessages.get_new_songs()
    markup = UserKeyboards.get_found_songs(songs, category='new', max_pages=12)

    await message.answer(text=text, reply_markup=markup, parse_mode='HTML')


async def handle_popular_songs_button(message: Message):
    await message.answer_chat_action(action='typing')

    songs = saved_songs.get_songs_from_catalog(category='popular', count=8, offset=0)
    text = UserMessages.get_popular_songs()
    markup = UserKeyboards.get_found_songs(songs, category='popular', max_pages=12)

    await message.answer(text=text, reply_markup=markup, parse_mode='HTML')


async def handle_search_song_button(message: Message):
    await message.answer_chat_action(action='typing')
    await message.answer(text=UserMessages.get_search_song(), parse_mode='HTML')


async def handle_songs_navigation_callbacks(callback: CallbackQuery, callback_data: SongsNavigationCallback):
    # Рассчитываем смещение
    max_pages = int(callback_data.get('max_pages'))
    songs_per_page = int(callback_data.get('count_per_page'))
    page_to_show_num = calculate_page_to_show_number(callback_data)
    offset = (page_to_show_num - 1) * songs_per_page

    # Получаем песни
    category = callback_data.get('category')
    songs = await get_next_page_songs(category, callback, songs_per_page, offset)

    # Создаём клавиатуру и отправляем
    markup = UserKeyboards.get_found_songs(
        songs=songs, current_page_num=page_to_show_num, category=callback_data.get('category'), max_pages=max_pages
    )
    await callback.message.edit_reply_markup(reply_markup=markup)


async def handle_show_song_callback(callback: CallbackQuery, callback_data: ShowSongCallback):
    await callback.answer()
    await callback.bot.send_chat_action(chat_id=callback.from_user.id, action='UPLOAD_VOICE')

    song_id, owner_id = callback_data.get('song_id'), callback_data.get('owner_id')
    song = await VkMusicApi.get_song_by_id(owner_id=owner_id, song_id=song_id)

    if not song:
        await VkMusicApi.get_song_by_id(owner_id=2001209496, song_id=123209496)
        await callback.message.answer('Произошла ошибка :(')
        return

    file = __get_song_file(song)

    try:
        file_msg = await send_audio_message(callback=callback, song=song, file=file, cover=None)
    except NetworkError:
        await callback.message.answer(text=UserMessages.get_audiofile_too_huge_error())
    else:
        songs_hashes.save_song_if_not_hashed(
            song_id=song.song_id, owner_id=song.owner_id, file_id=file_msg.audio.file_id
        )


# endregion


def register_navigation_handlers(dp: Dispatcher):
    # Кнопки меню
    dp.register_message_handler(handle_new_songs_button, lambda message: message.text == __("🎶 Новинки"))
    dp.register_message_handler(handle_popular_songs_button, lambda message: message.text == __("🎧 Популярное"))
    dp.register_message_handler(handle_search_song_button, lambda message: message.text == __("🔍 Поиск"))

    # Выбор языка
    dp.register_callback_query_handler(handle_language_choice_callback, LanguageChoiceCallback.filter())

    # Навигация по страницам с песнями
    dp.register_callback_query_handler(handle_songs_navigation_callbacks, SongsNavigationCallback.filter())

    # Показать песню (если подписан)
    dp.register_callback_query_handler(
        handle_show_song_callback, ShowSongCallback.filter(),
        IsSubscriberFilter(should_be_subscriber=True)
    )
