from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager

from bot.states import AddTaskStates

router = Router()


@router.message(F.text == "➕ Добавить задачу")
async def add_task_handler(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    await state.clear()
    await dialog_manager.start(AddTaskStates.title)
