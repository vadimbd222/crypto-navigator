"""Обработчик /settings: профиль и уведомления (этап 8)."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from models.db import get_user, set_notifications
from utils.ranks import get_rank

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала начни с команды /start!")
        return

    notif = "включены ✅" if user["notifications"] else "выключены ❌"
    await message.answer(
        "<b>⚙️ Настройки</b>\n\n"
        f"XP: <b>{user['xp']}</b>\n"
        f"Уровень: <b>{user['level']}</b> — {get_rank(user['level'])}\n"
        f"Уведомления: <b>{notif}</b>\n\n"
        "Хочешь переключить уведомления?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔕 Выключить" if user["notifications"] else "🔔 Включить",
                callback_data="toggle_notif",
            )],
        ]),
    )


@router.callback_query(F.data == "toggle_notif")
async def cb_toggle(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.answer("Сначала /start", show_alert=True)
        return
    new_value = 0 if user["notifications"] else 1
    await set_notifications(callback.from_user.id, new_value)
    state_text = "включены ✅" if new_value else "выключены ❌"
    await callback.answer(f"Уведомления {state_text}")
    await callback.message.answer(f"⚙️ Уведомления теперь <b>{state_text}</b>")