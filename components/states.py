from aiogram.fsm.state import State, StatesGroup

class Achievement(StatesGroup):
    add_achievement = State()
    edit_achievement = State()
