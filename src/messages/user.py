import aiogram.utils.markdown as fmt


class UserMessages:
    @staticmethod
    def get_welcome(user_name: str) -> str:
        return f'👋 Привет, {fmt.quote_html(user_name)}!'

    @staticmethod
    def get_popular() -> str:
        return '🎧 Популярное'

    @staticmethod
    def get_search_song() -> str:
        return (
            "<b>🔎 Чтобы найти музыку, отправьте мне что-то из этого: \n\n"
            "• Название песни или исполнителя \n"
            "• Ссылку на TikTok \n"
            "• Видео \n"
            "• Голосовое сообщение \n"
            "• Видеосообщение</b>"
        )

    @staticmethod
    def get_song_info(song_title: str, author_name: str) -> str:
        return (
            f'🎵 Название песни: <b>{song_title}</b> \n'
            f'🎸 Исполнитель: <b>{author_name}</b>'
        )

    @staticmethod
    def get_song_not_found() -> str:
        return "Песня не найдена 😔🎧"

    @staticmethod
    def get_search_results():
        return "🔎 Результаты поиска:"

    @staticmethod
    def get_audio_file_caption(bot_username: str) -> str:
        return f'<a href="https://t.me/{bot_username}">Найти музыку<a>'
