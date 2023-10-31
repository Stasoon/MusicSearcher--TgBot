from aiogram.utils.callback_data import CallbackData


LanguageChoiceCallback = CallbackData("choice_lang", "lang_code")

ShowSongCallback = CallbackData("show_found_song", "owner_id", "song_id")

SongsNavigationCallback = CallbackData(
    "songs_nav", "page_num", "count_per_page", "action", "category", "max_pages"
)
