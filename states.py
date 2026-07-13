from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    choosing_language = State()
    choosing_level = State()


class SettingsStates(StatesGroup):
    waiting_daily_time = State()
    waiting_daily_count = State()


class DonateStates(StatesGroup):
    waiting_custom_amount = State()
    waiting_comment = State()


class AdminStates(StatesGroup):
    waiting_broadcast = State()
