from datetime import datetime, timedelta
from typing import Generator

from peewee import DoesNotExist

from .models import User
from .reflinks import increase_users_count


# region SQL Create

def create_user_if_not_exist(telegram_id: int, firstname: str, username: str = None, reflink: str = None) -> None:
    if not get_user_by_telegram_id_or_none(telegram_id):
        reg_time = datetime.now()
        User.create(
            name=firstname, telegram_id=telegram_id, username=username,
            referral_link=reflink, registration_timestamp=reg_time
        )
        increase_users_count(reflink=reflink)
    else:
        User.update(name=firstname, username=username).where(User.telegram_id == telegram_id)

# endregion


# region SQL Select

def get_user_or_none(telegram_id: int) -> User | None:
    return User.get_or_none(User.telegram_id == telegram_id)


def get_users_total_count() -> int:
    return User.select().count()


def get_online_users_count(minutes_threshold=15) -> int:
    threshold_time = datetime.now() - timedelta(minutes=minutes_threshold)
    return User.select().where(User.last_activity >= threshold_time).count()


def get_users_registered_within_hours_count(hours: int) -> int:
    start_time = datetime.now() - timedelta(hours=hours)
    users_count = User.select().where(User.registration_timestamp >= start_time).count()

    return users_count


def get_user_lang_code(telegram_id: int) -> str | None:
    user = get_user_by_telegram_id_or_none(telegram_id)
    lang_code = user.lang_code if user else None
    return lang_code


def get_user_ids() -> Generator[int, any, any]:
    yield from (user.telegram_id for user in User.select())


def get_all_users() -> Generator[User, any, any]:
    """ Возвращает генератор с пользователями """
    yield from (user for user in User.select())


def get_user_by_telegram_id_or_none(telegram_id: int) -> User | None:
    try:
        user = User.get(User.telegram_id == telegram_id)
        return user
    except DoesNotExist:
        return None


def get_users_languages() -> list[str]:
    unique_lang_codes = User.select(User.lang_code).distinct()
    unique_lang_codes = [lang_code.lang_code for lang_code in unique_lang_codes]
    return unique_lang_codes


def get_users_count_by_language(lang_code: str) -> int:
    return User.select().where(User.lang_code == lang_code).count()


# endregion


# region Update

def update_user_lang_code(telegram_id: int, new_lang_code: str = 'ru') -> None:
    user = User.get_or_none(User.telegram_id == telegram_id)
    if not user: return

    user.lang_code = new_lang_code
    user.save()


# endregion
