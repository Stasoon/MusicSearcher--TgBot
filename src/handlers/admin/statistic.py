import psutil
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from src.misc.admin_states import StatsGetting
from src.database import users
from src.database.songs_hashes import get_hashed_songs_count


statistic_callback_data = CallbackData('statistic', 'value')

language_emoji_map = {
    'ru': '🇷🇺',
    'uk': '🇺🇦',
    'uz': '🇺🇿',
    'en': '🇬🇧',
    None: '🏳️'
}


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('📊 Статистика 📊')

    menu_markup = InlineKeyboardMarkup(row_width=2)\
        .add(
        InlineKeyboardButton(text='Месяц', callback_data=statistic_callback_data.new('month')),
        InlineKeyboardButton(text='Неделя', callback_data=statistic_callback_data.new('week')),
        InlineKeyboardButton(text='Сутки', callback_data=statistic_callback_data.new('day')),
        InlineKeyboardButton(text='Час', callback_data=statistic_callback_data.new('hour')),
        InlineKeyboardButton(text='⌨ Другое количество', callback_data=statistic_callback_data.new('other')),
    )

    back_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Назад', callback_data=statistic_callback_data.new('back'))
    )


class Messages:
    @staticmethod
    def get_statistic_info(key: str) -> str:
        return {
            'all_time': f'Всего пользовалось ботом: <b>{users.get_users_total_count()} юзеров</b>',
            'month': Messages.get_count_per_hours('месяц', 30 * 24),
            'week': Messages.get_count_per_hours('неделю', 7 * 24),
            'day': Messages.get_count_per_hours('сутки', 24),
            'hour': Messages.get_count_per_hours('час', 1),
            'other': '🔘 Введите количество часов, за которое хотите получить статистику: ',
        }.get(key)

    @staticmethod
    def __get_server_load_text():
        cpu_percent = psutil.cpu_percent(interval=1)  # interval - интервал в секундах
        memory_info = psutil.virtual_memory()
        memory_volume = memory_info.total / (1024 ** 3)
        used_memory = memory_info.used / (1024 ** 3)

        return (
            f'💻 Нагрузка сервера: \n'
            f'➖ Процессор: {cpu_percent}% \n'
            f'➖ Оперативная память: {memory_info.percent}% ({used_memory:.2f} Гб / {memory_volume:.2f} Гб) \n'
        )

    @staticmethod
    def get_menu():
        languages = users.get_users_languages()
        text = (
            f'📊 Статистика \n\n'
            f'🎵 Песен в кэше: {get_hashed_songs_count()} \n'
            f'👥 Всего: {users.get_users_total_count()} \n'
        )

        text += ' | '.join(
            [f"{language_emoji_map.get(lang)} {users.get_users_count_by_language(lang)}"
             for lang in languages]
        )
        text += '\n\n' + Messages.__get_server_load_text()

        return text + f' \n📊 Выберите, за какой промежуток времени просмотреть статистику:'

    @staticmethod
    def get_count_per_hours(time_word: str, hours: int):
        return f'За {time_word} в бота пришли: \n' \
               f'<b>{users.get_users_registered_within_hours_count(hours)} юзера(ов)</b>'


class Handlers:
    @staticmethod
    async def __handle_admin_statistic_button(message: Message):
        await message.answer(text=Messages.get_menu(), reply_markup=Keyboards.menu_markup)

    @staticmethod
    async def __handle_show_stats_callback(callback: CallbackQuery, state: FSMContext,
                                           callback_data: statistic_callback_data):
        value = callback_data.get('value')
        message = callback.message

        if value == 'back':
            await message.edit_text(text=Messages.get_menu(), reply_markup=Keyboards.menu_markup)
            await state.finish()
            return

        response = Messages.get_statistic_info(value)
        if response:
            await message.edit_text(text=response, reply_markup=Keyboards.back_markup)
        if value == 'other':
            await state.set_state(StatsGetting.wait_for_hours_count)

    @staticmethod
    async def __handle_get_hours_message(message: Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer('❗Вы ввели не число. Попробуйте снова:', reply_markup=Keyboards.back_markup)
            return

        users_count = users.get_users_registered_within_hours_count(int(message.text))
        await message.answer(
            text=Messages.get_count_per_hours(f'{message.text} часов', users_count),
            reply_markup=Keyboards.back_markup
        )
        await state.finish()

    @classmethod
    def register_admin_statistic_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(
            cls.__handle_admin_statistic_button, is_admin=True,
            text=Keyboards.reply_button_for_admin_menu.text
        )

        dp.register_callback_query_handler(
            cls.__handle_show_stats_callback, statistic_callback_data.filter(), state='*'
        )

        dp.register_message_handler(
            cls.__handle_get_hours_message,
            is_admin=True, state=StatsGetting.wait_for_hours_count
        )


