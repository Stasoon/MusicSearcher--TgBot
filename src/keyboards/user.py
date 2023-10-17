from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup, InlineKeyboardButton
)

from src.misc.callback_data import ShowSongCallback, SongsNavCallback
from src.utils.vk_api import Song


def get_formatted_duration(duration_seconds: int) -> str:
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    return f"{minutes:02}:{seconds:02}"


class UserKeyboards:
    @staticmethod
    def get_languages_markup() -> InlineKeyboardMarkup:
        pass

    @staticmethod
    def get_main_menu_markup() -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        markup.add('🎶 Новинки', '🎧 Популярное')
        markup.row('🔍 Поиск')
        return markup

    @staticmethod
    def __get_songs_nav_builder(current_page_num: int, category: str, count_per_page: int = 6) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(
                text='<', callback_data=SongsNavCallback.new(
                    page_num=current_page_num, count_per_page=count_per_page, action='prev', category=category
                )),
            InlineKeyboardButton(text=f'{current_page_num}/5', callback_data='*'),
            InlineKeyboardButton(
                text='>', callback_data=SongsNavCallback.new(
                    page_num=current_page_num, count_per_page=count_per_page, action='next', category=category
                ))
        ]
        return buttons

    @staticmethod
    def get_found_songs(
            songs: list[Song],
            current_page_num: int = 1,
            category: str = 'search',
            append_navigation: bool = True
    ) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for song in songs:
            print(f"{get_formatted_duration(song.duration)} | {song.artist} - {song.title}")
            print(ShowSongCallback.new(song_id=song.track_id, owner_id=song.owner_id))
            markup.row(
                InlineKeyboardButton(
                    text=f"{get_formatted_duration(song.duration)} | {song.artist} - {song.title}",
                    callback_data=ShowSongCallback.new(song_id=song.track_id, owner_id=song.owner_id)
                )
            )

        if append_navigation:
            nav_buttons = UserKeyboards.__get_songs_nav_builder(current_page_num, category)
            markup.row().add(*nav_buttons)
        return markup
