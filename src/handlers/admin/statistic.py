import os
import csv
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import psutil
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputFile
from aiogram.utils.callback_data import CallbackData
from peewee import fn

from src.database.models import DownloadsByDays, ChatSearchStats
from src.misc.admin_states import StatsGetting
from src.database import users, bot_chats
from src.database.song_caches import get_cached_songs_count
from src.database.users import get_all_users
from config import PathsConfig


class Utils:
    @staticmethod
    def __get_users_csv_filename() -> str:
        if not os.path.exists(PathsConfig.CSV_FOLDER):
            os.mkdir(PathsConfig.CSV_FOLDER)

        date = datetime.now().strftime("%Y.%m.%d")
        file_name = f"{PathsConfig.CSV_FOLDER}/Пользователи {date}.csv"
        if os.path.exists(file_name):
            os.remove(file_name)

        return file_name

    @staticmethod
    def write_users_to_csv() -> str:
        file_name = Utils.__get_users_csv_filename()

        with open(file_name, 'w', newline='', encoding='utf-8-sig') as csv_file:
            fieldnames = [
                'telegram_id', 'name', 'username', 'language',
                'registration_timestamp', 'referral_link'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Запишите каждую запись из таблицы в CSV файл
            for user in get_all_users():
                writer.writerow({
                    'telegram_id': user.telegram_id,
                    'name': user.name,
                    'username': user.username,
                    'language': user.lang_code,
                    'registration_timestamp': user.registration_timestamp,
                    'referral_link': user.referral_link if user.referral_link else '',
                })

        return file_name

    @staticmethod
    def write_user_ids_to_txt() -> str:
        with NamedTemporaryFile(delete=False) as temp_file:
            # Записываем данные во временный файл
            for user in get_all_users():
                temp_file.write(f"{user.telegram_id}\n".encode('utf-8'))

            # Получаем имя временного файла
            temp_file_path = temp_file.name
        return temp_file_path


statistic_callback = CallbackData('statistic', 'value')

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
        InlineKeyboardButton(text='Месяц', callback_data=statistic_callback.new('month')),
        InlineKeyboardButton(text='Неделя', callback_data=statistic_callback.new('week')),
        InlineKeyboardButton(text='Сутки', callback_data=statistic_callback.new('day')),
        InlineKeyboardButton(text='Час', callback_data=statistic_callback.new('hour')),
        InlineKeyboardButton(text='⌨ Другое количество', callback_data=statistic_callback.new('other')),
    ).row(
        InlineKeyboardButton(text='⏬ Экспорт пользователей ⏬', callback_data=statistic_callback.new('export'))
    )

    back_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Назад', callback_data=statistic_callback.new('back'))
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

        today = DownloadsByDays.get_or_none(date=datetime.today())
        yesterday = DownloadsByDays.get_or_none(date=datetime.today() - timedelta(days=1))

        text = (
            f'📊 Статистика \n\n'
            
            f'🎵 Аудио в базе: {get_cached_songs_count()} \n'
            f'Скачиваний сегодня: {today.downloads_count if today else 0} \n'
            f'Скачиваний вчера: {yesterday.downloads_count if yesterday else 0} \n'
            f'Скачиваний всего: {DownloadsByDays.select(fn.SUM(DownloadsByDays.downloads_count)).scalar() or 0} \n\n'
            
            f'💬 Всего чатов: {bot_chats.get_bot_chats_count()} \n'
            f'Поиск аудио в чате: {ChatSearchStats.select(fn.SUM(ChatSearchStats.downloads_count)).scalar() or 0} \n\n'
            
            f'👥 Всего пользователей: {users.get_users_total_count()} \n'
            f'🌐 Онлайн: {users.get_online_users_count()} \n'
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
    async def __handle_show_stats_callback(
            callback: CallbackQuery, state: FSMContext, callback_data: statistic_callback
    ):
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

    @staticmethod
    async def __handle_export_callback(callback: CallbackQuery):
        file_name = Utils.write_users_to_csv()

        with open(file_name, 'rb') as file:
            await callback.message.answer_document(document=file)

        # Отправляем временный файл как документ
        txt_temp_file_path = Utils.write_user_ids_to_txt()
        await callback.message.answer_document(document=InputFile(txt_temp_file_path, filename='user_ids.txt'))
        os.remove(txt_temp_file_path)
        await callback.answer()

    @classmethod
    def register_admin_statistic_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(
            cls.__handle_admin_statistic_button, is_admin=True,
            text=Keyboards.reply_button_for_admin_menu.text
        )

        dp.register_callback_query_handler(
            cls.__handle_export_callback, statistic_callback.filter(value='export'), is_admin=True
        )

        dp.register_callback_query_handler(
            cls.__handle_show_stats_callback, statistic_callback.filter(), state='*'
        )

        dp.register_message_handler(
            cls.__handle_get_hours_message,
            is_admin=True, state=StatsGetting.wait_for_hours_count
        )
