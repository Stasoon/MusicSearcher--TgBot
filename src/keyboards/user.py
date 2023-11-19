from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from src.misc.callback_data import (
    SongCallback, PlaylistCallback, PagesNavigationCallback, LanguageChoiceCallback, VkProfileCallback
)
from src.utils.vkpymusic import Song, Playlist
from src.database.models import VkProfile
from config import i18n


_ = i18n.gettext


def get_formatted_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    hours_str = f"{hours:02}:" if hours else ""
    return f"{hours_str}{minutes:02}:{seconds:02}"


class UserKeyboards:
    # Обязательные подписки

    @classmethod
    def get_not_subbed_markup(cls, channels_to_sub) -> InlineKeyboardMarkup | None:
        """
        Возвращает клавиатуру с каналами, на которые должен подписаться пользователь,
        и кнопкой 'Проверить подписку'
        """
        if len(channels_to_sub) == 0:
            return None

        channels_markup = InlineKeyboardMarkup(row_width=1)
        [
            channels_markup.add( InlineKeyboardButton(text=channel.title, url=channel.url) )
            for channel in channels_to_sub
        ]
        check_sub_button = InlineKeyboardButton(text=_('✅ Проверить ✅'), callback_data='check_subscription')

        channels_markup.add(check_sub_button)
        return channels_markup

    # Навигация

    @staticmethod
    def get_main_menu_markup() -> ReplyKeyboardMarkup:
        """ Возвращает клавиатуру главного меню """
        markup = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        markup.add(_('🎶 Новинки'), _('🎧 Популярное'))
        markup.row(_('🔍 Поиск'))
        return markup

    @staticmethod
    def __get_songs_navigation_buttons(
            category: str,
            current_page_num: int,
            max_pages: int = 10,
            count_per_page: int = 8,
            target_data: str | int = 'None'
    ) -> list[InlineKeyboardButton]:
        """ Возвращает список кнопок для навигации по страницам с песнями """
        buttons = [
            InlineKeyboardButton(
                text='❮❮', callback_data=PagesNavigationCallback.new(
                    category=category, target_data=target_data, direction='prev',
                    page_num=current_page_num, count_per_page=count_per_page, max_pages=max_pages,
                )),
            InlineKeyboardButton(text=f'{current_page_num}/{max_pages}', callback_data='*'),
            InlineKeyboardButton(
                text='❯❯', callback_data=PagesNavigationCallback.new(
                    category=category, target_data=target_data, direction='next',
                    page_num=current_page_num, count_per_page=count_per_page, max_pages=max_pages,
                ))
        ]
        return buttons

    @staticmethod
    def get_found_songs(
            songs: list[Song],
            current_page_num: int = 1,
            max_pages: int = 10,
            category: str = 'search',
            target_data: str | int = 'None',
            append_navigation: bool = True
    ) -> InlineKeyboardMarkup:
        """ Возвращает клавиатуру с найденными песнями и навигацией по ним """
        markup = InlineKeyboardMarkup()
        [
            markup.row(InlineKeyboardButton(
                text=f"{get_formatted_duration(song.duration)} | {song.title} - {song.artist}",
                callback_data=SongCallback.new(
                    id=song.song_id, owner_id=song.owner_id
                )
            ))
            for song in songs
        ]

        if append_navigation:
            nav_buttons = UserKeyboards.__get_songs_navigation_buttons(
                category=category, current_page_num=current_page_num,
                max_pages=max_pages, target_data=target_data
            )
            markup.row().add(*nav_buttons)
        return markup

    @staticmethod
    def get_found_playlists(
            playlists: list[Playlist],
            current_page_num: int = 1,
            max_pages: int = 10,
            category: str = 'search',
            target_data: str | int = 'None',
            append_navigation: bool = True
    ) -> InlineKeyboardMarkup:
        """ Возвращает клавиатуру с найденными песнями и навигацией по ним """
        markup = InlineKeyboardMarkup()
        for playlist in playlists:
            markup.row(InlineKeyboardButton(
                text=str(playlist),
                callback_data=PlaylistCallback.new(
                    id=playlist.playlist_id, owner_id=playlist.owner_id, access_key=playlist.access_key
                )
            ))
        if append_navigation:
            nav_buttons = UserKeyboards.__get_songs_navigation_buttons(
                category=category, current_page_num=current_page_num,
                max_pages=max_pages, target_data=target_data
            )
            markup.row().add(*nav_buttons)
        return markup

    @staticmethod
    def get_recognize_song_from_video_button() -> InlineKeyboardMarkup:
        """  """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(text=_('🎵 Узнать песню 🎵'), callback_data='recognize_song_from_video'))
        return markup

    # Выбор языка
    @staticmethod
    def get_languages_markup() -> InlineKeyboardMarkup:
        """ Возвращает инлайн клавиатуру с выбором языка"""
        markup = InlineKeyboardMarkup(row_width=1, resize_keyboard=True, is_persistent=True)
        markup.add(InlineKeyboardButton('🇷🇺 Русский', callback_data=LanguageChoiceCallback.new(lang_code='ru')))
        markup.add(InlineKeyboardButton('🇺🇦 Український', callback_data=LanguageChoiceCallback.new(lang_code='uk')))
        markup.add(InlineKeyboardButton('🇺🇿 O\'zbekcha', callback_data=LanguageChoiceCallback.new(lang_code='uz')))
        return markup

    # Профили
    @staticmethod
    def get_user_saved_profiles(profiles: list[VkProfile]) -> InlineKeyboardMarkup:
        """ Возвращает строку с сохранёнными юзером профилями """
        markup = InlineKeyboardMarkup(row_width=1)

        if profiles:
            for profile in profiles:
                profile_button = InlineKeyboardButton(
                    text=profile.name, callback_data=VkProfileCallback.new(action='show', profile_id=profile.id)
                )
                markup.add(profile_button)

        markup.add(InlineKeyboardButton(text=_('➕ Добавить профиль ➕'), callback_data='add_profile'))
        return markup

    @staticmethod
    def get_actions_with_profile(vk_profile: VkProfile) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        show_audios = InlineKeyboardButton(
            text=_('Аудиозаписи'),
            callback_data=VkProfileCallback.new(action='audios', profile_id=vk_profile.id))
        show_playlists = InlineKeyboardButton(
            text=_('Плейлисты'),
            callback_data=VkProfileCallback.new(action='playlists', profile_id=vk_profile.id))
        delete_profile = InlineKeyboardButton(
            text=_('Удалить'),
            callback_data=VkProfileCallback.new(action='remove', profile_id=vk_profile.id))

        markup.add(show_audios, show_playlists, delete_profile)
        return markup

    @staticmethod
    def get_cancel_profile_adding() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(text=_('Отмена'), callback_data='cancel_profile_adding'))
        return markup
