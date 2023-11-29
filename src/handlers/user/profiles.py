import json

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest

from src.database import vk_profiles
from src.handlers.user.menu_buttons import calculate_page_to_show_number
from src.messages.user import UserMessages
from src.keyboards.user import UserKeyboards
from src.misc.callback_data import VkProfileCallback, PlaylistCallback, PagesNavigationCallback
from src.misc.user_states import VkProfileAddingStates
from src.utils.vk_parsing.VkProfileParser import VkProfileParser, ProfileLinkValidator
from src.utils.vkpymusic import SessionsManager, Playlist
from src.utils.cache_songs import redis_client


# region Utils

async def __send_saved_profiles(to_message: Message, user_id: int):
    user_saved_profiles = vk_profiles.get_vk_profiles_for_user(
        user_telegram_id=user_id
    )
    await to_message.answer(
        text=UserMessages.get_user_saved_profiles(),
        reply_markup=UserKeyboards.get_user_saved_profiles(profiles=user_saved_profiles),
        disable_web_page_preview=True
    )


async def __send_profile_is_private(callback: CallbackQuery):
    await callback.answer(text=UserMessages.get_profile_is_private(), show_alert=True)
    await __send_saved_profiles(to_message=callback.message, user_id=callback.from_user.id)

    try:
        await callback.message.delete()
    except BadRequest:
        pass


# endregion

# region Handlers

async def handle_profiles_command(message: Message, state: FSMContext):
    await state.finish()
    await __send_saved_profiles(to_message=message, user_id=message.from_user.id)


async def handle_add_profile_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VkProfileAddingStates.wait_for_page_link.state)

    await callback.message.edit_text(
        text=UserMessages.get_profiles_adding_guide(),
        reply_markup=UserKeyboards.get_cancel_profile_adding(),
        disable_web_page_preview=True
    )


async def handle_profile_link_message(message: Message, state: FSMContext):
    if not ProfileLinkValidator.is_profile_link_valid(message.text):
        await message.answer(
            text=UserMessages.get_profile_link_invalid_retry(),
            reply_markup=UserKeyboards.get_cancel_profile_adding(),
            disable_web_page_preview=True
        )
        return

    profile_id, profile_title = await VkProfileParser.get_id_and_title_by_profile_link(profile_link=message.text)
    if not profile_id or not profile_title:
        await message.answer(text=UserMessages.get_profile_not_found())
        await state.finish()
        return

    profile = vk_profiles.create_or_update_profile(profile_id=profile_id, name=profile_title, username=None)
    vk_profiles.save_vk_profile_for_user(user_telegram_id=message.from_user.id, vk_profile=profile)
    await state.finish()
    await __send_saved_profiles(to_message=message, user_id=message.from_user.id)


async def handle_cancel_profile_adding_callback(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.delete()
    await __send_saved_profiles(to_message=callback.message, user_id=callback.from_user.id)


async def handle_show_profile_callback(callback: CallbackQuery, callback_data: VkProfileCallback):
    profile_id = int(callback_data.get('profile_id'))
    vk_profile = vk_profiles.get_profile(profile_id=profile_id)

    await callback.message.edit_text(
        text=UserMessages.get_profile_description(profile_name=vk_profile.name),
        reply_markup=UserKeyboards.get_actions_with_profile(vk_profile=vk_profile),
        parse_mode='HTML',
        disable_web_page_preview=True
    )


async def handle_remove_profile_callback(callback: CallbackQuery, callback_data: VkProfileCallback):
    profile_id = int(callback_data.get('profile_id'))
    profile = vk_profiles.get_profile(profile_id=profile_id)
    vk_profiles.remove_vk_profile_from_user_saves(
        user_telegram_id=callback.from_user.id, vk_profile=profile
    )

    await callback.message.delete()
    await callback.answer(text=UserMessages.get_profile_successfully_removed(profile_name=profile.name))
    await __send_saved_profiles(to_message=callback.message, user_id=callback.from_user.id)


# АУДИОЗАПИСИ ПРОФИЛЯ

async def handle_show_profile_audios_callback(callback: CallbackQuery, callback_data: VkProfileCallback):
    profile_id = int(callback_data.get('profile_id'))
    profile = vk_profiles.get_profile(profile_id)

    service = await SessionsManager().get_available_service()
    songs_count, profile_songs = await service.get_profile_songs(user_id=profile_id, count=8)

    if not profile_songs:
        await __send_profile_is_private(callback)
        return

    await callback.message.delete()
    await callback.message.answer(
        text=UserMessages.get_profile_description(profile_name=profile.name),
        reply_markup=UserKeyboards.get_found_songs(
            songs=profile_songs, category='profile_songs', max_pages=50, target_data=profile_id
        )
    )


# ПЛЕЙЛИСТЫ ПРОФИЛЯ

async def handle_show_profile_playlists_callback(callback: CallbackQuery, callback_data: VkProfileCallback):
    """ Показать плейлисты профиля """
    profile_id = int(callback_data.get('profile_id'))

    # Получаем плейлисты профиля
    service = await SessionsManager().get_available_service()
    playlists_count, profile_playlists = await service.get_profile_playlists(user_id=profile_id)

    # Если плейлисты не найдены, выводим сообщение об ошибке
    if not profile_playlists:
        await __send_profile_is_private(callback)
        return

    # Сохраняем плейлисты в Redis
    for playlist in profile_playlists:
        redis_client.setex(name=f'playlist_{playlist.playlist_id}_{playlist.owner_id}',
                               value=json.dumps(playlist.to_dict()), time=8600)

    # Формируем сообщение и отправляем
    markup = UserKeyboards.get_found_playlists(
        playlists=profile_playlists[:8], category='profile_playlists',
        max_pages=playlists_count // 8, target_data=profile_id
    )
    profile = vk_profiles.get_profile(profile_id)
    await callback.message.edit_text(
        text=UserMessages.get_profile_description(profile_name=profile.name),
        reply_markup=markup
    )


async def handle_profile_playlists_navigation(callback: CallbackQuery, callback_data: PagesNavigationCallback):
    """ Навигация по плейлистам профиля """
    songs_per_page = int(callback_data.get('count_per_page'))
    page_to_show_num = calculate_page_to_show_number(callback_data)
    offset = (page_to_show_num - 1) * songs_per_page

    service = await SessionsManager().get_available_service()
    count, playlists = await service.get_profile_playlists(
        user_id=callback_data.get('target_data'), count=songs_per_page, offset=offset
    )

    markup = UserKeyboards.get_found_playlists(
        playlists=playlists, current_page_num=page_to_show_num,
        category=callback_data.get('category'), max_pages=int(callback_data.get('max_pages')),
        target_data=callback_data.get('target_data')
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except BadRequest:
        await callback.answer()
        pass


async def handle_show_playlist_songs_callback(callback: CallbackQuery, callback_data: PlaylistCallback):
    """ Показать песни плейлиста """
    playlist_id, owner_id = callback_data.get('id'), callback_data.get('owner_id')

    # Получаем информацию о плейлисте из Redis
    playlist = redis_client.get(f'playlist_{playlist_id}_{owner_id}')
    if not playlist:
        return
    playlist = Playlist.from_json(json.loads(playlist))

    # Получаем песни из плейлиста
    session = await SessionsManager().get_available_service()
    playlist_songs = await session.get_playlist_songs(
        playlist_id=playlist_id, owner_id=owner_id, access_key=playlist.access_key
    )

    # Формируем сообщение и отправляем
    markup = UserKeyboards.get_found_songs(
        songs=playlist_songs, category='playlist_songs',
        target_data=f'{playlist_id}_{owner_id}', max_pages=playlist.count // 8
    )
    if playlist.photo:
        await callback.message.answer_photo(photo=playlist.photo, caption=playlist.title, reply_markup=markup)
    else:
        await callback.message.answer(text=playlist.title, reply_markup=markup)
    await callback.message.delete()


async def handle_playlist_songs_navigation(callback: CallbackQuery, callback_data: PagesNavigationCallback):
    songs_per_page = int(callback_data.get('count_per_page'))
    page_to_show_num = calculate_page_to_show_number(callback_data)
    offset = (page_to_show_num - 1) * songs_per_page

    playlist_id, owner_id = map(int, callback_data.get('target_data').split('_'))
    playlist = redis_client.get(f'playlist_{playlist_id}_{owner_id}')
    if not playlist:
        return
    playlist = Playlist.from_json(json.loads(playlist))

    service = await SessionsManager().get_available_service()
    songs = await service.get_playlist_songs(
        playlist_id=playlist_id, owner_id=owner_id, access_key=playlist.access_key, count=songs_per_page, offset=offset
    )

    markup = UserKeyboards.get_found_songs(
        songs=songs, current_page_num=page_to_show_num,
        category=callback_data.get('category'), max_pages=int(callback_data.get('max_pages')),
        target_data=callback_data.get('target_data')
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except BadRequest:
        await callback.answer()
        pass


# endregion

def register_profiles_handlers(dp: Dispatcher):
    # Отмена добавления профиля
    dp.register_callback_query_handler(
        handle_cancel_profile_adding_callback,
        lambda callback: callback.data == 'cancel_profile_adding',
        state='*'
    )

    # Команда /profiles
    dp.register_message_handler(handle_profiles_command, Command("profiles"), state='*')

    # Нажатие на профиль
    dp.register_callback_query_handler(handle_show_profile_callback, VkProfileCallback.filter(action='show'))

    # Добавление профиля
    dp.register_callback_query_handler(
        handle_add_profile_callback,
        lambda callback: callback.data == 'add_profile'
    )

    # Ввод ссылки на профиль
    dp.register_message_handler(handle_profile_link_message, state=VkProfileAddingStates.wait_for_page_link)

    # Показать аудиозаписи профиля
    dp.register_callback_query_handler(handle_show_profile_audios_callback, VkProfileCallback.filter(action='audios'))

    # Показать плейлисты профиля
    dp.register_callback_query_handler(
        handle_show_profile_playlists_callback, VkProfileCallback.filter(action='playlists')
    )
    # Навигация по плейлистам профиля
    dp.register_callback_query_handler(
        handle_profile_playlists_navigation, PagesNavigationCallback.filter(category='profile_playlists')
    )

    # Показать плейлист
    dp.register_callback_query_handler(handle_show_playlist_songs_callback, PlaylistCallback.filter())
    # Навигация по песням плейлиста
    dp.register_callback_query_handler(
        handle_playlist_songs_navigation, PagesNavigationCallback.filter(category='playlist_songs')
    )

    # Удаление профиля
    dp.register_callback_query_handler(handle_remove_profile_callback, VkProfileCallback.filter(action='remove'))
