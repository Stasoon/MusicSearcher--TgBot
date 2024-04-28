import aiogram.utils.markdown as fmt
from config import i18n
from src.database.models import VkProfile

_ = i18n.gettext


class UserMessages:
    # Приветствие
    @staticmethod
    def get_welcome(user_name: str) -> str:
        return _("👋 Привет, {user_name}!").format(user_name=fmt.quote_html(user_name))

    # Выбор языка
    @staticmethod
    def get_choose_language() -> str:
        return _('🌏 Выберите язык:')

    @staticmethod
    def get_language_selected() -> str:
        return _('✅ Язык выбран')

    # Обязательные подписки
    @staticmethod
    def get_user_must_subscribe() -> str:
        return _('❗Подпишитесь на каналы, чтобы получить песню❗')

    @staticmethod
    def get_must_go_to_bot_and_subscribe() -> str:
        return _('Нажмите и подпишитесь на спонсоров в боте')

    @staticmethod
    def get_user_subscribed() -> str:
        return _('✅ Готово! \nМожете пользоваться ботом.')

    @staticmethod
    def get_not_all_channels_subscribed() -> str:
        return _('Вы подписались не на все каналы 😔')

    # Тексты для после кнопок меню
    @staticmethod
    def get_popular_songs() -> str:
        return _('🎧 Популярное')

    @staticmethod
    def get_new_songs() -> str:
        return _('🎶 Новинки')

    @staticmethod
    def get_search_song() -> str:
        return _(
            "<b>🔎 Чтобы найти музыку, отправьте мне что-то из этого: \n\n"
            "• Название песни или исполнителя \n"
            "• Ссылку на TikTok \n"
            "• Видео \n"
            "• Голосовое сообщение \n"
            "• Видеосообщение</b>"
        )

    # Профили
    @staticmethod
    def get_user_saved_profiles() -> str:
        return _('👥 Сохранённые профили:')

    @staticmethod
    def get_profile_description(profile_name: str) -> str:
        return _('👤 Профиль: <b>{profile_name}</b>').format(profile_name=fmt.quote_html(profile_name))

    @staticmethod
    def get_profile_successfully_removed(profile_name: str) -> str:
        return _('✅ Профиль {profile_name} удалён').format(profile_name=fmt.quote_html(profile_name))

    @staticmethod
    def get_profiles_adding_guide() -> str:
        return _(
            '<b>Отправь мне ссылку на страницу или сообщество.</b> \n\n'
            'Например: \n\n'
            '🔘 @durov \n'
            '🔘 vk.com/durov \n'
            '🔘 https://vk.com/id258650556 \n'
        )

    # Описания к песням
    @staticmethod
    def get_song_info(song_title: str, author_name: str) -> str:
        return _(
            '🎵 Название песни: <b>{song_title}</b> \n'
            '🎸 Исполнитель: <b>{author_name}</b>'
        ).format(song_title=fmt.quote_html(song_title), author_name=fmt.quote_html(author_name))

    @staticmethod
    def get_audio_file_caption(bot_username: str) -> str:
        return '<b><a href="https://t.me/{bot_username}?start=Sarafan">Ꮋᴀйᴛи ᴄʙᴏй ᴧюбиʍый ᴛᴩᴇᴋ</a></b>'\
            .format(bot_username=bot_username)

    # Ошибки
    @staticmethod
    def get_song_not_found_error() -> str:
        return _("Песня не найдена 😔🎧 \nПерефразируйте запрос и попробуйте снова")

    @staticmethod
    def get_profile_link_invalid_retry() -> str:
        return _(
            '<b>Неверная ссылка.</b> \n\n'
            'Попробуйте ещё раз, например: \n\n'
            '🔘 @durov \n'
            '🔘 vk.com/durov \n'
            '🔘 https://vk.com/id258650556 \n'
        )

    @staticmethod
    def get_profile_is_private() -> str:
        return _('❗Аудиозаписи профиля/сообщества скрыты настройками приватности')

    @staticmethod
    def get_song_not_recognized() -> str:
        return _('Не удалось узнать песню 😢')

    @staticmethod
    def get_profile_not_found() -> str:
        return _("😢 Страница не найдена. \nВозможно, вы отправили неверную ссылку или короткое имя.")

    @staticmethod
    def get_file_too_big_error() -> str:
        return _("Файл слишком много весит 😔")

    @staticmethod
    def get_throttled_error() -> str:
        return _("Пожалуйста, не так часто 🙏")
