import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


def get_markup_from_text(text: str) -> InlineKeyboardMarkup:
    """
    Формирует InlineKeyboardMarkup по отправленному тексту.
    Разделение кнопок в строке - символ "|"
    Перенос кнопок на другой ряд - "\n" (просто перенос строки)
    """
    markup = InlineKeyboardMarkup()  # По умолчанию - 1 кнопка в ряду

    # Разбиваем текст на строки и обрабатываем каждую строку
    lines = text.split('\n')
    for line in lines:
        items = line.strip().split('|')
        row_buttons = []
        for item in items:
            item_parts = item.strip().split()
            title = ' '.join(item_parts[:-1])  # Берем все слова, кроме последнего, как текст кнопки
            url = item_parts[-1]  # Последнее слово в строке считаем ссылкой
            button = InlineKeyboardButton(text=title, url=url)
            row_buttons.append(button)

        markup.row(*row_buttons)
    return markup


def get_inline_kb_from_json(data: dict | str) -> InlineKeyboardMarkup:
    """ Из словаря с клавиатурой делает объект """
    if isinstance(data, str):
        data = json.loads(data)
    markup = InlineKeyboardMarkup.to_object(data)
    return markup


def get_json_string_from_kb(keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup) -> str:
    """ Из клавиатуры делает json строку """
    return keyboard.as_json()
