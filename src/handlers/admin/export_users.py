import os
import csv
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import KeyboardButton, Message

from src.database.users import get_all_users
from config import PathsConfig


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('📥 Экспорт пользователей 📥')


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
    def write_users_to_xl() -> str:
        file_name = Utils.__get_users_csv_filename()

        with open(file_name, 'w', newline='', encoding='utf-8-sig') as csv_file:
            fieldnames = ['telegram_id', 'name', 'registration_timestamp', 'referral_link']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Запишите каждую запись из таблицы в CSV файл
            for user in get_all_users():
                writer.writerow({
                    'name': user.name,
                    'username': user.username,
                    'language': user.lang_code,
                    'telegram_id': user.telegram_id,
                    'registration_timestamp': user.registration_timestamp,
                    'referral_link': user.referral_link if user.referral_link else '',
                })

        return file_name


class Handlers:
    @staticmethod
    async def __handle_admin_export_button(message: Message):
        file_name = Utils.write_users_to_xl()

        with open(file_name, 'rb') as file:
            await message.answer_document(document=file)

    @classmethod
    def register_export_users_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(cls.__handle_admin_export_button, is_admin=True,
                                    text=Keyboards.reply_button_for_admin_menu.text)
