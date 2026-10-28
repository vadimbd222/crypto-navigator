"""Обработчик /top: таблица лидеров (этап 8)."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from models.db import get_top
from utils.ranks import get_rank

router = Router()

MEDALS = ["🥇", "🥈", "🥉"]


@router.message(Command("top"))
async def cmd_top(message: Message):
    rows = await get_top(10)
    if not rows:
        await message.answer("🏆 Таблица лидеров пока пуста. Начни с /start!")
        return

    lines = ["<b>🏆 Таблица лидеров</b>\n"]
    for i, row in enumerate(rows, 1):
        medal = MEDALS[i - 1] if i <= 3 else f"{i}."
        name = row["username"] or f"user{row['telegram_id']}"
        lines.append(
            f"{medal} <b>{name}</b> — {row['xp']} XP · ур. {row['level']} · {get_rank(row['level'])}"
        )

    await message.answer("\n".join(lines))