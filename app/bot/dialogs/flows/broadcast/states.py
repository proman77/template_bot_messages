from aiogram.fsm.state import State, StatesGroup


class BroadcastSG(StatesGroup):
    MAIN = State()
    SELECT_LANG = State()
    INPUT_MESSAGE = State()
    PREVIEW = State()
    CONFIRM = State()
    MONITORING = State()
