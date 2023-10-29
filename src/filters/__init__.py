from aiogram import Dispatcher

from .is_admin import IsAdminFilter
from .is_subscriber import IsSubscriberFilter


def register_all_filters(dp: Dispatcher):
    # сюда прописывать фильтры
    filters = (
        IsAdminFilter,
        IsSubscriberFilter
    )

    for f in filters:
        dp.filters_factory.bind(f)
