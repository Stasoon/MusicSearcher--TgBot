from aiogram.utils.callback_data import CallbackData


ShowSongCallback = CallbackData("get_song", "song_id", "owner_id")

SongsNavCallback = CallbackData("songs_nav", "page_num", "count_per_page", "action", "category")
