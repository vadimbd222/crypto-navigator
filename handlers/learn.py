"""Обработчик /learn: обучающие карточки (этап 7)."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from models.db import record_progress, update_xp

router = Router()

CARDS = {
    "blockchain": {
        "term": "Блокчейн",
        "definition": "Цепочка блоков с записями, которую нельзя незаметно изменить. Копии цепочки хранятся на тысячах компьютеров по всему миру, поэтому подделать историю транзакций практически невозможно.",
    },
    "bitcoin": {
        "term": "Биткоин",
        "definition": "Первая и самая дорогая криптовалюта. Создана в 2009 году человеком (или группой) под псевдонимом Сатоши Накамото. Всего будет выпущено только 21 миллион биткоинов — поэтому его называют «цифровым золотом».",
    },
    "wallet": {
        "term": "Кошелёк",
        "definition": "Программа или устройство, где хранятся твои ключи от криптовалюты. Сам кошелёк не содержит монеты — только ключи доступа к ним в блокчейне. Бывают горячие (приложение) и холодные (флешка-устройство).",
    },
    "keys": {
        "term": "Приватный и публичный ключ",
        "definition": "Публичный ключ — как номер счёта: его можно показывать, чтобы получать переводы. Приватный ключ — как пароль от сейфа: его нельзя никому показывать, иначе монеты украдут.",
    },
    "exchange": {
        "term": "Биржа",
        "definition": "Площадка, где криптовалюты покупают и продают по рыночной цене: Binance, Bybit, OKX и другие. Цена Bitcoin на бирже — это просто то, сколько люди сейчас готовы за него заплатить.",
    },
    "volatility": {
        "term": "Волатильность",
        "definition": "Сила колебаний цены. Криптовалюты очень волатильны: Bitcoin за день может измениться на 5–10%, а мелкие монеты — и на 50%. Отсюда главное правило: не вкладывай больше, чем готов потерять.",
    },
    "halving": {
        "term": "Халвинг",
        "definition": "Событие в сети Bitcoin примерно раз в 4 года: награда майнерам за блок уменьшается вдвое. Новых биткоинов появляется меньше — обычно после халвинга рынок оживает.",
    },
    "smart_contract": {
        "term": "Смарт-контракт",
        "definition": "Программа в блокчейне, которая выполняется сама: «если получу 100 монет — сразу отправлю билет». Никто не может отменить или подменить её работу в процессе.",
    },
}


def cards_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for key, card in CARDS.items():
        pair.append(InlineKeyboardButton(text=card["term"], callback_data=f"learn:{key}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("learn"))
async def cmd_learn(message: Message):
    await message.answer(
        "<b>🎓 Обучающие карточки</b>\n\n"
        "Выбери термин — объясню простыми словами.\n"
        "За каждую изученную карточку: <b>+5 XP</b>!",
        reply_markup=cards_keyboard(),
    )


@router.callback_query(F.data.startswith("learn:"))
async def cb_learn(callback: CallbackQuery):
    key = (callback.data or "").split(":", 1)[1]
    card = CARDS.get(key)
    if card is None:
        await callback.answer("Карточка не найдена", show_alert=True)
        return
    await callback.answer()
    await update_xp(callback.from_user.id, 5)
    await record_progress(callback.from_user.id, "learn_card", 5)
    await callback.message.answer(
        f"🎓 <b>{card['term']}</b>\n\n{card['definition']}\n\n<i>+5 XP</i>"
    )