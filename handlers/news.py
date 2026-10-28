"""Обработчик /news: свежие новости о криптовалютах (этап 7)."""

import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message

from models.db import update_xp
from services.cryptocompare import get_latest_news
from utils.http import ServiceError

router = Router()


@router.message(Command("news"))
async def cmd_news(message: Message):
    await message.answer("📰 Запрашиваю свежие новости...")
    try:
        news = await get_latest_news(5)
    except ServiceError:
        await message.answer("⚠️ Сервис новостей временно недоступен. Попробуй позже.")
        return

    if not news:
        await message.answer("⚠️ Новостей не нашлось. Попробуй позже.")
        return

    lines = ["<b>📰 Свежие новости о криптовалютах</b>\n"]
    for i, item in enumerate(news, 1):
        title = html.escape(item["title"], quote=False)
        source = html.escape(item["source"], quote=False)
        lines.append(f"{i}. <a href=\"{item['url']}\">{title}</a>")
        lines.append(f"   <i>источник: {source}</i>\n")

    await update_xp(message.from_user.id, 2)
    await message.answer(
        "\n".join(lines),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )