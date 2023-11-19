from aiogram.utils.callback_data import CallbackData


LanguageChoiceCallback = CallbackData("choice_lang", "lang_code")

SongCallback = CallbackData("show_item", "id", "owner_id")
PlaylistCallback = CallbackData("show_item", "id", "owner_id", "access_key")

PagesNavigationCallback = CallbackData(
    "navigation", "direction",  "category", "page_num", "count_per_page", "max_pages", "target_data"
)

VkProfileCallback = CallbackData(
    'vk_profile', 'profile_id', 'action'
)
