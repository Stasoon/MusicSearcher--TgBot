from aiogram.dispatcher.filters.state import State, StatesGroup


class StatsGetting(StatesGroup):
    wait_for_hours_count = State()


class SubscriptionChannelAdding(StatesGroup):
    wait_for_post = State()
    wait_for_url = State()


class BotSubscriptionStates(StatesGroup):
    id_to_give_subscription = State()
    id_to_take_back_subscription = State()


class JoinRequestChannelAdding(StatesGroup):
    wait_for_post = State()
    wait_for_welcome_text = State()
    wait_for_goodbye_text = State()


class JoinRequestChannelEditing(StatesGroup):
    edit_welcome_text = State()
    edit_goodbye_text = State()


class AdminAdding(StatesGroup):
    wait_for_new_admin_id = State()
    wait_for_admin_to_delete_id = State()


class MailingPostCreating(StatesGroup):
    wait_for_content_message = State()
    wait_for_markup_data = State()
    wait_for_confirm = State()


class AdvertisementAdding(StatesGroup):
    wait_for_content_message = State()
    add_preview = State()
    wait_for_markup_data = State()
    wait_for_confirm = State()


class ReferralLinkStates(StatesGroup):
    create = State()
    delete = State()
