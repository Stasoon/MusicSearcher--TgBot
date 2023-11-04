from aiogram.dispatcher.filters.state import State, StatesGroup


class StatsGetting(StatesGroup):
    wait_for_hours_count = State()


class ChannelAdding(StatesGroup):
    wait_for_post = State()
    wait_for_url = State()


class AdminAdding(StatesGroup):
    wait_for_new_admin_id = State()
    wait_for_admin_to_delete_id = State()


class MailingPostCreating(StatesGroup):
    wait_for_content_message = State()
    wait_for_markup_data = State()
    wait_for_confirm = State()


class AdvertisementEditing(StatesGroup):
    wait_for_content_message = State()
    wait_for_markup_data = State()


class ReferralLinkStates(StatesGroup):
    create = State()
    delete = State()
    find = State()
