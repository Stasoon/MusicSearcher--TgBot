from typing import Literal

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher

from src.misc.callback_data import PagesNavigationCallback
from src.database import song_catalogs
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.utils.vkpymusic import SessionsManager, Song
from config import i18n
from config.settings import MAX_SONG_PAGES_COUNT, SONGS_PER_PAGE


# region Utils

__ = i18n.lazy_gettext


def calculate_page_to_show_number(callback_data: PagesNavigationCallback) -> int:
    direction = callback_data.get('direction')
    max_pages = int(callback_data.get('max_pages'))
    current_page_num = int(callback_data.get('page_num'))

    page_to_show_num = 1
    if direction == 'next':
        page_to_show_num = (current_page_num + 1) if current_page_num < max_pages else 1
    elif direction == 'prev':
        page_to_show_num = (current_page_num - 1) if current_page_num > 1 else max_pages
    return page_to_show_num


#################   РАЗДЕЛИТЬ ЭТО ПО МОДУЛЯМ
async def get_next_page_songs(
        category: Literal['new', 'popular', 'search'],
        callback: CallbackQuery,
        songs_per_page: int,
        offset: int,
        target_data
) -> list[Song]:
    match category:
        case 'search':
            service = await SessionsManager().get_available_service()
            count, songs = await service.search_songs_by_text(
                text=callback.message.text, count=songs_per_page, offset=offset
            )
            return songs
        case 'popular' | 'new':
            return song_catalogs.get_songs_from_catalog(category=category, count=songs_per_page, offset=offset)
        case 'profile_songs':
            service = await SessionsManager().get_available_service()
            count, songs = await service.get_profile_songs(
                user_id=target_data, count=songs_per_page, offset=offset
            )
            return songs


# endregion


# region Menu


async def handle_new_songs_button(message: Message, state: FSMContext):
    await state.finish()
    await message.answer_chat_action(action='typing')

    songs = song_catalogs.get_songs_from_catalog('new', count=SONGS_PER_PAGE, offset=0)
    text = UserMessages.get_new_songs()
    markup = UserKeyboards.get_found_songs(songs, category='new', max_pages=MAX_SONG_PAGES_COUNT)

    await message.answer(text=text, reply_markup=markup, parse_mode='HTML')


async def handle_popular_songs_button(message: Message, state: FSMContext):
    await state.finish()
    await message.answer_chat_action(action='typing')

    songs = song_catalogs.get_songs_from_catalog(category='popular', count=SONGS_PER_PAGE, offset=0)
    text = UserMessages.get_popular_songs()
    markup = UserKeyboards.get_found_songs(songs, category='popular', max_pages=MAX_SONG_PAGES_COUNT)

    await message.answer(text=text, reply_markup=markup, parse_mode='HTML')


async def handle_search_song_button(message: Message, state: FSMContext):
    await state.finish()
    await message.answer_chat_action(action='typing')
    await message.answer(text=UserMessages.get_search_song(), parse_mode='HTML')


async def handle_songs_navigation_callbacks(callback: CallbackQuery, callback_data: PagesNavigationCallback):
    # Рассчитываем смещение
    songs_per_page = int(callback_data.get('count_per_page'))
    page_to_show_num = calculate_page_to_show_number(callback_data)
    offset = (page_to_show_num - 1) * songs_per_page

    # Получаем песни
    category = callback_data.get('category')
    target_data = callback_data.get('target_data')
    songs = await get_next_page_songs(category, callback, songs_per_page, offset, target_data)

    if len(songs) < songs_per_page:
        await callback.answer()
        return

    # Создаём клавиатуру и отправляем
    markup = UserKeyboards.get_found_songs(
        songs=songs, current_page_num=page_to_show_num,
        category=callback_data.get('category'), max_pages=int(callback_data.get('max_pages')),
        target_data=target_data
    )
    await callback.message.edit_reply_markup(reply_markup=markup)


async def handle_empty_callbacks(callback: CallbackQuery):
    await callback.answer()


# endregion


async def handle_old_buttons(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Бот обновился, поэтому старые кнопки не работают! \nНажмите /start')


def register_navigation_handlers(dp: Dispatcher):
    # Для старых пользователей
    dp.register_message_handler(
        handle_old_buttons,
        lambda message: message.text in ('🎙Популярное', '🔥Мировой чарт', '🔍Поиск', '🎧Новинки'),
        state='*'
    )

    # Кнопки меню
    dp.register_message_handler(handle_new_songs_button, Text(equals=__("🎶 Новинки")), state='*')
    dp.register_message_handler(handle_popular_songs_button, Text(equals=__("🎧 Популярное")), state='*')
    dp.register_message_handler(handle_search_song_button, Text(equals=__("🔍 Поиск")), state='*')

    # Навигация по страницам с песнями
    dp.register_callback_query_handler(
        handle_songs_navigation_callbacks, PagesNavigationCallback.filter(), state='*'
    )
    dp.register_callback_query_handler(handle_empty_callbacks, lambda callback: callback.data == '*', state='*')
