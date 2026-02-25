import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, Bold

from bot.api_client import DjangoAPIClient
from bot.keyboards import (
    get_tasks_overview_keyboard,
    get_tasks_detail_keyboard,
    get_tasks_del_all_confirm_keyboard,
)
from bot.utils.date_parser import plural_tasks


logger = logging.getLogger(__name__)
router = Router()


def _build_tasks_lines(tasks: list) -> list[str]:
    """Возвращает список строк для отображения задач."""
    lines = []
    for t in tasks:
        created = (t.get("created_at") or "")[:10]
        cat = t.get("category_name") or "—"
        status = "✅" if t.get("is_completed") else "⬜"
        lines.append(f"{status} {t['title']} | {created} | {cat}")
    return lines


def _render_tasks_text(tasks: list, title: str = "Ваши задачи:") -> str:
    lines = _build_tasks_lines(tasks)
    return as_list(Bold(title), *lines).as_html()


async def _show_tasks_overview(
    target: Message | CallbackQuery,
    tasks: list,
    api_client: DjangoAPIClient,
    is_callback: bool = False,
) -> None:
    text = _render_tasks_text(tasks)
    keyboard = get_tasks_overview_keyboard()
    if is_callback:
        await target.message.edit_text(text, reply_markup=keyboard)
        await target.answer()
    else:
        await target.answer(text, reply_markup=keyboard)


@router.message(F.text == "📋 Мои задачи")
async def list_tasks(message: Message, api_client: DjangoAPIClient, state: FSMContext):
    await state.clear()
    tasks = await api_client.get_tasks(message.from_user.id)

    if not tasks:
        await message.answer("У вас пока нет задач.")
        return

    await _show_tasks_overview(message, tasks, api_client, is_callback=False)


@router.callback_query(F.data == "tasks_overview")
async def tasks_overview_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Возврат к обзору списка задач."""
    telegram_id = callback.from_user.id
    tasks = await api_client.get_tasks(telegram_id)

    if not tasks:
        await callback.message.edit_text("У вас пока нет задач.", reply_markup=None)
        await callback.answer()
        return

    await _show_tasks_overview(callback, tasks, api_client, is_callback=True)


@router.callback_query(F.data == "tasks_detail")
async def tasks_detail_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Переход к выборочному удалению."""
    telegram_id = callback.from_user.id
    tasks = await api_client.get_tasks(telegram_id)

    if not tasks:
        await callback.message.edit_text("У вас пока нет задач.", reply_markup=None)
        await callback.answer()
        return

    text = _render_tasks_text(tasks, "Выберите задачу для удаления:")
    keyboard = get_tasks_detail_keyboard(tasks, mode="delete")
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "tasks_toggle")
async def tasks_toggle_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Переход к режиму отметки задач выполненными."""
    telegram_id = callback.from_user.id
    tasks = await api_client.get_tasks(telegram_id)

    if not tasks:
        await callback.message.edit_text("У вас пока нет задач.", reply_markup=None)
        await callback.answer()
        return

    text = _render_tasks_text(tasks, "Нажмите на задачу, чтобы отметить выполненной:")
    keyboard = get_tasks_detail_keyboard(tasks, mode="toggle")
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_task:"))
async def toggle_task_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Переключение статуса выполнения задачи."""
    task_id = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    try:
        tasks = await api_client.get_tasks(telegram_id)
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return

        new_status = not task.get("is_completed", False)
        await api_client.update_task(
            telegram_id, task_id, {"is_completed": new_status}
        )
    except Exception as e:
        logger.exception("Failed to toggle task %s", task_id)
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
        return

    status_text = "выполнена" if new_status else "не выполнена"
    await callback.answer(f"✅ Задача отмечена как {status_text}")

    tasks = await api_client.get_tasks(telegram_id)
    if not tasks:
        await callback.message.edit_text("У вас пока нет задач.", reply_markup=None)
        return

    text = _render_tasks_text(tasks, "Нажмите на задачу, чтобы отметить выполненной:")
    keyboard = get_tasks_detail_keyboard(tasks, mode="toggle")
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "tasks_del_all")
async def tasks_del_all_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Подтверждение удаления всех задач."""
    telegram_id = callback.from_user.id
    tasks = await api_client.get_tasks(telegram_id)
    count = len(tasks)

    plural = plural_tasks(count)
    await callback.message.edit_text(
        f"Удалить все {count} {plural}?",
        reply_markup=get_tasks_del_all_confirm_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "tasks_del_all_confirm")
async def tasks_del_all_confirm_callback(
    callback: CallbackQuery, api_client: DjangoAPIClient
):
    """Удаление всех задач."""
    telegram_id = callback.from_user.id

    try:
        count = await api_client.delete_all_tasks(telegram_id)
        plural = plural_tasks(count)
        await callback.message.edit_text(
            f"✅ Удалено {count} {plural}.",
            reply_markup=None,
        )
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
        return

    await callback.answer("✅ Все задачи удалены")


@router.callback_query(F.data.startswith("del_task:"))
async def delete_task_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Удаление одной задачи (из режима выборочного удаления)."""
    task_id = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    try:
        await api_client.delete_task(telegram_id, task_id)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
        return

    await callback.answer("✅ Задача удалена")

    tasks = await api_client.get_tasks(telegram_id)
    if not tasks:
        await callback.message.edit_text("У вас пока нет задач.", reply_markup=None)
        return

    text = _render_tasks_text(tasks, "Выберите задачу для удаления:")
    keyboard = get_tasks_detail_keyboard(tasks, mode="delete")
    await callback.message.edit_text(text, reply_markup=keyboard)
