"""Обработчик /price: курсы монет + inline-кнопки."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)

from models.db import update_xp
from services.coingecko import FIATS, POPULAR_COINS, SYMBOL_ALIASES, fmt, get_prices
from utils.http import ServiceError

router = Router()

COIN_EMOJI = {"usd": "🇺🇸", "eur": "🇪🇺", "rub": "🇷🇺"}


def coins_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с популярными монетами (2 кнопки в ряд)."""
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for coin_id, name in POPULAR_COINS.items():
        pair.append(InlineKeyboardButton(text=name, callback_data=f"price:{coin_id}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def price_text(coin_id: str) -> str:
    """Формирует текст с курсами монеты."""
    data = await get_prices(coin_id)
    prices = data["prices"]
    lines = [f"💰 <b>{data['name']}</b>\n"]
    for vs in FIATS:
        value = prices.get(vs)
        if value is not None:
            lines.append(f"{COIN_EMOJI[vs]} {fmt(value)} {vs.upper()}")
    change = prices.get("usd_24h_change")
    if change is not None:
        arrow = "📈" if change >= 0 else "📉"
        lines.append(f"\n{arrow} за 24 часа: {change:+.2f}%")
    if data.get("from_cache"):
        lines.append("\n<i>💡 данные из кэша — обновление раз в минуту</i>")
    return "\n".join(lines)


@router.message(Command("price"))
async def cmd_price(message: Message):
    await update_xp(message.from_user.id, 2)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        await message.answer(
            "<b>💰 Курсы монет</b>\n\n"
            "Напиши /price и монету, например:\n"
            "<code>/price bitcoin</code> или <code>/price btc</code>\n\n"
            "Или выбери из списка:",
            reply_markup=coins_keyboard(),
        )
        return

    query = parts[1].strip().lower()
    coin_id = SYMBOL_ALIASES.get(query, query)
    try:
        text = await price_text(coin_id)
    except LookupError:
        await message.answer(
            f"🤔 Не знаю монету <code>{query}</code>.\n"
            "Попробуй одну из популярных:",
            reply_markup=coins_keyboard(),
        )
        return
    except ServiceError:
        await message.answer("⚠️ Сервис курсов временно недоступен. Попробуй позже.")
        return
    await message.answer(
        text,
        reply_markup=coins_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data.startswith("price:"))
async def cb_price(callback: CallbackQuery):
    coin_id = (callback.data or "").split(":", 1)[1]
    try:
        text = await price_text(coin_id)
    except LookupError:
        await callback.answer("Монета не найдена", show_alert=True)
        return
    except ServiceError:
        await callback.answer("Сервис курсов недоступен", show_alert=True)
        return
    await callback.answer()
    await update_xp(callback.from_user.id, 2)
    await callback.message.answer(text)