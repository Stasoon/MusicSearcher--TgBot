from typing import Generator
from datetime import datetime, timedelta

from .models import User
from .reflinks import increase_users_count


# region SQL Create

def create_user(telegram_id: int, name: str, reflink: str = None) -> None:
    if not get_user_by_telegram_id_or_none(telegram_id):
        reg_time = datetime.now()
        User.create(name=name, telegram_id=telegram_id, referral_link=reflink, registration_timestamp=reg_time)
        increase_users_count(reflink=reflink)

# endregion


# region SQL Select

def get_users_total_count() -> int:
    return User.select().count()


def get_users_by_hours(hours: int):
    start_time = datetime.now() - timedelta(hours=hours)
    users_count = User.select().where(User.registration_timestamp >= start_time).count()

    return users_count


def get_user_ids() -> Generator:
    yield from (user.telegram_id for user in User.select())


def get_all_users() -> tuple:
    yield from ((user.telegram_id, user.name, user.referral_link, user.registration_timestamp) for user in
                User.select())


def get_user_by_telegram_id_or_none(telegram_id: int) -> None:
    return User.get_or_none(User.telegram_id == telegram_id)

# endregion
