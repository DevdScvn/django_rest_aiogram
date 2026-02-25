import logging
from datetime import date, timedelta

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Select, Cancel, Back
from aiogram_dialog.widgets.input import TextInput

from bot.states import AddTaskStates


async def on_title_entered(message: Message, widget, manager: DialogManager, text: str):
    manager.dialog_data["title"] = text
    await manager.next()


async def on_description_entered(message: Message, widget, manager: DialogManager, text: str):
    manager.dialog_data["description"] = text or ""
    await manager.next()


async def on_skip_description(callback: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["description"] = ""
    await manager.next()


logger = logging.getLogger(__name__)


async def get_categories(dialog_manager: DialogManager, **kwargs):
    api = dialog_manager.middleware_data.get("api_client")
    if not api:
        logger.error("api_client not found in middleware_data")
        return {"categories": []}

    telegram_id = dialog_manager.event.from_user.id
    try:
        categories = await api.get_categories(telegram_id)
    except Exception as e:
        logger.exception("Failed to fetch categories for dialog: %s", e)
        return {"categories": []}

    dialog_manager.dialog_data["_categories"] = categories
    return {"categories": categories}


async def on_category_selected(callback, select, manager: DialogManager, item_id: str):
    categories = manager.dialog_data.get("_categories", [])
    if item_id and item_id != "none":
        for cat in categories:
            if str(cat.get("id")) == item_id:
                manager.dialog_data["category_id"] = item_id
                manager.dialog_data["category_name"] = cat.get("name", "—")
                break
    else:
        manager.dialog_data["category_id"] = None
        manager.dialog_data["category_name"] = "Без категории"
    await manager.next()


async def on_no_category(callback: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["category_id"] = None
    manager.dialog_data["category_name"] = "Без категории"
    await manager.next()


async def on_due_date_entered(message: Message, widget, manager: DialogManager, text: str):
    manager.dialog_data["due_date"] = text.strip() or None
    await manager.next()


async def on_skip_due_date(callback: CallbackQuery, button, manager: DialogManager):
    manager.dialog_data["due_date"] = None
    await manager.next()


async def on_tomorrow_click(callback: CallbackQuery, button, manager: DialogManager):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    manager.dialog_data["due_date"] = tomorrow
    await manager.next()


async def get_confirm_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return {
        "title": data.get("title", ""),
        "description": data.get("description", "") or "—",
        "category": data.get("category_name", "Без категории"),
        "due_date": data.get("due_date") or "—",
    }


async def on_confirm(callback: CallbackQuery, button, manager: DialogManager):
    api = manager.middleware_data["api_client"]
    telegram_id = manager.event.from_user.id
    data = manager.dialog_data
    task_data = {
        "title": data["title"],
        "description": data.get("description", ""),
        "category_id": data.get("category_id"),
        "due_date": data.get("due_date"),
    }
    try:
        await api.create_task(telegram_id, task_data)
        await manager.done()
        await callback.message.answer("✅ Задача создана!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")


add_task_dialog = Dialog(
    Window(
        Const("📝 Введите название задачи:"),
        TextInput(id="title_input", on_success=on_title_entered),
        Cancel(Const("❌ Отмена")),
        state=AddTaskStates.title,
    ),
    Window(
        Const("📄 Введите описание (или нажмите Пропустить):"),
        TextInput(id="desc_input", on_success=on_description_entered),
        Button(Const("⏭ Пропустить"), id="skip_desc", on_click=on_skip_description),
        Back(Const("◀ Назад")),
        Cancel(Const("❌ Отмена")),
        state=AddTaskStates.description,
    ),
    Window(
        Const("📁 Выберите категорию:"),
        Select(
            Format("{item[name]}"),
            id="category_select",
            item_id_getter=lambda x: str(x["id"]) if x else "none",
            items="categories",
            on_click=on_category_selected,
        ),
        Button(Const("Без категории"), id="no_cat", on_click=on_no_category),
        Back(Const("◀ Назад")),
        Cancel(Const("❌ Отмена")),
        getter=get_categories,
        state=AddTaskStates.category,
    ),
    Window(
        Const("📅 Введите дату исполнения (DD.MM.YYYY) или выберите:"),
        TextInput(id="due_input", on_success=on_due_date_entered),
        Button(Const("📆 Завтра"), id="due_tomorrow", on_click=on_tomorrow_click),
        Button(Const("⏭ Пропустить"), id="skip_due", on_click=on_skip_due_date),
        Back(Const("◀ Назад")),
        Cancel(Const("❌ Отмена")),
        state=AddTaskStates.due_date,
    ),
    Window(
        Format("Подтвердите:\n\n📌 {title}\n📄 {description}\n📁 {category}\n📅 {due_date}"),
        Button(Const("✅ Создать"), id="confirm", on_click=on_confirm),
        Back(Const("◀ Назад")),
        Cancel(Const("❌ Отмена")),
        getter=get_confirm_data,
        state=AddTaskStates.confirm,
    ),
)
