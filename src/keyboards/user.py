from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from src.misc.callback_data import ShowSongCallback, SongsNavigationCallback, LanguageChoiceCallback
from src.utils.vk_music_api import VkSong
from config import i18n


_ = i18n.gettext


def get_formatted_duration(duration_seconds: int) -> str:
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    hours_str = f"{hours:02}:" if hours else ""
    return f"{hours_str}{minutes:02}:{seconds:02}"


class UserKeyboards:
    @staticmethod
    def get_languages_markup() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1, resize_keyboard=True, is_persistent=True)
        markup.add(InlineKeyboardButton('🇷🇺 Русский', callback_data=LanguageChoiceCallback.new(lang_code='ru')))
        markup.add(InlineKeyboardButton('🇺🇦 Український', callback_data=LanguageChoiceCallback.new(lang_code='uk')))
        markup.add(InlineKeyboardButton('🇺🇿 O\'zbekcha', callback_data=LanguageChoiceCallback.new(lang_code='uz')))
        return markup

    @classmethod
    def get_not_subbed_markup(cls, channels_to_sub_data) -> InlineKeyboardMarkup | None:
        if len(channels_to_sub_data) == 0:
            return None

        channels_markup = InlineKeyboardMarkup(row_width=1)
        [
            channels_markup.add( InlineKeyboardButton(text=channel.title, url=channel.url) )
            for channel in channels_to_sub_data
        ]
        check_sub_button = InlineKeyboardButton(text=_('✅ Проверить ✅'), callback_data='check_subscription')

        channels_markup.add(check_sub_button)
        return channels_markup

    @staticmethod
    def get_main_menu_markup() -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        markup.add(_('🎶 Новинки'), _('🎧 Популярное'))
        markup.row(_('🔍 Поиск'))
        return markup

    @staticmethod
    def __get_songs_navigation_buttons(
            category: str,
            current_page_num: int,
            max_pages: int = 10,
            count_per_page: int = 8
    ) -> list[InlineKeyboardButton]:
        buttons = [
            InlineKeyboardButton(
                text='❮❮', callback_data=SongsNavigationCallback.new(
                    category=category, action='prev',
                    page_num=current_page_num, count_per_page=count_per_page, max_pages=max_pages
                )),
            InlineKeyboardButton(text=f'{current_page_num}/{max_pages}', callback_data='*'),
            InlineKeyboardButton(
                text='❯❯', callback_data=SongsNavigationCallback.new(
                    category=category, action='next',
                    page_num=current_page_num, count_per_page=count_per_page, max_pages=max_pages
                ))
        ]
        return buttons

    @staticmethod
    def get_found_songs(
            songs: list[VkSong],
            current_page_num: int = 1,
            max_pages: int = 10,
            category: str = 'search',
            append_navigation: bool = True
    ) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for song in songs:
            markup.row(
                InlineKeyboardButton(
                    text=f"{get_formatted_duration(song.duration)} | {song.artist} - {song.title}",
                    callback_data=ShowSongCallback.new(song_id=song.song_id, owner_id=song.owner_id)
                )
            )

        if append_navigation:
            nav_buttons = UserKeyboards.__get_songs_navigation_buttons(
                category=category, current_page_num=current_page_num,
                max_pages=max_pages
            )
            markup.row().add(*nav_buttons)
        return markup

    @staticmethod
    def get_(bot_username: str) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(url=f'https://t.me/{bot_username}', text='🎵 Найти песню 🎵'))
        return markup

    @staticmethod
    def get_recognize_song_from_video_button() -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(text='🎵 Узнать песню 🎵', callback_data='recognize_song_from_video'))
        return markup
