from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.api_client import DjangoAPIClient
from bot.states import AddCategoryStates
from bot.keyboards import get_categories_keyboard, get_cancel_keyboard


router = Router()


@router.message(F.text == "📁 Мои категории")
async def list_categories(message: Message, api_client: DjangoAPIClient, state: FSMContext):
    await state.clear()
    categories = await api_client.get_categories(message.from_user.id)

    if not categories:
        await message.answer(
            "У вас пока нет категорий.\n\nНажмите кнопку ниже, чтобы создать первую:",
            reply_markup=get_categories_keyboard(),
        )
        return

    lines = [f"• {c.get('name', '—')}" for c in categories]
    text = "📁 Ваши категории:\n\n" + "\n".join(lines)
    await message.answer(text, reply_markup=get_categories_keyboard(categories))


@router.callback_query(F.data.startswith("del_category:"))
async def delete_category_callback(callback: CallbackQuery, api_client: DjangoAPIClient):
    """Удаление категории."""
    category_id = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    try:
        await api_client.delete_category(telegram_id, category_id)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
        return

    await callback.answer("✅ Категория удалена")

    categories = await api_client.get_categories(telegram_id)
    if not categories:
        await callback.message.edit_text(
            "У вас пока нет категорий.\n\nНажмите кнопку ниже, чтобы создать первую:",
            reply_markup=get_categories_keyboard(),
        )
        return

    lines = [f"• {c.get('name', '—')}" for c in categories]
    text = "📁 Ваши категории:\n\n" + "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=get_categories_keyboard(categories))


@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategoryStates.name)
    await callback.message.answer(
        "📝 Введите название новой категории:",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_add_category")
async def cancel_add_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено.")
    await callback.answer()


@router.message(AddCategoryStates.name, F.text)
async def add_category_name_entered(
    message: Message,
    state: FSMContext,
    api_client: DjangoAPIClient,
):
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым. Введите название категории:")
        return

    try:
        await api_client.create_category(message.from_user.id, name)
        await state.clear()
        await message.answer(f"✅ Категория «{name}» создана!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
