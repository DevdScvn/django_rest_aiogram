from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    title = State()
    description = State()
    category = State()
    due_date = State()
    confirm = State()


class AddCategoryStates(StatesGroup):
    name = State()
