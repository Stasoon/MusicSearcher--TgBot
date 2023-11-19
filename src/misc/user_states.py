from aiogram.dispatcher.filters.state import State, StatesGroup


class VkProfileAddingStates(StatesGroup):
    wait_for_page_link = State()
