from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои задачи")],
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="📁 Мои категории")],
        ],
        resize_keyboard=True,
    )


def get_categories_keyboard(categories: list | None = None) -> InlineKeyboardMarkup:
    """Клавиатура: кнопки удаления для каждой категории + добавить."""
    buttons = []
    if categories:
        for c in categories:
            name = (c.get("name") or "—")[:25]
            if len((c.get("name") or "")) > 25:
                name += "…"
            buttons.append([
                InlineKeyboardButton(
                    text=f"🗑 {name}",
                    callback_data=f"del_category:{c['id']}",
                )
            ])
    buttons.append([
        InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add_category")],
    ])


def get_tasks_overview_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура обзора: удалить все, выборочное удаление, отметить выполненным."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑 Удалить все", callback_data="tasks_del_all"),
            InlineKeyboardButton(text="📝 Удалить выборочно", callback_data="tasks_detail"),
        ],
        [
            InlineKeyboardButton(text="✅ Отметить выполненным", callback_data="tasks_toggle"),
        ],
    ])


def get_tasks_detail_keyboard(tasks: list, mode: str = "delete") -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для каждой задачи. mode: 'delete' | 'toggle'."""
    buttons = []
    for t in tasks:
        title = (t["title"][:25] + "…") if len(t["title"]) > 25 else t["title"]
        if mode == "delete":
            buttons.append([
                InlineKeyboardButton(
                    text=f"🗑 {title}",
                    callback_data=f"del_task:{t['id']}",
                )
            ])
        else:
            status = "✅" if t.get("is_completed") else "⬜"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{status} {title}",
                    callback_data=f"toggle_task:{t['id']}",
                )
            ])
    buttons.append([
        InlineKeyboardButton(text="◀ Назад к списку", callback_data="tasks_overview")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasks_del_all_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, удалить все",
                callback_data="tasks_del_all_confirm",
            ),
            InlineKeyboardButton(text="❌ Отмена", callback_data="tasks_overview"),
        ],
    ])
