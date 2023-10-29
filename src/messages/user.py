import aiogram.utils.markdown as fmt
from config import i18n

_ = i18n.gettext


class UserMessages:
    @staticmethod
    def get_welcome(user_name: str) -> str:
        return _('👋 Привет, {user_name}!').format(user_name=fmt.quote_html(user_name))

    @staticmethod
    def get_choose_language() -> str:
        return _('🌏 Выберите язык:')

    @staticmethod
    def get_language_selected() -> str:
        return _('✅ Язык выбран')

    @staticmethod
    def get_user_must_subscribe() -> str:
        return _('❗Подпишитесь на каналы, чтобы получить песню❗')

    @staticmethod
    def get_user_subscribed() -> str:
        return _('✅ Готово! \nМожете пользоваться ботом.')

    @staticmethod
    def get_not_all_channels_subscribed() -> str:
        return _('Вы подписались не на все каналы 😔')

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

    @staticmethod
    def get_song_info(song_title: str, author_name: str) -> str:
        return _(
            '🎵 Название песни: <b>{song_title}</b> \n'
            '🎸 Исполнитель: <b>{author_name}</b>'
        ).format(song_title=song_title, author_name=author_name)

    @staticmethod
    def get_audio_file_caption(bot_username: str) -> str:
        return '<b><a href="https://t.me/{bot_username}">👉 <u>Найти музыку</u> 🎧</a></b>'\
            .format(bot_username=bot_username)

    @staticmethod
    def get_song_not_found_error() -> str:
        return _("Песня не найдена 😔🎧")

    @staticmethod
    def get_audiofile_too_huge_error() -> str:
        return _("Аудиофайл слишком много весит 😔")
